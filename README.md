# Flask & FullCalendar Webカレンダー

これは、シンプルなWebベースのカレンダーアプリケーションです。バックエンドは **Flask** と **SQLite** を使用したREST APIで構築されており、フロントエンドは **FullCalendar (v6)** を使用してインタラクティブなUIを提供します。

## 概要

このプロジェクトは、FullCalendarライブラリをFlaskバックエンドと連携させる方法を示すデモです。ユーザーはカレンダー上で日付を選択して予定を作成したり、既存の予定をクリックして削除したりできます。すべてのデータはサーバーサイドのSQLiteデータベース (`calendar.db`) に保存されます。

## 主な機能

  * **イベントの表示:** 月・週・日ビューでデータベースから取得した予定を表示します。
  * **イベントの作成:**
      * カレンダーの日付をクリックまたはドラッグして、新しい予定を作成します。
      * 月ビューで単一日を選択すると、開始時間（例: `14:30`）の入力を求められ、時間指定の予定を作成できます。
      * 時間を省略すると、終日予定として登録されます。
  * **イベントの削除:**
      * カレンダー上の既存の予定をクリックすると、確認ダイアログが表示されます。
      * 「OK」を押すと、API経由でデータベースからイベントが削除されます。
  * **永続化:** 作成・削除された予定は、サーバー上のSQLiteデータベースに即座に反映されます。

## 使用技術

  * **バックエンド:**
      * Python 3
      * Flask (Webフレームワーク/API)
      * SQLite3 (データベース)
  * **フロントエンド:**
      * HTML5
      * JavaScript
      * FullCalendar v6 (CDN経由)

## 実行方法

このアプリケーションは、FlaskサーバーがAPIと`index.html`の両方を提供するシンプルな構成で動作します。

### 1\. 依存関係のインストール

Flaskライブラリをインストールする必要があります。

```bash
# (推奨) 仮想環境の作成・有効化
# python -m venv venv
# source venv/bin/activate  (macOS/Linux)
# venv\Scripts\activate   (Windows)

pip install flask
```

### 2\. (重要) APIパスの修正

このプロジェクトを `python calendar-app.py` で直接実行して `http://127.0.0.1:8001/` でアクセスする場合、`index.html` がリクエストするAPIパスを修正する必要があります。

**`index.html` を開き、以下の3箇所を変更してください:**

1.  **読み込み:**

      * 変更前: `events: '/calendar/api/events',`
      * 変更後: `events: '/api/events',`

2.  **作成 (POST):**

      * 変更前: `fetch('/calendar/api/events', {`
      * 変更後: `fetch('/api/events', {`

3.  **削除 (DELETE):**

      * 変更前: `fetch('/calendar/api/events/' + clickInfo.event.id, {`
      * 変更後: `fetch('/api/events/' + clickInfo.event.id, {`

### 3\. サーバーの起動

パスを修正したら、Pythonスクリプトを実行してサーバーを起動します。

```bash
python calendar-app.py
```

`calendar.db` ファイルが（存在しない場合）自動的に作成され、コンソールに以下のように表示されます。

```
 * Serving Flask app 'calendar-app'
 * Debug mode: on
Database initialized.
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:8001
Press CTRL+C to quit
```

### 4\. アプリケーションへのアクセス

ブラウザで `http://127.0.0.1:8001/` を開くと、カレンダーが表示されます。

-----

## (オプション) リバースプロキシ経由での実行

`calendar-app.py` のコメントや `index.html` の元のパス (`/calendar/api/...`) が示唆するように、このアプリケーションはApacheやNginxなどのリバースプロキシの背後で実行することも想定されています。

その場合、`index.html` のパス修正は不要ですが、代わりにリバースプロキシ側で以下の設定が必要になります。

1.  `python calendar-app.py` を `127.0.0.1:8001` で実行します。
2.  `index.html` をWebサーバーのドキュメントルート（例: `/var/www/html/`）に配置します。
3.  リバースプロキシで、`/calendar/api/` へのリクエストを `http://127.0.0.1:8001/api/` に転送（プロキシ）するように設定します。

## APIエンドポイント (Flask)

`calendar-app.py` は以下のAPIエンドポイントを提供します。

  * `GET /api/events`
      * すべてのカレンダーイベントをJSON形式で返します。
  * `POST /api/events`
      * JSONボディ ( `{ "title": "...", "start": "...", "end": "..." }` ) を受け取り、新しいイベントをDBに作成します。
      * 成功すると、作成されたイベントの `id` を返します。
  * `DELETE /api/events/<int:id>`
      * 指定されたIDのイベントをDBから削除します。
  * `GET /`
      * `index.html` をレンダリングして返します。
