# KVS to MP3｜Windows 音訊批次轉檔 GUI

> 以 Python Tkinter 建立的桌面工具，串接 `vgmstream-cli` 與 FFmpeg，將本機支援的 `.kvs` 音訊轉成 192 kbps MP3。

[GitHub 面試作品導覽](https://github.com/garyai8146-jpg/Yihop_LineBOT/blob/main/PORTFOLIO.md)

## 主要功能

- 批次掃描指定資料夾內的 `.kvs` 檔案。
- 使用 vgmstream 解碼為暫存 WAV，交由 FFmpeg 編碼為 MP3。
- 在背景執行緒處理轉檔工作，介面提供進度與錯誤提示。
- 以 `sys._MEIPASS` 兼容 PyInstaller 打包的檔案路徑。
- 將部分失敗資訊輸出到桌面 `KVS_Error_Log.txt` 便於排查。

**權限取捨：** 目前原始碼在啟動時會嘗試透過 Windows UAC 以管理員身分重新執行，並非只在確有必要時要求提權。正式發行前應優先採最小權限原則，必要時才請求提升權限。

## 技術棧

Python · Tkinter · threading · subprocess · Windows UAC · vgmstream · FFmpeg

## 使用方式

### 已打包版本

前往 [Releases](https://github.com/garyai8146-jpg/kvs-to-mp3/releases)，下載 `KVS_Decryptor.7z`，解壓縮後再依封裝內容啟動。Release 提供的是 **7z 壓縮包**，不是直接下載單獨的 EXE。

### 從原始碼啟動

1. 安裝 Python 3（Windows）。
2. 下載 [FFmpeg](https://ffmpeg.org/download.html) 和 [vgmstream](https://github.com/vgmstream/vgmstream/releases) 的 Windows 命令列程式。
3. 將 `ffmpeg.exe`、`vgmstream-cli.exe` 與其所需 DLL 放在 `kvs.py` 相同資料夾，或依程式搜尋邏輯配置路徑。
4. 執行：

```powershell
python kvs.py
```

## 已知限制

- 解碼是否成功取決於 vgmstream 對實際 KVS 變體的支援，**不保證可處理所有版本或加密格式**。
- 需要 Windows，且目前提權方式、子程序錯誤處理與 GUI 執行緒互動尚需更完整的測試。
- 本儲存庫不提供受版權保護的遊戲音訊。請只處理有權使用的檔案。

## 面試展示

推薦說明 `GUI → 背景工作 → 外部解碼器 → 暫存 WAV → MP3` 的管線設計、子程序錯誤回報、Windows 檔案權限與最小權限原則。
