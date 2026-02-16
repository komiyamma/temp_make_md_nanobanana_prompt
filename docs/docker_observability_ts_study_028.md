# 第28章：Composeの起動順：healthyになってから次へ ⏳🔁

## ① 今日のゴール 🎯✨

この章が終わると、次ができるようになります👇😊

* 「DBが起動した **“だけ”** じゃダメで、**使える状態(healthy)** になってからAPIを起動」できる ✅
* Composeの `depends_on` を **条件付き（condition）** で書ける ✅（`service_started / service_healthy / service_completed_successfully`）([Docker Documentation][1])
* `healthcheck` をCompose側で設定して、**起動直後の“接続失敗ログ”を減らす** ✅([Docker Documentation][1])
* スクリプト/CIで便利な `docker compose up -d --wait` も使える ✅([Docker Documentation][2])

---

## ② 図（1枚）🖼️🧠

DBは「起動中…」の時間があるので、そこを待つのがポイントです👇

```text
[dbコンテナ]  起動 ▶ healthcheck合格(healthy) ▶ OK🙆
      │
      └──（ここを待てたら勝ち🥳）
             ▼
        [apiコンテナ] 起動 ▶ /ready が最初から通りやすい✨
```

Composeは基本、依存順に“起動はする”けど、**“ready(利用可能)”までは待たない**んでした。([Docker Documentation][1])
そこで **healthcheck + condition: service_healthy** を使います 💪😼([Docker Documentation][1])

---

## ③ 手を動かす（5〜10手順）🛠️🚀

ここでは「DB(Postgres) → API(Node/TS)」のよくある構成でやります😊
（ファイル名は `compose.yaml` でも `docker-compose.yml` でもOKです）

---

### Step 0️⃣：フォルダ構成（例）📁

```text
project/
  compose.yaml
  api/
    Dockerfile
    package.json
    src/
      index.ts
```

---

### Step 1️⃣：まず“ダメな起動順”を体験する 😇💥

**compose.yaml（ダメ版）**：depends_on はあるけど「healthy待ち」じゃない

```yaml
services:
  db:
    image: postgres:18
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: app
      POSTGRES_DB: app

  api:
    build: ./api
    environment:
      DATABASE_URL: postgres://app:app@db:5432/app
    depends_on:
      - db
    ports:
      - "3000:3000"
```

これで起動👇

```powershell
docker compose up --build
```

起動直後、APIがDBに接続しようとして **「接続できない！」ログ** が出ることがあります😵‍💫
（Composeは“コンテナが起動して動いてる”ところまでで、DBが接続受付できるかは待たないため）([Docker Documentation][1])

---

### Step 2️⃣：DBに healthcheck を付ける 💚🩺

次はDB側に `healthcheck` を付けます。Composeの `healthcheck` は DockerfileのHEALTHCHECKと同様の仕組みで、Compose側で値を上書きもできます。([Docker Documentation][3])

**compose.yaml（改善①：dbにhealthcheck追加）**

```yaml
services:
  db:
    image: postgres:18
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: app
      POSTGRES_DB: app
    healthcheck:
      # Postgres公式イメージに入ってる pg_isready を使う定番パターン👍
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB} -h localhost"]
      interval: 5s
      timeout: 3s
      retries: 20
      start_period: 10s
      # start_interval は Docker Compose v2.20.2 で導入（起動直後のチェック間隔を短くしたい時に便利）:contentReference[oaicite:7]{index=7}
      start_interval: 2s

  api:
    build: ./api
    environment:
      DATABASE_URL: postgres://app:app@db:5432/app
    depends_on:
      - db
    ports:
      - "3000:3000"
```

💡ポイント：`$${POSTGRES_USER}` みたいに `$` を2個にしてるのは、Composeの変数展開とぶつからないようにするためです（これ、超つまづきポイント😇🪤）

---

### Step 3️⃣：depends_on を“条件付き”にする ⏳✅

ここが本命です🔥
`depends_on` の **long syntax** を使って、`condition: service_healthy` を指定します。([Docker Documentation][3])

**compose.yaml（改善②：healthyになるまでAPIを待つ）**

```yaml
services:
  db:
    image: postgres:18
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: app
      POSTGRES_DB: app
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB} -h localhost"]
      interval: 5s
      timeout: 3s
      retries: 20
      start_period: 10s
      start_interval: 2s

  api:
    build: ./api
    environment:
      DATABASE_URL: postgres://app:app@db:5432/app
    depends_on:
      db:
        condition: service_healthy
        # restart: true は「Compose操作による依存サービスの更新時に、依存先が更新されたらこのサービスも再起動」:contentReference[oaicite:9]{index=9}
        restart: true
    ports:
      - "3000:3000"
```

✅これで、Composeは **dbがhealthyになるまで apiを開始しない** という挙動になります。([Docker Documentation][3])

---

### Step 4️⃣：動作確認コマンド 👀🧾

起動👇

```powershell
docker compose up --build
```

別ターミナルで状態確認👇

```powershell
docker compose ps
```

見たいポイントはここ👇😆

* db の STATUS に **healthy** が付く（時間差で付く）
* その後に api が起動してくる（“接続失敗ログ”が減る）✨

---

### Step 5️⃣：スクリプト/CIでさらに便利にする（おまけ）🤖🏗️

`docker compose up -d --wait` は、**サービスが running / healthy になるまで待ってから** コマンドが返ります（しかも detached を暗黙で使います）。([Docker Documentation][2])

```powershell
docker compose up -d --wait --wait-timeout 120
```

⚠️注意：`docker compose wait` は “起動待ち” じゃなくて、**コンテナが停止するまで待つ**コマンドです。名前が紛らわしい〜🤣🪤([Docker Documentation][4])

---

## ④ つまづきポイント（3つ）🪤😵‍💫

1. **depends_on だけで“ready待ち”できると思っちゃう**
   → 起動順にはなるけど、**ready(利用可能)は待たない**のが基本です。([Docker Documentation][1])
   → 対策：`condition: service_healthy` を使う ✅([Docker Documentation][1])

2. **healthcheck が失敗し続けて “unhealthy沼”** 😇
   → `start_period` を増やす / `retries` を増やす / `timeout` を伸ばす、が効きます。`healthcheck` の各項目はComposeの正式オプションです。([Docker Documentation][3])

3. **`$${POSTGRES_USER}` を `$POSTGRES_USER` にして死ぬ** 💀
   → Composeの変数展開と混ざって、意図通りに実行されないことがあります。
   → 対策：コンテナ内の環境変数を参照したいときは `$` をエスケープする癖をつける 🙆‍♂️

---

## ⑤ ミニ課題（15分）⏳🎮

**課題A（やさしめ）**：わざとDBの起動を遅くして、待ててるか観察👀

* `start_period` を 1s にしてみる（失敗しがち）→ 20s に戻す（成功しやすい）
* `docker compose ps` の STATUS がどう変わるかメモ📝

**課題B（ちょい実戦）**：initコンテナ（DBマイグレーション）を挟む🧪
`service_completed_successfully` を使って「マイグレーション完了後にAPI起動」にしてみよう✨([Docker Documentation][1])

（例イメージ）

```yaml
depends_on:
  migrate:
    condition: service_completed_successfully
```

---

## ⑥ AIに投げるプロンプト例（コピペOK）🤖📋✨

**プロンプト1：healthcheck をいい感じに作る**

```text
Docker Compose の db(Postgres) に healthcheck を付けたい。
pg_isready を使って、起動が遅い環境でも安定する interval/timeout/retries/start_period のおすすめ値を提案して。
compose.yaml の該当部分だけ YAML で出して。
```

**プロンプト2：depends_on の設計をチェックしてもらう**

```text
この compose.yaml の depends_on 設計は妥当？
「起動直後の接続失敗ログを減らしたい」という目的に対して改善案があれば教えて。
（condition の種類も含めて）
```

---

次の章（第29章）は、ログ🧾→メトリクス📈→ヘルス💚 を “一本の型” にまとめて、障害対応の手順をテンプレ化していきますよ〜🔥🕵️‍♂️🧯

[1]: https://docs.docker.com/compose/how-tos/startup-order/ "Control startup order | Docker Docs"
[2]: https://docs.docker.com/reference/cli/docker/compose/up/ "docker compose up | Docker Docs"
[3]: https://docs.docker.com/reference/compose-file/services/ "Services | Docker Docs"
[4]: https://docs.docker.com/reference/cli/docker/compose/wait/ "docker compose wait | Docker Docs"
