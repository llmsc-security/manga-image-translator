# syntax=docker/dockerfile:1.4

# ---------------------------------------------------------------
# Base image – PyTorch with CUDA 11.8 (can be overridden via build-arg)
# ---------------------------------------------------------------
ARG BASE_IMAGE=pytorch/pytorch:2.5.1-cuda11.8-cudnn9-runtime
FROM ${BASE_IMAGE} AS final

# ---------------------------------------------------------------
# Environment variables (common to build and runtime)
# ---------------------------------------------------------------
ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Etc/UTC \
    PYTHONPATH=/app \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_TIMEOUT=600 \
    PIP_RETRIES=10 \
    PIP_DEFAULT_TIMEOUT=600

WORKDIR /app

# ---------------------------------------------------------------
# System dependencies (bash needed for entrypoint, libgl1 for OpenCV/matplotlib)
# ---------------------------------------------------------------
RUN apt-get update -o Acquire::Retries=5 -o Acquire::http::Timeout=120 && \
    apt-get install -y --no-install-recommends \
        g++ \
        wget \
        ffmpeg \
        libsm6 \
        libxext6 \
        libgl1 \
        bash && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------------
# Python dependencies
# ---------------------------------------------------------------
COPY requirements.txt ./
RUN python -m pip install --upgrade pip setuptools wheel && \
    python -m pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------------
# Application source code
# ---------------------------------------------------------------
COPY . ./

# ---------------------------------------------------------------
# Runtime preparation (tmp permissions, log file)
# ---------------------------------------------------------------
RUN chmod 1777 /tmp && \
    mkdir -p /var/log && touch /var/log/app.log

# ---------------------------------------------------------------
# Entrypoint (make sure the script is executable)
# ---------------------------------------------------------------
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
