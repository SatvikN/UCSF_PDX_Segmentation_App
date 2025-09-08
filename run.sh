#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="${SCRIPT_DIR}"
CONTAINER_NAME="pdx-seg-app"
PORT="8000"

# Determine if GPU is requested
USE_GPU=${GPU:-0}
if [[ "${USE_GPU}" == "1" ]]; then
  IMAGE_NAME="pdx-seg-app:gpu"
  DOCKERFILE="Dockerfile.gpu"
  GPU_FLAG="--gpus all"
  echo "🚀 Building GPU-enabled image..."
else
  IMAGE_NAME="pdx-seg-app:latest"
  DOCKERFILE="Dockerfile"
  GPU_FLAG=""
  echo "🚀 Building CPU-only image..."
fi

# Optional: force architecture if building on Apple Silicon and deps are x86-only
PLATFORM_FLAG=${PLATFORM_FLAG:-""}
# PLATFORM_FLAG="--platform=linux/amd64"

# Build the Docker image
echo "📦 Building Docker image: ${IMAGE_NAME}"
docker build ${PLATFORM_FLAG} -f "${DOCKERFILE}" -t "${IMAGE_NAME}" "${APP_DIR}"

# Stop/remove existing container if running
echo "🛑 Stopping existing container (if any)..."
docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true

# Run the container
echo "🏃 Starting container..."
docker run --name "${CONTAINER_NAME}" --rm -p ${PORT}:8000 ${GPU_FLAG} \
  "${IMAGE_NAME}"

echo "✅ Container started successfully!"
echo "🌐 App available at: http://localhost:${PORT}"


