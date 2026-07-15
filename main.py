import os
import datetime
import google.generativeai as genai

JST = datetime.timezone(datetime.timedelta(hours=9))

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in environment variables.")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = "テスト稼働です。現在の状況について、論理的かつ簡潔に1行で述べてください。"
    response = model.generate_content(prompt)

    output_dir = "archives"
    os.makedirs(output_dir, exist_ok=True)
    
    current_time = datetime.datetime.now(JST).strftime("%Y-%m-%d_%H-%M-%S")
    file_path = os.path.join(output_dir, f"archive_{current_time}.md")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(response.text)
        
    print(f"Successfully generated: {file_path}")

if __name__ == "__main__":
    main()
