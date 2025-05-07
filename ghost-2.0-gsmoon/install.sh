#!/bin/bash
# 설치 스크립트

# 기본 의존성 설치
pip install numpy==1.24.4 pillow==10.2.0

# 의존성 충돌 회피를 위해 --no-deps 옵션 사용하여 패키지 개별 설치
pip install --no-deps pytorch-lightning==2.5.0.post0
pip install --no-deps matplotlib==3.7.3
pip install --no-deps scikit-image==0.21.0
pip install --no-deps lpips==0.1.4
pip install --no-deps imgaug==0.4.0
pip install --no-deps pytorch-msssim==1.0.0
pip install --no-deps h5py==3.12.1
pip install --no-deps transformers==4.48.2
pip install --no-deps kornia==0.8.0
pip install --no-deps chumpy==0.70
pip install --no-deps wandb==0.19.6
pip install --no-deps lightning==2.5.0.post0
pip install --no-deps omegaconf==2.3.0
pip install --no-deps adabound==0.0.5
pip install --no-deps torchmetrics==1.6.1
pip install --no-deps torchfile==0.1.0
pip install --no-deps mediapipe==0.10.21
pip install --no-deps einops==0.8.0
pip install --no-deps insightface==0.7.3
pip install --no-deps onnx==1.17.0
pip install --no-deps onnxruntime==1.20.1
pip install --no-deps huggingface-hub==0.25.0
pip install --no-deps diffusers==0.24.0

# simple-lama-inpainting 대체 패키지 설치
pip install git+https://github.com/advimman/lama.git

echo "설치가 완료되었습니다."