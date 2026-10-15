import copy,json,subprocess,sys,time,pathlib
ctx=sys.argv[1]; label=sys.argv[2]
def run(args,obj=None):
 r=subprocess.run(['kubectl','--context='+ctx,'--request-timeout=30s','-n','pulsar']+args,input=json.dumps(obj) if obj else None,text=True,capture_output=True,timeout=300)
 if r.returncode: raise RuntimeError(r.stderr)
 return r.stdout
sts=json.loads(run(['get','statefulset/pulsar-bookie','-o','json']))
c=copy.deepcopy(sts['spec']['template']['spec']['initContainers'][0]); c['name']='verify-clusterid'; c['command']=['sh','-c']; c['args']=['set -e; bin/apply-config-from-env.py conf/bookkeeper.conf; export BOOKIE_MEM="-Xmx128M"; for i in 1 2 3; do time timeout 15 bin/bookkeeper shell whatisinstanceid; done']; c['resources']['requests']['cpu']='500m'; c['resources']['limits']['cpu']='1'
name='sizing-init-'+str(int(time.time()))
job={'apiVersion':'batch/v1','kind':'Job','metadata':{'name':name},'spec':{'backoffLimit':0,'activeDeadlineSeconds':240,'ttlSecondsAfterFinished':3600,'template':{'metadata':{'labels':{'app':'pulsar','release':'pulsar','component':'sizing-check'}},'spec':{'restartPolicy':'Never','serviceAccountName':'pulsar-bookie','securityContext':sts['spec']['template']['spec']['securityContext'],'containers':[c]}}}}
run(['create','-f','-'],job); print(label,name,flush=True)
try:
 run(['wait','--for=condition=complete','job/'+name,'--timeout=260s'])
 logs=run(['logs','job/'+name]); pathlib.Path('/Users/ilkka/Waltti/analysis/sizing-campaign-20261015/'+label+'-init-smoke.log').write_text(logs); print(label, '\n'.join(x for x in logs.splitlines() if x.startswith('real') or 'InstanceId:' in x),flush=True)
 pathlib.Path('/Users/ilkka/Waltti/analysis/sizing-campaign-20261015/'+label+'-pulsar-init-smoke.json').write_text(json.dumps(json.loads(run(['get','job/'+name,'-o','json'])),indent=2))
except:
 print(run(['get','pods','-l','job-name='+name,'-o','wide']),flush=True)
 print(run(['logs','job/'+name]),flush=True)
 raise
