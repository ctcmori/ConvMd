# Office-to-Markdown Converter - Production Ready

## 概要

本システムは、Office文書（Excel、Word、PowerPoint）をMarkdown形式に変換し、Dify RAGナレッジベースに自動登録するAIパワードコンバーターです。Azure OpenAIのGPTモデルを活用して高品質な変換を実現します。

## 主要機能

- **多形式サポート**: Excel (.xlsx)、Word (.docx)、PowerPoint (.pptx)
- **AI変換**: Azure OpenAI GPTによる高品質なMarkdown変換
- **Dify連携**: RAGナレッジベースへの自動登録
- **文字エンコーディング**: 日本語対応（UTF-8-BOM）
- **監視モード**: ファイル変更の自動検知・処理
- **構造化ログ**: JSON形式での詳細ログ出力
- **本番環境対応**: セキュリティ強化された環境変数設定

## クイックスタート

### 1. 環境変数設定

本番環境では、セキュリティのため以下の環境変数を設定してください：

```bash
# Azure OpenAI設定
AZURE_OPENAI_ENDPOINT=https://your-resource-name.cognitiveservices.azure.com
AZURE_OPENAI_API_KEY=your-azure-openai-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name

# Dify設定
DIFY_BASE_URL=http://your-dify-server/v1/
DIFY_API_KEY=your-dify-api-key
DIFY_DATASET_ID=your-dataset-id
```

### 2. 依存関係インストール

```bash
pip install -r requirements.txt
```

### 3. 実行

#### 一回実行モード
```bash
# バッチファイル使用（推奨）
run_production.bat

# または直接実行
python src\main.py --config config\config.production.yaml --single
```

#### 監視モード
```bash
# バッチファイル使用（推奨）
run_production_watch.bat

# または直接実行
python src\main.py --config config\config.production.yaml --watch
```

## プロジェクト構造

```
ConvMd/
├── src/
│   ├── main.py                 # メインエントリポイント
│   └── office_converter/       # コアライブラリ
│       ├── converters/         # 変換エンジン
│       ├── llm/               # Azure OpenAI連携
│       ├── services/          # 各種サービス
│       └── config/            # 設定管理
├── config/
│   ├── config.yaml            # 開発用設定
│   └── config.production.yaml # 本番用設定（要環境変数）
├── input_documents/           # 変換対象ファイル格納
├── logs/                     # ログファイル出力先
├── PRODUCTION_SETUP.md       # 本番セットアップガイド
├── run_production.bat        # 本番実行スクリプト
└── run_production_watch.bat  # 本番監視スクリプト
```

## システム要件

- Python 3.8+
- Windows 10/11 (WSL2サポート)
- Azure OpenAI リソース
- Dify サーバー

## セキュリティ

- ✅ API キーは環境変数で管理
- ✅ 本番設定ファイルにはプレースホルダーのみ
- ✅ GitHub Secret Scanning対応
- ✅ ログファイルにAPIキーは出力しない

## トラブルシューティング

### 環境変数が設定されていない場合
```
[ERROR] AZURE_OPENAI_ENDPOINT 環境変数が設定されていません
```
→ PRODUCTION_SETUP.md を参照して環境変数を設定してください

### 文字化け問題
- UTF-8-BOM エンコーディングを使用
- 日本語文字は自動的に適切にエンコードされます

### Dify登録エラー
- DIFY_BASE_URL の末尾に "/v1/" が必要
- DIFY_DATASET_ID が正しく設定されているか確認

## ログ

- ログファイル: `logs/converter_YYYYMMDDHHMMSS.log`
- 形式: JSON構造化ログ
- レベル: INFO, WARNING, ERROR

## 開発者向け

### 開発環境セットアップ
```bash
# 開発用設定で実行
python src\main.py --config config\config.yaml --single
```

### テスト実行
```bash
pytest tests/
```

## ライセンス

[ライセンス情報を追加]

## サポート

問題や質問がある場合は、GitHubのIssuesまでお願いします。