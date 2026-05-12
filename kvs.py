import os
import sys
import ctypes
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

def 判斷是否為管理員():
    """ 檢查當前是否以管理員權限執行 """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def 獲取資源路徑(檔名):
    測試路徑 = []
    if hasattr(sys, '_MEIPASS'):
        測試路徑.append(os.path.join(sys._MEIPASS, 檔名))
    腳本目錄 = os.path.dirname(os.path.abspath(__file__))
    測試路徑.append(os.path.join(腳本目錄, 檔名))
    測試路徑.append(os.path.join(os.getcwd(), 檔名))
    for 路徑 in 測試路徑:
        if os.path.exists(路徑): return 路徑
    return os.path.join(腳本目錄, 檔名)

class KVS解密轉碼器GUI:
    def __init__(self, 視窗主體):
        self.主體 = 視窗主體
        self.主體.title("KVS轉MP3工具")
        self.主體.geometry("600x380")
        
        self.ffmpeg_path = 獲取資源路徑("ffmpeg.exe")
        self.vgmstream_path = 獲取資源路徑("vgmstream-cli.exe")
        
        self.來源路徑 = tk.StringVar()
        self.輸出路徑 = tk.StringVar()
        self.構建介面()

    def 構建介面(self):
        tk.Label(self.主體, text="KVS 來源目錄:", font=("Microsoft JhengHei", 10)).pack(pady=(15, 0))
        f1 = tk.Frame(self.主體); f1.pack(fill='x', padx=30)
        tk.Entry(f1, textvariable=self.來源路徑).pack(side='left', expand=True, fill='x')
        tk.Button(f1, text="瀏覽", command=lambda: self.來源路徑.set(filedialog.askdirectory())).pack(side='right', padx=5)

        tk.Label(self.主體, text="MP3 輸出目錄:", font=("Microsoft JhengHei", 10)).pack(pady=(10, 0))
        f2 = tk.Frame(self.主體); f2.pack(fill='x', padx=30)
        tk.Entry(f2, textvariable=self.輸出路徑).pack(side='left', expand=True, fill='x')
        tk.Button(f2, text="瀏覽", command=lambda: self.輸出路徑.set(filedialog.askdirectory())).pack(side='right', padx=5)

        self.進度標籤 = tk.Label(self.主體, text="狀態：等待任務中", font=("Microsoft JhengHei", 9), fg="green")
        self.進度標籤.pack(pady=(20, 0))
        
        self.進度條 = ttk.Progressbar(self.主體, orient="horizontal", length=450, mode="determinate")
        self.進度條.pack(pady=5)

        self.按鈕_執行 = tk.Button(self.主體, text="啟動轉碼", command=self.啟動任務, 
                                 bg="#d32f2f", fg="white", font=("Microsoft JhengHei", 10, "bold"), width=25)
        self.按鈕_執行.pack(pady=20)

    def 啟動任務(self):
        if not os.path.exists(self.ffmpeg_path) or not os.path.exists(self.vgmstream_path):
            messagebox.showerror("錯誤", "引擎缺失，請確認 ffmpeg.exe 與 vgmstream-cli.exe 存在。")
            return
        if not self.來源路徑.get() or not self.輸出路徑.get():
            messagebox.showwarning("提示", "請設定完整目錄路徑")
            return
        threading.Thread(target=self.核心任務, daemon=True).start()

    def 核心任務(self):
        in_dir, out_dir = self.來源路徑.get(), self.輸出路徑.get()
        try:
            files = [f for f in os.listdir(in_dir) if f.lower().endswith('.kvs')]
        except Exception as e:
            messagebox.showerror("權限或路徑錯誤", f"無法讀取目錄:\n{str(e)}")
            return

        if not files:
            messagebox.showinfo("提示", "目錄內沒有 .kvs 檔案")
            return

        self.按鈕_執行.config(state="disabled")
        self.進度條["maximum"] = len(files)
        成功數 = 0
        錯誤日誌 = []

        for i, f in enumerate(files):
            self.進度標籤.config(text=f"解密與轉碼中 ({i+1}/{len(files)}): {f}")
            
            in_file = os.path.join(in_dir, f)
            out_file = os.path.join(out_dir, f"{os.path.splitext(f)[0]}.mp3")
            temp_wav = os.path.join(out_dir, f"temp_decode_{i}.wav")
            
            try:
                # 階段一：vgmstream
                cmd_decode = [self.vgmstream_path, '-o', temp_wav, in_file]
                res_decode = subprocess.run(cmd_decode, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                if res_decode.returncode == 0 and os.path.exists(temp_wav):
                    # 階段二：FFmpeg
                    cmd_encode = [self.ffmpeg_path, '-i', temp_wav, '-acodec', 'libmp3lame', '-ab', '192k', out_file, '-y']
                    res_encode = subprocess.run(cmd_encode, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    
                    if res_encode.returncode == 0:
                        成功數 += 1
                    else:
                        錯誤日誌.append(f"FFmpeg 錯誤 ({f}): {res_encode.stderr}")
                    os.remove(temp_wav)
                else:
                    錯誤日誌.append(f"Vgmstream 錯誤 ({f}): {res_decode.stderr}")
                    
            except Exception as e:
                錯誤日誌.append(f"執行階段崩潰 ({f}): {str(e)}")

            self.進度條["value"] = i + 1
            self.主體.update_idletasks()

        # 寫入錯誤日誌至桌面
        if 錯誤日誌:
            桌面路徑 = os.path.join(os.path.expanduser("~"), "Desktop", "KVS_Error_Log.txt")
            try:
                with open(桌面路徑, "w", encoding="utf-8") as f:
                    f.write("\n".join(錯誤日誌))
                備註 = f"\n但有錯誤發生，已於桌面生成 KVS_Error_Log.txt"
            except Exception as e:
                備註 = f"\n(日誌寫入失敗: {e})"
        else:
            備註 = ""

        self.按鈕_執行.config(state="normal")
        self.進度標籤.config(text="任務結束")
        messagebox.showinfo("任務完成", f"成功提取：{成功數} / {len(files)}{備註}")

if __name__ == "__main__":
    if not 判斷是否為管理員():
        # 自動呼叫 UAC 提權並重新執行本腳本
        腳本絕對路徑 = os.path.abspath(sys.argv[0])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{腳本絕對路徑}"', None, 1)
        sys.exit()
    else:
        root = tk.Tk()
        app = KVS解密轉碼器GUI(root)
        root.mainloop()