FROM python:3.10-slim

# 1. 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libopus-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ❗️ 핵심: 최신 pip 대신, 메타데이터 오류를 무시해주는 24.0 버전을 설치합니다.
RUN pip install --no-cache-dir "pip<24.1"

# 이제 requirements.txt를 설치하면 omegaconf 2.0.6도 조용히 깔립니다.
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt

COPY . .

# 5. Ryzen 4500 (6코어) 최적화 환경 변수 주입
ENV OMP_NUM_THREADS=6
ENV MKL_NUM_THREADS=6
ENV PYTHONUNBUFFERED=1

# 6. 실행
CMD ["python", "main.py"]