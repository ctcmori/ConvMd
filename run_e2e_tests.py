# -*- coding: utf-8 -*-
"""
エンドツーエンドテスト実行スクリプト

Dify RAG統合システムの完全な動作確認を行うコマンドラインスクリプトです。
本番環境と同等の条件でシステムの検証を実行し、詳細なレポートを生成します。
"""

import os
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tests.e2e.test_complete_workflow import run_complete_e2e_tests


def main():
    \"\"\"エンドツーエンドテスト実行のメイン関数\"\"\"
    
    parser = argparse.ArgumentParser(
        description=\"Dify RAG統合システム エンドツーエンドテスト\",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=\"\"\"
使用例:
  python run_e2e_tests.py                    # 基本実行
  python run_e2e_tests.py --output reports   # レポート出力先指定
  python run_e2e_tests.py --check-env        # 環境変数確認のみ
  
環境変数:
  DIFY_API_KEY      Dify APIキー (必須)
  DIFY_DATASET_ID   Difyデータセット ID (必須)
  DIFY_BASE_URL     Dify API ベースURL (オプション)
        \"\"\"
    )
    
    parser.add_argument(
        \"--output\", \"-o\",
        type=str,
        default=\"test_reports\",
        help=\"テストレポートの出力ディレクトリ (デフォルト: test_reports)\"
    )
    
    parser.add_argument(
        \"--check-env\",
        action=\"store_true\",
        help=\"環境変数の確認のみ実行\"
    )
    
    parser.add_argument(
        \"--verbose\", \"-v\",
        action=\"store_true\",
        help=\"詳細な出力を表示\"
    )
    
    args = parser.parse_args()
    
    # 出力ディレクトリの作成
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(\"🔍 Dify RAG統合システム エンドツーエンドテスト\")
    print(\"=\" * 50)
    print(f\"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\")
    print(f\"レポート出力先: {output_dir.absolute()}\")
    print()
    
    # 環境変数チェック
    print(\"📋 環境設定確認\")
    print(\"-\" * 20)
    
    required_env_vars = {
        \"DIFY_API_KEY\": \"Dify APIキー\",
        \"DIFY_DATASET_ID\": \"Difyデータセット ID\"
    }
    
    optional_env_vars = {
        \"DIFY_BASE_URL\": \"Dify API ベースURL\"
    }
    
    env_status = {}
    all_required_set = True
    
    for var_name, description in required_env_vars.items():
        value = os.getenv(var_name)
        is_set = bool(value)
        env_status[var_name] = {
            \"description\": description,
            \"is_set\": is_set,
            \"required\": True,
            \"value_preview\": value[:20] + \"...\" if value and len(value) > 20 else value
        }
        
        status_icon = \"✅\" if is_set else \"❌\"
        value_display = f\"設定済み ({value[:10]}...)\" if is_set else \"未設定\"
        print(f\"{status_icon} {description}: {value_display}\")
        
        if not is_set:
            all_required_set = False
    
    for var_name, description in optional_env_vars.items():
        value = os.getenv(var_name)
        is_set = bool(value)
        env_status[var_name] = {
            \"description\": description,
            \"is_set\": is_set,
            \"required\": False,
            \"value_preview\": value[:20] + \"...\" if value and len(value) > 20 else value
        }
        
        status_icon = \"ℹ️\" if is_set else \"⚪\"
        value_display = f\"設定済み ({value})\" if is_set else \"デフォルト使用\"
        print(f\"{status_icon} {description}: {value_display}\")
    
    # 環境設定レポート保存
    env_report = {
        \"timestamp\": datetime.now().isoformat(),
        \"environment_variables\": env_status,
        \"all_required_set\": all_required_set
    }
    
    with open(output_dir / \"environment_check.json\", \"w\", encoding=\"utf-8\") as f:
        json.dump(env_report, f, ensure_ascii=False, indent=2)
    
    print()
    
    # 環境チェックのみの場合
    if args.check_env:
        if all_required_set:
            print(\"✅ 環境設定は正常です。テスト実行が可能です。\")
            return 0
        else:
            print(\"❌ 必要な環境変数が不足しています。\")
            print(\"\\n設定方法:\")
            for var_name, info in env_status.items():
                if info[\"required\"] and not info[\"is_set\"]:
                    print(f\"  export {var_name}='your_value_here'\")
            return 1
    
    # 必須環境変数チェック
    if not all_required_set:
        print(\"❌ 必要な環境変数が設定されていません。\")
        print(\"--check-env オプションで詳細を確認してください。\")
        return 1
    
    print(\"🚀 エンドツーエンドテスト実行開始\")
    print(\"-\" * 30)
    
    # テスト実行
    try:
        success = run_complete_e2e_tests(str(output_dir))
        
        # 結果サマリー
        print(\"\\n📊 テスト実行結果サマリー\")
        print(\"-\" * 25)
        
        if success:
            print(\"✅ 全エンドツーエンドテスト: 合格\")
            print(\"🎉 システムは本番環境への展開準備が完了しています！\")
            
            # 成功時の推奨次ステップ
            print(\"\\n📋 推奨次ステップ:\")
            print(\"1. ✅ パフォーマンステスト結果の確認\")
            print(\"2. 📝 運用マニュアルの最終確認\") 
            print(\"3. 🚀 本番環境への展開実行\")
            print(\"4. 📊 運用監視の開始\")
            
        else:
            print(\"❌ エンドツーエンドテスト: 不合格\")
            print(\"🔧 問題の修正が必要です。\")
            
            # 失敗時の推奨対応
            print(\"\\n🔍 推奨対応手順:\")
            print(\"1. 📄 詳細レポートの確認\")
            print(\"2. 🐛 エラー原因の特定と修正\")
            print(\"3. 🔧 設定やコードの調整\")
            print(\"4. 🔄 修正後の再テスト実行\")
        
        # レポートファイル一覧
        print(f\"\\n📁 生成されたレポート:\")
        for report_file in output_dir.glob(\"*.xml\"):
            print(f\"  - {report_file.name}\")
        for report_file in output_dir.glob(\"*.json\"):
            print(f\"  - {report_file.name}\")
        
        return 0 if success else 1
        
    except Exception as e:
        print(f\"❌ テスト実行中にエラーが発生しました:\")
        print(f\"   {type(e).__name__}: {str(e)}\")
        
        if args.verbose:
            import traceback
            print(\"\\n🔍 詳細なエラートレース:\")
            traceback.print_exc()
        
        return 1


if __name__ == \"__main__\":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(\"\\n\\n⏸️  ユーザーによりテストが中断されました\")
        sys.exit(130)
    except Exception as e:
        print(f\"\\n❌ 予期しないエラーが発生しました: {e}\")
        sys.exit(1)