import json
import os
import subprocess
import time
import urllib.request
import uuid
from pathlib import Path

root = Path(__file__).resolve().parents[1]
base = "http://localhost:" + os.environ.get("HTTP_PORT", "8083")


def request(path, payload=None, expected=200):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(base + path, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as response:
        assert response.status == expected, response.status
        return json.load(response)


assert request("/health") == {"status": "ok"}
note = request("/notes", {"text": "ansible-" + uuid.uuid4().hex}, expected=201)
assert note in request("/notes")
print("PASS: Nginx /health HTTP 200, note write/read", flush=True)

ids = subprocess.check_output(["docker", "compose", "ps", "-q"], cwd=root, text=True).split()
containers = json.loads(subprocess.check_output(["docker", "inspect", *ids], text=True))
assert len(containers) == 3
for container in containers:
    service = container["Config"]["Labels"]["com.docker.compose.service"]
    assert set(container["NetworkSettings"]["Networks"]) == {"mipt-prac3_lab"}
    bindings = container["HostConfig"]["PortBindings"] or {}
    if service == "nginx":
        assert set(bindings) == {"80/tcp"}
    else:
        assert not bindings
print("PASS: three containers, one network, only Nginx published", flush=True)

subprocess.run(["docker", "compose", "restart", "app"], cwd=root, check=True)
for _ in range(60):
    try:
        if request("/health") == {"status": "ok"}:
            break
    except OSError:
        pass
    time.sleep(1)
else:
    raise RuntimeError("Application did not start after restart")
assert note in request("/notes")
print("PASS: launch script starts after container restart; SQLite note survived", flush=True)
