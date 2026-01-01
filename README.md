# QRPicker

🖱 画面範囲を選択して QRコード / バーコードを即読み取り  
📋 結果を自動コピー・URL は即オープン可能  
🔔 通知・⌨ ホットキー・📋 履歴を自由に設定可能な Windows 常駐ツール

---

## ✨ 特徴

- ✅ 画面範囲をドラッグ選択して QR / Barcode を読み取り
- ✅ Ctrl + Shift + Q（変更可）で即起動
- ✅ タスクトレイ常駐
- ✅ URL 自動判定（開く / コピー）
- ✅ コピー履歴保存（config.ini で件数指定）
- ✅ Windows 通知 ON / OFF 切替
- ✅ DPI スケーリング対応（高解像度でもズレなし）
- ✅ 二重起動防止
- ✅ exe 単体配布可能（Python 不要）

---

## 🖥 動作環境

- Windows 10 / 11（64bit）
- Python 3.10 / 3.11（開発時）
- exe 版は Python 不要

---

## 🚀 使い方（exe 版）

1. `QRPicker.exe` と `config.ini` を同じフォルダに置く
2. `QRPicker.exe` を起動
3. タスクトレイに常駐
4. **Ctrl + Shift + Q** でスキャン開始
5. 範囲をドラッグ → 自動コピー

---

## ⚙ 設定（config.ini）

- ホットキー変更
- 通知 ON / OFF
- 履歴保存件数
- ダーク / ライトテーマ

👉 詳細は `config.ini` 内コメント参照

---

## 🔨 ビルド方法（開発者向け）

```bat
build.bat
