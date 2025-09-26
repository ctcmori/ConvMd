FROM python:3.11-slim

# 作業ディレクトリの設定
WORKDIR /app

# システムパッケージの更新と必要なパッケージのインストール
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libreoffice \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係のコピーとインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY src/ ./src/
COPY prompts/ ./prompts/
COPY config/ ./config/
COPY run_e2e_tests.py ./
COPY run_integration_tests.py ./
COPY deployment/ ./deployment/

# 必要なディレクトリの作成
RUN mkdir -p logs input output temp test_reports

# 非ルートユーザーの作成
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# 環境変数の設定
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Dify統合用環境変数（実行時に設定が必要）
ENV DIFY_BASE_URL=https://api.dify.ai/v1
ENV LOG_LEVEL=INFO

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "from src.office_converter.services.dify_api_client import DifyAPIClient; print('Health check passed')"

# アプリケーションの実行
CMD ["python", "src/main.py"]

# ラベル
LABEL maintainer="ConvMd Project"
LABEL version="2.0.0"
LABEL description="Office-to-Markdown変換システム with Dify RAG統合"
LABEL org.opencontainers.image.source="https://github.com/ctcmori/ConvMd"