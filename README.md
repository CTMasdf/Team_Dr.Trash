# Smart Recycle AI — AI 기반 자동 쓰레기 분류 시스템

> YOLO 기반 객체 인식 + 임베디드 제어 + 실시간 관리자 대시보드를 하나로 묶은 스마트 분리수거 통합 시스템

**팀 쓰레기 박사단** | 명지전문대학교 캡스톤디자인 2026  
**팀장: 최태민** · H/W: 한규철, 배준성, 정승현 · S/W: 김호중, 김용우  
**기간:** 2026.03 ~ 2026.06 (3개월) | **예산:** 1,074,704원

[![YouTube](https://img.shields.io/badge/YouTube-시연영상-red?logo=youtube)](https://www.youtube.com/watch?v=cHrGiQw6l7s)
[![GitHub](https://img.shields.io/badge/GitHub-소스코드-black?logo=github)](https://github.com/CTMasdf/Team_Dr.Trash)

> **이 저장소는 팀장(최태민)이 직접 작성한 코드만 포함합니다.**  
> 팀원 담당 코드(YOLOv4-Tiny 추론 모듈, Spring Boot, React, Android, Arduino)는 별도 관리됩니다.

---

## 제가 맡은 역할

| 구분 | 내용 |
|------|------|
| 포지션 | 팀장 (Project Manager) · 시스템 통합 |
| 개발 범위 | Raspberry Pi 메인 프로그램 전체 (`main.py` 531줄, `service.py`) |
| AI 연동 | 팀원 구현 YOLOv4-Tiny 모듈 호출 — 카메라 캡처 → 분류 결과 수신 → 후처리 파이프라인 구축 |
| UI | tkinter 기반 7인치 터치스크린 5개 화면 상태 관리 |
| 통신 | Arduino Mega 시리얼(UART 115200), Spring Boot REST API(POST) |
| 센서 | 초음파 4채널 적재량 파싱 및 서버 동기화 |
| 기타 | 전체 일정 조율, 발표 자료 총괄, 하드웨어 통합 디버깅 |

---

## 시스템 구성

### 전체 아키텍처 (3계층)

```
[Edge Layer]                    [Hub Layer]               [Client Layer]
Raspberry Pi 4                  Spring Boot               React Web Dashboard
 ├─ YOLOv4-Tiny 연동       →   REST API 수신        →   실시간 적재량 모니터링
 ├─ tkinter Touch UI             MySQL 저장                경고 알림 / 분류 이력
 └─ Serial UART                  WebSocket 발행       →   Android App 알림
        ↓
Arduino Mega
 ├─ DC 기어드 모터 (X축 레일)
 ├─ 서보모터 (개폐구)
 ├─ 리니어 액추에이터 (투하)
 ├─ IR 센서 (투입 감지)
 └─ 초음파 센서 ×4 (적재량)
```

### 동작 흐름

```
1. IR 센서 감지 (Arduino)
   → "TRASH_DETECTED" 시리얼 신호 전송

2. 카메라 캡처 후 팀원 구현 YOLOv4-Tiny 모듈 호출
   → 분류 결과(label, confidence) 수신 및 후처리
   → 4종 분류 + 오염물(Defective) 판별, 평균 3초 이내

3. 분류 결과 → Arduino 시리얼 전송
   → X축 DC모터로 해당 통 위치 이동
   → 위치 감지 센서 확인 후 액추에이터로 투하

4. 초음파 센서로 적재량 측정
   → "BIN:80,45,60,30" 형식 파싱
   → REST API로 서버 POST 전송

5. tkinter UI 업데이트 + 초기 화면 복귀
```

---

## 하드웨어 사양

| 항목 | 사양 |
|------|------|
| 제품 크기 | 가로 161.5cm × 세로 86cm × 높이 100cm |
| 메인 제어 | Raspberry Pi 4B (8GB) |
| 센서/모터 제어 | Arduino Mega (핀 확장 목적으로 Uno → Mega 변경) |
| 카메라 | Raspberry Pi Camera Module |
| 디스플레이 | 7인치 라즈베리파이 터치스크린 |
| 전원 | SMPS 12V → DC 컨버터로 5V 분배 |
| 구동부 | DC 기어드 모터, 리니어 액추에이터, 서보모터 |
| 제어 방식 | 4094 시프트 레지스터 (Arduino 핀 부족 해결) |
| 센서 | IR 센서 ×2, 초음파 센서 ×4, 금속 센서 |

---

## 기술 스택

| 구분 | 기술 |
|------|------|
| 임베디드 | Python (Raspberry Pi), tkinter |
| AI 연동 | YOLOv4-Tiny 모듈 연동, OpenCV (카메라 캡처) |
| 통신 | Serial UART (115200 baud), REST API (HTTP POST), TCP/IP Socket |
| 서버 (팀원) | Spring Boot, MySQL, JPA, Spring Security (JWT), WebSocket |
| 프론트 (팀원) | React, Android (Kotlin) |
| 협업 | GitHub, Padlet |

---

## 서버 전송 데이터 형식

```json
{
  "deviceCode": "DEVICE_001",
  "binCode": "BIN_001_PLASTIC",
  "trashTypeCode": "PLASTIC",
  "isDefective": false,
  "confidence": 0.94,
  "imageUrl": "",
  "fillPercent": 45
}
```

초음파 파싱 형식 (Arduino → Raspberry Pi):
```
BIN:80,45,60,30
→ GENERAL:80% / PLASTIC:45% / CAN:60% / GLASS:30%
```

---

## 환경 설정

```bash
git clone https://github.com/CTMasdf/Team_Dr.Trash.git
cd Team_Dr.Trash
pip install -r requirements.txt
```

`config.json`:
```json
{
  "SERVER_URL": "http://your-server-ip:8080/api/trash",
  "SERIAL_PORT": "/dev/ttyUSB0",
  "BAUD_RATE": 115200
}
```

---

## 성과 및 한계

**정량적 성과**
- AI 처리 속도: 평균 3초 이내
- 분류 동작 사이클: 15~25초
- 총 개발 기간: 3개월 / 예산 107만원

**향후 개선 방향**
- NPU (Google Coral, Movidius) 도입으로 추론 속도 개선
- 센서 융합으로 분류 정확도 향상
- 오류 발생 시 SW 자동 복구 로직 추가
