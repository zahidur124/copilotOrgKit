#!/usr/bin/env bash
# Local releases: $APP_DIR/releases/<sha>; $APP_DIR/current points at the live one.
# deploy: unpack HEAD, switch, health-check, and switch back on failure.
set -uo pipefail
cd "$(dirname "$0")/.."
set -a; . ./deploy.env; set +a
REL="$APP_DIR/releases"; mkdir -p "$REL"

up()   { for _ in $(seq 1 20); do curl -fsS "http://127.0.0.1:$1$HEALTH_PATH" >/dev/null 2>&1 && return 0; sleep 0.5; done; return 1; }
stop() { [ -f "$APP_DIR/pid" ] && kill "$(cat "$APP_DIR/pid")" 2>/dev/null; rm -f "$APP_DIR/pid"; sleep 0.5; }
# A release starts with its own deploy.env, so a rollback never runs the new release's START.
start(){ (cd "$APP_DIR/current" && cmd=$(. ./deploy.env; printf '%s' "$START") && exec env PORT="$PORT" nohup sh -c "exec $cmd" >"$APP_DIR/app.log" 2>&1 </dev/null) & echo $! >"$APP_DIR/pid"; }

case "${1:-}" in
  deploy)
    sha=$(git rev-parse --short HEAD)
    rm -rf "${REL:?}/$sha"; mkdir -p "$REL/$sha"; git archive HEAD | tar -x -C "$REL/$sha"
    prev=$(readlink "$APP_DIR/current" || true)
    ln -sfn "$REL/$sha" "$APP_DIR/current"; stop; start
    if up "$PORT"; then
      [ -n "$prev" ] && [ "$prev" != "$REL/$sha" ] && ln -sfn "$prev" "$APP_DIR/previous"
      echo "PASS: $sha is live and healthy on :$PORT"; exit 0
    fi
    echo "FAIL: $sha failed its health check; rolling back to ${prev:-nothing}"
    stop
    if [ -n "$prev" ]; then
      ln -sfn "$prev" "$APP_DIR/current"; start
      up "$PORT" && echo "PASS: rolled back to $(basename "$prev"), healthy" || echo "FAIL: rollback target is unhealthy too"
    fi
    exit 1 ;;
  rollback)
    prev=$(readlink "$APP_DIR/previous" || true)
    [ -n "$prev" ] || { echo "FAIL: no previous release"; exit 1; }
    cur=$(readlink "$APP_DIR/current")
    ln -sfn "$prev" "$APP_DIR/current"; ln -sfn "$cur" "$APP_DIR/previous"; stop; start
    up "$PORT" && echo "PASS: rolled back to $(basename "$prev")" || { echo "FAIL: $(basename "$prev") unhealthy"; exit 1; } ;;
  health)
    curl -fsS "http://127.0.0.1:$PORT$HEALTH_PATH" && echo && echo "PASS: healthy" || { echo "FAIL: no health answer on :$PORT"; exit 1; } ;;
  smoke)
    PORT=$SMOKE_PORT sh -c "exec $START" >/dev/null 2>&1 </dev/null & pid=$!
    if up "$SMOKE_PORT"; then kill $pid; echo "PASS: app starts and answers $HEALTH_PATH"; exit 0; fi
    kill $pid 2>/dev/null; echo "FAIL: app did not answer $HEALTH_PATH on :$SMOKE_PORT"; exit 1 ;;
  *) echo "usage: deploy.sh deploy|rollback|health|smoke"; exit 2 ;;
esac
