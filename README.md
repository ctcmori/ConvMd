# ConvMd - Office文書変換システム

Excel、Word、PowerPointファイルをPDF経由でMarkdownに変換するOffice文書コンバーター。COM方式による高品質PDF変換とAzure OpenAI統合によるMarkdown生成を実現。

## 🚀 主な機能

- **多形式対応**: Excel (.xlsx/.xls)、Word (.docx/.doc)、PowerPoint (.pptx/.ppt)
- **高品質変換**: Windows COM API による印刷品質PDF生成
- **図形保持**: 元文書の図形、グラフ、画像を完全保持
- **自動最適化**: 用紙向き、余白を自動最適化
- **AI変換**: Azure OpenAI による高品質Markdown変換
- **フォルダ監視**: リアルタイム監視による自動処理

## 📋 システム要件

- Python 3.9以上
- Windows環境（Microsoft Office COM API使用）
- Azure OpenAI APIアクセス権

## 🔧 インストール

```bash
# リポジトリをクローン
git clone https://github.com/ctcmori/ConvMd.git
cd ConvMd

# 仮想環境作成・アクティベート
python -m venv venv
venv\Scripts\activate  # Windows

# 依存パッケージインストール
pip install -r requirements.txt
```

## ⚙️ 設定

`config/config.yaml`を作成：

```yaml
folders:
  input: "C:\\Temp\\ConvMD\\INPUT"
  output: "C:\\Temp\\ConvMD\\OUTPUT"
  intermediate: "C:\\Temp\\ConvMD\\TEMP_PDF"

azure_openai:
  endpoint: "https://your-resource.openai.azure.com/"
  api_key: "your-api-key"
  deployment_name: "your-deployment"
  api_version: "2024-02-15-preview"

logging:
  level: "INFO"
```

## 🏃‍♂️ 使用方法

```bash
# フォルダ監視モード（推奨）
python src/main.py --watch

# 単一実行モード
python src/main.py --single

# 特定ファイル処理
python src/main.py --single --input path/to/document.xlsx
```

## 📊 変換品質

### Excel変換の例
- **入力**: 172行×57列の複雑なスプレッドシート（図形36個）
- **出力**: 186KB、5ページのPDF（横向き自動設定）
- **品質**: 図形・レイアウト完全保持、テキスト検索可能

### 技術仕様
- **図形保持**: ページあたり30-51個の図形/パス
- **フォント**: MS-Gothic、MS-Mincho、MS-PGothic対応
- **画像**: ページあたり2個の画像オブジェクト
- **サイズ**: 最適な横向きレイアウト（841.9 x 595.3）

## 🏗️ アーキテクチャ

```
src/
├── office_converter/
│   ├── converters/         # PDF変換エンジン
│   │   └── pdf_converter.py
│   ├── services/           # コアサービス
│   │   ├── azure_openai_client.py
│   │   └── logger_service.py
│   ├── config/             # 設定管理
│   └── utils/              # ユーティリティ
└── main.py                 # メインエントリポイント
```

## 🔍 変換プロセス

1. **ファイル検出**: 対応形式の自動判別
2. **COM変換**: Windows Office API による高品質PDF生成
3. **品質最適化**: 用紙向き・余白の自動調整
4. **テキスト抽出**: PDF からのテキスト抽出
5. **AI変換**: Azure OpenAI による Markdown 生成
6. **出力**: 構造化 Markdown ファイル

## 🛠️ 開発・デバッグ

```bash
# PDF品質確認
python analyze_pdf_details.py path/to/output.pdf

# テスト実行
pytest tests/ -v

# ログレベル設定
# config.yaml で level: "DEBUG" に変更
```

## 📝 ライセンス

MIT License

## 🤝 貢献

プルリクエストやイシューの報告を歓迎します。