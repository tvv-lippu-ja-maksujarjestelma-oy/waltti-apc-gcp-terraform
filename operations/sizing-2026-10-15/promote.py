#!/usr/bin/env python3
"""One-time production promotion of frozen, reviewed resource patches after observation."""
import argparse,copy,datetime,hashlib,json,pathlib,subprocess,time
import observe
ROOT=pathlib.Path(__file__).resolve().parent

def run(args,timeout=90):
 r=subprocess.run(args,text=True,capture_output=True,timeout=timeout)
 if r.returncode:raise RuntimeError(r.stderr[-3000:])
 return r.stdout

def podspec(obj):
 return obj['spec']['jobTemplate']['spec']['template']['spec'] if obj['kind']=='CronJob' else obj['spec']['template']['spec']

def command(p,args):return ['kubectl','--context='+p['context'],'--request-timeout=30s','-n',p['namespace']]+args

def fingerprints(obj):
 return {field:{c['name']:{k:v for k,v in c.items() if k!='resources'} for c in podspec(obj).get(field,[])} for field in ['containers','initContainers']}

def approved_pr(pr,current):
 if current['headRefOid']!=pr['head']:raise RuntimeError('PR changed since review: '+pr['url'])
 if current['state']!='OPEN' or current['mergeable']!='MERGEABLE':raise RuntimeError('PR not mergeable: '+pr['url'])
 for check in current['statusCheckRollup']:
  if check.get('status','COMPLETED')!='COMPLETED' or check.get('conclusion',check.get('state')) not in ['SUCCESS','SKIPPED','NEUTRAL']:
   raise RuntimeError('PR check not successful: '+pr['url'])

def preflight(config,plan):
 objects={};errors=[]
 for repo,head in config.get('default_branch_heads',{}).items():
  if run(['gh','api','repos/'+repo+'/git/ref/heads/main','--jq','.object.sha']).strip()!=head:errors.append('Default branch changed since review: '+repo)
 for pr in config['pull_requests']:
  try:approved_pr(pr,json.loads(run(['gh','pr','view',pr['url'],'--json','headRefOid,state,mergeable,statusCheckRollup'])))
  except Exception as exc:errors.append(str(exc))
 for p in plan:
  key=p['namespace']+'/'+p['name']
  obj=json.loads(run(command(p,['get',p['kind'],p['name'],'-o','json'])))
  objects[key]=obj
  images={c['name']:c['image'] for c in podspec(obj)['containers']}
  if images!=config['production_images'][key]:errors.append('Production image changed: '+key)
  run(command(p,['patch',p['kind'],p['name'],'--type=strategic','-p',json.dumps(p['patch']),'--dry-run=server','-o','name']))
 apps=observe.kubectl('dev',['-n','argocd','get','applications.argoproj.io','-o','json'])['items']
 affected=[];target_names={p['name'] for p in plan if p['namespace']=='prod'}
 for app in apps:
  status=app.get('status',{});resources=status.get('resources',[])
  if not any(r.get('namespace')=='prod' and r.get('name') in target_names for r in resources):continue
  affected.append(app)
  if status.get('sync',{}).get('status')!='Synced' or status.get('health',{}).get('status')!='Healthy' or app.get('operation'):
   errors.append('Argo drift/unhealthy/in-flight operation: '+app['metadata']['name'])
 if not affected:errors.append('No production Argo applications found')
 prod=observe.collect_environment('prod')
 errors+=prod['errors']
 operations=json.loads(run(['gcloud','container','operations','list','--project=apc-prod-397611','--location=europe-west3','--filter=status!=DONE','--format=json']))
 if operations:errors.append('GKE operation active in production')
 return objects,affected,prod,errors

def rollback_patch(p,before):
 patch=copy.deepcopy(p['patch']);spec=patch['spec']['jobTemplate']['spec']['template']['spec'] if p['kind']=='CronJob' else patch['spec']['template']['spec']
 for field in ['containers','initContainers']:
  for c in spec.get(field,[]):
   previous=next(x for x in podspec(before).get(field,[]) if x['name']==c['name']).get('resources',{})
   for bucket,values in c['resources'].items():
    for resource in values:values[resource]=previous.get(bucket,{}).get(resource)
 return patch

def validate_supervised_approval(approval,plan_bytes):
 if approval.get('approved_plan_sha256')!=hashlib.sha256(plan_bytes).hexdigest():raise RuntimeError('Approved sizing scope changed')
 plan=json.loads(plan_bytes)
 if len(plan)!=18 or any(p['context']!=observe.CONTEXTS['prod'] or p['name'].startswith('vehicle-position-splitter-') for p in plan):raise RuntimeError('Supervised scope must exclude all splitters and target only production')

def pod_images(plan):
 pods=observe.kubectl('prod',['get','pods','-A','-o','json'])['items'];out={}
 for p in plan:
  key=p['namespace']+'/'+p['name'];out[key]={}
  for pod in pods:
   if pod['metadata']['namespace']!=p['namespace'] or not pod['metadata']['name'].startswith(p['name']+'-'):continue
   for c in pod.get('status',{}).get('containerStatuses',[]):
    if c.get('imageID'):out[key].setdefault(c['name'],set()).add(c['imageID'].split('@')[-1])
 return out

def verify_images(plan,expected):
 actual=pod_images(plan)
 for key,containers in expected.items():
  for name,digests in containers.items():
   if actual.get(key,{}).get(name,set())-digests:raise RuntimeError('Running image digest changed: '+key+'/'+name)

def await_healthy(baseline,started,timeout=300):
 deadline=time.monotonic()+timeout
 while True:
  health=observe.collect_environment('prod')
  checks=observe.assess({'errors':health['errors'],'environments':{'prod':health}},{'environments':{'prod':baseline}},started)
  if not checks:
   with (ROOT/'production-health.jsonl').open('a') as f:f.write(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'health':health})+'\n')
   return health
  hard=[x for x in checks if 'restart/OOM' in x or 'image changed' in x or 'failed job' in x]
  if hard or time.monotonic()>=deadline:raise RuntimeError(str(checks))
  print('Waiting for production to settle:',str(checks)[:500],flush=True);time.sleep(15)

def roll_statefulset(p,before,baseline,started,expected_images):
 replicas=before['spec'].get('replicas',1)
 def partition(n):
  run(command(p,['patch','statefulset',p['name'],'--type=merge','-p',json.dumps({'spec':{'updateStrategy':{'type':'RollingUpdate','rollingUpdate':{'partition':n}}}})]))
 partition(replicas)
 run(command(p,['patch','statefulset',p['name'],'--type=strategic','-p',json.dumps(p['patch'])]))
 for ordinal in reversed(range(replicas)):
  print('ROLLING PULSAR POD',p['name']+'-'+str(ordinal),flush=True);partition(ordinal)
  print(run(command(p,['rollout','status','statefulset/'+p['name'],'--timeout=900s']),timeout=940).strip(),flush=True)
  await_healthy(baseline,started,timeout=300)
  verify_images([p],{p['namespace']+'/'+p['name']:expected_images})
 run(command(p,['patch','statefulset',p['name'],'--type=json','-p',json.dumps([{'op':'replace','path':'/spec/updateStrategy','value':before['spec']['updateStrategy']}])]))


def main():
 parser=argparse.ArgumentParser();parser.add_argument('--preflight-only',action='store_true');parser.add_argument('--supervised-approved',action='store_true');args=parser.parse_args()
 config=json.loads((ROOT/'promotion-config.json').read_text());plan=json.loads((ROOT/'production.json').read_text())
 if args.supervised_approved:
  approval=json.loads((ROOT/'supervised-production-approval.json').read_text())
  validate_supervised_approval(approval,(ROOT/'production.json').read_bytes())
 elif not args.preflight_only:
  baseline=json.loads((ROOT/'observation-baseline.json').read_text());samples=[json.loads(x) for x in (ROOT/'samples.jsonl').read_text().splitlines()]
  eligible,reason=observe.gate(samples,baseline['time'],time.time())
  if not eligible:raise RuntimeError(reason)
  if (ROOT/'production-result.json').exists():return
 if not args.preflight_only and ((ROOT/'production-result.json').exists() or (ROOT/'production-attempt.json').exists()):raise RuntimeError('Prior production attempt exists; inspect it before continuing')
 before,apps,baseline,errors=preflight(config,plan)
 report={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'errors':errors,'targets':len(plan)}
 (ROOT/'production-preflight.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
 if args.preflight_only:return
 if errors:
  (ROOT/'production-result.json').write_text(json.dumps({'status':'BLOCKED','reason':errors,'at':report['at']},indent=2));return
 (ROOT/'production-attempt.json').write_text(json.dumps({'started':time.time()}))
 (ROOT/'production-baseline.json').write_text(json.dumps({'objects':before,'applications':apps,'health':baseline},indent=2))
 expected_images=pod_images(plan)
 changed=[];paused=[];root_app=None;started=time.time()
 try:
  run(['python3',str(ROOT/'pulsar_init_smoke.py'),observe.CONTEXTS['prod'],'prod-before'],timeout=400)
  # Pause the parent first so it cannot re-enable child auto-sync during rollout.
  root_app=observe.kubectl('dev',['-n','argocd','get','applications.argoproj.io','argocd-settings','-o','json'])
  if root_app.get('operation'):raise RuntimeError('Parent Argo reconciliation is in flight')
  observe.kubectl('dev',['-n','argocd','patch','applications.argoproj.io','argocd-settings','--type=merge','-p',json.dumps({'spec':{'syncPolicy':{'automated':None}}}),'-o','json'])
  # Disable automated reconciliation during controlled rollouts; do not sync full applications.
  for app in apps:
   name=app['metadata']['name'];observe.kubectl('dev',['-n','argocd','patch','application.argoproj.io',name,'--type=merge','-p',json.dumps({'spec':{'syncPolicy':{'automated':None}}}),'-o','json']);paused.append(app)
  for pr in config['pull_requests']:
   if json.loads(run(['gh','pr','view',pr['url'],'--json','isDraft']))['isDraft']:run(['gh','pr','ready',pr['url']])
   run(['gh','pr','merge',pr['url'],'--'+pr['method'],'--match-head-commit',pr['head']])
  for p in plan:
   key=p['namespace']+'/'+p['name'];changed.append(p)
   print('PRODUCTION RESIZE',key,flush=True)
   if p['kind']=='StatefulSet':
    roll_statefulset(p,before[key],baseline,started,expected_images[key])
   else:
    run(command(p,['patch',p['kind'],p['name'],'--type=strategic','-p',json.dumps(p['patch'])]))
    if p['kind']!='CronJob':print(run(command(p,['rollout','status',p['kind']+'/'+p['name'],'--timeout=900s']),timeout=940).strip(),flush=True)
   after=json.loads(run(command(p,['get',p['kind'],p['name'],'-o','json'])))
   if fingerprints(after)!=fingerprints(before[key]):raise RuntimeError('Unexpected non-resource change: '+key)
   await_healthy(baseline,started,timeout=300)
   verify_images(plan,expected_images)
   (ROOT/'production-progress.json').write_text(json.dumps({'last_verified':key,'completed':len(changed),'total':len(plan),'at':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2))
  run(['python3',str(ROOT/'certificate_smoke.py'),'prod-after',observe.CONTEXTS['prod'],'prod'],timeout=300)
  # Keep automatic reconciliation paused while node consolidation settles.
  for minute in range(15):
   await_healthy(baseline,started,timeout=300)
   verify_images(plan,expected_images)
   print('PRODUCTION OBSERVATION',minute+1,'/15 healthy',flush=True)
   time.sleep(60)
  await_healthy(baseline,started,timeout=300)
  for app in paused:
   current_app=observe.kubectl('dev',['-n','argocd','get','applications.argoproj.io',app['metadata']['name'],'-o','json'])
   if current_app['spec']['source']!=app['spec']['source']:raise RuntimeError('Application source changed during sizing: '+app['metadata']['name'])
  for app in paused:
   observe.kubectl('dev',['-n','argocd','patch','application.argoproj.io',app['metadata']['name'],'--type=merge','-p',json.dumps({'spec':{'syncPolicy':app['spec']['syncPolicy']}}),'-o','json'])
  observe.kubectl('dev',['-n','argocd','patch','applications.argoproj.io','argocd-settings','--type=merge','-p',json.dumps({'spec':{'syncPolicy':root_app['spec']['syncPolicy']}}),'-o','json'])
  result={'status':'SUCCEEDED','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'targets':len(changed)}
 except Exception as exc:
  failures=[]
  for p in reversed(changed):
   try:
    run(command(p,['patch',p['kind'],p['name'],'--type=strategic','-p',json.dumps(rollback_patch(p,before[p['namespace']+'/'+p['name']]))]))
    if p['kind']=='StatefulSet':run(command(p,['patch',p['kind'],p['name'],'--type=json','-p',json.dumps([{'op':'replace','path':'/spec/updateStrategy','value':before[p['namespace']+'/'+p['name']]['spec']['updateStrategy']}])]))
    if p['kind']!='CronJob':run(command(p,['rollout','status',p['kind']+'/'+p['name'],'--timeout=900s']),timeout=940)
   except Exception as rollback_error:failures.append(str(rollback_error))
  result={'status':'FAILED','error':str(exc),'rollback_errors':failures,'argo_apps_left_without_automated_sync':[a['metadata']['name'] for a in paused]+(['argocd-settings'] if root_app else []),'reason':'Resource requests rolled back; reconcile merged source before restoring automated sync.'}
 (ROOT/'production-result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
if __name__=='__main__':main()
