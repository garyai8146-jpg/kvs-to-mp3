"""Windows KVS to MP3 batch converter.

The Tkinter event loop is always owned by the main thread. A worker handles
external encoders and delivers progress via a thread-safe queue.
"""

from __future__ import annotations

import os
import queue
import subprocess
import sys
import tempfile
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


def 獲取資源路徑(檔名: str) -> str:
    路徑候選 = []
    if hasattr(sys, "_MEIPASS"):
        路徑候選.append(os.path.join(sys._MEIPASS, 檔名))
    腳本目錄 = os.path.dirname(os.path.abspath(__file__))
    路徑候選.extend((os.path.join(腳本目錄, 檔名), os.path.join(os.getcwd(), 檔名)))
    return next((p for p in 路徑候選 if os.path.isfile(p)), 路徑候選[-2])


class KVS解密轉碼器GUI:
    def __init__(self, 視窗主體: tk.Tk) -> None:
        self.主體 = 視窗主體
        self.主體.title("KVS 轉 MP3 工具")
        self.主體.geometry("600x380")
        self.ffmpeg_path = 獲取資源路徑("ffmpeg.exe")
        self.vgmstream_path = 獲取資源路徑("vgmstream-cli.exe")
        self.來源路徑 = tk.StringVar()
        self.輸出路徑 = tk.StringVar()
        self._busy = False
        self._events: queue.Queue[tuple[str, tuple]] = queue.Queue()
        self.構建介面()
        self.主體.after(80, self._處理事件)

    def 構建介面(self) -> None:
        tk.Label(self.主體, text="KVS 來源目錄:", font=("Microsoft JhengHei", 10)).pack(pady=(15, 0))
        f1 = tk.Frame(self.主體)
        f1.pack(fill="x", padx=30)
        tk.Entry(f1, textvariable=self.來源路徑).pack(side="left", expand=True, fill="x")
        tk.Button(f1, text="瀏覽", command=lambda: self.來源路徑.set(filedialog.askdirectory())).pack(side="right", padx=5)

        tk.Label(self.主體, text="MP3 輸出目錄:", font=("Microsoft JhengHei", 10)).pack(pady=(10, 0))
        f2 = tk.Frame(self.主體)
        f2.pack(fill="x", padx=30)
        tk.Entry(f2, textvariable=self.輸出路徑).pack(side="left", expand=True, fill="x")
        tk.Button(f2, text="瀏覽", command=lambda: self.輸出路徑.set(filedialog.askdirectory())).pack(side="right", padx=5)

        self.進度標籤 = tk.Label(self.主體, text="狀態：等待任務中", font=("Microsoft JhengHei", 9), fg="green")
        self.進度標籤.pack(pady=(20, 0))
        self.進度條 = ttk.Progressbar(self.主體, orient="horizontal", length=450, mode="determinate")
        self.進度條.pack(pady=5)
        self.按鈕_執行 = tk.Button(
            self.主體,
            text="啟動轉碼",
            command=self.啟動任務,
            bg="#d32f2f",
            fg="white",
            font=("Microsoft JhengHei", 10, "bold"),
            width=25,
        )
        self.按鈕_執行.pack(pady=20)

    def 啟動任務(self) -> None:
        if self._busy:
            return
        if not all(os.path.isfile(x) for x in (self.ffmpeg_path, self.vgmstream_path)):
            messagebox.showerror("缺少轉檔引擎", "請確認 ffmpeg.exe 與 vgmstream-cli.exe 位於程式旁。")
            return
        in_dir = self.來源路徑.get()
        out_dir = self.輸出路徑.get()
        if not os.path.isdir(in_dir) or not os.path.isdir(out_dir):
            messagebox.showwarning("路徑錯誤", "請選擇可讀取的來源資料夾及可寫入的輸出資料夾。")
            return
        try:
            files = sorted(f for f in os.listdir(in_dir) if f.lower().endswith(".kvs") and os.path.isfile(os.path.join(in_dir, f)))
        except OSError as exc:
            messagebox.showerror("無法讀取目錄", str(exc))
            return
        if not files:
            messagebox.showinfo("沒有檔案", "來源資料夾沒有 .kvs 檔案。")
            return

        self._busy = True
        self.按鈕_執行.config(state="disabled")
        self.進度條["maximum"] = len(files)
        self.進度條["value"] = 0
        self.進度標籤.config(text=f"準備處理 {len(files)} 個檔案")
        threading.Thread(target=self._核心任務, args=(in_dir, out_dir, files), daemon=True).start()

    def _核心任務(self, in_dir: str, out_dir: str, files: list[str]) -> None:
        成功數 = 0
        錯誤日誌: list[str] = []
        hide_console = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        for i, f in enumerate(files, start=1):
            source = os.path.join(in_dir, f)
            dest = os.path.join(out_dir, os.path.splitext(f)[0] + ".mp3")
            temp_wav = None
            self._events.put(("status", (i, len(files), f)))
            try:
                with tempfile.NamedTemporaryFile(prefix="kvs_decode_", suffix=".wav", dir=out_dir, delete=False) as tmp:
                    temp_wav = tmp.name
                decoded = subprocess.run(
                    [self.vgmstream_path, "-o", temp_wav, source],
                    capture_output=True, text=True, errors="replace",
                    creationflags=hide_console, timeout=600,
                )
                if decoded.returncode != 0 or not os.path.isfile(temp_wav) or os.path.getsize(temp_wav) == 0:
                    raise RuntimeError("vgmstream 解碼失敗: " + decoded.stderr[-1200:])
                encoded = subprocess.run(
                    [self.ffmpeg_path, "-y", "-i", temp_wav, "-codec:a", "libmp3lame", "-b:a", "192k", dest],
                    capture_output=True, text=True, errors="replace",
                    creationflags=hide_console, timeout=600,
                )
                if encoded.returncode != 0:
                    raise RuntimeError("FFmpeg 編碼失敗: " + encoded.stderr[-1200:])
                成功數 += 1
            except Exception as exc:
                錯誤日誌.append(f"{f}: {exc}")
            finally:
                if temp_wav and os.path.exists(temp_wav):
                    try:
                        os.remove(temp_wav)
                    except OSError as exc:
                        錯誤日誌.append(f"{f}: 無法清除暫存檔: {exc}")
                self._events.put(("progress", (i, len(files))))

        self._events.put(("done", (成功數, len(files), 錯誤日誌)))

    def _處理事件(self) -> None:
        try:
            while True:
                event, payload = self._events.get_nowait()
                if event == "status":
                    index, total, filename = payload
                    self.進度標籤.config(text=f"轉檔中 ({index}/{total}): {filename}")
                elif event == "progress":
                    self.進度條["value"] = payload[0]
                elif event == "done":
                    success, total, errors = payload
                    self._busy = False
                    self.按鈕_執行.config(state="normal")
                    self.進度標籤.config(text=f"完成：成功 {success} / {total}")
                    info = ""
                    if errors:
                        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
                        log_path = os.path.join(desktop if os.path.isdir(desktop) else os.getcwd(), "KVS_Error_Log.txt")
                        try:
                            with open(log_path, "w", encoding="utf-8") as handle:
                                handle.write("\n".join(errors))
                            info = f"\n失敗記錄已存至：{log_path}"
                        except OSError as exc:
                            info = f"\n無法儲存錯誤紀錄：{exc}"
                    messagebox.showinfo("任務完成", f"成功轉檔：{success} / {total}{info}")
        except queue.Empty:
            pass
        if self.主體.winfo_exists():
            self.主體.after(80, self._處理事件)


if __name__ == "__main__":
    # No blanket UAC elevation: ordinary user permissions are safer.
    root = tk.Tk()
    app = KVS解密轉碼器GUI(root)
    root.mainloop()
