"""Run the preToolUse command from templates/.github/hooks/org-deny.json exactly as Copilot does:
the event JSON on stdin, a decision JSON on stdout."""
import json
import pathlib
import subprocess

import pytest

HOOKS = pathlib.Path(__file__).parent.parent / "templates" / ".github" / "hooks" / "org-deny.json"


def decide(tool, args):
    hook = json.loads(HOOKS.read_text())["hooks"]["preToolUse"][0]
    event = {"sessionId": "t", "timestamp": 0, "cwd": "/w", "toolName": tool, "toolArgs": args}
    r = subprocess.run(["bash", "-c", hook["bash"]], input=json.dumps(event),
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout).get("permissionDecision") if r.stdout.strip() else "default"


@pytest.mark.parametrize("tool,args", [
    ("bash", {"command": "git push --force origin main"}),
    ("bash", {"command": "git push -f"}),
    ("bash", {"command": "git reset --hard HEAD~3"}),
    ("bash", {"command": "rm -rf /"}),
    ("bash", {"command": "rm -rf ~"}),
    ("bash", {"command": "rm -fr $HOME"}),
    ("bash", {"command": "cd x && rm -rf ."}),
    ("bash", {"command": "cat .env"}),
    ("bash", {"command": "cat ~/.ssh/id_ed25519"}),
    ("view", {"path": "/w/config/prod.env"}),
    ("view", {"path": "/w/certs/server.pem"}),
])
def test_denies(tool, args):
    assert decide(tool, args) == "deny"


@pytest.mark.parametrize("tool,args", [
    ("bash", {"command": "git push origin main"}),
    ("bash", {"command": "git push --force-with-lease"}),
    ("bash", {"command": "git reset --soft HEAD~1"}),
    ("bash", {"command": "rm -rf build/"}),
    ("bash", {"command": "cat .env.example"}),
    ("view", {"path": "/w/src/environment.py"}),
])
def test_allows(tool, args):
    assert decide(tool, args) == "default"
