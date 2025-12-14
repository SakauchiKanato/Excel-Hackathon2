import os
import shutil
from flask import Flask, request, send_file, jsonify, send_from_directory
from flask_cors import CORS
from ai_service import analyze_image_with_ai
from excel_service import create_analysis_excel

# Flaskアプリの作成
# static_folderを指定して、frontendフォルダの中身を配信できるようにする
# backendフォルダの親にあるfrontendフォルダを指定
frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../frontend")
app = Flask(__name__, static_folder=frontend_dir)

# CORS設定（リストにあったflask-corsを使用）
CORS(app)

@app.route('/')
def serve_index():
    """ルートURLにアクセスしたらindex.htmlを返す"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """その他の静的ファイル（css, jsなど）を返す"""
    return send_from_directory(app.static_folder, path)

@app.route('/analyze', methods=['POST'])
def analyze():
    """画像を受け取って分析し、Excelを返すAPI"""
    
    # ファイルが送られてきているかチェック
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # 一時ファイルとして保存
    temp_filename = f"temp_{file.filename}"
    file.save(temp_filename)

    try:
        print(f"Analyzing {file.filename}...")
        
        # 1. AI分析 (ai_service.py利用)
        json_result = analyze_image_with_ai(temp_filename)
        
        # 2. Excel生成 (excel_service.py利用)
        student_name = json_result.get('student_name', 'result')
        output_filename = f"{student_name}_分析結果.xlsx"
        excel_path = create_analysis_excel(json_result, output_filename)

        # 3. ファイルを返す
        return send_file(
            excel_path,
            as_attachment=True,
            download_name=output_filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        # 後始末（一時ファイル削除）
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

if __name__ == '__main__':
    # サーバー起動 (0.0.0.0で外部アクセス許可、ポート8000)
    app.run(host='0.0.0.0', port=8000)