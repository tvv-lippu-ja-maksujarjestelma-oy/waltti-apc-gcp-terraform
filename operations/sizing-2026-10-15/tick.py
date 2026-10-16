#!/usr/bin/env python3
"""Launchd entry point: observe, gate, then attempt frozen production promotion once."""
import datetime,fcntl,json,pathlib,subprocess,sys,time
ROOT=pathlib.Path(__file__).resolve().parent

def main():
 with (ROOT/'campaign.lock').open('w') as lock:
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:return
  if (ROOT/'production-result.json').exists():return
  if (ROOT/'production-attempt.json').exists():
   (ROOT/'production-result.json').write_text(json.dumps({'status':'BLOCKED','reason':'A prior production attempt was interrupted; review live state before retrying.'},indent=2));return
  subprocess.run([sys.executable,str(ROOT/'observe.py')],check=True,timeout=240)
  baseline=json.loads((ROOT/'observation-baseline.json').read_text())
  if time.time()<baseline['time']+86400:return
  status=json.loads((ROOT/'status.json').read_text())
  if not status['production_eligible']:
   (ROOT/'production-result.json').write_text(json.dumps({'status':'BLOCKED','reason':status['reason'],'at':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2));return
  subprocess.run([sys.executable,str(ROOT/'promote.py')],check=True,timeout=21600)
  # Notify the account owner locally; no Slack/email messages are sent.
  result=json.loads((ROOT/'production-result.json').read_text())
  subprocess.run(['osascript','-e','display notification "Sizing campaign finished. See analysis/sizing-campaign-20261015/production-result.json" with title "Waltti sizing"'],capture_output=True,timeout=15)
  print(json.dumps(result),flush=True)
if __name__=='__main__':main()
