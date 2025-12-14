import pandas as pd
import xlsxwriter

def create_analysis_excel(data, filename):
    """JSONデータから分析用Excelを作成する"""
    
    # データをPandasフレームに変換
    questions = data.get('questions', [])
    if not questions:
        # データがない場合のダミー
        questions = [{"topic": "データなし", "max_score": 0, "score": 0}]
        
    df = pd.DataFrame(questions)
    
    # 単元ごとの集計
    df_summary = df.groupby('topic')[['score', 'max_score']].sum().reset_index()
    # 得点率計算（ゼロ除算回避）
    df_summary['rate'] = df_summary.apply(lambda x: (x['score'] / x['max_score'] * 100) if x['max_score'] > 0 else 0, axis=1)

    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    workbook = writer.book

    # シート1: 詳細
    df.to_excel(writer, sheet_name='詳細データ', index=False)
    
    # シート2: 分析レポート
    ws = workbook.add_worksheet('分析レポート')
    
    # スタイル定義
    header_fmt = workbook.add_format({'bold': True, 'font_size': 14})
    table_header_fmt = workbook.add_format({'bold': True, 'bg_color': '#DDEBF7', 'border': 1})
    
    # 基本情報
    ws.write('B2', f"氏名: {data.get('student_name', '生徒')}", header_fmt)
    ws.write('B3', f"合計点: {data.get('total_score', 0)} 点", header_fmt)

    # 表書き込み
    ws.write_row('B6', ['単元', '得点', '配点', '得点率(%)'], table_header_fmt)
    for i, row in df_summary.iterrows():
        ws.write(6 + i, 1, row['topic'])
        ws.write(6 + i, 2, row['score'])
        ws.write(6 + i, 3, row['max_score'])
        ws.write(6 + i, 4, round(row['rate'], 1))

    # レーダーチャート作成
    chart = workbook.add_chart({'type': 'radar', 'subtype': 'filled'})
    num_rows = len(df_summary)
    
    if num_rows > 0:
        chart.add_series({
            'name':       '単元別達成度',
            'categories': ['分析レポート', 6, 1, 6 + num_rows - 1, 1],
            'values':     ['分析レポート', 6, 4, 6 + num_rows - 1, 4],
            'fill':       {'color': '#4472C4', 'transparency': 50},
            'line':       {'color': '#4472C4'},
        })

    chart.set_title({'name': '苦手単元の可視化'})
    chart.set_y_axis({'min': 0, 'max': 100})
    ws.insert_chart('F2', chart)
    
    writer.close()
    return filename