#!/usr/bin/env bash
set -euo pipefail

# ===== Variables (surchargeables via env) =====
REMOTE="${REMOTE:-origin}"
BRANCH="${BRANCH:-main}"
POLL="${POLL:-10}"
IMAGE_NAME="${IMAGE_NAME:-lab1}"
CONTAINER_NAME="${CONTAINER_NAME:-lab1}"
PORT="${PORT:-8000}"

# ===== Utils =====
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

rebuild_and_restart() {
  log "Build image: ${IMAGE_NAME}:latest"
  docker build -t "${IMAGE_NAME}:latest" .

  log "Stop & remove previous container if exists: ${CONTAINER_NAME}"
  docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true

  log "Run container: ${CONTAINER_NAME} (host ${PORT} -> 8000)"
  docker run -d --name "${CONTAINER_NAME}" -p "${PORT}:8000" "${IMAGE_NAME}:latest" >/dev/null

  log "Redeploy done."
}

# ===== State =====
last_deployed="$(git rev-parse HEAD 2>/dev/null || echo "")"

log "Watching remote '${REMOTE}/${BRANCH}' every ${POLL}s..."
while true; do
  if ! git fetch "${REMOTE}" "${BRANCH}" >/dev/null 2>&1; then
    log "git fetch failed; retrying in ${POLL}s..."
    sleep "${POLL}"
    continue
  fi

  remote_commit="$(git rev-parse FETCH_HEAD)"
  if [[ -z "${last_deployed}" ]]; then
    last_deployed="$(git rev-parse HEAD)"
  fi

  if [[ "${remote_commit}" != "${last_deployed}" ]]; then
    log "New remote commit detected: ${remote_commit}"
    git pull --rebase "${REMOTE}" "${BRANCH}"
    rebuild_and_restart
    last_deployed="${remote_commit}"
  fi

  sleep "${POLL}"
done
