# 第27章：Compose networks：内部ネットワークで閉じ込める🕸️🔒

この章は「**同じマシン上に“部屋”を作って、通していい通信だけ通す**」がゴールです😊
Docker Compose のネットワークは、ざっくり言うと **コンテナ同士が話せる“グループ”**。ここを分けると、被害半径が一気に小さくなります🛡️✨

---

## この章でできるようになること✅

* 「公開していい入口」だけを外に出す🚪🌐
* DB/Redis みたいな中身は **内部ネットワークに閉じ込める**🍱🔐
* 「AはBに話していいけど、Cには話させない」を Compose で表現できる🧩
* “うっかり全部つながってた事故”をネットワーク設計で防げる😇💥

---

## まず超重要な3点だけ🧠✨

## 1) Compose はデフォで「全部つながる」😺

![Network Rooms](./picture/docker_safe_isolation_ts_study_027_01_network_rooms.png)

Compose は、何も書かないと **アプリ用のネットワークを1つ作って**、各サービスをそこに参加させます。
だからサービス同士は基本「届く」し、**サービス名で名前解決**できます📡✨ ([Docker Documentation][1])

> つまり…
> `api` から `db` に `db:5432` で繋がっちゃう、が標準状態です（便利だけど、隔離としては雑になりやすい）😅

---

## 2) 「ports」は“外へのドア”、ネットワークは“部屋の中の通路”🚪🕸️

![Ports vs Network](./picture/docker_safe_isolation_ts_study_027_02_ports_vs_network.png)

* **ネットワーク**：コンテナ同士が話すための通路
* **ports**：ホスト（＝あなたのPC）や外部から入るためのドア

`ports` はホスト⇄コンテナのポート対応を作ります。何も指定しないと **0.0.0.0（全IF）にバインド**しがちなので要注意⚠️ ([Docker Documentation][2])
さらに Docker 側も「ポート公開はデフォだと危険寄り」ってハッキリ言ってます😱 ([Docker Documentation][3])

👉 コツ：開発中は `127.0.0.1:` を付けて **自分のPCだけ**に限定しよう🧯✨ ([Docker Documentation][3])

---

## 3) 「internal: true」で“外部と切れたネットワーク”が作れる🔒

![Internal True Isolation](./picture/docker_safe_isolation_ts_study_027_03_internal_true.png)

Compose は通常、ネットワークに外部接続性を持たせます。
`internal: true` にすると **externally isolated network（外部から隔離されたネットワーク）** を作れます🧊 ([Docker Documentation][4])

「DBは外に出なくていい」「勝手に外へ通信してほしくない」みたいな層に刺さります🎯

---

## ネットワーク設計の型：3層に分ける🍰✨

![Three Layer Network Design](./picture/docker_safe_isolation_ts_study_027_04_three_layers.png)

ここからは“よくある個人開発の型”でいきます👇

* **edge**：外（ホスト）に公開する“入口”だけ
* **app_net**：入口 ⇄ アプリの通路
* **data_net**：アプリ ⇄ DB/Redis の通路（ここを `internal: true` で閉じる）🔒

そして大事なのがこれ👇
**同じネットワークを共有してないサービス同士は、基本的に会話できない**（＝壁ができる）🧱✨
Docker Docs でも「proxy は db とネットワークを共有しないから隔離される」例が出ています。 ([Docker Documentation][4])

---

## ハンズオン：閉じ込めネットワークを作って“壁”を体感しよう🧪🧱

## 0) 構成イメージ🗺️

![Hands-on Network Map](./picture/docker_safe_isolation_ts_study_027_05_handson_map.png)

* ブラウザ → `proxy`（入口）
* `proxy` → `api`（中）
* `api` → `redis`（奥）
* `proxy` は `redis` に届かない（壁！）🧱

---

## 1) `compose.yaml` を作る📝

プロジェクト直下に `compose.yaml` を作って、これをコピペ👇

```yaml
services:
  proxy:
    image: nginx:alpine
    ports:
      - "127.0.0.1:8080:80"
    volumes:
      - ./proxy/nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - api
    networks:
      - edge
      - app_net

  api:
    image: traefik/whoami:latest
    networks:
      - app_net
      - data_net

  redis:
    image: redis:alpine
    networks:
      - data_net

  # デバッグ用（必要な時だけ起動して疎通チェックする）
  debug_app:
    image: curlimages/curl:latest
    command: ["sleep", "infinity"]
    networks:
      - app_net
    profiles: ["debug"]

  debug_data:
    image: curlimages/curl:latest
    command: ["sleep", "infinity"]
    networks:
      - data_net
    profiles: ["debug"]

networks:
  edge: {}
  app_net: {}
  data_net:
    internal: true
```

ポイント💡

* `proxy` だけ `ports` を持つ（入口だけ外へ）🚪
* `redis` は `ports` なし（ホストから直接入れない）🙅‍♂️
* `proxy` は `data_net` に入れてない（DB層に壁）🧱
* `data_net` は `internal: true` で“外部隔離”🔒 ([Docker Documentation][4])
* 追加ネットワークは「サービス側で許可しないと繋がらない」ルール🧩 ([Docker Documentation][4])

---

## 2) `proxy/nginx.conf` を作る🧷

`proxy` フォルダを作って、その中に `nginx.conf` を作成👇

```nginx
server {
  listen 80;

  location / {
    proxy_pass http://api:80;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  }
}
```

ここで `api` って書けるのが Compose の気持ちよさです😆
同じネットワーク上だと **サービス名で発見可能**だから！ ([Docker Documentation][1])

---

## 3) 起動してみる▶️

```powershell
docker compose up -d
docker compose ps
```

---

## 4) 動作確認👀✨

ブラウザ or curl で👇

```powershell
curl http://127.0.0.1:8080/
```

`whoami` の情報が返ってきたらOK🎉（proxy→api ルートが通ってる）

---

## “壁”を確認するデバッグ実験🧱🧪

![Debugging the Wall](./picture/docker_safe_isolation_ts_study_027_06_debug_wall.png)

## 実験A：`app_net` から `redis` を見ようとして失敗する（壁がある）❌

デバッグ用コンテナを起動して中へ👇

```powershell
docker compose --profile debug up -d debug_app
docker compose exec debug_app sh
```

中で `redis` を引いてみる👇

```sh
## DNS解決できない or 接続できない（proxy層と同じで data_net にいないから）
curl -v redis:6379
```

**「同じネットワークを共有してないと届かない」**を体感できたら勝ちです🏆
この“共有してないから隔離される”考え方が核です🔥 ([Docker Documentation][4])

---

## 実験B：`data_net` 側なら `redis` が見える✅

```powershell
docker compose --profile debug up -d debug_data
docker compose exec debug_data sh
```

```sh
## こっちは data_net にいるので redis に届く（疎通そのものは確認できる）
curl -v redis:6379
```

Redis はHTTPじゃないのでレスポンスは期待どおりじゃないけど、**接続はできる**はずです👍
「見える/見えないの境界」がネットワークで決まるのが大事✨

> もっと気持ちよく確認したい人へ😎
> `redis-cli` が入ったイメージ（公式の `redis` など）を“デバッグ専用”で使うのもアリ！

---

## 超よくある事故パターン3つ😇💣（ここだけ覚えて）

## 事故1：DBに `ports` を付けちゃう🫠

「とりあえず繋がらないから `6379:6379` で出しちゃえ！」
→ これ、**最小公開**の真逆です😱

`ports` は外へのドア。必要な入口以外はドアを付けない🚪✂️
（`ports` はホスト側に公開するための機能）([Docker Documentation][2])

---

## 事故2：全部同じネットワークに入れちゃう🙈

![One Network Accident](./picture/docker_safe_isolation_ts_study_027_07_accident_one_net.png)

便利なんだけど、隔離が消えます。
“壁”が欲しいところは **ネットワークを分けて、共有しない**が基本🧱✨ ([Docker Documentation][4])

---

## 事故3：`ports` を 0.0.0.0 で全開放しちゃう🌐😱

`ports` のホストIPを省略すると全IFにバインドされることがあるので注意⚠️ ([Docker Documentation][2])
開発中はこう👇（自分のPCだけに限定）

```yaml
ports:
  - "127.0.0.1:8080:80"
```

「localhost を付けるとホストだけアクセス可能」という注意喚起も公式にあります🧯 ([Docker Documentation][3])

---

## AI拡張を使うときの“ネットワーク視点”の安全ルール🤖🛡️

AIが提案してきた Compose 差分を見たら、まずここだけチェック✅

* `ports:` が増えてない？（特に DB/Redis に付いてない？）🚪⚠️
* 追加した `networks:` が“全部同じ”になってない？🕸️💥
* `internal: true` を外してない？🔒😱
* 「とりあえず privileged」「とりあえず docker.sock」みたいな“危険カード”が混ざってない？🗑️🔥

AIは速いけど、**隔離の設計判断は人間の役目**にすると事故が減ります🙂✨

---

## 仕上げ：この章のチェックリスト✅🕔

* 外に出すのは入口だけ（基本は `proxy`/`web` だけ）🚪
* DB/Redis は `ports` なし（内部ネットワークに閉じ込め）🍱
* “話していい組”だけ同じネットワークに入れる🧱
* データ層は `internal: true` を検討🔒 ([Docker Documentation][4])
* ネットワーク名やサービス名で繋ぐ（同一ネットワーク上で発見可能）📛📡 ([Docker Documentation][1])

---

次は第28章で、この“境界”をさらに強くして **DB/Redis を内部専用に固定**しつつ、「開発用/テスト用の分離」もやっていきます🧪🔐✨

[1]: https://docs.docker.com/compose/how-tos/networking/?utm_source=chatgpt.com "Networking in Compose"
[2]: https://docs.docker.com/reference/compose-file/services/ "Services | Docker Docs"
[3]: https://docs.docker.com/engine/network/port-publishing/?utm_source=chatgpt.com "Port publishing and mapping"
[4]: https://docs.docker.com/reference/compose-file/networks/ "Networks | Docker Docs"
