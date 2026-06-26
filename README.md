# Smart Trash AI - Edge Gateway System (Raspberry Pi)

본 저장소는 Spring Boot 관리용 웹 서버, YOLOv4-Tiny 기반의 객체 인식 파이프라인, 그리고 Arduino 하드웨어 제어를 Serial(UART) 통신으로 연결하는 Raspberry Pi 기반의 Edge Gateway 애플리케이션입니다.

---

## 📺 프로젝트 시연 영상

아래의 이미지 또는 링크를 클릭하시면 시스템 작동 영상을 확인하실 수 있습니다:

[![Smart Trash AI 시연 영상](https://img.shields.io/badge/YouTube-시연_영상_보기-red?style=for-the-badge&logo=youtube)](https://www.youtube.com/watch?v=cHrGiQiQw6l7s)

* **동작 영상**: [YouTube에서 보기](https://www.youtube.com/watch?v=cHrGiQiQw6l7s)
* **공식 채널**: [Genkkk11 YouTube 채널](https://www.youtube.com/@genkkk11)

---

## 🛠️ 핵심 역할 및 기여도 (프로젝트 매니저 & 시스템 통합 엔지니어)

팀의 **프로젝트 매니저(팀장)**이자 **시스템 통합 엔지니어**로서, 전체 개발 라이프사이클을 관리하고 멀티 티어 아키텍처를 유기적으로 연결하는 핵심 데이터 파이프라인을 설계 및 구현했습니다:

* **프로젝트 관리 및 시스템 아키텍처 설계**: 6인으로 구성된 팀의 기능 요구사항 정의, 통신 인터페이스 규격 수립, 마일스톤 일정을 주도했습니다. GitHub 기반의 버전 관리 체계를 구축하고, 하드웨어(H/W) 및 소프트웨어(S/W) 서브 팀 간의 개발 진행 상황을 조율했습니다.
* **Edge-to-Cloud 통합**: Raspberry Pi에서 추출된 AI 추론 데이터를 구조화된 JSON 패킷으로 변환하고, REST API를 통해 Spring Boot 중앙 집중식 서버로 안정적으로 전송하는 통신 스크립트를 개발했습니다.
* **Edge-to-Hardware 제어 브릿지**: Raspberry Pi와 Arduino Mega 간의 신뢰성 높은 시리얼 통신 프로토콜을 설계하여, 분류 결과에 따라 모터 및 액추에이터 등 물리적 구동부를 실시간으로 정밀 제어할 수 있도록 구현했습니다.

---

## 🏗️ 시스템 데이터 흐름 (System Data Flow)

[ 웹 카메라 ] ──(영상 스트림)──> [ Raspberry Pi (YOLOv4-Tiny) ]
│
┌──────────────────────────────┴──────────────────────────────┐
▼ (Serial / UART)                                             ▼ (HTTP REST API / JSON)
[ Arduino Mega (모터 및 구동부 제어) ]                          [ Spring Boot 웹 서버 ]

---

## 🚀 주요 기능 (본인 기여 부분)

### 1. 객체 인식 및 파이프라인 구축 (`/src/inference/`)
* Raspberry Pi 환경에서 OpenCV를 활용한 실시간 웹캠 비디오 스트리밍 및 이미지 전처리 파이프라인을 구현했습니다.
* custom-training된 YOLOv4-Tiny 모델을 로드하여 4가지 주요 카테고리(페트병, 캔, 유리병, 종이)를 분류하고, 오염도를 3초 이내에 판단하는 추론 로직을 완성했습니다.

### 2. 아두이노 시리얼 통신 제어 (`/src/communication/serial_client.py`)
* AI 분류 데이터에 기반하여 구동 명령을 하드웨어에 전달하는 Serial/UART 패킷 전송 프레임워크를 개발했습니다.
* 통신 예외 처리 및 타임아웃 로직을 철저히 설계하여, 하드웨어 구동 중 데이터 유실 없이 실시간으로 분류 액추에이터가 동작하도록 보장했습니다.

### 3. 웹 서버 REST API 연동 (`/src/communication/api_client.py`)
* 실시간 객체 분류 결과 및 장비의 상태 진단 데이터를 정제된 JSON 페이로드로 변환하는 모듈을 구현했습니다.
* 안정적인 HTTP POST 요청 시퀀스를 통해 중앙 MySQL 데이터베이스를 업데이트하고, 웹 및 모바일 관리자 대시보드에 실시간 데이터가 동기화되도록 연동했습니다.

---

## 💻 기술 스택 및 개발 환경
* **OS**: Raspberry Pi OS (Debian)
* **Language**: Python 3.x
* **Libraries**: OpenCV, PySerial, Requests, NumPy
* **AI Framework**: Darknet / OpenCV DNN Module (YOLOv4-Tiny)
* **Collaboration Tools**: GitHub, Notion

---

## ⚙️ 시작하기 및 환경 설정

```bash
# 저장소 복제
git clone [https://github.com/your-username/smart-trash-ai-edge-gateway.git](https://github.com/your-username/smart-trash-ai-edge-gateway.git)
cd smart-trash-ai-edge-gateway

# 필수 패키지 설치
pip install -r requirements.txt
