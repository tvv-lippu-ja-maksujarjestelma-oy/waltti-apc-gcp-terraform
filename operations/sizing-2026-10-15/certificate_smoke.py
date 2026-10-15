import collections
import datetime
import json
import pathlib
import subprocess
import sys
import time
import uuid

phase = sys.argv[1]
prefix = 'cost-sizing-' + uuid.uuid4().hex[:8]
base = ['kubectl', '--context='+sys.argv[2], '--request-timeout=20s', '-n', sys.argv[3]]
samples = []
created = []

def run(args, obj=None):
    result = subprocess.run(base + args, input=json.dumps(obj) if obj else None,
                            text=True, capture_output=True, timeout=75)
    if result.returncode:
        raise RuntimeError(result.stderr[:1500])
    return result.stdout

try:
    run(['create', '-f', '-'], {'apiVersion': 'cert-manager.io/v1', 'kind': 'Issuer',
        'metadata': {'name': prefix}, 'spec': {'selfSigned': {}}})
    for i in range(3):
        name = prefix + '-' + str(i)
        obj = {'apiVersion': 'cert-manager.io/v1', 'kind': 'Certificate',
               'metadata': {'name': name}, 'spec': {'secretName': name,
               'dnsNames': ['cost-sizing.invalid'], 'duration': '1h',
               'privateKey': {'algorithm': 'ECDSA', 'size': 256},
               'issuerRef': {'name': prefix, 'kind': 'Issuer'}}}
        started = time.monotonic()
        run(['create', '-f', '-'], obj)
        created.append(name)
        run(['wait', 'certificate/' + name, '--for=condition=Ready', '--timeout=60s'])
        certificate = json.loads(run(['get', 'certificate/' + name, '-o', 'json']))
        assert any(c['type'] == 'Ready' and c['status'] == 'True'
                   for c in certificate['status']['conditions'])
        sample = {'issuance_seconds': time.monotonic() - started, 'ready': True}
        samples.append(sample)
        print(phase, sample, flush=True)
finally:
    for name in created:
        run(['delete', 'certificate/' + name, '--ignore-not-found', '--wait=false'])
        run(['delete', 'secret/' + name, '--ignore-not-found', '--wait=false'])
    run(['delete', 'issuer/' + prefix, '--ignore-not-found', '--wait=false'])

pathlib.Path('/tmp/waltti-cm-smoke-' + phase + '.json').write_text(json.dumps({
    'phase': phase, 'time': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'samples': samples, 'scope': 'Self-signed issuance and webhook admission in dev; does not exercise external ACME DNS challenges.'}, indent=2))
