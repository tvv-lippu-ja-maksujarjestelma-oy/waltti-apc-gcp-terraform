#!/usr/bin/env python3
"""Read-only sizing observation. Missing evidence always blocks production eligibility."""
import argparse, concurrent.futures, datetime, fcntl, json, pathlib, subprocess, time
ROOT = pathlib.Path(__file__).resolve().parent
CONTEXTS = {'dev':'gke_apc-sandbox_europe-west3_prototype','staging':'gke_apc-staging-388907_europe-west3_staging','prod':'gke_apc-prod-397611_europe-west3_prod'}
PULSAR = '''import json,urllib.request
base="http://pulsar-broker:8080/admin/v2/"
def get(path):
 for attempt in range(3):
  try:
   with urllib.request.urlopen(base+path,timeout=12) as r:return json.load(r)
  except Exception:
   if attempt==2:raise
out={}
for ns in get("namespaces/TENANT"):
 for topic in get("persistent/"+ns):
  stats=get("persistent/"+topic.removeprefix("persistent://")+"/stats")
  out[topic]={"in":stats.get("msgInCounter",0),"out":stats.get("msgOutCounter",0),"subscriptions":{k:{"backlog":v.get("msgBacklog",0),"consumers":len(v.get("consumers",[]))} for k,v in stats.get("subscriptions",{}).items() if not k.startswith("reader-")}}
print(json.dumps(out))'''
def kubectl(env,args,timeout=90):
 r=subprocess.run(['kubectl','--context='+CONTEXTS[env],'--request-timeout=25s']+args,text=True,capture_output=True,timeout=timeout)
 if r.returncode: raise RuntimeError(r.stderr[-2000:])
 return json.loads(r.stdout)
def collect_environment(env):
 namespaces={env,'pulsar','cert-manager'} | ({'argocd','staging'} if env=='dev' else set())
 result={'errors':[], 'workloads':{}, 'pods':{}, 'metrics':{}, 'certificates':{}, 'topics':{}}
 for resource in ['deployments','statefulsets','pods','jobs','certificates.cert-manager.io']:
  for o in kubectl(env,['get',resource,'-A','-o','json'])['items']:
   ns=o['metadata']['namespace'];name=o['metadata']['name'];key=ns+'/'+name
   if ns not in namespaces: continue
   if resource in ['deployments','statefulsets']:
    desired=o['spec'].get('replicas',1);ready=o.get('status',{}).get('readyReplicas',0)
    result['workloads'][key]={'ready':ready,'desired':desired,'generation':o['metadata']['generation'],'observed':o.get('status',{}).get('observedGeneration',0),'images':{c['name']:c['image'] for c in o['spec']['template']['spec']['containers']},'resources':{c['name']:c.get('resources',{}) for c in o['spec']['template']['spec']['containers']}}
    if ready!=desired or result['workloads'][key]['observed']<o['metadata']['generation']:result['errors'].append(key+': workload not ready')
   elif resource=='pods':
    statuses=o.get('status',{}).get('containerStatuses',[])+o.get('status',{}).get('initContainerStatuses',[])
    phase=o.get('status',{}).get('phase','Unknown')
    result['pods'][o['metadata']['uid']]={'name':key,'phase':phase,'restarts':sum(c.get('restartCount',0) for c in statuses),'oom':any(c.get('lastState',{}).get('terminated',{}).get('reason')=='OOMKilled' or c.get('state',{}).get('terminated',{}).get('reason')=='OOMKilled' for c in statuses)}
    is_job=any(owner.get('kind')=='Job' for owner in o['metadata'].get('ownerReferences',[]))
    if is_job and phase=='Pending' and time.time()-datetime.datetime.fromisoformat(o['metadata']['creationTimestamp'].replace('Z','+00:00')).timestamp()>300:result['errors'].append(key+': batch pod pending over 5 minutes')
    if not is_job and phase not in ['Succeeded','Failed'] and not o['metadata'].get('deletionTimestamp') and not any(c['type']=='Ready' and c['status']=='True' for c in o.get('status',{}).get('conditions',[])):result['errors'].append(key+': pod not ready')
   elif resource=='jobs':
    if o.get('status',{}).get('failed',0) and any(c['type']=='Failed' and c['status']=='True' for c in o.get('status',{}).get('conditions',[])):
     result.setdefault('failed_jobs',{})[key]=o['metadata']['creationTimestamp']
   else:
    ready=any(c['type']=='Ready' and c['status']=='True' for c in o.get('status',{}).get('conditions',[]))
    result['certificates'][key]={'ready':ready,'expires':o.get('status',{}).get('notAfter')}
    if not ready:result['errors'].append(key+': certificate not ready')
 metrics=kubectl(env,['get','--raw','/apis/metrics.k8s.io/v1beta1/pods'])
 for o in metrics['items']:
  if o['metadata']['namespace'] in namespaces:result['metrics'][o['metadata']['namespace']+'/'+o['metadata']['name']]={c['name']:c['usage'] for c in o['containers']}
 if not result['metrics']:result['errors'].append('No container metrics')
 tenant={'dev':'apc-sandbox','staging':'apc-staging','prod':'apc-prod'}[env]
 result['topics']=kubectl(env,['-n','pulsar','exec','pulsar-broker-0','-c','pulsar-broker','--','python3','-c',PULSAR.replace('TENANT',tenant)],timeout=180)
 if not result['topics']:result['errors'].append('No Pulsar topic statistics')
 expected=['source/mqtt-apc-from-vehicle','deduplicated/mqtt-apc-from-vehicle-deduplicated','aggregated/aggregated-apc-journey','anonymized/anonymized-apc-journey']
 expected += ['source/'+prefix+'-fi-'+city for prefix in ['gtfsrt-vp','splitted-gtfsrt-vp'] for city in ['jyvaskyla','kuopio','lahti']]
 for name in expected:
  topic='persistent://'+tenant+'/'+name;stats=result['topics'].get(topic)
  if not stats:result['errors'].append('Missing core topic: '+name)
  elif not any(sub['consumers']>0 for sub in stats['subscriptions'].values()):result['errors'].append('No connected core topic consumer: '+name)
 for name,subs in {'aggregated/aggregated-apc-journey':['anonymizer-apc-sub','pulsar-mqtt-forwarder-raportointi'],'anonymized/anonymized-apc-journey':['pulsar-mqtt-forwarder-rtpi']}.items():
  stats=result['topics'].get('persistent://'+tenant+'/'+name,{})
  for sub in subs:
   if not stats.get('subscriptions',{}).get(sub,{}).get('consumers',0):result['errors'].append('Missing critical consumer: '+sub)
 result['bookkeeper']=kubectl(env,['-n','pulsar','exec','pulsar-bookie-0','-c','pulsar-bookie','--','python3','-c',"import urllib.request,json; base='http://localhost:8000/api/v1/'; get=lambda p:json.load(urllib.request.urlopen(base+p,timeout=15)); cluster=get('bookie/cluster_info'); print(json.dumps({'cluster':cluster,'underreplicated_ledgers':get('autorecovery/list_under_replicated_ledger/') if cluster['clusterUnderReplicated'] else []}))"])
 cluster=result['bookkeeper']['cluster']
 if cluster.get('writableBookiesCount')!=4 or cluster.get('readonlyBookiesCount') or cluster.get('unavailableBookiesCount') or not cluster.get('auditorElected') or not cluster.get('ledgerReplicationEnabled'):result['errors'].append('BookKeeper replication/writability unhealthy')
 known=json.loads((ROOT/'known-underreplication.json').read_text()) if (ROOT/'known-underreplication.json').exists() else {}
 unexpected=set(result['bookkeeper']['underreplicated_ledgers'])-set(known.get(env,[]))
 if unexpected:result['errors'].append('New underreplicated ledgers: '+str(sorted(unexpected)[:20]))
 return result

def sample():
 out={'time':time.time(),'iso':datetime.datetime.now(datetime.timezone.utc).isoformat(),'environments':{},'errors':[]}
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  futures={pool.submit(collect_environment,e):e for e in ['dev','staging']}
  for f,e in futures.items():
   try:
    out['environments'][e]=f.result();out['errors'] += [e+': '+x for x in out['environments'][e]['errors']]
   except Exception as exc:out['errors'].append(e+': collection failed: '+str(exc))
 return out

def assess(current,baseline,start):
 errors=list(current['errors'])
 for env,b in baseline['environments'].items():
  c=current['environments'].get(env)
  if not c:continue
  for key,w in b['workloads'].items():
   if key not in c['workloads']:errors.append(env+': missing workload '+key)
   elif c['workloads'][key]['images']!=w['images']:errors.append(env+': image changed '+key)
  for uid,p in c['pods'].items():
   if p['phase'] in ['Succeeded','Failed']:continue
   if p['oom'] or p['restarts']>b['pods'].get(uid,{}).get('restarts',0):errors.append(env+': restart/OOM '+p['name'])
  for key,created in c.get('failed_jobs',{}).items():
   if datetime.datetime.fromisoformat(created.replace('Z','+00:00')).timestamp()>=start:errors.append(env+': failed job '+key)
  for topic,stats in c['topics'].items():
   prior=b['topics'].get(topic,{}).get('subscriptions',{})
   for sub,value in stats['subscriptions'].items():
    if value['backlog']>max(2000,prior.get(sub,{}).get('backlog',0)+2000):errors.append(env+': backlog '+topic+'/'+sub+'='+str(value['backlog']))
 return errors

def gate(samples,start,now):
 if now-start<86400:return False,'24 hours not complete'
 relevant=sorted((s for s in samples if s['time']>=start),key=lambda s:s['time'])
 if not relevant or relevant[0]['time']-start>600 or now-relevant[-1]['time']>600:return False,'Missing observation coverage'
 if any(b['time']-a['time']>900 for a,b in zip(relevant,relevant[1:])):return False,'Observation gap over 15 minutes'
 if any(s.get('errors') for s in relevant):return False,'An unhealthy or unknown sample needs review'
 return True,'24 hours of healthy observations complete; production preflight still required'

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--arm',action='store_true');parser.add_argument('--sample',action='store_true');args=parser.parse_args()
 with (ROOT/'observer.lock').open('w') as lock:
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:return
  current=sample()
  if args.sample:
   (ROOT/'preflight.json').write_text(json.dumps(current,indent=2));print(json.dumps({'errors':current['errors'],'workloads':{e:len(v['workloads']) for e,v in current['environments'].items()}}));return
  baseline_path=ROOT/'observation-baseline.json'
  if args.arm:
   if current['errors']:raise RuntimeError('Cannot arm: '+str(current['errors']))
   if baseline_path.exists():raise RuntimeError('Already armed; baseline cannot be reset silently')
   baseline_path.write_text(json.dumps(current,indent=2))
  baseline=json.loads(baseline_path.read_text());current['errors']=assess(current,baseline,baseline['time'])
  with (ROOT/'samples.jsonl').open('a') as f:f.write(json.dumps(current)+'\n')
  samples=[json.loads(s) for s in (ROOT/'samples.jsonl').read_text().splitlines()]
  eligible,reason=gate(samples,baseline['time'],current['time'])
  report={'updated':current['iso'],'observation_started':baseline['iso'],'earliest_production':datetime.datetime.fromtimestamp(baseline['time']+86400,datetime.timezone.utc).isoformat(),'samples':len(samples),'errors':current['errors'],'production_eligible':eligible,'reason':reason}
  (ROOT/'status.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
if __name__=='__main__':main()
