import os
import sqlite3
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# --- データベース設定 ---
DB_FILE = "calendar.db"

def get_db():
    """データベース接続を取得"""
    db = sqlite3.connect(DB_FILE)
    db.row_factory = sqlite3.Row # 列名でアクセスできるようにする
    return db

def init_db():
    """データベースを初期化（テーブル作成）"""
    if not os.path.exists(DB_FILE):
        with app.app_context():
            db = get_db()
            with db:
                db.execute("""
                    CREATE TABLE events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        start TEXT NOT NULL,
                        end TEXT
                    );
                """)
            print("Database initialized.")

# --- ページ表示 (Web UI) ---
@app.route('/')
def index():
    """カレンダーのWebページ (index.html) を表示"""
    return render_template('index.html')

# --- カレンダーAPI (データ通信) ---

@app.route('/api/events', methods=['GET'])
def get_events():
    """DBから全ての予定を取得してFullCalendarに渡す"""
    db = get_db()
    events_cursor = db.execute("SELECT id, title, start, [end] FROM events")
    events = [dict(row) for row in events_cursor.fetchall()]
    return jsonify(events)

@app.route('/api/events', methods=['POST'])
def create_event():
    """FullCalendarから送られた新しい予定をDBに保存"""
    data = request.get_json()
    
    # バリデーション (簡易)
    if not data or 'title' not in data or 'start' not in data:
        return jsonify({"error": "Missing data"}), 400

    db = get_db()
    try:
        cursor = db.execute(
            "INSERT INTO events (title, start, [end]) VALUES (?, ?, ?)",
            (data['title'], data['start'], data.get('end')) # endは無くてもよい
        )
        db.commit()
        
        # 作成したイベントのIDを返す
        return jsonify({"id": cursor.lastrowid, "status": "success"}), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500

# ★★★ 新しく追加した削除API ★★★
@app.route('/api/events/<int:id>', methods=['DELETE'])
def delete_event(id):
    """指定されたIDの予定をDBから削除"""
    db = get_db()
    try:
        db.execute("DELETE FROM events WHERE id = ?", (id,))
        db.commit()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
# ★★★ ここまで ★★★


# --- サーバー起動 ---
if __name__ == '__main__':
    init_db()
    # 外部から直接アクセスさせず、Apache経由のみにする
    app.run(host='127.0.0.1', port=8001, debug=True)
    