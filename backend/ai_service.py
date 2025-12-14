import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# .envファイルからAPIキーを読み込み
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    # サーバーログに警告を出す
    print("Warning: GEMINI_API_KEY not found in .env file.")

# Geminiの設定
if api_key:
    genai.configure(api_key=api_key)

def analyze_image_with_ai(image_path):
    """Gemini Flashモデルを使って画像を解析しJSONを返す"""
    
    # モデル設定 (JSONモード)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config={"response_mime_type": "application/json"}
    )

    with open(image_path, "rb") as f:
        image_data = f.read()

    # プロンプト
    prompt = """
    このテスト画像の採点結果を解析してください。
    出力は以下のJSONスキーマに厳密に従ってください：
    {
      "student_name": "生徒の名前（不明なら'生徒'）",
      "total_score": 合計得点（数値）,
      "questions": [
        { 
          "topic": "単元名（計算、図形、関数、文章題、漢字、文法など内容から推測）", 
          "max_score": 配点（数値）, 
          "score": 得点（数値） 
        }
      ]
    }
    """

    try:
        response = model.generate_content([
            prompt,
            {"mime_type": "image/jpeg", "data": image_data}
        ])
        return json.loads(response.text)
    except Exception as e:
        print(f"AI Error: {e}")
        # エラー時は空のデータを返してシステムが落ちないようにする
        return {"student_name": "Error", "total_score": 0, "questions": []}