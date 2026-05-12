![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Ready-green.svg)
![vgmstream](https://img.shields.io/badge/vgmstream-Integrated-purple.svg)
![Platform](https://img.shields.io/badge/OS-Windows-lightgrey.svg)

## 📖 專案簡介 (Introduction)
本專案為針對光榮特庫摩 (KOEI TECMO) 旗下遊戲（如《信長之野望 Online》）專屬之 `.kvs` 加密音軌格式所開發的**桌面端自動化解密與轉碼工具**。

有別於一般的單純轉檔腳本，本系統整合了底層的 **UAC 提權機制**、**多執行緒 GUI 異步處理**，以及 **vgmstream + FFmpeg 雙引擎管線 (Pipeline)**，能無痛突破系統目錄的讀寫限制，將受保護的遊戲音軌提取並批量轉碼為標準 192kbps MP3 格式。

## ✨ 核心工程亮點 (Key Features)

* **🛡️ 自動 UAC 提權 (Auto-Escalation)**
  利用 `ctypes.windll.shell32` 動態偵測執行權限。若來源目錄位於系統保護區（如 `C:\Program Files (x86)`），系統將自動呼叫 Windows 管理員權限，避免存取被拒 (Permission Denied)。
* **⚙️ 雙引擎自動化管線 (Dual-Engine Pipeline)**
  透過 `subprocess` 無縫串接解密與編碼流程：先由 `vgmstream` 將專利 KVS 格式解壓為 WAV，再自動導流至 `FFmpeg` 壓縮成 MP3，並具備暫存檔生命週期管理（自動銷毀）。
* **🧵 非同步 GUI 與進度防呆 (Asynchronous UX)**
  基於 `tkinter` 與 `threading` 模組構建。耗時的轉碼任務獨立於背景執行緒，確保主視窗 (Main Thread) 渲染順暢不卡頓，並提供實時進度反饋與按鈕防呆鎖定。
* **📦 依賴隔離與綠色封裝 (Portable Environment)**
  具備進階的路徑嗅探邏輯 (`sys._MEIPASS`)，完美支援 PyInstaller 封裝。能將所有必要的外部執行檔 (`.exe`) 與 C++ 動態連結庫 (`.dll`) 靜默打包進單一執行檔中，實現「點擊即用」的免安裝體驗。
* **📝 強制錯誤捕獲 (Error Handling & Logging)**
  捨棄傳統的靜默失敗，當底層引擎回報 `stderr` 時，系統會自動收集崩潰原因，並於使用者桌面生成 `KVS_Error_Log.txt`，大幅降低除錯成本。

---

## 🚀 系統需求與使用方式 (Usage)

### 方案 A：直接執行可攜式版本 (推薦)
1. 於 Releases 頁面下載打包好的 `KVS_Decryptor.exe`。
2. 點擊執行（若提示需管理員權限請按「是」）。
3. 選擇 `.kvs` 檔案來源目錄與輸出目錄，點擊開始即可。

### 方案 B：由原始碼執行 (開發者模式)
1. 確認已安裝 Python 3.x。
2. 下載 [FFmpeg](https://ffmpeg.org/download.html) 與 [vgmstream-cli](https://github.com/vgmstream/vgmstream/releases) Windows 版本。
3. 將 `ffmpeg.exe`、`vgmstream-cli.exe` 以及 vgmstream 附帶的 **所有 `.dll` 檔案** 放置於本腳本同層目錄。
4. 執行腳本：
   ```powershell
   python kvs.py
