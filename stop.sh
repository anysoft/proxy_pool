#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

PROJECT_DIR="$(pwd -P)"
GRACE_SECONDS="${GRACE_SECONDS:-15}"
DRY_RUN="${DRY_RUN:-0}"

TARGET_PIDS=""
STOPPED_SCREENS=0

log() {
  printf '%s\n' "$*"
}

append_pid() {
  local pid="$1"

  case "$pid" in
    ''|*[!0-9]*)
      return
      ;;
  esac

  if [ "$pid" = "$$" ] || [ "$pid" = "${PPID:-}" ]; then
    return
  fi

  case " $TARGET_PIDS " in
    *" $pid "*)
      return
      ;;
    *)
      TARGET_PIDS="$TARGET_PIDS $pid"
      ;;
  esac
}

process_cwd() {
  local pid="$1"

  if [ -L "/proc/$pid/cwd" ]; then
    readlink "/proc/$pid/cwd" 2>/dev/null || true
    return
  fi

  if command -v lsof >/dev/null 2>&1; then
    lsof -a -d cwd -p "$pid" -Fn 2>/dev/null | sed -n 's/^n//p' | head -n 1
  fi
}

process_command() {
  local pid="$1"
  ps -p "$pid" -o command= 2>/dev/null || true
}

is_project_process() {
  local pid="$1"
  local cwd
  local cmd

  cwd="$(process_cwd "$pid")"
  [ "$cwd" = "$PROJECT_DIR" ] || return 1

  cmd="$(process_command "$pid")"
  case "$cmd" in
    *"proxyPool.py server"*|*"proxyPool.py schedule"*|*"gunicorn"*)
      return 0
      ;;
  esac

  return 1
}

collect_descendants() {
  local parent="$1"
  local child

  for child in $(pgrep -P "$parent" 2>/dev/null || true); do
    append_pid "$child"
    collect_descendants "$child"
  done
}

collect_targets() {
  local pid
  local roots=""

  TARGET_PIDS=""

  for pid in $(pgrep -f 'proxyPool.py (server|schedule)' 2>/dev/null || true); do
    if is_project_process "$pid"; then
      append_pid "$pid"
      roots="$roots $pid"
    fi
  done

  for pid in $(pgrep -f gunicorn 2>/dev/null || true); do
    if is_project_process "$pid"; then
      append_pid "$pid"
      roots="$roots $pid"
    fi
  done

  for pid in $roots; do
    collect_descendants "$pid"
  done
}

quit_screen_session() {
  local session="$1"

  command -v screen >/dev/null 2>&1 || return 0
  screen -ls 2>/dev/null | grep -q "[.]$session[[:space:]]" || return 0

  if [ "$DRY_RUN" = "1" ]; then
    log "Would stop screen session: $session"
  else
    screen -S "$session" -X quit || true
  fi
  STOPPED_SCREENS=1
}

running_pids() {
  local pid

  for pid in "$@"; do
    if kill -0 "$pid" 2>/dev/null; then
      printf '%s\n' "$pid"
    fi
  done
}

print_targets() {
  local pid

  for pid in "$@"; do
    printf '  %s  %s\n' "$pid" "$(process_command "$pid")"
  done
}

stop_pids() {
  local pids="$1"
  local pid
  local remaining
  local elapsed=0

  [ -n "$pids" ] || return

  log "Stopping ProxyPool processes:"
  print_targets $pids

  if [ "$DRY_RUN" = "1" ]; then
    log "Dry run only; no signals sent."
    return
  fi

  for pid in $pids; do
    kill -TERM "$pid" 2>/dev/null || true
  done

  while [ "$elapsed" -lt "$GRACE_SECONDS" ]; do
    remaining="$(running_pids $pids | tr '\n' ' ')"
    [ -z "$remaining" ] && return
    sleep 1
    elapsed=$((elapsed + 1))
  done

  remaining="$(running_pids $pids | tr '\n' ' ')"
  if [ -n "$remaining" ]; then
    log "Force stopping remaining processes after ${GRACE_SECONDS}s:"
    print_targets $remaining
    for pid in $remaining; do
      kill -KILL "$pid" 2>/dev/null || true
    done
  fi
}

quit_screen_session proxy_pool_server
quit_screen_session proxy_pool_schedule

collect_targets
if [ -z "$TARGET_PIDS" ]; then
  if [ "$STOPPED_SCREENS" = "1" ]; then
    collect_targets
  fi
fi

if [ -z "$TARGET_PIDS" ]; then
  log "No running ProxyPool processes found under $PROJECT_DIR."
  exit 0
fi

stop_pids "$TARGET_PIDS"
log "ProxyPool stop completed."
