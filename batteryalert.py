# Note:
# 👉 Convert your batteryalert.py → .exe file
# 👉 Send that .exe to your friend
# 👉 It runs like a normal app (no Python needed)

# pip install pyinstaller
# pyinstaller --onefile --noconsole batteryalert.py

import psutil
import time
import os
import sys
import winshell
from win32com.client import Dispatch
from winotify import Notification, audio
import win32con
import win32gui
import win32api
import threading
import shutil
# ---------------- SETTINGS ----------------
LOW_BATTERY = 20
FULL_BATTERY = 100
CHECK_INTERVAL = 20  # seconds
# ------------------------------------------


def show_notification(title, message, sound=audio.Default):
    """Helper function to show Windows toast notification with max duration"""
    toast = Notification(
        app_id="Battery Alert",
        title=title,
        msg=message,
        duration="long"  # <-- stays ~25 seconds
    )
    toast.set_audio(sound, loop=False)
    toast.show()


def check_charger_on_shutdown():
    """Check if charger is connected during shutdown"""
    battery = psutil.sensors_battery()
    if battery and battery.power_plugged:
        show_notification("⚡ Charger Connected",
                          "Suggestion: Please remove the charger before shutting down.",
                          audio.Reminder)


def add_shortcut_to_startup():
    """
    Copy EXE to AppData and create startup shortcut.
    Removes duplicate EXEs/shortcuts automatically.
    """

    # ---------------- APPDATA LOCATION ----------------
    appdata_dir = os.path.join(
        os.getenv("LOCALAPPDATA"),
        "BatteryAlert"
    )

    os.makedirs(appdata_dir, exist_ok=True)

    # ---------------- SOURCE EXE ----------------
    current_exe = sys.executable

    # ---------------- DESTINATION EXE ----------------
    target_exe = os.path.join(
        appdata_dir,
        "batteryalert.exe"
    )

    # ---------------- DELETE OLD DUPLICATES ----------------
    try:
        if os.path.exists(target_exe):

            # If old exe exists and is different
            if os.path.abspath(current_exe) != os.path.abspath(target_exe):
                os.remove(target_exe)

    except Exception as e:
        print("Could not remove old exe:", e)

    # ---------------- COPY EXE ----------------
    try:
        if os.path.abspath(current_exe) != os.path.abspath(target_exe):
            shutil.copy2(current_exe, target_exe)
            print("✅ EXE copied to AppData")

    except Exception as e:
        print("Copy failed:", e)
        return

    # ---------------- STARTUP FOLDER ----------------
    startup = winshell.startup()

    shortcut_path = os.path.join(
        startup,
        "BatteryAlert.lnk"
    )

    # ---------------- REMOVE OLD SHORTCUT ----------------
    try:
        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)

    except Exception as e:
        print("Could not remove old shortcut:", e)

    # ---------------- CREATE NEW SHORTCUT ----------------
    try:
        shell = Dispatch("WScript.Shell")

        shortcut = shell.CreateShortCut(shortcut_path)

        shortcut.Targetpath = target_exe

        shortcut.WorkingDirectory = appdata_dir

        shortcut.IconLocation = target_exe

        shortcut.save()

        print("✅ Startup shortcut created")

    except Exception as e:
        print("Shortcut creation failed:", e)


def ensure_autostart():
    """Ensure autostart shortcut is present"""
    try:
        add_shortcut_to_startup()
    except Exception as e:
        print("⚠️ Could not add to startup:", e)


# ---------------- WINDOWS SHUTDOWN HOOK ----------------
class WindowsShutdownHandler:
    def __init__(self):
        message_map = {
            win32con.WM_QUERYENDSESSION: self.on_shutdown,
            win32con.WM_ENDSESSION: self.on_shutdown,
        }
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = message_map
        wc.lpszClassName = "BatteryReminderClass"
        hinst = wc.hInstance = win32api.GetModuleHandle(None)
        self.classAtom = win32gui.RegisterClass(wc)
        self.hwnd = win32gui.CreateWindow(
            self.classAtom,
            "Battery Reminder Window",
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            hinst,
            None
        )
        win32gui.PumpMessages()

    def on_shutdown(self, hwnd, msg, wparam, lparam):
        check_charger_on_shutdown()
        return True  # allow shutdown to continue
# --------------------------------------------------------


def main():
    time.sleep(5)
    ensure_autostart()

    # Initial "running" notification
    show_notification("BatteryAlert Running...",
                      "I will keep an eye on your battery and notify you! 😊")

    # Run shutdown handler in a separate thread
    threading.Thread(target=WindowsShutdownHandler, daemon=True).start()

    while True:
        battery = psutil.sensors_battery()
        percent = battery.percent
        charging = battery.power_plugged

        if percent <= LOW_BATTERY and not charging:
            show_notification("🔋 Low Battery",
                              f"Battery is at {percent}%. Please plug in your charger!")

        elif percent >= FULL_BATTERY and charging:
            show_notification("⚡ Battery Full",
                              f"Battery is at {percent}%. Please unplug your charger!")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
