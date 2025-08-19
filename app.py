# app.py (v5 - データベース対応版)

from flask import Flask, render_template, request, flash, redirect, url_for
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text # 文字列でSQLを実行するために追加

# --- データベース設定 ---
# 1. Flaskアプリケーションの初期化
app = Flask(__name__)

# 2. データベース接続情報の設定
# Renderの環境変数 'DATABASE_URL' を読み込む。
# もし環境変数がなければ、ローカルテスト用にSQLite（ファイルベースのDB）を使う。
db_url = os.environ.get('DATABASE_URL')
if not db_url:
    # RenderのPostgreSQL URLの 'postgres://' を 'postgresql://' に置換する
    # SQLAlchemyが正しく解釈できるようにするため
    raise ValueError("DATABASE_URL is not set. Please set it in your environment.")

# RenderのURLスキームを修正
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # 推奨設定

# 3. データベースオブジェクトの作成
db = SQLAlchemy(app)

# 4. flashメッセージ（アラート）機能のために秘密鍵を設定
app.secret_key = 'supersecretkey_for_db'


# --- データベースのテーブル定義 (モデル) ---
# Reportという名前のテーブルを定義します。これがCSVの代わりになります。
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True) # 各行を識別するためのユニークなID
    report_date = db.Column(db.String(80), nullable=False)
    site_name = db.Column(db.String(255), nullable=False)
    team = db.Column(db.String(80), nullable=False)
    person_in_charge = db.Column(db.String(80), nullable=False)
    volume = db.Column(db.Integer, nullable=False) # ユーザーの要望により、プルダウンから数値入力に変更。既存のDBテーブルで型変更が必要な場合は、マイグレーションツール（例: Alembic）の使用を検討してください。
    arranged_quantity = db.Column(db.String(80), nullable=True)
    length_breakdown = db.Column(db.String(255), nullable=True)
    good_products = db.Column(db.String(255), nullable=True)
    site_inventory = db.Column(db.String(255), nullable=True)
    delivery_due_date = db.Column(db.String(255), nullable=True)
    delivery_destination = db.Column(db.String(255), nullable=True)
    defects = db.Column(db.Integer, nullable=False)
    condition = db.Column(db.String(80), nullable=False)
    notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Report {self.id}>'

# アプリケーションのコンテキスト内でデータベーステーブルを作成
with app.app_context():
    db.create_all()


# --- マスターデータ (これは変わりません) ---
MASTER_DATA = {
    'teams': ["永野", "檀上", "稲垣", "社長"],
    'persons': ["永野", "稲垣", "檀上", "社長", "貞重", "眞鍋", "村田"],
    'conditions': ["良好", "普通", "ぬかるみ", "積雪"]
}


# --- ルート (URLと関数の紐付け) ---

# メインページ（入力フォーム画面）
@app.route('/')
def index():
    return render_template('index.html', master=MASTER_DATA)


# 報告一覧ページ (CSVを読む代わりに、データベースからデータを取得)
@app.route('/reports')
def reports():
    # データベースから全ての報告を、IDの降順（新しい順）で取得
    all_reports = Report.query.order_by(Report.id.desc()).all()
    return render_template('reports.html', reports=all_reports)


# フォームが送信された時の処理 (CSVに書き込む代わりに、データベースに保存)
@app.route('/submit', methods=['POST'])
def submit():
    # フォームからデータを取得
    date = request.form.get('report_date')
    site_name = request.form.get('site_name')
    team = request.form.get('team')
    person_in_charge = request.form.get('person_in_charge')
    volume = int(request.form.get('volume'))
    arranged_quantity = request.form.get('arranged_quantity')
    length_breakdown = request.form.get('length_breakdown')
    good_products = request.form.get('good_products')
    site_inventory = request.form.get('site_inventory')
    delivery_due_date = request.form.get('delivery_due_date')
    delivery_destination = request.form.get('delivery_destination')
    defects = request.form.get('defects')
    condition = request.form.get('condition')
    notes = request.form.get('notes')

    # 新しい報告オブジェクトを作成
    new_report = Report(
        report_date=date,
        site_name=site_name,
        team=team,
        person_in_charge=person_in_charge,
        volume=volume,
        arranged_quantity=arranged_quantity,
        length_breakdown=length_breakdown,
        good_products=good_products,
        site_inventory=site_inventory,
        delivery_due_date=delivery_due_date,
        delivery_destination=delivery_destination,
        defects=int(defects), # 文字列を整数に変換
        condition=condition,
        notes=notes
    )

    # データベースセッションに追加して、コミット（保存）する
    db.session.add(new_report)
    db.session.commit()

    flash(f"「{team}チーム」の報告がデータベースに正常に保存されました！")
    
    # 一覧ページにリダイレクトして、今保存したデータが追加されているのを確認できるようにする
    return redirect(url_for('reports'))


# このファイルが直接実行されたら、開発用サーバーを起動
if __name__ == '__main__':
    app.run(debug=True)
