#!/usr/bin/env python3
"""One-time production promotion of frozen, reviewed resource patches after observation."""
import argparse,copy,datetime,json,pathlib,subprocess,time
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

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--preflight-only',action='store_true');args=parser.parse_args()
 config=json.loads((ROOT/'promotion-config.json').read_text());plan=json.loads((ROOT/'production.json').read_text())
 if not args.preflight_only:
  baseline=json.loads((ROOT/'observation-baseline.json').read_text());samples=[json.loads(x) for x in (ROOT/'samples.jsonl').read_text().splitlines()]
  eligible,reason=observe.gate(samples,baseline['time'],time.time())
  if not eligible:raise RuntimeError(reason)
  if (ROOT/'production-result.json').exists():return
 before,apps,baseline,errors=preflight(config,plan)
 report={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'errors':errors,'targets':len(plan)}
 (ROOT/'production-preflight.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
 if args.preflight_only:return
 if errors:
  (ROOT/'production-result.json').write_text(json.dumps({'status':'BLOCKED','reason':errors,'at':report['at']},indent=2));return
 (ROOT/'production-attempt.json').write_text(json.dumps({'started':time.time()}))
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
   run(['gh','pr','ready',pr['url']]);run(['gh','pr','merge',pr['url'],'--'+pr['method'],'--match-head-commit',pr['head']])
  for p in plan:
   key=p['namespace']+'/'+p['name'];changed.append(p)
   print('PRODUCTION RESIZE',key,flush=True)
   run(command(p,['patch',p['kind'],p['name'],'--type=strategic','-p',json.dumps(p['patch'])]))
   if p['kind']!='CronJob':run(command(p,['rollout','status',p['kind']+'/'+p['name'],'--timeout=900s']),timeout=940)
   after=json.loads(run(command(p,['get',p['kind'],p['name'],'-o','json'])))
   if fingerprints(after)!=fingerprints(before[key]):raise RuntimeError('Unexpected non-resource change: '+key)
   health=observe.collect_environment('prod');checks=observe.assess({'errors':health['errors'],'environments':{'prod':health}},{'environments':{'prod':baseline}},started)
   if checks:raise RuntimeError(str(checks))
  run(['python3',str(ROOT/'certificate_smoke.py'),'prod-after',observe.CONTEXTS['prod'],'prod'],timeout=300)
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
    if p['kind']!='CronJob':run(command(p,['rollout','status',p['kind']+'/'+p['name'],'--timeout=900s']),timeout=940)
   except Exception as rollback_error:failures.append(str(rollback_error))
  result={'status':'FAILED','error':str(exc),'rollback_errors':failures,'argo_apps_left_without_automated_sync':[a['metadata']['name'] for a in paused]+(['argocd-settings'] if root_app else []),'reason':'Resource requests rolled back; reconcile merged source before restoring automated sync.'}
 (ROOT/'production-result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
if __name__=='__main__':main()
