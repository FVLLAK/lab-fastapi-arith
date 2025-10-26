#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="${IMAGE_NAME:-lab1}"
CONTAINER_NAME="${CONTAINER_NAME:-lab1}"
PORT="${PORT:-8000}"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

compute_tree_hash() {
  if command -v sha1sum >/dev/null 2>&1; then
    find src -type f -not -path "*/__pycache__/*" -print0 | sort -z | xargs -0 sha1sum | sha1sum | awk '{print $1}'
  else
    find src -type f -not -path "*/__pycache__/*" -print0 | sort -z | xargs -0 shasum | shasum | awk '{print $1}'
  fi
}

rebuild_and_restart() {
  log "Build image: ${IMAGE_NAME}:latest"
  docker build -t "${IMAGE_NAME}:latest" .

  log "Stop & remove previous container if exists: ${CONTAINER_NAME}"
  docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true

  log "Run container: ${CONTAINER_NAME} (host ${PORT} -> 8000)"
  docker run -d --name "${CONTAINER_NAME}" -p "${PORT}:8000" "${IMAGE_NAME}:latest" >/dev/null

  log "Redeploy done."
}

rebuild_and_restart

if command -v inotifywait >/dev/null 2>&1; then
  log "Using inotifywait (Linux) to watch src/"
  inotifywait -m -r -e modify,create,delete,move --format '%w%f' src | while read -r p; do
    log "Change detected: $p"; rebuild_and_restart; done
elif command -v fswatch >/dev/null 2>&1; then
  log "Using fswatch (macOS) to watch src/"
  fswatch -r src | while read -r p; do
    log "Change detected: $p"; rebuild_and_restart; done
else
  log "No inotifywait/fswatch found. Fallback to polling every 2s."
  prev="$(compute_tree_hash || true)"
  while true; do
    sleep 2
    curr="$(compute_tree_hash || true)"
    if [[ "$curr" != "$prev" ]]; then
      log "Change detected via polling."
      rebuild_and_restart
      prev="$curr"
    fi
  done
fi
