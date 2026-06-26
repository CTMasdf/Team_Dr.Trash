#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import time
import tkinter as tk
import serial

from core.camera_service import (
    init_camera,
    capture_image,
    stop_camera
)

from core.yolo_service import detect

from core.api_service import (
    send_result,
    check_server,
    load_bin_status,
    print_fill_status,
    get_fill_percent,
    request_staff_call
)

# ==============================
# 설정
# ==============================
SERIAL_PORT = '/dev/ttyUSB0'
BAUDRATE    = 115200

# ==============================
# 시리얼 연결
# ==============================
try:
    ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
    time.sleep(2)
    print("[Serial] 아두이노 연결 성공")
except Exception as e:
    print("[Serial] 연결 실패:", e)
    ser = None

# ==============================
# 적재량 로컬 캐시
# ==============================
fill_cache = {
    "BIN_001_GENERAL": 0,
    "BIN_001_PLASTIC": 0,
    "BIN_001_CAN":     0,
    "BIN_001_GLASS":   0,
}

ARDUINO_KEY_MAP = {
    "GENERAL": "BIN_001_GENERAL",
    "PLASTIC": "BIN_001_PLASTIC",
    "CAN":     "BIN_001_CAN",
    "GLASS":   "BIN_001_GLASS",
}

# ==============================
# UI 클래스
# ==============================
class RecycleUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Smart Trash AI")
        self.root.configure(bg="#E8F5E9")
        self.root.geometry("800x480")
        self.root.attributes('-fullscreen', True)
        self.root.configure(cursor="none")
        self.root.bind("<Escape>", self.exit_program)
        self.current_screen = "main"
        self.show_main()
        self.root.after(5000, self.refresh_bin_status)

    def exit_program(self, event=None):
        print("[System] 종료")
        self.root.destroy()

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def refresh_bin_status(self):
        try:
            old_data = get_fill_percent()
            load_bin_status()
            new_data = get_fill_percent()
            if old_data != new_data and self.current_screen == "main":
                print("[Sync] 적재량 변경 감지 → 화면 갱신")
                self.show_main()
        except Exception as e:
            print("[Sync Error]", e)
        self.root.after(5000, self.refresh_bin_status)

    def show_main(self):
        self.current_screen = "main"
        self.clear()

        main_frame = tk.Frame(self.root, bg="#E8F5E9")
        main_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            main_frame,
            text="Smart Trash AI",
            font=("Arial", 30, "bold"),
            bg="#E8F5E9",
            fg="#2C5F2D"
        ).pack(pady=10)

        tk.Label(
            main_frame,
            text="쓰레기를 투입구에 넣어주세요",
            font=("Arial", 18),
            bg="#E8F5E9",
            fg="#555555"
        ).pack(pady=8)

        fill_data = get_fill_percent()

        status_frame = tk.Frame(main_frame, bg="#E8F5E9")
        status_frame.pack(pady=20)

        items = [
            ("플라스틱", "BIN_001_PLASTIC", "#4CAF50"),
            ("캔",       "BIN_001_CAN",     "#FF9800"),
            ("유리",     "BIN_001_GLASS",   "#2196F3"),
            ("일반",     "BIN_001_GENERAL", "#9E9E9E"),
        ]

        for name, key, color in items:
            fill = fill_data.get(key, 0)

            if fill >= 95:
                bar_color   = "#E53935"
                status_text = f"{fill}%\nFULL"
            elif fill >= 80:
                bar_color   = "#FBC02D"
                status_text = f"{fill}%\n주의"
            else:
                bar_color   = color
                status_text = f"{fill}%"

            card = tk.Frame(
                status_frame,
                bg="white",
                width=120,
                height=160,
                bd=2,
                relief="ridge"
            )
            card.pack(side="left", padx=8)
            card.pack_propagate(False)

            tk.Label(
                card,
                text=name,
                font=("Arial", 14, "bold"),
                bg="white",
                fg=color
            ).pack(pady=10)

            bar_bg = tk.Frame(card, bg="#DDDDDD", width=80, height=22)
            bar_bg.pack(pady=10)
            bar_bg.pack_propagate(False)

            fill_width = int(80 * fill / 100)
            tk.Frame(bar_bg, bg=bar_color, width=fill_width, height=22).place(x=0, y=0)

            tk.Label(
                card,
                text=status_text,
                font=("Arial", 18, "bold"),
                bg="white",
                fg=bar_color,
                justify="center"
            ).pack(pady=8)

        tk.Button(
            main_frame,
            text="[ ! ] 직원 호출",
            font=("Arial", 18, "bold"),
            bg="#E53935",
            fg="white",
            activebackground="#C62828",
            relief="flat",
            padx=30,
            pady=12,
            command=self.call_staff
        ).pack(pady=10)

    def call_staff(self):
        self.current_screen = "staff"
        request_staff_call()
        self.clear()

        tk.Label(
            self.root,
            text="직원을 호출했습니다",
            font=("Arial", 30, "bold"),
            bg="#E8F5E9",
            fg="#E53935"
        ).pack(pady=120)

        tk.Label(
            self.root,
            text="잠시만 기다려주세요",
            font=("Arial", 20),
            bg="#E8F5E9",
            fg="#555555"
        ).pack()

        self.root.after(5000, self.show_main)

    def show_detected(self):
        self.current_screen = "detected"
        self.clear()

        tk.Label(
            self.root,
            text="쓰레기 감지됨",
            font=("Arial", 34, "bold"),
            bg="#E8F5E9",
            fg="#2C5F2D"
        ).pack(pady=100)

        tk.Label(
            self.root,
            text="AI 분석을 시작합니다...",
            font=("Arial", 20),
            bg="#E8F5E9",
            fg="#555555"
        ).pack()

    def show_sorting(self):
        self.current_screen = "sorting"
        self.clear()

        self.loading_label = tk.Label(
            self.root,
            text="AI 분류 중",
            font=("Arial", 34, "bold"),
            bg="#E8F5E9",
            fg="#2C5F2D"
        )
        self.loading_label.pack(pady=130)

        tk.Label(
            self.root,
            text="잠시만 기다려주세요",
            font=("Arial", 18),
            bg="#E8F5E9",
            fg="#555555"
        ).pack()

        self.loading_dots = 0
        self.animate_loading()

    def animate_loading(self):
        dots = "." * (self.loading_dots % 4)
        if not self.loading_label.winfo_exists():
            return
        self.loading_label.config(text=f"AI 분류 중{dots}")
        self.loading_dots += 1
        self.loading_animation = self.root.after(500, self.animate_loading)

    def show_result(self, trash_type):
        self.current_screen = "result"

        if hasattr(self, "loading_animation"):
            self.root.after_cancel(self.loading_animation)

        self.clear()

        name_map = {
            "GENERAL": "일반쓰레기",
            "PLASTIC": "플라스틱",
            "CAN":     "캔",
            "GLASS":   "유리"
        }

        display_name = name_map.get(trash_type, trash_type)

        tk.Label(
            self.root,
            text=f"{display_name}",
            font=("Arial", 38, "bold"),
            bg="#E8F5E9",
            fg="#2C5F2D"
        ).pack(pady=90)

        tk.Label(
            self.root,
            text="분류 완료 — 아두이노 동작 중",
            font=("Arial", 24),
            bg="#E8F5E9",
            fg="#555555"
        ).pack()

        self.root.after(30000, self.show_main)

    def show_detection_fail(self):
        self.current_screen = "fail"

        if hasattr(self, "loading_animation"):
            self.root.after_cancel(self.loading_animation)

        self.clear()

        tk.Label(
            self.root,
            text="인식 실패",
            font=("Arial", 34, "bold"),
            bg="#E8F5E9",
            fg="#E53935"
        ).pack(pady=110)

        tk.Label(
            self.root,
            text="쓰레기를 다시 넣어주세요",
            font=("Arial", 20),
            bg="#E8F5E9",
            fg="#555555"
        ).pack()

        self.root.after(2000, self.show_main)

    def show_done(self):
        self.current_screen = "done"

        if hasattr(self, "loading_animation"):
            self.root.after_cancel(self.loading_animation)

        self.clear()

        tk.Label(
            self.root,
            text="분류가 완료되었습니다",
            font=("Arial", 34, "bold"),
            bg="#E8F5E9",
            fg="#2C5F2D"
        ).pack(pady=100)

        tk.Label(
            self.root,
            text="이용해 주셔서 감사합니다 😊",
            font=("Arial", 22),
            bg="#E8F5E9",
            fg="#555555"
        ).pack()

        self.root.after(3000, self.show_main)


# ==============================
# AI 처리 함수
# ==============================
def process_trash(ui):
    print("[System] AI 분류 시작")
    ui.root.after(0, ui.show_sorting)

    try:
        image_path = capture_image()
        result     = detect(image_path)

        print("[YOLO Result]", result)

        if result is None:
            print("[System] 감지 실패")
            ui.root.after(0, ui.show_detection_fail)
            return

        label = result.get("label", "UNKNOWN").upper()

        if label == "DEFECTIVE":
            label = "GENERAL"
            result["label"] = "general"

        ui.root.after(0, lambda: ui.show_result(label))

        send_to_arduino(label)
        send_result(result, image_path)

        print(f"[System] 아두이노로 '{label}' 전송 완료")

    except Exception as e:
        print("[ERROR]", e)
        ui.root.after(0, ui.show_main)


# ==============================
# 아두이노로 분류 명령 전송
# ==============================
def send_to_arduino(label):
    if ser:
        try:
            ser.write((label + '\n').encode())
            print(f"[Serial] 전송: {label}")
        except Exception as e:
            print(f"[Serial] 전송 실패: {e}")
    else:
        print("[Serial] 연결 없음 → 전송 스킵")


# ==============================
# 적재량 서버 전송
# ==============================
def send_fill_to_server():
    import requests
    from core.api_service import SERVER_URL

    for arduino_key, bin_key in ARDUINO_KEY_MAP.items():
        fill_percent = fill_cache.get(bin_key, 0)
        try:
            payload = {
                "deviceCode":    "DEVICE_001",
                "binCode":       bin_key,
                "trashTypeCode": arduino_key,
                "isDefective":   False,
                "defectReason":  "",
                "confidence":    1.0,
                "imageUrl":      "",
                "fillPercent":   fill_percent
            }
            response = requests.post(SERVER_URL, json=payload, timeout=3)
            print(f"[Server] 적재량 전송 {arduino_key}: {fill_percent}% ({response.status_code})")
        except Exception as e:
            print(f"[Server] 적재량 전송 실패 {arduino_key}: {e}")


# ==============================
# 초음파 데이터 파싱
# 아두이노 출력 형식: "BIN:80,45,60,30"
# ==============================
def parse_fill_data(line):
    try:
        # BIN:per_1,per_2,per_3,per_4
        data = line.replace("BIN:", "").strip()
        values = data.split(",")

        keys = ["GENERAL", "PLASTIC", "CAN", "GLASS"]
        for i, key in enumerate(keys):
            if i < len(values):
                bin_key = ARDUINO_KEY_MAP.get(key)
                if bin_key:
                    fill_cache[bin_key] = int(values[i].strip())

        print(f"[적재량 업데이트] {fill_cache}")

    except Exception as e:
        print(f"[파싱 오류] {e}")


# ==============================
# 아두이노 시리얼 수신 루프
# ==============================
def serial_read_loop(ui):
    print("[Serial] 수신 루프 시작")

    while True:
        if ser and ser.in_waiting > 0:
            try:
                line = ser.readline().decode('utf-8', errors='replace').strip()

                if not line:
                    continue

                print(f"[Arduino] {line}")

                if line == "TRASH_DETECTED":
                    print("[System] 쓰레기 감지 → AI 분류 시작")
                    ui.root.after(0, ui.show_detected)
                    time.sleep(0.5)
                    threading.Thread(
                        target=process_trash,
                        args=(ui,),
                        daemon=True
                    ).start()

                elif line.startswith("BIN:"):
                    parse_fill_data(line)
                    threading.Thread(
                        target=send_fill_to_server,
                        daemon=True
                    ).start()
                    ui.root.after(0, ui.show_done)

            except Exception as e:
                print(f"[Serial Error] {e}")

        time.sleep(0.05)


# ==============================
# 메인
# ==============================
def main():
    print("[System] Starting Smart Trash AI...")

    if not check_server():
        print("[System] 서버 연결 실패 — 오프라인 모드로 진행")

    load_bin_status()
    print_fill_status()

    init_camera()

    root = tk.Tk()
    ui   = RecycleUI(root)

    serial_thread = threading.Thread(
        target=serial_read_loop,
        args=(ui,),
        daemon=True
    )
    serial_thread.start()

    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\n[System] 종료 요청")
    finally:
        stop_camera()
        if ser:
            ser.close()
        print("[System] 자원 정리 완료")


if __name__ == "__main__":
    main()