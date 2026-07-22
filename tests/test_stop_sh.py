#!/usr/bin/env python3
"""Tests for stop.sh teardown (fake docker/pgrep/lsof shims on PATH).

The fakes never touch the real Docker daemon and only ever report the
detached sleeper processes this test spawns, so nothing real is killed.
"""

import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import deploy

REPO_ROOT = Path(__file__).resolve().parent.parent
SERVER_PORT = 5901


def spawn_detached(extra_args: list) -> int:
    """Start an orphaned python sleeper and return its PID.

    Orphaned (double-forked via bash) so init reaps it on death and kill -0
    inside stop.sh stops succeeding immediately, instead of seeing a zombie
    child of this test process for 10 seconds.
    """
    args = " ".join(shlex.quote(a) for a in extra_args)
    out = subprocess.run(
        ["bash", "-c",
         f'{shlex.quote(sys.executable)} -c "import time; time.sleep(120)" {args} '
         f'> /dev/null 2>&1 & echo $!'],
        capture_output=True, text=True, check=True)
    return int(out.stdout.strip())


def is_alive(pid: int) -> bool:
    """True while a PID exists (signal 0 probe)"""
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False


def wait_gone(pid: int, timeout: float = 5.0) -> bool:
    """Wait until a PID disappears, returning False on timeout"""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if not is_alive(pid):
            return True
        time.sleep(0.1)
    return False


def write_fake_bin(bin_dir: Path, name: str, body: str):
    """Create an executable shim named after a real command"""
    path = bin_dir / name
    path.write_text("#!/bin/bash\n" + body)
    path.chmod(0o755)


def build_sandbox(tmp: Path, sb: dict) -> dict:
    """Create fake docker/pgrep/lsof on PATH and return the env for stop.sh.

    The fake lsof reports BOTH the instance's server and a foreign python
    process as listeners on SERVER_PORT, and answers cwd queries with the
    workspace only for the instance's server — the port-collision scenario
    stop.sh must not over-kill.
    """
    bin_dir = tmp / "bin"
    bin_dir.mkdir()
    write_fake_bin(bin_dir, "docker", f'''echo "$@" >> "{sb['docker_log']}"
case "$*" in
    *config_files*) echo "{sb['compose_file']}" ;;
    *"--filter label=com.docker.compose.project --format"*)
        printf '%s\\n' "toolomics_{sb['instance_id']}_shell" "toolomics_{sb['instance_id']}_searxng" \\
            "toolomics_deadbeef_shell" "unrelated_project" ;;
esac
exit 0
''')
    write_fake_bin(bin_dir, "pgrep", f"echo {sb['supervisor_pid']}\n")
    write_fake_bin(bin_dir, "lsof", f'''case "$*" in
    "-ti :{SERVER_PORT}") printf '%s\\n' {sb['server_pid']} {sb['foreign_pid']} ;;
    "-a -p {sb['server_pid']} -d cwd -Fn") printf 'p%s\\nn%s\\n' {sb['server_pid']} "{sb['workspace_abs']}" ;;
    "-a -p {sb['foreign_pid']} -d cwd -Fn") printf 'p%s\\nn%s\\n' {sb['foreign_pid']} "{sb['foreign_cwd']}" ;;
esac
exit 0
''')
    return {**os.environ,
            "PATH": f"{bin_dir}:{os.environ['PATH']}",
            "PYTHON_PATH": sys.executable,
            "NO_COLOR": "1"}


def run_teardown(volumes: bool = False) -> dict:
    """Run stop.sh in a sandbox and return the observed outcome"""
    tmp = Path(tempfile.mkdtemp(prefix="toolomics_stop_test_"))
    pids = []
    try:
        repo = tmp / "repo"
        repo.mkdir()
        shutil.copy(REPO_ROOT / "stop.sh", repo / "stop.sh")

        workspace = tmp / "ws"
        workspace.mkdir()
        instance_id = hashlib.md5(str(workspace.resolve()).encode()).hexdigest()[:8]
        assert instance_id == deploy.generate_instance_id(str(workspace))

        compose_file = tmp / "docker-compose.yml"
        compose_file.write_text("services: {}\n")
        (repo / f"config_{instance_id}.json").write_text(json.dumps([
            {"path": "mcp_host/pdf/server.py", "port": SERVER_PORT, "enabled": True},
            {"path": "mcp_host/shell/docker-compose.yml", "port": 5902, "enabled": True},
        ]))

        server_pid = spawn_detached(["mcp_host/pdf/server.py", str(SERVER_PORT)])
        foreign_pid = spawn_detached(["mcp_host/pdf/server.py", str(SERVER_PORT)])
        supervisor_pid = spawn_detached(["deploy.py", "--workspace", str(workspace)])
        pids = [server_pid, foreign_pid, supervisor_pid]

        docker_log = tmp / "docker.log"
        docker_log.touch()
        env = build_sandbox(tmp, {
            "instance_id": instance_id,
            "compose_file": compose_file,
            "docker_log": docker_log,
            "server_pid": server_pid,
            "foreign_pid": foreign_pid,
            "supervisor_pid": supervisor_pid,
            "workspace_abs": str(workspace.resolve()),
            "foreign_cwd": str(tmp.resolve()),  # another instance's workspace
        })

        cmd = ["bash", str(repo / "stop.sh"), str(workspace)]
        if volumes:
            cmd.append("--volumes")
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=60)
        return {
            "result": result,
            "log": docker_log.read_text(),
            "instance_id": instance_id,
            "compose_file": str(compose_file),
            "supervisor_gone": wait_gone(supervisor_pid),
            "server_gone": wait_gone(server_pid),
            "foreign_alive": is_alive(foreign_pid),
        }
    finally:
        for pid in pids:
            if is_alive(pid):
                os.kill(pid, 9)
        shutil.rmtree(tmp, ignore_errors=True)


def test_stop_sh_tears_down_instance():
    out = run_teardown()
    result, log, iid = out["result"], out["log"], out["instance_id"]
    assert result.returncode == 0, result.stdout + result.stderr
    assert out["supervisor_gone"], "deploy.py supervisor was not stopped"
    assert out["server_gone"], "Python MCP server was not killed"
    assert "1 Python MCP server(s) killed" in result.stdout
    assert f"compose -p toolomics_{iid}_shell -f {out['compose_file']} down --remove-orphans" in log
    assert f"compose -p toolomics_{iid}_searxng -f {out['compose_file']} down --remove-orphans" in log
    assert "-p toolomics_deadbeef_shell" not in log, "other instance was torn down"
    assert "-p unrelated_project" not in log, "non-toolomics project was torn down"


def test_stop_sh_spares_foreign_python_on_same_port():
    """Port numbers repeat across instance configs: a python listener whose
    cwd is another workspace must survive (regression for cross-instance kill)."""
    out = run_teardown()
    assert out["result"].returncode == 0
    assert out["foreign_alive"], "python process of another workspace was killed"
    assert "is not from this workspace" in out["result"].stdout


def test_stop_sh_volumes_flag_reaches_compose_down():
    out = run_teardown(volumes=True)
    assert out["result"].returncode == 0, out["result"].stdout + out["result"].stderr
    assert (f"compose -p toolomics_{out['instance_id']}_shell -f {out['compose_file']} "
            f"down --remove-orphans --volumes") in out["log"]


def test_stop_sh_rejects_unknown_option():
    result = subprocess.run(["bash", str(REPO_ROOT / "stop.sh"), "--bogus"],
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 1
    assert "Unknown option" in result.stdout


if __name__ == "__main__":
    tests = [(name, fn) for name, fn in sorted(globals().items())
             if name.startswith("test_") and callable(fn)]
    for name, fn in tests:
        fn()
        print(f"PASS {name}")
    print(f"{len(tests)} tests passed")
