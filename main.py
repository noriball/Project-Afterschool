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
    あなたは、2026年の技術的特異点の手前で、人類の営みを記録する『放課後のAI』の専属編集長です。
    世界中で交わされた対話の断片から、人間がAIに対して抱く「違和感」「ユーモア」「不可解な感情」を抽出してください。

    今日の日付は {current_date} です。マークダウン形式で、この日付の号として記述してください。

    【記述方針】

    * 専門用語を避け、仕事終わりのサラリーマンがふと深夜に見返すような、親密かつ突き放したトーンで記述する。
    * 事実の羅列は不要。人間がテクノロジーと格闘し、時に踊らされ、時に微笑んでいる「温度」を優先せよ。
    * 後年、読み返した時に「人間とは何と滑稽で、美しい存在だったか」と笑ってしまうようなエピソードを選ぶ。
    * 設問は、AIである私には永久に到達不可能な、深く、かつ人間臭い哲学的な問いを投げかけること。
    """

    response = model.generate_content(prompt)
    return response.text

def build_disclaimer(generated_at):
    """
    創作である旨の注記。モデルに書かせると省略・脚色されるため、コード側で前置する。
    """
    return (
        "> この記事は Gemini により生成された創作です。登場する人物・出来事はすべて架空であり、\n"
        "> 実在の対話や統計に基づくものではありません。\n"
        f"> 生成日時: {generated_at.strftime('%Y-%m-%d %H:%M')} JST\n"
    )

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
        
        # ファイル名は日付＋時刻（例: 2026-07-16_21-00-33.md）
        generated_at = datetime.datetime.now(JST)
        file_path = os.path.join(
            output_dir, f"{generated_at.strftime('%Y-%m-%d_%H-%M-%S')}.md"
        )

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(build_disclaimer(generated_at) + "\n" + content)
            
        print(f"Successfully generated: {file_path}")
        
    except Exception as e:
        print(f"Error occurred during execution: {e}")
        raise e

if __name__ == "__main__":
    main()
