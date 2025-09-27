@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo Office-to-Markdown Converter 本番実行
echo ==========================================

REM 環境変数の確認
echo 環境変数チェック中...

if "%AZURE_OPENAI_ENDPOINT%"=="" (
    echo [ERROR] AZURE_OPENAI_ENDPOINT 環境変数が設定されていません
    goto :error
)

if "%AZURE_OPENAI_API_KEY%"=="" (
    echo [ERROR] AZURE_OPENAI_API_KEY 環境変数が設定されていません
    goto :error
)

if "%AZURE_OPENAI_DEPLOYMENT_NAME%"=="" (
    echo [ERROR] AZURE_OPENAI_DEPLOYMENT_NAME 環境変数が設定されていません
    goto :error
)

if "%DIFY_BASE_URL%"=="" (
    echo [ERROR] DIFY_BASE_URL 環境変数が設定されていません
    goto :error
)

if "%DIFY_API_KEY%"=="" (
    echo [ERROR] DIFY_API_KEY 環境変数が設定されていません
    goto :error
)

if "%DIFY_DATASET_ID%"=="" (
    echo [ERROR] DIFY_DATASET_ID 環境変数が設定されていません
    goto :error
)

echo [OK] 全ての環境変数が設定されています
echo.

REM 実行開始
echo 一回実行モードで開始します...
python src\main.py --config config\config.production.yaml --single

if !errorlevel! neq 0 (
    echo [ERROR] 実行中にエラーが発生しました
    goto :error
)

echo.
echo [SUCCESS] 処理が完了しました
pause
exit /b 0

:error
echo.
echo [ERROR] 実行に失敗しました
echo.
echo 環境変数設定の詳細は PRODUCTION_SETUP.md をご確認ください
pause
exit /b 1