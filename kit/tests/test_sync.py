"""Run scripts/sync.sh against a fake org: local bare repos, and a stub `gh`
that lists them, clones them and records `pr create` calls."""
import os
import pathlib
import shutil
import subprocess

KIT = pathlib.Path(__file__).parent.parent
TEMPLATES = KIT / "templates"


def git(*args, cwd):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
                   cwd=cwd, check=True, capture_output=True)


def make_repo(org, name, with_templates):
    work = org / f"{name}-work"
    work.mkdir()
    git("init", "-q", "-b", "main", cwd=work)
    (work / "README.md").write_text(name)
    if with_templates:
        shutil.copytree(TEMPLATES, work, dirs_exist_ok=True)
    git("add", "-A", cwd=work)
    git("commit", "-qm", "init", cwd=work)
    git("clone", "-q", "--bare", str(work), str(org / f"{name}.git"), cwd=org)


def run_sync(tmp_path):
    stub = tmp_path / "bin" / "gh"
    stub.parent.mkdir(exist_ok=True)
    stub.write_text(f"""#!/usr/bin/env bash
case "$1 $2" in
  "repo list") printf '%s\\n' current stale .github-private ;;
  "repo clone") git clone -q "{tmp_path}/org/${{3#*/}}.git" "$4" ;;
  "pr create") echo "$PWD $*" >> "{tmp_path}/prs.log" ;;
esac
""")
    stub.chmod(0o755)
    env = {**os.environ, "PATH": f"{stub.parent}:{os.environ['PATH']}", "ORG": "acme",
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    return subprocess.run(["bash", str(KIT / "scripts" / "sync.sh")], env=env,
                          capture_output=True, text=True)


def test_sync_opens_one_pr_only_where_templates_differ(tmp_path):
    org = tmp_path / "org"
    org.mkdir()
    make_repo(org, "current", with_templates=True)
    make_repo(org, "stale", with_templates=False)

    r = run_sync(tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    prs = (tmp_path / "prs.log").read_text().splitlines()
    assert len(prs) == 1 and "/stale " in prs[0]

    branches = subprocess.run(["git", "branch", "--list", "org-kit-sync-*"],
                              cwd=org / "stale.git", capture_output=True, text=True).stdout
    assert branches.strip()

    r = run_sync(tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert len((tmp_path / "prs.log").read_text().splitlines()) == 1
