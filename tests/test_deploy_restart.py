#!/usr/bin/env python3
"""Tests for deploy.py crash-restart supervision (ProcessManager)."""

import socket
import sys
import time
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import deploy
from deploy import PendingRestart, ProcessInfo, ProcessManager


def make_manager() -> ProcessManager:
    """Build a ProcessManager pointed at a throwaway workspace"""
    workspace = Path(tempfile.mkdtemp(prefix="toolomics_test_"))
    return ProcessManager(workspace_dir=workspace, instance_id="testinst")


def make_process_info(process_type: str) -> ProcessInfo:
    """Build a ProcessInfo carrying a dummy proc (never started)"""
    return ProcessInfo(proc=object(), file_path="mcp/fake/server.py", port=5001,
                       process_type=process_type)


def test_python_server_restarts_on_any_exit():
    manager = make_manager()
    assert manager._needs_restart(make_process_info('python'), failed=True)
    assert manager._needs_restart(make_process_info('python'), failed=False)


def test_docker_bootstrap_restarts_only_on_failure():
    manager = make_manager()
    assert manager._needs_restart(make_process_info('docker'), failed=True)
    assert not manager._needs_restart(make_process_info('docker'), failed=False)


def test_no_restart_during_shutdown():
    manager = make_manager()
    manager.shutdown_event.set()
    assert not manager._needs_restart(make_process_info('python'), failed=True)


def test_backoff_doubles_and_caps_attempts():
    manager = make_manager()
    path = "mcp/crashy/server.py"

    for attempt in range(deploy.RESTART_MAX_ATTEMPTS):
        before = time.time()
        manager._schedule_restart(path, 5001, 'python')
        expected_delay = min(deploy.RESTART_BASE_DELAY_S * 2 ** attempt,
                             deploy.RESTART_MAX_DELAY_S)
        actual_delay = manager.pending_restarts[-1].restart_at - before
        assert abs(actual_delay - expected_delay) < 0.5, \
            f"attempt {attempt}: expected ~{expected_delay}s, got {actual_delay}s"

    assert len(manager.pending_restarts) == deploy.RESTART_MAX_ATTEMPTS
    assert manager.abandoned_servers == []

    # One crash beyond the cap: abandoned, no new restart queued
    manager._schedule_restart(path, 5001, 'python')
    assert manager.abandoned_servers == [path]
    assert len(manager.pending_restarts) == deploy.RESTART_MAX_ATTEMPTS


def test_launch_waits_for_backoff_delay():
    manager = make_manager()
    launched = []
    manager.start_python_server = lambda path, port: launched.append((path, port))

    manager.pending_restarts.append(
        PendingRestart("srv.py", 5001, 'python', restart_at=time.time() + 60))
    manager._launch_due_restarts()
    assert launched == []

    manager.pending_restarts[0].restart_at = time.time() - 1
    manager._launch_due_restarts()
    assert launched == [(Path("srv.py"), 5001)]
    assert manager.pending_restarts == []


def test_failed_relaunch_consumes_an_attempt():
    manager = make_manager()

    def broken_start(path, port):
        raise RuntimeError("boom")

    manager.start_python_server = broken_start
    manager.pending_restarts.append(
        PendingRestart("srv.py", 5001, 'python', restart_at=time.time() - 1))
    manager._launch_due_restarts()

    assert len(manager.restart_history["srv.py"]) == 1
    assert len(manager.pending_restarts) == 1  # rescheduled with backoff


def test_backoff_delay_clamps_at_ceiling():
    manager = make_manager()
    saved = (deploy.RESTART_MAX_ATTEMPTS, deploy.RESTART_MAX_DELAY_S)
    deploy.RESTART_MAX_ATTEMPTS = 6
    deploy.RESTART_MAX_DELAY_S = 10.0
    try:
        for _ in range(6):  # uncapped doubling would reach 64s
            before = time.time()
            manager._schedule_restart("srv.py", 5001, 'python')
        last_delay = manager.pending_restarts[-1].restart_at - before
        assert abs(last_delay - 10.0) < 0.5, f"expected clamp at 10s, got {last_delay}s"
    finally:
        (deploy.RESTART_MAX_ATTEMPTS, deploy.RESTART_MAX_DELAY_S) = saved


def test_abandonment_is_reported_immediately():
    manager = make_manager()
    reported = []
    manager._report_abandonment = lambda path: reported.append(path)
    saved = deploy.RESTART_MAX_ATTEMPTS
    deploy.RESTART_MAX_ATTEMPTS = 1
    try:
        manager._schedule_restart("srv.py", 5001, 'python')
        assert reported == []
        manager._schedule_restart("srv.py", 5001, 'python')
        assert reported == ["srv.py"]
        assert manager.abandoned_servers == ["srv.py"]
    finally:
        deploy.RESTART_MAX_ATTEMPTS = saved


def test_docker_restart_invokes_compose_relaunch():
    manager = make_manager()
    launched = []
    manager.start_docker_compose = lambda path, port: launched.append((path, port))

    manager.pending_restarts.append(
        PendingRestart("mcp/foo/docker-compose.yml", 5005, 'docker', restart_at=time.time() - 1))
    manager._launch_due_restarts()

    assert launched == [(Path("mcp/foo/docker-compose.yml"), 5005)]
    assert manager.pending_restarts == []


def test_busy_port_defers_python_restart():
    manager = make_manager()
    launched = []
    manager.start_python_server = lambda path, port: launched.append(path)

    blocker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    blocker.bind(("0.0.0.0", 0))
    blocker.listen(1)
    busy_port = blocker.getsockname()[1]
    try:
        manager.pending_restarts.append(
            PendingRestart("srv.py", busy_port, 'python', restart_at=time.time() - 1))
        manager._launch_due_restarts()

        assert launched == []
        assert len(manager.pending_restarts) == 1  # deferred, not dropped
        assert len(manager.restart_history["srv.py"]) == 1  # attempt consumed
    finally:
        blocker.close()


def test_crash_loop_is_restarted_then_abandoned():
    """End-to-end: a server that always crashes is restarted then given up on"""
    workspace = Path(tempfile.mkdtemp(prefix="toolomics_test_"))
    server_file = workspace / "server.py"
    server_file.write_text("import sys, time\ntime.sleep(0.02)\nsys.exit(1)\n")

    saved = (deploy.RESTART_MAX_ATTEMPTS, deploy.RESTART_BASE_DELAY_S,
             deploy.RESTART_MAX_DELAY_S)
    deploy.RESTART_MAX_ATTEMPTS = 2
    deploy.RESTART_BASE_DELAY_S = 0.05
    deploy.RESTART_MAX_DELAY_S = 0.1
    try:
        manager = ProcessManager(workspace_dir=workspace, instance_id="testinst")
        manager.start_python_server(server_file, 0)
        exit_code = None
        try:
            manager.monitor_processes(check_interval=0.01)
        except SystemExit as e:
            exit_code = e.code

        assert exit_code == 1, f"expected exit 1 after abandonment, got {exit_code}"
        assert manager.abandoned_servers == [str(server_file)]
        assert len(manager.restart_history[str(server_file)]) == 2
        # Recovered crashes are dropped from failed_processes; only the final
        # unrecovered crash (the one that triggered abandonment) remains
        assert len(manager.failed_processes) == 1
    finally:
        (deploy.RESTART_MAX_ATTEMPTS, deploy.RESTART_BASE_DELAY_S,
         deploy.RESTART_MAX_DELAY_S) = saved


if __name__ == "__main__":
    tests = [(name, fn) for name, fn in sorted(globals().items())
             if name.startswith("test_") and callable(fn)]
    for name, fn in tests:
        fn()
        print(f"PASS {name}")
    print(f"{len(tests)} tests passed")
