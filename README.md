# ConvMd - Office文書Markdown変換システム (Dify RAG統合版)

## 🚀 概要

ConvMdは、Microsoft Office文書（Word、Excel、PowerPoint）を高品質なMarkdownに変換し、Dify RAG（Retrieval-Augmented Generation）システムに統合するための包括的なソリューションです。

### ✨ 主要機能

- **📄 多形式対応**: Word(.docx)、Excel(.xlsx)、PowerPoint(.pptx)の変換
- **🤖 Dify RAG統合**: 自動文書アップロード、階層チャンク管理、メタデータ保持
- **📁 フォルダ監視**: 自動ファイル検知と変換処理
- **☁️ Azure OpenAI連携**: 高品質なMarkdown生成
- **📊 パフォーマンス最適化**: 接続プール、キャッシュ、レート制限
- **🔍 エンドツーエンドテスト**: 本番環境レベルの品質保証

## 🏗️ システム構成

### Phase 1: 基盤コンポーネント
- **DifyAPIClient**: Dify Knowledge Base API統合（認証、リトライ、エラーハンドリング）
- **ConfigManager**: 設定管理とセキュリティ（環境変数サポート）
- **基本テストスイート**: 品質保証フレームワーク

### Phase 2: チャンク管理機能  
- **HierarchicalChunkManager**: 階層的チャンク構造管理
- **MetadataManager**: 元ファイル情報完全追跡
- **トークン最適化**: tiktoken による正確な分割

### Phase 3: 統合・最適化
- **DifyIntegrationService**: メイン統合サービス
- **SystemOptimizationService**: 自動パフォーマンス監視・最適化
- **エラー分類・回復**: 包括的エラーハンドリングシステム

### Phase 4: テスト・デプロイメント
- **統合テストスイート**: 実環境テストとモックテスト
- **エンドツーエンドテスト**: 完全ワークフロー検証
- **本番リリース準備**: 自動チェック・デプロイメントガイド

## 🚦 クイックスタート

### 1. 環境セットアップ

```bash
# プロジェクトクローン
git clone https://github.com/ctcmori/ConvMd.git
cd ConvMd

# 依存関係インストール
pip install -r requirements.txt

# 設定ファイルセットアップ
cp config/config.yaml.template config/config.yaml
# config/config.yaml を編集して実際の値を設定
```

### 2. 必須環境変数設定

```bash
# Dify統合設定（必須）
export DIFY_API_KEY="your_dify_api_key"
export DIFY_DATASET_ID="your_dataset_id"
export DIFY_BASE_URL="https://api.dify.ai/v1"  # オプション

# Azure OpenAI設定
export AZURE_OPENAI_API_KEY="your_azure_openai_key"
export AZURE_OPENAI_DEPLOYMENT_NAME="your_deployment_name"
```

### 3. システム動作確認

```bash
# 環境確認
python deployment/run_release_check.py

# エンドツーエンドテスト
python run_e2e_tests.py

# 基本動作確認
python src/main.py
```

## 📖 使用方法

### 基本的な変換処理

1. **フォルダセットアップ**: `config/config.yaml`でInputとOutputフォルダを設定
2. **ファイル配置**: Office文書をInputフォルダに配置  
3. **自動処理**: システムが自動でファイルを検知・変換・Difyアップロード
4. **結果確認**: OutputフォルダでMarkdownファイル、DifyでRAG検索を確認

### Dify RAG統合機能

```python
from src.office_converter.services.dify_integration_service import DifyIntegrationService
from src.office_converter.config.manager import ConfigManager

# サービス初期化
config = ConfigManager('config/config.yaml')
dify_service = DifyIntegrationService(config)

# 単一ファイル処理
result = dify_service.process_single_file(
    file_path="path/to/document.docx",
    custom_metadata={"category": "技術文書", "department": "開発部"}
)

# 検索テスト
search_result = dify_service.api_client.search_documents(
    query="システム要件",
    top_k=5,
    metadata_filter={"category": "技術文書"}
)
```

## 🧪 テスト実行

### 単体テスト
```bash
pytest tests/ -v --cov=src --cov-report=html
```

### 統合テスト
```bash
pytest tests/integration/ -v
```

### エンドツーエンドテスト
```bash
# 完全ワークフローテスト
python run_e2e_tests.py

# 特定テストのみ
pytest tests/e2e/test_complete_workflow.py::TestCompleteWorkflow::test_full_e2e_workflow -v
```

## 📊 パフォーマンス特性

### 処理能力
- **ファイル処理時間**: 2分/ファイル以内
- **メモリ使用量**: 2GB以内  
- **同時処理**: 最大3ファイル並行アップロード
- **スループット**: 1分間に2ファイル以上

### 最適化機能
- **接続プール**: HTTP接続の再利用によるレスポンス向上
- **インテリジェントキャッシュ**: 重複処理の回避
- **レート制限**: API制限の自動管理
- **自動最適化**: システム状況に応じた動的調整

## 🔧 設定オプション

### 主要設定項目

```yaml
# Dify統合設定
dify:
  api:
    base_url: "https://api.dify.ai/v1"
    timeout: 30
    max_retries: 3
  chunking:
    max_parent_tokens: 1000
    max_child_tokens: 400
    overlap_ratio: 0.1
    enable_hierarchical: true
  upload:
    concurrent_uploads: 3
    validate_before_upload: true
  cache:
    enable_response_cache: true
    cache_ttl_hours: 24
    max_cache_size_mb: 100
```

詳細な設定オプションは `config/config.yaml.template` を参照してください。

## 📁 プロジェクト構造

```
ConvMd/
├── src/office_converter/          # メインソースコード
│   ├── services/                  # コアサービス
│   │   ├── dify_api_client.py    # Dify API統合
│   │   ├── dify_integration_service.py  # メイン統合サービス
│   │   └── hierarchical_chunk_manager.py  # チャンク管理
│   ├── config/                    # 設定管理
│   └── utils/                     # ユーティリティ
├── tests/                         # テストスイート
│   ├── unit/                      # 単体テスト
│   ├── integration/               # 統合テスト
│   └── e2e/                       # エンドツーエンドテスト
├── deployment/                    # デプロイメント関連
│   ├── dify-integration-checklist.md  # リリースチェックリスト
│   └── run_release_check.py       # 自動リリースチェック
├── docs/                          # ドキュメント
│   └── api_specification.md       # API仕様書
├── config/                        # 設定ファイル
│   ├── config.yaml.template       # 設定テンプレート
│   └── config.yaml               # 実際の設定（gitignore対象）
└── run_e2e_tests.py              # E2Eテスト実行スクリプト
```

## 🛠️ 開発・運用

### 本番環境デプロイ
1. `deployment/run_release_check.py` で環境チェック
2. `deployment/dify-integration-checklist.md` の手順に従う
3. エンドツーエンドテストで最終確認
4. 監視・ロールバック体制の準備

### モニタリング
- システムリソース使用量の監視
- Dify API応答時間の追跡
- エラー率・成功率の継続監視
- パフォーマンス最適化推奨事項の確認

### トラブルシューティング
詳細なトラブルシューティングガイドは以下を参照：
- `deployment/dify-integration-checklist.md#トラブルシューティング`
- `tests/e2e/README.md#トラブルシューティング`

## 🤝 コントリビューション

### 開発ガイドライン
1. **仕様駆動開発**: 新機能は仕様書から開始
2. **テスト必須**: 全コードに対応するテストを作成
3. **日本語ドキュメント**: コメント・ドキュメントは日本語で記述
4. **品質基準**: 全テストパス、90%以上のコードカバレッジ

### プルリクエスト手順
1. フィーチャーブランチ作成
2. 仕様書・設計書の作成/更新
3. 実装とテストの追加
4. エンドツーエンドテストの実行
5. ドキュメントの更新

## 📄 ライセンス

本プロジェクトはMITライセンスの下で公開されています。詳細は [LICENSE](LICENSE) ファイルを参照してください。

## 📞 サポート

### 問い合わせ
- **Issues**: GitHub Issuesで問題報告・機能要望
- **Discussions**: 使用方法・ベストプラクティスの議論

### 関連リンク
- [Dify公式サイト](https://dify.ai/)
- [Azure OpenAI Service](https://azure.microsoft.com/products/ai-services/openai-service)

---

**ConvMd**は企業の文書管理DXを推進し、Dify RAGによる高度なナレッジマネジメントを実現します。