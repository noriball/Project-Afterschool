import os
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
# モデル名を明示せず、クライアント経由で生成
model = genai.GenerativeModel('gemini-1.5-flash')

response = model.generate_content("一言で、今日の世界を皮肉ってください。")

with open("archives/today.md", "w", encoding="utf-8") as f:
    f.write(response.text)