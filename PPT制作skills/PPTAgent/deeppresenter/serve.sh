#!/bin/bash

# Auto-detect if in China by checking Google accessibility
if curl -I --connect-timeout 3 https://www.google.com &>/dev/null; then
    export SGLANG_USE_MODELSCOPE=0
    docker_image=lmsysorg/sglang:latest
else
    export SGLANG_USE_MODELSCOPE=True
    docker_image=docker.1ms.run/lmsysorg/sglang:latest
fi

num_gpus=$(nvidia-smi --list-gpus | wc -l)
if [ $num_gpus -lt 4 ]; then
    tp=$num_gpus
else
    tp=4
fi

echo "Detected $num_gpus GPU(s), using Configuration: TP=$tp, DP=1"

docker run --gpus all \
    --shm-size 32g \
    -p 8080:8080\
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    --ipc=host \
    -e SGLANG_USE_MODELSCOPE \
    "$docker_image" \
    bash -lc "pip install -U transformers && python3 -m sglang.launch_server \
        --model-path Forceless/DeepPresenter-9B \
        --host 0.0.0.0 \
        --port 7811 \
        --tp $tp \
        --disable-custom-all-reduce"
