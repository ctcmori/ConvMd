# Dify RAG統合システム API仕様書

## 概要

Dify RAG統合システムは、Office文書をMarkdownに変換し、Dify Knowledge Baseと統合するための包括的なAPIセットを提供します。

### ベースURL
```
https://api.yourservice.com/v1
```

### サポートされる形式
- **入力**: PDF、DOCX、XLSX、PPTX、TXT、MD
- **出力**: Markdown、JSON（メタデータ付き）
- **文字エンコーディング**: UTF-8

## 認証

### APIキー認証
```http
Authorization: Bearer your_api_key_here
```

### 環境変数
```bash
export API_KEY="your_api_key"
export DIFY_API_KEY="your_dify_api_key"  
export AZURE_OPENAI_API_KEY="your_azure_openai_key"
```

## エラーハンドリング

### エラーレスポンス形式
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "ファイル形式がサポートされていません",
    "details": {
      "field": "file_type",
      "supported_types": [".pdf", ".docx"]
    },
    "request_id": "req_123456789"
  }
}
```

### エラーコード一覧

| コード | HTTPステータス | 説明 |
|--------|---------------|------|
| `INVALID_API_KEY` | 401 | APIキーが無効 |
| `RATE_LIMIT_EXCEEDED` | 429 | レート制限超過 |
| `FILE_TOO_LARGE` | 413 | ファイルサイズ上限超過 |
| `UNSUPPORTED_FORMAT` | 400 | 非対応ファイル形式 |
| `CONVERSION_FAILED` | 500 | 変換処理失敗 |
| `DIFY_INTEGRATION_ERROR` | 502 | Dify API連携エラー |

## API エンドポイント

### 1. 単一ファイル変換

#### `POST /convert/single`

```http
POST /convert/single HTTP/1.1
Content-Type: multipart/form-data

file: (binary)
metadata: {"category": "技術文書", "department": "開発部"}
```

**レスポンス:**
```json
{
  "result": {
    "conversion_id": "conv_123456",
    "markdown_content": "# 技術仕様書\n\n## 概要\n...",
    "metadata": {
      "original_filename": "spec.docx",
      "file_size": 1024576,
      "conversion_time": "2024-01-01T10:00:00Z"
    },
    "dify_document_id": "doc_789012",
    "chunks": [
      {
        "id": "chunk_001",
        "content": "...",
        "tokens": 150,
        "type": "parent"
      }
    ]
  }
}
```

### 2. Dify統合

#### `POST /dify/upload`

Dify Knowledge Baseへの文書アップロード

```http
POST /dify/upload HTTP/1.1
Content-Type: application/json

{
  "markdown_content": "# 文書タイトル\n\n内容...",
  "metadata": {
    "title": "技術仕様書",
    "category": "documentation"
  },
  "chunking_config": {
    "max_parent_tokens": 1000,
    "max_child_tokens": 400,
    "overlap_ratio": 0.1
  }
}
```

#### `GET /dify/search`

Difyでの文書検索

```http
GET /dify/search?q=認証機能&top_k=5&category=技術文書
```

**レスポンス:**
```json
{
  "results": [
    {
      "document_id": "doc_123",
      "title": "認証システム設計書",
      "content": "認証機能の実装について...",
      "score": 0.95,
      "metadata": {
        "category": "技術文書",
        "created_at": "2024-01-01T10:00:00Z"
      }
    }
  ],
  "total_results": 15,
  "query_time_ms": 125
}
```

### 3. バッチ処理

#### `POST /batch/process`

複数ファイルの一括処理

```http
POST /batch/process HTTP/1.1
Content-Type: multipart/form-data

files[]: (binary files)
config: {
  "concurrent_uploads": 3,
  "continue_on_error": false
}
```

### 4. ステータス確認

#### `GET /status/{job_id}`

処理状況の確認

```http
GET /status/job_123456
```

**レスポンス:**
```json
{
  "job_id": "job_123456",
  "status": "processing",
  "progress": {
    "total_files": 10,
    "processed_files": 7,
    "success_count": 6,
    "error_count": 1
  },
  "estimated_completion": "2024-01-01T10:15:00Z"
}
```

## Python SDK

### インストール
```bash
pip install convmd-dify-sdk
```

### 基本的な使用方法

```python
from convmd_dify import DifyIntegrationClient

# クライアント初期化
client = DifyIntegrationClient(
    api_key="your_api_key",
    dify_api_key="your_dify_api_key",
    base_url="https://api.yourservice.com/v1"
)

# 単一ファイル変換
result = client.convert_file(
    file_path="document.docx",
    metadata={"category": "技術文書", "department": "開発部"}
)

print(f"変換完了: {result.dify_document_id}")
print(f"チャンク数: {len(result.chunks)}")

# Dify検索
search_results = client.search_documents(
    query="認証機能",
    top_k=5,
    metadata_filter={"category": "技術文書"}
)

for doc in search_results:
    print(f"- {doc.title}: {doc.score:.2f}")
```

### 高度な使用例

```python
# バッチ処理
batch_job = client.process_batch(
    file_paths=["doc1.docx", "doc2.pdf", "doc3.pptx"],
    config={
        "concurrent_uploads": 3,
        "continue_on_error": True
    }
)

# 進捗監視
while not batch_job.is_completed():
    status = batch_job.get_status()
    print(f"進捗: {status.progress.processed_files}/{status.progress.total_files}")
    time.sleep(5)

# 結果取得
results = batch_job.get_results()
for result in results:
    if result.success:
        print(f"✅ {result.filename}: {result.dify_document_id}")
    else:
        print(f"❌ {result.filename}: {result.error_message}")
```

### エラーハンドリング

```python
from convmd_dify.exceptions import (
    ConversionError, 
    DifyIntegrationError, 
    RateLimitError
)

try:
    result = client.convert_file("document.docx")
except RateLimitError as e:
    print(f"レート制限: {e.retry_after}秒後に再試行")
    time.sleep(e.retry_after)
except ConversionError as e:
    print(f"変換エラー: {e.message}")
except DifyIntegrationError as e:
    print(f"Dify統合エラー: {e.message}")
```

## レート制限

| エンドポイント | 制限 | 時間窓 |
|---------------|------|-------|
| `/convert/*` | 100リクエスト | 1分 |
| `/dify/*` | 60リクエスト | 1分 |
| `/batch/*` | 10リクエスト | 1分 |

### レート制限ヘッダー
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
Retry-After: 60
```

## セキュリティ

### HTTPS必須
本番環境では全てのAPIアクセスでHTTPS接続が必要です。

### APIキー管理
- 定期的なローテーション推奨（90日毎）
- 環境変数での管理
- ログ出力時のマスキング

### データ保護
- 一時ファイルの自動削除
- メモリ内容の適切な消去
- 機密情報のログ出力禁止

## 制限事項

### ファイルサイズ
- 単一ファイル: 最大100MB
- バッチ処理: 最大1GB（全ファイル合計）

### 同時処理数
- 単一ユーザー: 最大10並行リクエスト
- バッチ処理: 最大3並行アップロード

### サポート言語
- 日本語（主要対応）
- 英語
- 中国語（簡体字）

## 監視・メトリクス

### ヘルスチェック
```http
GET /health
```

**レスポンス:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T10:00:00Z",
  "services": {
    "conversion": "healthy",
    "dify_integration": "healthy",
    "azure_openai": "healthy"
  }
}
```

### メトリクス
```http
GET /metrics
```

## サポート・連絡先

- **ドキュメント**: https://docs.yourservice.com
- **Issue報告**: https://github.com/ctcmori/ConvMd/issues
- **技術サポート**: support@yourservice.com

---

この仕様書は継続的に更新されます。最新版は常にGitHubリポジトリで確認してください。