# app.py (上書き)

from flask import Flask, render_template, request, flash, redirect, url_for
import csv
import os

# Flaskアプリケーションの初期化
app = Flask(__name__)
app.secret_key = 'supersecretkey'

# 保存するCSVファイルの名前
CSV_FILE = 'reports.csv'

# マスターデータ
MASTER_DATA = {
    'teams': ["永野", "檀上", "稲垣", "社長"],
    'persons': ["永野", "稲垣", "檀上", "社長", "貞重", "眞鍋", "村田"],
    'volumes': ["84本", "90本"],
    'conditions': ["良好", "普通", "ぬかるみ", "積雪"]
}


# メインページ（入力フォーム画面）
@app.route('/')
def index():
    return render_template('index.html', master=MASTER_DATA)


# --- ★ここから新しい機能を追加 ---
# 報告一覧ページ
@app.route('/reports')
def reports():
    report_list = []
    # CSVファイルが存在するか確認
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'r', encoding='utf-8-sig') as f:
            # DictReaderを使って、各行を辞書として読み込む
            reader = csv.DictReader(f)
            for row in reader:
                report_list.append(row)
    # 読み込んだデータをHTMLテンプレートに渡す (新しい順に並び替える)
    return render_template('reports.html', reports=reversed(report_list))
# --- ★ここまで新しい機能 ---


# フォームが送信された時の処理
@app.route('/submit', methods=['POST'])
def submit():
    report_data = {
        'date': request.form.get('report_date'),
        'team': request.form.get('team'),
        'person_in_charge': request.form.get('person_in_charge'),
        'volume': request.form.get('volume'),
        'defects': request.form.get('defects'),
        'condition': request.form.get('condition'),
        'notes': request.form.get('notes')
    }
    
    file_exists = os.path.isfile(CSV_FILE)
    
    with open(CSV_FILE, 'a', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=report_data.keys())
        if not file_exists or os.path.getsize(CSV_FILE) == 0:
            writer.writeheader()
        writer.writerow(report_data)

    print("--- 新しい作業報告が reports.csv に保存されました ---")
    print(report_data)
    print("----------------------------------------------------")
    
    flash(f"「{report_data['team']}チーム」の報告が保存され、全員に通知が送信されました！")
    
    return redirect(url_for('index'))


# このファイルが直接実行されたら、開発用サーバーを起動
if __name__ == '__main__':
    app.run(debug=True)
