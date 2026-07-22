#!/bin/bash

# stop.sh — tear down one Toolomics instance completely.
#
# start.sh has no teardown path: Ctrl+C only stops the deploy.py supervisor,
# while the Docker MCP services keep running through their
# 'restart: unless-stopped' policy (they even come back after a Docker daemon
# restart or a reboot). This script stops everything belonging to the instance
# of one workspace and leaves every other instance untouched:
#   1. the deploy.py supervisor (first, so killed servers are not restarted)
#   2. the Python MCP servers on the ports recorded in config_<instance_id>.json
#   3. every Docker Compose project named toolomics_<instance_id>_*
#
# Usage: ./stop.sh [workspace] [--volumes]
#   workspace   The workspace passed to start.sh (default: workspace)
#   --volumes   Also remove the instance's named Docker volumes (deletes data!)

PYTHON=${PYTHON_PATH:-python3}

# ---------------------------------------------------------------------------
# Pretty output helpers (same as start.sh; colors off when piped or NO_COLOR)
# ---------------------------------------------------------------------------
if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then
    C_RESET=$'\033[0m'
    C_BOLD=$'\033[1m'
    C_DIM=$'\033[2m'
    C_RED=$'\033[31m'
    C_GREEN=$'\033[32m'
    C_YELLOW=$'\033[33m'
    C_BLUE=$'\033[34m'
    C_CYAN=$'\033[36m'
else
    C_RESET='' C_BOLD='' C_DIM='' C_RED='' C_GREEN='' C_YELLOW='' C_BLUE='' C_CYAN=''
fi

section() { printf '\n%s%s=== %s ===%s\n' "$C_BOLD" "$C_BLUE" "$1" "$C_RESET"; }
step()    { printf '%s▸ %s%s\n' "$C_CYAN" "$1" "$C_RESET"; }
info()    { printf '  %s\n' "$1"; }
detail()  { printf '    %s%s%s\n' "$C_DIM" "$1" "$C_RESET"; }
ok()      { printf '  %s✓%s %s\n' "$C_GREEN" "$C_RESET" "$1"; }
warn()    { printf '  %s⚠️%s  %s\n' "$C_YELLOW" "$C_RESET" "$1"; }
fail()    { printf '  %s✗%s %s\n' "$C_RED" "$C_RESET" "$1"; }

usage() {
    echo "Usage: $0 [workspace] [--volumes]"
    echo "  workspace   The workspace passed to start.sh (default: workspace)"
    echo "  --volumes   Also remove the instance's named Docker volumes (deletes data!)"
}

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
WORKSPACE=""
REMOVE_VOLUMES=false
for arg in "$@"; do
    case "$arg" in
        -h|--help) usage; exit 0 ;;
        --volumes) REMOVE_VOLUMES=true ;;
        -*) fail "Unknown option: $arg"; usage; exit 1 ;;
        *)
            if [ -n "$WORKSPACE" ]; then
                fail "Only one workspace argument is allowed"; usage; exit 1
            fi
            WORKSPACE="$arg"
            ;;
    esac
done
WORKSPACE=${WORKSPACE:-workspace}
VOLUMES_FLAG=""
[ "$REMOVE_VOLUMES" = true ] && VOLUMES_FLAG="--volumes"

# Relative workspace paths must resolve like they do when start.sh runs from
# the repository root, so always operate from the directory of this script.
cd "$(dirname "$0")" || exit 1

if ! command -v "$PYTHON" &> /dev/null; then
    fail "Python not found at '$PYTHON' (needed to derive the instance ID)"
    info "Set the PYTHON_PATH environment variable to your Python executable."
    exit 1
fi

resolve_path() {
    "$PYTHON" -c "import sys; from pathlib import Path; print(Path(sys.argv[1]).resolve())" "$1"
}

# Same derivation as deploy.py generate_instance_id(): md5 of the resolved
# workspace path, first 8 hex characters.
INSTANCE_ID=$("$PYTHON" -c "import hashlib, sys
from pathlib import Path
print(hashlib.md5(str(Path(sys.argv[1]).resolve()).encode()).hexdigest()[:8])" "$WORKSPACE")
if [ -z "$INSTANCE_ID" ]; then
    fail "Could not derive the instance ID for workspace '$WORKSPACE'"
    exit 1
fi
WORKSPACE_ABS=$(resolve_path "$WORKSPACE")
INSTANCE_CONFIG="config_${INSTANCE_ID}.json"
RSTUDIO_PORT=$((9000 + 16#$INSTANCE_ID % 1000))  # same formula as deploy.py

SUPERVISORS_STOPPED=0
PYTHON_KILLED=0
DOCKER_DOWNED=0
INCOMPLETE=0

# ---------------------------------------------------------------------------
# 1. deploy.py supervisor — stopped first so it cannot restart the servers we
#    are about to kill. Its SIGTERM handler shuts down its children too.
# ---------------------------------------------------------------------------
find_supervisor_pids() {
    # A relative --workspace in the supervisor's command line is resolved
    # against our own cwd (the repo root), which assumes the supervisor was
    # started from there too — true for anything launched via start.sh.
    local pid cmd ws_arg
    for pid in $(pgrep -f 'deploy\.py' 2>/dev/null); do
        cmd=$(ps -p "$pid" -o command= 2>/dev/null)
        case "$cmd" in
            *[Pp]ython*" deploy.py"*|*[Pp]ython*"/deploy.py"*) ;;
            *) continue ;;
        esac
        ws_arg=$(printf '%s\n' "$cmd" | sed -n 's/.*--workspace[= ][= ]*\([^ ][^ ]*\).*/\1/p')
        [ -n "$ws_arg" ] || ws_arg="workspace"  # deploy.py's --workspace default
        [ "$(resolve_path "$ws_arg")" = "$WORKSPACE_ABS" ] && echo "$pid"
    done
}

any_alive() {
    local pid
    for pid in "$@"; do
        kill -0 "$pid" 2>/dev/null && return 0
    done
    return 1
}

stop_supervisors() {
    local pids pid waited=0
    pids=$(find_supervisor_pids)
    if [ -z "$pids" ]; then
        ok "No running deploy.py supervisor for this workspace"
        return
    fi
    for pid in $pids; do
        step "Stopping deploy.py supervisor (PID $pid)..."
        kill "$pid" 2>/dev/null && SUPERVISORS_STOPPED=$((SUPERVISORS_STOPPED + 1))
    done
    # Graceful shutdown terminates every supervised server; give it a moment
    while [ $waited -lt 10 ] && any_alive $pids; do
        sleep 1
        waited=$((waited + 1))
    done
    for pid in $pids; do
        if kill -0 "$pid" 2>/dev/null; then
            warn "Supervisor $pid still alive after ${waited}s, force killing"
            kill -9 "$pid" 2>/dev/null
        fi
    done
    ok "Supervisor stopped"
}

# ---------------------------------------------------------------------------
# 2. Python MCP servers — their ports are recorded in the instance config.
#    Only processes whose command mentions python are killed (same rule as the
#    port cleanup in start.sh); anything else is reported and left alone.
# ---------------------------------------------------------------------------
python_server_ports() {
    "$PYTHON" -c "
import json, sys
try:
    entries = json.load(open(sys.argv[1]))
except Exception:
    sys.exit(0)
for entry in entries:
    if 'server.py' in entry.get('path', '') and entry.get('port'):
        print(entry['port'])
" "$INSTANCE_CONFIG"
}

proc_cwd() {
    lsof -a -p "$1" -d cwd -Fn 2>/dev/null | sed -n 's/^n//p' | head -n 1
}

listener_belongs_to_instance() {
    # Instances assign ports from their own config without cross-instance
    # coordination, so the port alone does not identify ours: require the
    # listener's working directory (deploy.py starts every server with
    # cwd=workspace) to be this workspace.
    [ "$(proc_cwd "$1")" = "$WORKSPACE_ABS" ]
}

kill_python_listener() {
    local port=$1 pid cmd
    for pid in $(lsof -ti :"$port" 2>/dev/null); do
        cmd=$(ps -p "$pid" -o command= 2>/dev/null)
        case "$cmd" in
            *[Pp]ython*)
                if ! listener_belongs_to_instance "$pid"; then
                    warn "Python process on port $port (PID $pid) is not from this workspace, leaving it alone"
                    detail "$cmd"
                    continue
                fi
                step "Killing Python MCP server on port $port (PID $pid)"
                detail "$cmd"
                kill "$pid" 2>/dev/null || continue
                TERMED_PIDS="$TERMED_PIDS $pid"
                PYTHON_KILLED=$((PYTHON_KILLED + 1))
                ;;
            '') ;;  # process already gone
            *)
                warn "Port $port is used by a non-Python process (PID $pid), leaving it alone"
                detail "$cmd"
                ;;
        esac
    done
}

stop_python_servers() {
    local port pid
    if [ ! -f "$INSTANCE_CONFIG" ]; then
        warn "Config file $INSTANCE_CONFIG not found, skipping Python server cleanup"
        return
    fi
    if ! command -v lsof &> /dev/null; then
        warn "lsof not found, skipping Python server cleanup"
        return
    fi
    TERMED_PIDS=""
    for port in $(python_server_ports); do
        kill_python_listener "$port"
    done
    if [ -n "$TERMED_PIDS" ]; then
        sleep 2  # grace period before escalating to SIGKILL
        for pid in $TERMED_PIDS; do
            kill -0 "$pid" 2>/dev/null && kill -9 "$pid" 2>/dev/null
        done
        ok "$PYTHON_KILLED Python MCP server(s) killed"
    else
        ok "No Python MCP servers left running"
    fi
}

# ---------------------------------------------------------------------------
# 3. Docker MCP services — every compose project deploy.py created for this
#    instance is named toolomics_<instance_id>_<service_slug>. Projects and
#    their compose files are recovered from the labels compose stamped on the
#    containers, so this also covers services later removed from the repo.
# ---------------------------------------------------------------------------
detect_compose_cmd() {
    if docker compose version > /dev/null 2>&1; then
        COMPOSE=(docker compose)
    elif command -v docker-compose &> /dev/null; then
        COMPOSE=(docker-compose)
    else
        COMPOSE=()
        warn "Neither 'docker compose' nor 'docker-compose' found, will fall back to 'docker rm -f'"
    fi
}

instance_projects() {
    docker ps -a --filter "label=com.docker.compose.project" \
        --format '{{.Label "com.docker.compose.project"}}' 2>/dev/null \
        | sort -u | grep "^toolomics_${INSTANCE_ID}_"
}

project_compose_file() {
    docker ps -a --filter "label=com.docker.compose.project=$1" \
        --format '{{.Label "com.docker.compose.project.config_files"}}' 2>/dev/null \
        | head -n 1 | cut -d, -f1
}

run_compose_down() {
    local project=$1
    shift
    [ ${#COMPOSE[@]} -gt 0 ] || return 1
    # Port values only need to make the compose file parse ('down' never
    # publishes ports); INSTANCE_ID and WORKSPACE_PATH are the real ones.
    INSTANCE_ID="$INSTANCE_ID" WORKSPACE_PATH="$WORKSPACE" \
    MCP_PORT=65535 FASTMCP_PORT=65535 \
    RSTUDIO_PORT="$RSTUDIO_PORT" SEARXNG_PORT=8080 \
        "${COMPOSE[@]}" -p "$project" "$@" down --remove-orphans $VOLUMES_FLAG
}

force_remove_project() {
    local project=$1 ids nets vols rm_flags="-f"
    [ "$REMOVE_VOLUMES" = true ] && rm_flags="-f -v"  # -v drops anonymous volumes
    ids=$(docker ps -aq --filter "label=com.docker.compose.project=$project" 2>/dev/null)
    [ -n "$ids" ] && docker rm $rm_flags $ids > /dev/null 2>&1
    nets=$(docker network ls -q --filter "label=com.docker.compose.project=$project" 2>/dev/null)
    [ -n "$nets" ] && docker network rm $nets > /dev/null 2>&1
    if [ "$REMOVE_VOLUMES" = true ]; then
        vols=$(docker volume ls -q --filter "label=com.docker.compose.project=$project" 2>/dev/null)
        [ -n "$vols" ] && docker volume rm $vols > /dev/null 2>&1
    fi
}

sweep_leftover_resources() {
    # Networks/volumes can outlive their containers (e.g. after a manual
    # 'docker rm -f'); those projects have no container labels left to find,
    # but compose resource names keep the project prefix.
    local nets vols
    nets=$(docker network ls --format '{{.Name}}' 2>/dev/null | grep "^toolomics_${INSTANCE_ID}_")
    if [ -n "$nets" ]; then
        step "Removing leftover networks of instance $INSTANCE_ID"
        docker network rm $nets > /dev/null 2>&1
    fi
    if [ "$REMOVE_VOLUMES" = true ]; then
        vols=$(docker volume ls -q 2>/dev/null | grep "^toolomics_${INSTANCE_ID}_")
        if [ -n "$vols" ]; then
            step "Removing leftover volumes of instance $INSTANCE_ID"
            docker volume rm $vols > /dev/null 2>&1
        fi
    fi
}

down_project() {
    local project=$1 compose_file
    compose_file=$(project_compose_file "$project")
    step "Bringing down $project..."
    if [ -n "$compose_file" ] && [ -f "$compose_file" ]; then
        detail "compose file: $compose_file"
        if run_compose_down "$project" -f "$compose_file"; then
            ok "$project removed"
            return
        fi
        warn "compose down with $compose_file failed, retrying from container labels"
    fi
    if run_compose_down "$project"; then
        ok "$project removed"
        return
    fi
    warn "compose down failed for $project, force removing its containers"
    force_remove_project "$project"
    ok "$project containers force removed"
}

stop_docker_projects() {
    local project projects
    if ! command -v docker &> /dev/null; then
        warn "docker CLI not found, skipping Docker teardown"
        return
    fi
    if ! docker info > /dev/null 2>&1; then
        warn "Docker daemon not reachable, skipping Docker teardown"
        warn "The instance's containers ('restart: unless-stopped') will come back when the daemon does;"
        warn "rerun this script once Docker is running."
        INCOMPLETE=1
        return
    fi
    detect_compose_cmd
    projects=$(instance_projects)
    if [ -z "$projects" ]; then
        ok "No Docker Compose projects found for instance $INSTANCE_ID"
    else
        for project in $projects; do
            down_project "$project"
            DOCKER_DOWNED=$((DOCKER_DOWNED + 1))
        done
    fi
    sweep_leftover_resources
}

# ---------------------------------------------------------------------------
# Teardown
# ---------------------------------------------------------------------------
section "Toolomics Teardown"
info "Workspace:    $C_BOLD$WORKSPACE$C_RESET"
info "Instance ID:  $C_BOLD$INSTANCE_ID$C_RESET"
info "Config File:  $C_BOLD$INSTANCE_CONFIG$C_RESET"
[ "$REMOVE_VOLUMES" = true ] && warn "Named Docker volumes of this instance will be REMOVED (--volumes)"

section "Stopping deploy.py Supervisor"
stop_supervisors

section "Stopping Python MCP Servers"
stop_python_servers

section "Stopping Docker MCP Services"
stop_docker_projects

if [ "$INCOMPLETE" -ne 0 ]; then
    section "TEARDOWN INCOMPLETE"
    fail "Docker teardown was skipped, rerun: ./stop.sh $WORKSPACE"
else
    section "TEARDOWN COMPLETE"
fi
ok "Supervisors stopped:        $SUPERVISORS_STOPPED"
ok "Python servers killed:      $PYTHON_KILLED"
ok "Docker projects torn down:  $DOCKER_DOWNED"
info "Restart the instance any time with: ./start.sh <start_port> <end_port> $WORKSPACE"
exit $INCOMPLETE
