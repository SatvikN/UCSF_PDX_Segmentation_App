#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="${SCRIPT_DIR}"
IMAGE_NAME="pdx-seg-app:latest"
CONTAINER_NAME="pdx-seg-app"
PORT="8000"

# Set GPU=1 to enable GPU (Linux + NVIDIA only)
GPU_FLAG=${GPU_FLAG:-""}
if [[ "${GPU:-0}" == "1" ]]; then
  GPU_FLAG="--gpus all"
fi

# Optional: force architecture if building on Apple Silicon and deps are x86-only
PLATFORM_FLAG=${PLATFORM_FLAG:-""}
# PLATFORM_FLAG="--platform=linux/amd64"

docker build ${PLATFORM_FLAG} -t "${IMAGE_NAME}" "${APP_DIR}"

# Stop/remove if already running
docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true

docker run --name "${CONTAINER_NAME}" --rm -p ${PORT}:8000 ${GPU_FLAG} \
  "${IMAGE_NAME}"


