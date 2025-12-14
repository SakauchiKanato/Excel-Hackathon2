import os
import shutil
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from ai_service import analyze_image_with_ai
from excel_service import create_analysis_excel

app = FastAPI()

# ------------------------------------------------------------------
# 1. APIエンドポイント (画像を受け取りExcelを返す)
# ------------------------------------------------------------------
@app.post("/analyze")
async def analyze_endpoint(file: UploadFile = File(...)):
    # 画像を一時保存
    temp_filename = f"temp_{file.filename}"
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        print(f"Analyzing {file.filename}...")
        
        # AI分析実行
        json_result = analyze_image_with_ai(temp_filename)
        
        # Excel生成実行
        student_name = json_result.get('student_name', 'result')
        output_filename = f"{student_name}_分析結果.xlsx"
        excel_path = create_analysis_excel(json_result, output_filename)

        # ファイルをクライアントに返す
        return FileResponse(
            excel_path, 
            filename=output_filename, 
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}

    finally:
        # 後始末（一時ファイルの削除）
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

# ------------------------------------------------------------------
# 2. フロントエンド配信設定 (HTMLなどを表示する)
# ------------------------------------------------------------------
# backendフォルダの親ディレクトリにあるfrontendフォルダを探す
current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.join(current_dir, "../frontend")

# ルートURL (/) にアクセスした時、frontendフォルダの中身を表示する
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")