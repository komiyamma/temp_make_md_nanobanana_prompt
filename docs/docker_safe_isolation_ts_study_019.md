# 第19章：ボリューム権限（UID/GID）とDBデータの守り方🗃️🛡️

この章はひとことで言うと――
**「DBデータの“宝箱”を、権限ミスで壊さない💥＆消さない🧨」**ための回です😄✨

---

## 1) まず結論：DBデータは“基本 named volume”で守るのが最強💪🧱

Docker公式でも、**コンテナが生成・利用する永続データは volume を推奨**しています（ホストOS依存が減って、Dockerが管理できるから）([Docker Documentation][1])
Composeでも、**top-level `volumes` に named volume を定義して使い回す**のが王道です([Docker Documentation][2])

なので迷ったらこう👇

* ✅ **DBのデータ** → **named volume**（まずこれ）
* ⚠️ **bind mount（ホストのフォルダ直刺し）** → “必要な時だけ”＋“場所を選ぶ”

---

## 2) UID/GIDってなに？（超ざっくり）🪪👤

Linuxではファイルに「持ち主」がいて、持ち主は **UID（ユーザーID）/ GID（グループID）**で決まります👀
DBコンテナは、データフォルダに **書き込み**できないと起動できません（初期化で詰む）😇💥

つまり…

> **「コンテナ内のプロセスのUID/GID」と「データフォルダの所有者」がズレると死ぬ**
> これが“権限事故”の正体です🧯

---

## 3) Windows + Docker Desktopでハマりやすいポイント🪤🪟

bind mount で **Windows側のフォルダ（例: C:\〜）**をDBデータ置き場にすると、速度だけじゃなく権限・ファイルシステム特性でも事故りやすいです💣

Docker公式のWSLベストプラクティスでも、**bind mountするデータはLinuxファイルシステム側（WSL内）に置くのが推奨**されています([Docker Documentation][3])
MicrosoftのWSL公式ドキュメントも、**性能面ではWSL側のファイルシステムに置くのが速い**と明言しています([Microsoft Learn][4])

さらに、WindowsフォルダをMySQLのデータディレクトリにマウントして初期化で権限エラーになる例も報告されています（まさに“権限・FS差”で詰むパターン）([GitHub][5])

---

## 4) 「消していいデータ／ダメなデータ」仕分け🧠📦

ここ、設計初心者ほど“いきなり全部同じ場所”に置きがちです😂

## 絶対消しちゃダメ😱🧊

* DBの永続データ（例：Postgresのクラスタ、MySQLのdatadir）

## 消えても復元できる（けど面倒）😇

* 生成物キャッシュ、テンポラリ、ログ（※ただし監査ログは別）

👉 **DBデータは他と混ぜない**（巻き添え削除が起きるから）🧯✨

---

## 5) DB別：正しい“マウント先”を間違えない📌（ここ超重要）

## PostgreSQL：Postgres 18+ でマウント先が変わった⚠️

Docker公式（Docker Hubの説明）で、**PostgreSQL 18 以降は `PGDATA` がバージョン別になり、`VOLUME` も `/var/lib/postgresql` に変わった**と明記されています([Docker Hub][6])
さらに、**PostgreSQL 17 以下は `/var/lib/postgresql/data` にマウントしないと永続化がズレて匿名ボリュームに書かれてしまう**注意まで書かれています([Docker Hub][6])

> つまり、**“どこにマウントするか”をバージョンで変える必要がある**ってことです😵‍💫

## MySQL：データ保存は「Docker管理」か「ホスト側で権限を責任持つ」か

MySQL公式イメージも「データの保存方法は複数あるが、ホストにディレクトリを作ってマウントするなら **ディレクトリの存在・権限などをちゃんと面倒見てね**」と説明しています([Docker Hub][7])

---

## 6) 実践：Composeで“事故りにくい”DB永続化テンプレ📦✨

## A. Postgres 18+（おすすめ：まずこれ）🐘✅

* **named volume**
* **マウント先は `/var/lib/postgresql`**（18+の推奨）([Docker Hub][6])
* **イメージは major まで固定**（`postgres:18` みたいに）←これで勝手に18へ上がる事故を防ぐ🧯

```yaml
services:
  db:
    image: postgres:18
    restart: unless-stopped
    environment:
      POSTGRES_PASSWORD: example-password
      POSTGRES_DB: appdb
      POSTGRES_USER: appuser
    volumes:
      - pgdata:/var/lib/postgresql

volumes:
  pgdata:
```

## B. Postgres 17以下を使うなら🐘🧷

* **マウント先は `/var/lib/postgresql/data`**（17以下の重要注意）([Docker Hub][6])

```yaml
services:
  db:
    image: postgres:17
    restart: unless-stopped
    environment:
      POSTGRES_PASSWORD: example-password
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

## C. MySQL（基本は named volume でOK）🐬✅

```yaml
services:
  db:
    image: mysql:8.4
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: example-root
      MYSQL_DATABASE: appdb
      MYSQL_USER: appuser
      MYSQL_PASSWORD: example-pass
    volumes:
      - mysqldata:/var/lib/mysql

volumes:
  mysqldata:
```

---

## 7) “権限が合ってるか”をその場で確認する🔍👀

動いてるDBコンテナに入って、**データディレクトリの所有者（数字）**を見るのが早いです🏃‍♂️💨

例：Postgres（コンテナ名が `db` の場合）

```bash
docker compose exec db sh -lc "ls -ldn /var/lib/postgresql /var/lib/postgresql/* 2>/dev/null || true"
```

* `ls -ldn` は **UID/GIDを数字で表示**してくれます（名前解決に依存しない）👍

---

## 8) bind mountしたい場合の“安全なやり方”🧰🧷

「DBの実データをホスト側ツールで直接触りたい」みたいな理由で bind mount したくなる時、あります😅
その場合の鉄則👇

## ✅ 置き場所は “WSL内のLinuxファイルシステム”にする

Docker公式のWSLベストプラクティスがこの方針です([Docker Documentation][3])
（性能も安定性も良くなる）

## ✅ コンテナ内ユーザーのUID/GIDを“調べてから”合わせる

DBイメージによって微妙に違うことがあるので、決め打ちより「確認→合わせる」が安全です🧯

例：Postgresの `postgres` ユーザーのUID/GIDを確認

```bash
docker run --rm postgres:18 sh -lc "id -u postgres; id -g postgres"
```

出てきた数字が仮に `999` と `999` だったら、WSL側でフォルダを作って所有者を合わせる👇

```bash
mkdir -p ~/docker-data/postgres18
sudo chown -R 999:999 ~/docker-data/postgres18
```

---

## 9) “任意UIDで動かす”は最終手段（でも公式の逃げ道はある）🧪🧯

「自分のUIDでDBを動かしたい！」ってやると、**初期化の `initdb` が“そのUIDが /etc/passwd に存在しない”と失敗する**ケースがあります😇
Docker HubのPostgres公式説明でも、**数値UIDだけだと `initdb` がユーザーを引けず失敗する例**と、回避策（nss_wrapper / `/etc/passwd` のbind mount / 初期化とchown分離）が載っています([Docker Hub][6])

なのでこの章のおすすめ方針は👇

* ✅ まずは **公式のデフォルト運用（named volume）**
* ⚠️ どうしても必要になったら、公式の回避策を“そのまま”使う（自己流にしない）🧯

---

## 10) 演習（15分）⏱️📝

## 演習1：安全テンプレでDBを立てる🎮

1. 上の「Postgres 18+」Composeをコピペ
2. 起動👇

   ```bash
   docker compose up -d
   ```
3. データが volume に載ってるか確認👇

   ```bash
   docker volume ls
   docker volume inspect <ボリューム名>
   ```

## 演習2：うっかり消し事故を防ぐ🧨→🧯

* ✅ `docker compose down` は **ボリュームは消さない**
* ⚠️ `docker compose down -v` は **ボリュームを消す（＝DB全消し）** 😱

自分のチーム/自分ルールとして、**`-v` は封印コマンド**にしておくのが安全です🔒✨

---

## 11) AI拡張を使う人の“最重要チェック”🤖✅

GitHub Copilot や OpenAI 系のAIツールにComposeを書かせると、たまにこういう事故が混ざります😂

* 「Postgresのマウント先が古いまま」→ 18+で起動失敗/データ迷子
* 「image: postgres（バージョン固定なし）」→ いつの間にかメジャーが上がる
* 「bind mount を C:\… にしてる」→ 権限・FS差でハマる

AIの出力は、最低でもここだけ目視チェック👀✨

* ✅ **DBイメージは major 固定**
* ✅ **マウント先はそのDB/バージョンの推奨**（Postgres 18+は特に）([Docker Hub][6])
* ✅ **DBデータはまず named volume**([Docker Documentation][1])

---

## まとめ🎉

* DBデータは **named volume が基本**（最小事故ルート）([Docker Documentation][1])
* bind mount するなら **WSL内に置く**（公式推奨）([Docker Documentation][3])
* Postgresは **17以下と18+でマウント先が違う**のが超重要ポイント([Docker Hub][6])
* MySQLもホスト側に置くなら **権限は自分が責任持つ**([Docker Hub][7])

---

次の章（第20章）は「configs / env / files の整理術」だから、**“設定と秘密とただの値”を事故らず仕分ける🧰✨**流れで繋げるとめちゃ気持ちいいです😄

[1]: https://docs.docker.com/engine/storage/volumes/?utm_source=chatgpt.com "Volumes"
[2]: https://docs.docker.com/reference/compose-file/volumes/?utm_source=chatgpt.com "Define and manage volumes in Docker Compose"
[3]: https://docs.docker.com/desktop/features/wsl/best-practices/?utm_source=chatgpt.com "Best practices"
[4]: https://learn.microsoft.com/en-us/windows/wsl/filesystems?utm_source=chatgpt.com "Working across Windows and Linux file systems"
[5]: https://github.com/docker/for-win/issues/4824?utm_source=chatgpt.com "[WSL2] Permissions problem with mounted windows volume"
[6]: https://hub.docker.com/_/postgres "postgres - Official Image | Docker Hub"
[7]: https://hub.docker.com/_/mysql "mysql - Official Image | Docker Hub"
