# KVS to MP3｜把重複的音訊轉檔工作變成一個工具

我遇到的問題很簡單：有些遊戲音效是特殊的 `.kvs` 格式，不能直接拿一般播放器或轉檔軟體批次處理。與其每次手動操作多個命令列工具，我做了一個 Windows 小程式，把選資料夾、解碼、轉 MP3 和錯誤整理放在同一個畫面。

**[看看其他作品](https://github.com/garyai8146-jpg/Yihop_LineBOT/blob/main/PORTFOLIO.md)**

## 怎麼運作

1. 選擇含有 `.kvs` 檔案的資料夾與 MP3 輸出資料夾。
2. 背景工作依序呼叫 `vgmstream-cli`，把支援的音訊解碼成暫存 WAV。
3. 再交由 FFmpeg 轉成 192 kbps MP3。
4. 完成後清除暫存 WAV，顯示成功數量；有錯誤時輸出記錄。

介面使用 Tkinter；轉檔放在工作執行緒，進度則透過 Queue 交回主執行緒更新，避免背景執行緒直接操作視窗。新版也**不再強制要求管理員權限**。

## 執行方式

**打包版本：** 到 [Releases](https://github.com/garyai8146-jpg/kvs-to-mp3/releases) 下載 `KVS_Decryptor.7z`，解壓縮後使用。既有 Release 是舊版封裝，未必包含這次原始碼的安全與執行緒修正，請以最新原始碼為準。

**原始碼：** Windows 安裝 Python 3、[FFmpeg](https://ffmpeg.org/download.html)、[vgmstream](https://github.com/vgmstream/vgmstream/releases)，把 `ffmpeg.exe`、`vgmstream-cli.exe` 與必要 DLL 放在程式同層，再執行：

```powershell
python kvs.py
```

## 這個專案學到什麼

小工具不只是把兩條指令串起來：工作很久時 GUI 不能卡住、失敗的檔案要能追查、暫存檔要清乾淨，也不應該因為方便就讓整個程式長期用管理員權限執行。

## 注意事項

解碼成功取決於 vgmstream 支援的 KVS 變體，不保證每種遊戲音訊都能處理。GitHub Actions 會做 Python 語法與基本安全檢查；實際 Windows GUI、外部解碼器及不同檔案格式仍需要在 Windows 上驗收。請只處理有使用權的音訊。
