#!/bin/bash

# invoke.sh - Build and run manga-image-translator Docker container
# Port mapping: 11080:8000

set -e

echo "=========================================="
echo "Manga Image Translator Docker Build & Run Script"
echo "=========================================="

# Configuration
CONTAINER_NAME="manga-image-translator-server"
IMAGE_NAME="manga-image-translator:latest"
PORT_HOST="11080"
PORT_CONTAINER="8000"
DOCKER_GPU_FLAG="${DOCKER_GPU_FLAG:-"--gpus all"}"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --build)
            BUILD_ONLY=true
            shift
            ;;
        --stop)
            STOP_ONLY=true
            shift
            ;;
        --rm)
            REMOVE_ONLY=true
            shift
            ;;
        --gpu)
            DOCKER_GPU_FLAG="--gpus all"
            shift
            ;;
        --cpu)
            DOCKER_GPU_FLAG=""
            shift
            ;;
        *)
            shift
            ;;
    esac
done

# Function to stop and remove container
stop_container() {
    echo "Stopping and removing existing container..."
    docker stop "${CONTAINER_NAME}" 2>/dev/null || true
    docker rm "${CONTAINER_NAME}" 2>/dev/null || true
}

# Function to build the image
build_image() {
    echo "=========================================="
    echo "Building Docker Image..."
    echo "=========================================="

    if [ -n "$DOCKER_GPU_FLAG" ]; then
        echo "Building with GPU support..."
    else
        echo "Building for CPU-only..."
    fi

    docker build -t "${IMAGE_NAME}" .

    if [ $? -eq 0 ]; then
        echo "Build successful: ${IMAGE_NAME}"
    else
        echo "Build failed!"
        exit 1
    fi
}

# Function to run the container
run_container() {
    echo "=========================================="
    echo "Starting Container..."
    echo "=========================================="
    echo "Container Name: ${CONTAINER_NAME}"
    echo "Image: ${IMAGE_NAME}"
    echo "Port Mapping: ${PORT_HOST}:${PORT_CONTAINER}"
    if [ -n "$DOCKER_GPU_FLAG" ]; then
        echo "GPU: Enabled"
    else
        echo "GPU: Disabled (CPU mode)"
    fi
    echo "=========================================="

    # Stop any existing container
    stop_container

    # Run the container
    if [ -n "$DOCKER_GPU_FLAG" ]; then
        docker run --name "${CONTAINER_NAME}" \
            --rm \
            --gpus all \
            -p "${PORT_HOST}:${PORT_CONTAINER}" \
            -e HOST="0.0.0.0" \
            -e PORT="${PORT_CONTAINER}" \
            "${IMAGE_NAME}"
    else
        docker run --name "${CONTAINER_NAME}" \
            --rm \
            -p "${PORT_HOST}:${PORT_CONTAINER}" \
            -e HOST="0.0.0.0" \
            -e PORT="${PORT_CONTAINER}" \
            "${IMAGE_NAME}"
    fi
}

# Main execution
if [ "${STOP_ONLY}" = true ]; then
    stop_container
    echo "Container stopped and removed."
    exit 0
fi

if [ "${REMOVE_ONLY}" = true ]; then
    stop_container
    docker rmi "${IMAGE_NAME}" 2>/dev/null || true
    echo "Container and image removed."
    exit 0
fi

# Default behavior: build and run
build_image
run_container
