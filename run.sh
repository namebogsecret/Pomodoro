#!/usr/bin/env bash
set -euo pipefail

QUIET=0
NO_COLOR=""
PORT=8000

for arg in "$@"; do
    case "$arg" in
        --quiet) QUIET=1 ;;
        --no-color) NO_COLOR="1" ;;
        --port=*) PORT="${arg#*=}" ;;
        --help|-h)
            echo "Usage: $0 [--quiet] [--no-color] [--port=<num>]";
            exit 0
            ;;
        *)
            echo "Unknown option: $arg" >&2
            exit 1
            ;;
    esac
    shift $((0))
done

LOG_DIR="logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/run-$(date +'%Y%m%d_%H%M%S').log"
touch "$LOG_FILE"

log() {
    local lvl="$1"; shift
    if [[ $QUIET -eq 1 && $lvl == INFO ]]; then return; fi
    local ts="$(date '+%F %T%z')"
    local color="" reset=""
    if [[ -z $NO_COLOR ]]; then
        case "$lvl" in
            INFO) color="\e[32m" ;;
            WARN) color="\e[33m" ;;
            ERROR) color="\e[31m" ;;
        esac
        reset="\e[0m"
    fi
    printf "%b%s [%s] %s%b\n" "$color" "$ts" "$lvl" "$*" "$reset" | tee -a "$LOG_FILE"
}

run_step() {
    local step="$1"; shift
    log INFO "$step – $*"
    bash -c "$*" 2>&1 | tee -a "$LOG_FILE"
    return ${PIPESTATUS[0]}
}

trap 'log ERROR "Aborted (signal)"; exit 2' INT TERM

# 1. Git pull
if ! run_step git "git pull --ff-only"; then
    log ERROR "git pull failed"
    exit 1
fi

# 2. Dependencies
if [[ -f requirements.txt ]]; then
    if ! run_step deps "python -m pip install -r requirements.txt"; then
        log ERROR "Dependency install failed"
        exit 1
    fi
elif [[ -f package.json ]]; then
    if ! run_step deps "npm ci --ignore-scripts"; then
        log ERROR "Dependency install failed"
        exit 1
    fi
fi

# 3. Start command detection
cmd=""
if [[ -f start.sh ]]; then
    cmd="bash start.sh"
elif [[ -f package.json && $(command -v jq >/dev/null && jq -e '.scripts.start' package.json 2>/dev/null) ]]; then
    cmd="npm start"
elif [[ -f main.py ]]; then
    cmd="python main.py"
elif [[ -f index.html ]]; then
    if command -v lsof >/dev/null && lsof -i :$PORT -t >/dev/null 2>&1; then
        pid=$(lsof -i :$PORT -t | head -n1)
        log WARN "Port $PORT in use by PID $pid; killing"
        kill "$pid" || { log ERROR "Failed to kill process $pid"; exit 1; }
    elif command -v fuser >/dev/null 2>&1 && fuser "$PORT"/tcp >/dev/null 2>&1; then
        pid=$(fuser "$PORT"/tcp 2>/dev/null)
        log WARN "Port $PORT in use by PID $pid; killing"
        kill "$pid" || { log ERROR "Failed to kill process $pid"; exit 1; }
    fi
    cmd="python -m http.server $PORT"
else
    log ERROR "No start command found"
    exit 1
fi

# 4. Run command
if run_step start "$cmd"; then
    log INFO "\xE2\x9C\x93 SUCCESS"
    exit 0
else
    status=$?
    log ERROR "\xE2\x9C\x97 FAILED (code $status)"
    exit $status
fi
