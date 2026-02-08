#!/bin/bash

# entrypoint.sh - Start the FastAPI server for manga-image-translator
# Port: 8000

set -e

echo "=========================================="
echo "Manga Image Translator Server Starting..."
echo "=========================================="

# Set default values if not provided
HOST=${HOST:-"0.0.0.0"}
PORT=${PORT:-"8000"}
GPU=${GPU:-"false"}
VERBOSE=${VERBOSE:-"false"}
IGNORE_ERRORS=${IGNORE_ERRORS:-"false"}
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

echo "Configuration:"
echo "  Host: ${HOST}"
echo "  Port: ${PORT}"
echo "  GPU: ${GPU}"
echo "  Verbose: ${VERBOSE}"
echo "  Ignore Errors: ${IGNORE_ERRORS}"
echo "  Timestamp: ${TIMESTAMP}"
echo "=========================================="

# Build command arguments
CMD="python3 server/main.py"

if [ "${HOST}" != "127.0.0.1" ]; then
    CMD="${CMD} --host ${HOST}"
fi

CMD="${CMD} --port ${PORT}"

if [ "${GPU}" = "true" ]; then
    CMD="${CMD} --use-gpu"
fi

if [ "${VERBOSE}" = "true" ]; then
    CMD="${CMD} --verbose"
fi

if [ "${IGNORE_ERRORS}" = "true" ]; then
    CMD="${CMD} --ignore-errors"
fi

echo "Starting server on ${HOST}:${PORT}..."
exec ${CMD}
