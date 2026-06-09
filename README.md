# 🎙️ Ryo: RVC AI-Driven Discord Bot Engine

> **Python 기반 Discord API와 RVC(Retrieval-based Voice Conversion) 모델 탐구를 위한 AI 음성 합성 봇 프로젝트**

---

## 📌 Project Overview
본 프로젝트는 **Discord API**를 활용하여 고도화된 **RVC(Retrieval-based Voice Conversion) AI 모델**의 음성 추론 및 변환 성능을 탐구하고 실전 서빙 환경을 검증하는 것을 주 목적으로 합니다.

단순한 로컬 스크립트 실행을 넘어, **K3s(경량화 쿠버네티스)** 클러스터 인프라를 첫 도입하여 가상화 배포 환경을 구축했으며, **Tailscale** 오버레이 네트워크를 통해 보안성과 인프라 간 연결성을 확보한 주도적 솔로 해커톤 프로젝트입니다.

---

## 🛠 Tech Stack & Environment

### 1. Development & AI Language
* **Python:** 외부 AI 추론 모델 라이브러리 및 Discord API 파이프라인의 고성능 비동기 처리를 위한 단일 개발 언어 채택.
* **RVC (Retrieval-based Voice Conversion):** 고품질 음성 합성을 위한 RVC 모델 연동 및 오디오 오버레이 파이프라인 최적화.

### 2. Infrastructure & Networking
* **K3s (Lightweight Kubernetes):** 대규모 오케스트레이션의 오버레이를 줄인 경량 쿠버네티스 환경을 첫 도입하여 컨테이너 기반 봇 서빙 인프라 구축 및 자원 관리.
* **Tailscale:** 복잡한 방화벽 및 NAT 환경을 우회하고 클러스터 노드 간 안전한 메시(Mesh) 네트워크를 구성하기 위한 Zero-Trust VPN 기술 활용.

---

## 🏗 System Architecture Flow

```
[ Discord Client ] ──(Voice/Text Event)──> [ Tailscale VPN Secure Line ]
│
▼
[ K3s (Kubernetes) Cluster ]
│
▼
[ Python Bot Core ]
│ (Audio Extraction)
▼
[ RVC AI Model Engine ]
│ (Voice Conversion)
▼
[ Discord Voice Channel ] <──(Stream Audio)──────────┘
```

---

## 🎯 Key Engineering Points (핵심 성과 및 목적)

* **RVC AI 모델 서빙 최적화:** Python 비동기 환경에서 오디오 데이터의 디스크 I/O 및 메모리 병목을 줄이고, RVC 추론 엔진이 실시간에 가깝게 음성을 변환하여 서빙할 수 있도록 파이프라인 아키텍처 탐구.
* **첫 K3s 가상화 인프라 도입:** 기존 단일 컨테이너 환경에서 벗어나, 쿠버네티스(K3s) API를 활용한 컨테이너 생명 주기 관리 및 자원 제어를 직접 경험하고 인프라 관리 역량 확장.
* **메시 네트워크 기반 보안 통제:** 공인 IP 노출을 최소화하고, 분산된 리소스 간의 안전한 내부 통신을 위해 Tailscale 프라이빗 네트워크 인프라 융합.
* **WIP (Work In Progress):** 솔로 해커톤 형태의 프로토타이핑을 시작으로 코어 로직 검증을 완료했으며, 향후 인프라 리소스 모니터링 및 모델 고도화 단계를 준비 중입니다.

---

## 💾 Directory Structure
```
├── .gitignore
├── .env                  # 보안상 해당 파일 생략
├── README.md
├── main.py               # Python 기반 Discord API 및 메시지 핸들링 모듈
├── ryo.py
├── requirements.txt
├── ryo_bot.pth
├── added_IVF421_Flat_nprobe_1_ryo_bot_v2.index
├── Dockerfile
├── .dockerignore
└── deployment.yaml
```

---

📄 License This project is licensed under the MIT License - see the LICENSE file for details.
