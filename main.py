import os
import datetime
import google.generativeai as genai

JST = datetime.timezone(datetime.timedelta(hours=9))

def generate_archive_content(model):
    """
    アーカイブのコンテンツを生成するメインロジック。
    用途に応じてプロンプトをカスタマイズしてください。
    """
    current_date = datetime.datetime.now(JST).strftime("%Y-%m-%d")

    prompt = f"""
    あなたは優秀な思考整理のパートナーおよび記録アーキビストです。
    今日の日付は {current_date} です。
    
    本日の振り返り、または特定の研究・開発プロジェクトの進捗記録のベースとなる、
    構造化されたマークダウン形式のドキュメントを生成してください。
    
    構成案：
    1. # Archive: {current_date}
    2. ## 概要 (今日の主要なテーマや客観的な事実)
    3. ## 詳細分析 (論理的アプローチによる課題の本質と制約の特定)
    4. ## 次のアクションプラン (MECEを意識した具体的かつ実行可能なタスクリスト)
    
    各セクションについて、深く洞察された示唆に富む内容を記述してください。定型的な挨拶は不要です。
    """
    
    response = model.generate_content(prompt)
    return response.text

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in environment variables.")
    
    genai.configure(api_key=api_key)
    
    # 提供終了でジョブが止まらないよう、固定版ではなくエイリアスを使う
    model = genai.GenerativeModel('gemini-flash-latest')

    try:
        content = generate_archive_content(model)
        
        output_dir = "archives"
        os.makedirs(output_dir, exist_ok=True)
        
        # ファイル名は日付ベース（例: 2026-07-16.md）
        current_date = datetime.datetime.now(JST).strftime("%Y-%m-%d")
        file_path = os.path.join(output_dir, f"{current_date}.md")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        print(f"Successfully generated: {file_path}")
        
    except Exception as e:
        print(f"Error occurred during execution: {e}")
        raise e

if __name__ == "__main__":
    main()
