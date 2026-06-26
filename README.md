# Smart Trash AI - 자동 쓰레기 분류 시스템 (Smart Recycle AI)

본 저장소는 **딥러닝 기반 자동 분리수거 통합 시스템(Smart Trash AI)** 프로젝트의 메인 메커니즘을 관장하는 **Raspberry Pi 기반의 Edge Gateway 애플리케이션 및 시스템 통합 소스 코드**를 담고 있습니다. 

Spring Boot 중앙 웹 서버, React/Android 관리자 대시보드, YOLOv4-Tiny 기반의 실시간 객체 인식 파이프라인, 그리고 아두이노 메가(Arduino Mega) 하드웨어 제어 시스템을 하나로 묶어주는 핵심 컨트롤 타워 역할을 수행합니다.

---

## 📺 프로젝트 시연 영상 및 채널

아래의 이미지 또는 링크를 클릭하시면 전체 시스템의 실제 작동 영상을 확인하실 수 있습니다:

[![Smart Trash AI 시연 영상](https://img.shields.io/badge/YouTube-시연_영상_보기-red?style=for-the-badge&logo=youtube)](https://www.youtube.com/watch?v=cHrGiQiQw6l7s)

* **제품 데모 영상**: [YouTube에서 보기](https://www.youtube.com/watch?v=cHrGiQiQw6l7s)
* **공식 개발자 채널**: [Genkkk11 YouTube 채널](https://www.youtube.com/@genkkk11)

---

## 🛠️ 팀장 및 역할 정의 (Project Manager & Integration Engineer)

본 프로젝트는 총 6인으로 구성된 팀 프로젝트로, 저는 **프로젝트 매니저(팀장)**이자 **시스템 통합 엔지니어**로서 전체 개발 라이프사이클을 리드하고 이종(Heterogeneous) 플랫폼 간의 데이터 파이프라인을 구축했습니다.

* **총괄 프로젝트 매니징**: 기능 요구사항 정의(PRD), 멀티 티어 아키텍처 수립, WBS 기반의 마일스톤 관리 및 일정 조율을 주도했습니다. GitHub 기반의 버전 관리 체계를 정립하여 H/W 및 S/W 서브 팀 간의 개발 진행 상황을 매끄럽게 동기화했습니다.
* **엣지 컴퓨팅 기반 시스템 통합**: 단일 카메라 구조 환경에서 OpenCV 스트리밍, YOLO 인프라 레이어, 아두이노 구동 제어, 클라우드 서버 API 연동이 예외 처리 없이 유기적으로 맞물려 돌아가도록 전체 파이프라인을 단독 설계 및 구현했습니다.

---

## 🏗️ 전체 시스템 아키텍처 (System Data Flow)

투입 감지부터 관리자 관제 대시보드 반영까지 **평균 3초 이내**에 완결되는 End-to-End 데이터 흐름입니다.

[ 쓰레기 투입 ]
│ (IR 센서 감지)
▼
[ 웹 카메라 ] ──(영상 스트림)──> [ Raspberry Pi 4B (YOLOv4-Tiny) ] ── (3초 이내 판별)
│
┌──────────────────────────────┴──────────────────────────────┐
▼ (Serial / UART)                                             ▼ (HTTP REST API / JSON)
[ Arduino Mega (구동부 제어) ]                                  [ Spring Boot 웹 서버 ]
├─ 서보 모터 (개폐구 제어)                                             │ (WebSocket / REST)
├─ DC 기어드 모터 (X축 레일 이동)                                      ▼
└─ 리니어 액추에이터 (릴레이 모듈 제어 배출)                [ React Web / Kotlin App 대시보드 ]
(실시간 적재량 및 상태 모니터링)

---

## 🚀 주요 구현 기능 (본인 기여 부분)

### 1. 실시간 객체 인식 및 분리 파이프라인 구축 (`/src/inference/`)
* Raspberry Pi 4B(8GB) 환경에서 OpenCV를 활용한 고효율 비디오 스트리밍 전처리 파이프라인을 구축했습니다.
* Custom 학습된 **YOLOv4-Tiny 모델**을 레이어 단에서 로드하여, 4가지 핵심 클래스(PET, CAN, GLASS, PAPER) 및 음료 잔여물 등의 오염도를 실시간으로 판정하는 실시간 추론 로직을 구현했습니다.

### 2. 아두이노 메가 하드웨어 시리얼 통신 제어 (`/src/communication/serial_client.py`)
* AI 분류 데이터 및 센서 상태에 따라 핀 확장성을 확보한 **Arduino Mega** 물리 구동부에 정밀 명령을 하달하는 Serial(UART) 패킷 통신 프로토콜을 설계했습니다.
* 다중 모터 구동 환경에서 발생할 수 있는 데이터 유실 및 신호 간섭을 방지하기 위해 엄격한 타임아웃 처리와 커스텀 패킷 동기화 알고리즘을 적용했습니다.

### 3. 클라우드 관제 웹 서버 REST API 및 JSON 연동 (`/src/communication/api_client.py`)
* 엣지에서 생성된 실시간 분류 로그, 오염도 정보 및 초음파 센서 기반의 적재량 진단 데이터를 규격화된 JSON 페이로드로 가공했습니다.
* 백엔드 Spring Boot 서버와의 HTTP REST API(POST) 동기/비동기 연동을 통해 중앙 데이터베이스(MySQL)를 실시간 업데이트하고, 현장 관리자가 웹(React) 및 앱(Android)에서 실시간 WebSocket 알림을 수신할 수 있는 기반을 완성했습니다.

---

## 💻 기술 스택 및 개발 환경 (Tech Stack)
* **Hardware**: Raspberry Pi 4B, Arduino Mega, Web Camera, SMPS(12V), 릴레이 모듈, 리니어 액추에이터
* **OS / Environment**: Raspberry Pi OS (Debian), Microchip Studio
* **Language**: Python 3.x, C/C++
* **Libraries / Framework**: OpenCV, PySerial, Requests, NumPy, Darknet (OpenCV DNN Module)
* **Collaboration Tools**: GitHub, Notion

---

## ⚙️ 시작하기 및 환경 설정 (Prerequisites & Configuration)

```bash
# 1. 저장소 복제 (Repository Clone)
git clone [https://github.com/CTMasdf/Team_Dr.Trash.git](https://github.com/CTMasdf/Team_Dr.Trash.git)
cd Team_Dr.Trash

# 2. 필수 종속성 패키지 설치
pip install -r requirements.txt

중앙 환경 설정 파일 구성 (config.json)
서버 인프라 변경 및 포트 교체 시 유연하게 대응할 수 있도록 엔드포인트와 기기 포트 정보를 하드코딩 없이 외부 파일로 분리하여 관리합니다:

JSON
{
  "SERVER_URL": "http://your-web-server-ip:8080/api/trash",
  "SERIAL_PORT": "/dev/ttyACM0",
  "BAUD_RATE": 115200
}
