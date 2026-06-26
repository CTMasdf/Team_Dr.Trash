import requests
import json
import threading
import time

# ==========================================
# 서버 설정
# ==========================================
SERVER_IP   = "192.168.200.192"
SERVER_PORT = "8080"

BASE_URL      = f"http://{SERVER_IP}:{SERVER_PORT}"
EVENT_API_URL = f"{BASE_URL}/api/events"
SERVER_URL    = EVENT_API_URL   # main.py에서 import용

# ==========================================
# 장치 설정
# ==========================================
DEVICE_CODE = "DEVICE_001"

# ==========================================
# 통별 fill 상태 관리
# ==========================================
FILL_PERCENT = {
    "BIN_001_PLASTIC":  0,
    "BIN_001_CAN":      0,
    "BIN_001_GLASS":    0,
    "BIN_001_GENERAL":  0,
    "BIN_001_BEVERAGE": 0
}

# ==========================================
# binCode -> binId 매핑
# ==========================================
BIN_ID_MAP = {
    "BIN_001_PLASTIC":  1,
    "BIN_001_CAN":      2,
    "BIN_001_GLASS":    3,
    "BIN_001_GENERAL":  4,
    "BIN_001_BEVERAGE": 9
}

# ==========================================
# YOLO label 매핑
# ==========================================
TRASH_TYPE_MAP = {
    "plastic":   "PLASTIC",
    "can":       "CAN",
    "glass":     "GLASS",
    "general":   "GENERAL",
    "defective": "GENERAL"
}

BIN_CODE_MAP = {
    "plastic":   "BIN_001_PLASTIC",
    "can":       "BIN_001_CAN",
    "glass":     "BIN_001_GLASS",
    "general":   "BIN_001_GENERAL",
    "defective": "BIN_001_GENERAL"
}

# ==========================================
# 서버 상태 확인
# ==========================================
def check_server():
    try:
        response = requests.get(
            f"{BASE_URL}/api/bins/status/1",
            timeout=5
        )
        if response.status_code == 200:
            print("!!!!서버 연결 성공")
            return True
    except Exception as e:
        print(f"!!!!서버 연결 실패: {e}")
    return False


# ==========================================
# 서버에서 현재 적재량 복구
# ==========================================
def load_bin_status():
    global FILL_PERCENT

    print("📦 서버 적재량 동기화 시작")

    for bin_code, bin_id in BIN_ID_MAP.items():
        try:
            response = requests.get(
                f"{BASE_URL}/api/bins/status/{bin_id}",
                timeout=5
            )
            if response.status_code == 200:
                data         = response.json()
                fill_percent = data["fillPercent"]
                FILL_PERCENT[bin_code] = fill_percent
                print(f"✅ {bin_code} 적재량 복구: {fill_percent}%")
            else:
                print(f"❌ {bin_code} 조회 실패: {response.status_code}")
        except Exception as e:
            print(f"❌ {bin_code} 동기화 오류: {e}")


# ==========================================
# 현재 적재량 반환 (UI 표시용)
# ==========================================
def get_fill_percent():
    return FILL_PERCENT.copy()


# ==========================================
# 쓰레기 이벤트 전송 (YOLO 분류 결과)
# ==========================================
def send_result(result, image_path):
    global FILL_PERCENT

    if result is None:
        print("[API] 보낼 결과 없음")
        return

    try:
        label = result["label"]

        if label == "defective":
            label = "general"
            result["label"] = "general"

        bin_code = BIN_CODE_MAP.get(label, "BIN_001_GENERAL")

        if bin_code not in FILL_PERCENT:
            FILL_PERCENT[bin_code] = 0

        is_defective = (result["label"] == "defective")

        data = {
            "deviceCode":    DEVICE_CODE,
            "binCode":       bin_code,
            "trashTypeCode": TRASH_TYPE_MAP.get(label, "GENERAL"),
            "isDefective":   is_defective,
            "defectReason":  "오염 감지" if is_defective else None,
            "confidence":    result["confidence"],
            "imageUrl":      image_path,
            "fillPercent":   FILL_PERCENT[bin_code]
        }

        print("\n==============================")
        print("[API] 이벤트 전송")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print("==============================")

        response = requests.post(
            EVENT_API_URL,
            json=data,
            timeout=5
        )

        print(f"[API] Success: {response.status_code}")
        print("[API Response]", response.text)

    except Exception as e:
        print("[API ERROR]", e)


# ==========================================
# 직원 호출
# ==========================================
def request_staff_call():
    try:
        response = requests.post(
            f"{BASE_URL}/api/staff/call",
            timeout=5
        )
        print(f"[STAFF CALL] {response.status_code}")
    except Exception as e:
        print("[STAFF CALL ERROR]", e)


# ==========================================
# 현재 적재량 출력
# ==========================================
def print_fill_status():
    print("\n========== 현재 적재량 ==========")
    for k, v in FILL_PERCENT.items():
        print(f"{k}: {v}%")
    print("================================")