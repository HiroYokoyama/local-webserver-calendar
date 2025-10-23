# Flask Calendar Application

このリポジトリは、Flask (`calendar-app.py`) と FullCalendar (`index.html`) を使ったシンプルなWebカレンダーアプリケーションです。

このアプリケーションを **Gunicorn** と **Apache2 (リバースプロキシ)** を使って本番環境で動作させるための設定ファイルは以下の通りです。

## 1\. `calendar.service` (systemd サービスファイル)

Gunicorn (Flaskアプリ) をバックグラウンドで永続的に実行するため、`systemd` サービスとして登録します。

**配置場所:** `/etc/systemd/system/calendar.service`

**内容:**
(ファイルの `User`, `Group`, `WorkingDirectory`, `ExecStart` のパスは、ご自身の環境に合わせて修正してください。)

```ini
[Unit]
Description=Calendar Flask App (Gunicorn)
After=network.target

[Service]
# 1. 実行ユーザーとグループ (例: www-data, ubuntu, or your_username)
User=user
Group=user

# 2. アプリケーションのディレクトリ (app.py と calendar.db がある場所)
WorkingDirectory=/var/www/html/calendar-script/

# 3. 実行コマンド (Gunicornを起動)
#    - /path/to/.../venv/bin/gunicorn : 仮想環境内のgunicornのフルパス
#    - --workers 4 : 適宜調整 (CPUコア数x2+1程度が目安)
#    - --bind 127.0.0.1:8001 : app.py内の指定と合わせる
#    - app:app : (ファイル名 app.py の中の、Flaskインスタンス app を起動)
ExecStart=/home/user/miniconda3/bin/gunicorn --workers 4 --bind 127.0.0.1:8001 calendar-app:app

Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

**有効化コマンド:**

```bash
# ファイルを配置した後
sudo systemctl daemon-reload
sudo systemctl enable calendar.service
sudo systemctl start calendar.service
```

## 2\. `000-default.conf` (Apache2 バーチャルホスト設定)

Apache2 をリバースプロキシとして設定し、`/calendar` へのアクセスをGunicornが待機している `127.0.0.1:8001` (内部ポート) に転送します。

**配置場所:** `/etc/apache2/sites-available/000-default.conf` (または他の有効なApache設定ファイル)

**内容:**
(既存の設定ファイルに `<Location /calendar>...</Location>` ブロックを追記します。)

```apache
<VirtualHost *:80>
	# ... (既存の ServerAdmin, DocumentRoot, ErrorLog, CustomLog 設定) ...

	ServerAdmin webmaster@localhost
	DocumentRoot /var/www/html

	ErrorLog ${APACHE_LOG_DIR}/error.log
	CustomLog ${APACHE_LOG_DIR}/access.log combined

	# ... (既存の他の設定) ...
</VirtualHost>

    # === カレンダーアプリ用の設定 (ここから) ===
    <Location /calendar>
        # /calendar 以下のリクエストを、gunicorn の / (ルート) に中継する
        ProxyPass http://127.0.0.1:8001/
        ProxyPassReverse http://127.0.0.1:8001/
    </Location>
    # === カレンダーアプリ用の設定 (ここまで) ===

</VirtualHost>
```

**Apacheモジュールの有効化と再起動:**

```bash
# 必要なプロキシモジュールを有効化
sudo a2enmod proxy
sudo a2enmod proxy_http

# 設定を反映するためにApacheを再起動
sudo systemctl restart apache2
```
