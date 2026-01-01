""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""
"""
QRPicker Final Stable + Configurable Version
"""

# =============================
# 二重起動防止
# =============================
import sys
import ctypes

mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "QRPicker_Mutex")
if ctypes.windll.kernel32.GetLastError() == 183:
    sys.exit()

# =============================
# imports
# =============================
import tkinter as tk
from tkinter import messagebox
import threading
import webbrowser
import configparser

import cv2
import numpy as np
import mss
import pyperclip

import ctypes.wintypes
import pystray
from PIL import Image

from winotify import Notification

# =============================
# DPI 無効化（ズレ防止）
# =============================
ctypes.windll.user32.SetProcessDPIAware()

# =============================
# config.ini 読み込み
# =============================
config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")


def cfg(section, key, default):
    try:
        return config.get(section, key)
    except Exception:
        return default


# =============================
# 通知
# =============================
def notify(title, msg):
    if cfg("general", "notify", "true").lower() != "true":
        return
    Notification(
        app_id="QRPicker",
        title=title,
        msg=msg,
        duration="short"
    ).show()


def show_startup_notify():
    notify(
        "QRPicker Ready",
        "Ctrl + Shift + Q でスキャン\nEsc でキャンセル"
    )


# =============================
# グローバル
# =============================
scanning = False
history = []

# =============================
# resource path
# =============================
def resource_path(p):
    base = getattr(sys, "_MEIPASS", "")
    return base + "\\" + p if base else p


# =============================
# Tk root
# =============================
root = tk.Tk()
root.withdraw()

# =============================
# テーマ
# =============================
def is_dark():
    return cfg("general", "theme", "dark") == "dark"


# =============================
# 画面選択
# =============================
def select_screen():
    overlay = tk.Toplevel(root)
    overlay.attributes("-topmost", True)
    overlay.overrideredirect(True)
    overlay.attributes("-alpha", 0.35)

    sw = overlay.winfo_screenwidth()
    sh = overlay.winfo_screenheight()
    overlay.geometry(f"{sw}x{sh}+0+0")

    bg = "#000" if is_dark() else "#fff"
    canvas = tk.Canvas(overlay, bg=bg, highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)
    canvas.configure(cursor="cross")

    start = {}
    rect = None
    result = {"coords": None}

    def on_press(e):
        nonlocal rect
        start["x"], start["y"] = e.x, e.y
        rect = canvas.create_rectangle(
            e.x, e.y, e.x, e.y,
            outline="red", width=2
        )

    def on_drag(e):
        if rect:
            canvas.coords(rect, start["x"], start["y"], e.x, e.y)

    def on_release(e):
        result["coords"] = (
            min(start["x"], e.x),
            min(start["y"], e.y),
            max(start["x"], e.x),
            max(start["y"], e.y),
        )
        overlay.destroy()

    def on_esc(_e):
        result["coords"] = None
        overlay.destroy()

    canvas.bind("<ButtonPress-1>", on_press)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)
    overlay.bind("<Escape>", on_esc)

    overlay.focus_force()
    overlay.grab_set()
    overlay.wait_window()

    return result["coords"]


# =============================
# QR スキャン
# =============================
def scan_qr():
    global scanning
    if scanning:
        return
    scanning = True

    try:
        coords = select_screen()
        if not coords:
            return

        x1, y1, x2, y2 = coords
        w, h = x2 - x1, y2 - y1
        if w < 10 or h < 10:
            return

        with mss.mss() as sct:
            img = np.array(sct.grab({
                "left": x1,
                "top": y1,
                "width": w,
                "height": h
            }))

        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        from pyzbar.pyzbar import decode
        codes = decode(img)
        if not codes:
            messagebox.showinfo("QRPicker", "QRコードが見つかりません")
            return

        raw = codes[0].data
        text = None
        for enc in ("utf-8", "shift_jis"):
            try:
                text = raw.decode(enc)
                break
            except Exception:
                pass
        if text is None:
            text = raw.decode("utf-8", errors="ignore")

        pyperclip.copy(text)

        # 履歴
        max_hist = int(cfg("history", "max_items", "10"))

        history.insert(0, text)
        history[:] = history[:max_hist]

        if text.lower().startswith(("http://", "https://")):
            if messagebox.askyesno("URL検出", "URLを開きますか？"):
                webbrowser.open(text)
            else:
                notify("QRPicker", "URLをコピーしました")
        else:
            notify("QRPicker", "テキストをコピーしました")

    finally:
        scanning = False
        root.after(100, root.focus_force)


# =============================
# グローバルホットキー
# =============================
def hotkey_loop():
    user32 = ctypes.windll.user32

    MOD_CTRL = 0x0002 if cfg("hotkey", "ctrl", "true") == "true" else 0
    MOD_SHIFT = 0x0004 if cfg("hotkey", "shift", "true") == "true" else 0
    MOD_ALT = 0x0001 if cfg("hotkey", "alt", "false") == "true" else 0
    vk = ord(cfg("hotkey", "key", "Q").upper())

    if not user32.RegisterHotKey(None, 1, MOD_CTRL | MOD_SHIFT | MOD_ALT, vk):
        notify("QRPicker", "ホットキー登録失敗")
        return

    msg = ctypes.wintypes.MSG()
    try:
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
            if msg.message == 0x0312:
                root.after(0, scan_qr)
    finally:
        user32.UnregisterHotKey(None, 1)


# =============================
# トレイ
# =============================
def tray_scan(_icon, _item):
    root.after(0, scan_qr)


def tray_history(_icon, _item):
    if not history:
        notify("QRPicker", "履歴なし")
        return
    messagebox.showinfo("QRPicker 履歴", "\n\n".join(history))


def tray_exit(icon, _item):
    icon.stop()
    root.after(0, root.quit)


def tray_thread():
    image = Image.open(resource_path("icon.png"))
    menu = pystray.Menu(
        pystray.MenuItem("スキャン", tray_scan),
        pystray.MenuItem("履歴", tray_history),
        pystray.MenuItem("終了", tray_exit)
    )
    icon = pystray.Icon("QRPicker", image, "QRPicker", menu)
    icon.run()


# =============================
# 起動
# =============================
print("QRPicker Ready")

threading.Thread(target=tray_thread, daemon=True).start()
threading.Thread(target=hotkey_loop, daemon=True).start()

root.after(800, show_startup_notify)
root.mainloop()
