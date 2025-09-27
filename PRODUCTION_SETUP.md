# Office-to-Markdown Converter 本番環境設定ガイド

## 環境変数設定

本番環境では、セキュリティのため以下の環境変数を設定してください：

### Azure OpenAI 設定
```bash
# Azure OpenAI エンドポイント
export AZURE_OPENAI_ENDPOINT="https://your-resource-name.cognitiveservices.azure.com"

# Azure OpenAI APIキー
export AZURE_OPENAI_API_KEY="your-azure-openai-api-key"

# Azure OpenAI デプロイメント名
export AZURE_OPENAI_DEPLOYMENT_NAME="your-deployment-name"
```

### Dify 設定
```bash
# Dify APIベースURL
export DIFY_BASE_URL="http://your-dify-server/v1/"

# Dify APIキー
export DIFY_API_KEY="your-dify-api-key"

# DifyデータセットID
export DIFY_DATASET_ID="your-dataset-id"
```

## Windows 環境での設定方法

### コマンドプロンプト（一時的）
```cmd
set AZURE_OPENAI_ENDPOINT=https://your-resource-name.cognitiveservices.azure.com
set AZURE_OPENAI_API_KEY=your-azure-openai-api-key
set AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
set DIFY_BASE_URL=http://your-dify-server/v1/
set DIFY_API_KEY=your-dify-api-key
set DIFY_DATASET_ID=your-dataset-id
```

### PowerShell（一時的）
```powershell
$env:AZURE_OPENAI_ENDPOINT="https://your-resource-name.cognitiveservices.azure.com"
$env:AZURE_OPENAI_API_KEY="your-azure-openai-api-key"
$env:AZURE_OPENAI_DEPLOYMENT_NAME="your-deployment-name"
$env:DIFY_BASE_URL="http://your-dify-server/v1/"
$env:DIFY_API_KEY="your-dify-api-key"
$env:DIFY_DATASET_ID="your-dataset-id"
```

### システム環境変数（永続的）
1. Windows設定 → システム → 詳細情報 → システムの詳細設定
2. 「環境変数」ボタンをクリック
3. 「システム環境変数」で上記の変数を追加

## 実行方法

環境変数を設定後、以下のコマンドで実行：

```bash
# 一回実行モード
python src\main.py --config config\config.production.yaml --single

# 監視モード
python src\main.py --config config\config.production.yaml --watch
```

または、バッチファイルを使用：

```bash
# 一回実行モード
run_production.bat

# 監視モード
run_production_watch.bat
```

## セキュリティ注意事項

- APIキーは絶対にコードに直接書かない
- 本番環境では必ず環境変数を使用する
- .envファイルを使用する場合は.gitignoreに追加する
- 定期的にAPIキーを更新する