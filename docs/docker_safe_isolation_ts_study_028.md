# 第28章：サービス間の境界：DB/Redisを“内部専用”に固定する🍱🔐

## 28.1 この章でできるようになること🎯

![Zone Design](./picture/docker_safe_isolation_ts_study_028_01_zone_design.png)

* DB/Redisを **ホスト（Windows）や外部ネットから触れない** 状態にする🙅‍♂️🌐
* 「Webは公開OK / DBは内部だけ」みたいな **境界線（ゾーン）設計** ができる🗺️
* それでも必要になる「DBを覗く作業」を **安全にやる逃げ道** を持てる🧰✨

---

## 28.2 まず結論：やることは3つだけ✅✅✅

![Three Actions for Safety](./picture/docker_safe_isolation_ts_study_028_02_three_actions.png)

1. **DB/Redisに `ports:` を書かない**
   → `ports` は “ホストに穴を開ける” 行為。DB/Redisは穴を開けないのが基本🕳️🚫
   （Composeの基本ネットワーク上では、サービス同士は名前で到達できます）([Docker Documentation][1])

2. **ネットワークを分けて「話せる相手」を限定する**

* `public`（外に出る入口：Web/API）
* `private`（内側：DB/Redis）
  さらに `private` を `internal: true` にすると、**外部に出られないネットワーク**にできます（DBが勝手に外へ通信しない）([Docker Documentation][2])

3. **“どうしてもDBを触りたい”時の手段を決めておく**

* `docker compose exec` で中に入って操作（最優先）🧑‍🔧
* デバッグ用サービスを **profile** で必要なときだけ起動（安全＆便利）([Docker Documentation][3])
* 一時的に `127.0.0.1` バインドでだけ公開（最終手段）🏁
  ※ホストIP指定なしだと全IFにバインドされ得るので注意（短い構文の仕様）([Docker ドキュメント][4])

---

## 28.3 イメージ図：入口（public）と裏側（private）を分ける🚪🍱

![Architecture Map](./picture/docker_safe_isolation_ts_study_028_03_architecture_map.png)

* 👀 外から来るのは **Web/API** まで
* 🔒 **DB/Redisは private だけ**（publicに繋がない・portsも開けない）

```
[Internet] → (public) → web / api  → (private) → db / redis
                        ↑ここまで公開OK       ↑ここは内部だけ
```

---

## 28.4 ハンズオン：API + DB + Redis を「内側専用」にする🛠️🔥

![Hands-on Setup](./picture/docker_safe_isolation_ts_study_028_04_handson_setup.png)

ここでは例として

* `web`（外部公開）
* `api`（内部でDB/Redisに接続）
* `db` / `redis`（内部専用）
  にします🍱

### 28.4.1 compose.yaml（境界線入りのテンプレ）📦

ポイントはこれ👇

* `db` と `redis` は **portsなし**
* `db` と `redis` は **private のみ参加**
* `private` を `internal: true` にして **外部へ出られない** ようにする（より堅牢）([Docker Documentation][2])

```yaml
services:
  web:
    image: nginx:alpine
    ports:
      - "8080:80"   # 入口はここだけ
    depends_on:
      - api
    networks:
      - public

  api:
    image: node:alpine
    working_dir: /app
    volumes:
      - ./api:/app:ro
    command: ["node", "server.mjs"]
    environment:
      DATABASE_URL: postgres://app:app@db:5432/appdb
      REDIS_URL: redis://redis:6379
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    networks:
      - public
      - private

  db:
    image: postgres:alpine
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: app
      POSTGRES_DB: appdb
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d appdb"]
      interval: 5s
      timeout: 3s
      retries: 10
    volumes:
      - pgdata:/var/lib/postgresql/data
    networks:
      - private
    # ports: ←書かない！(内部専用)

  redis:
    image: redis:alpine
    networks:
      - private
    # ports: ←書かない！(内部専用)

networks:
  public: {}
  private:
    internal: true  # 外部に出られないネットワーク（より安全）

volumes:
  pgdata: {}
```

* `depends_on` と `healthcheck` で起動順・起動待ちを扱うのが現代Composeの定番です([Docker Documentation][5])
* そもそもComposeはプロジェクトごとにネットワークを作り、同じネット内のサービスは **サービス名で到達** できます([Docker Documentation][1])

### 28.4.2 APIの超ミニ実装（疎通確認用）🧪

`api/server.mjs`（最小の「DB/Redisに触れた」証拠を返すだけ）

```js
import http from "node:http";
import { Client } from "pg";
import { createClient } from "redis";

const port = 3000;

async function checkDb() {
  const client = new Client({ connectionString: process.env.DATABASE_URL });
  await client.connect();
  const r = await client.query("select now() as now");
  await client.end();
  return r.rows[0].now;
}

async function checkRedis() {
  const redis = createClient({ url: process.env.REDIS_URL });
  await redis.connect();
  await redis.set("ping", "pong");
  const v = await redis.get("ping");
  await redis.disconnect();
  return v;
}

http.createServer(async (req, res) => {
  try {
    const now = await checkDb();
    const ping = await checkRedis();
    res.writeHead(200, { "content-type": "application/json" });
    res.end(JSON.stringify({ ok: true, db_now: now, redis: ping }));
  } catch (e) {
    res.writeHead(500, { "content-type": "application/json" });
    res.end(JSON.stringify({ ok: false, error: String(e) }));
  }
}).listen(port, "0.0.0.0", () => {
  console.log(`api listening on ${port}`);
});
```

> ※この例は“教材用の最短”です。実務では secrets や read-only、依存の固定などと組み合わせていきます🔒✨

### 28.4.3 起動して確認（Windows / PowerShell）🪟⚡

```powershell
docker compose up -d --build
docker compose ps
```

**(A) Webだけ見える** ✅

* ブラウザで `http://localhost:8080`（nginxが出ればOK）

**(B) DBはホストから見えない** ✅
（DBに ports を開けてないので、ホスト側からの 5432 は失敗するはず）

```powershell
Test-NetConnection 127.0.0.1 -Port 5432
Test-NetConnection 127.0.0.1 -Port 6379
```

**(C) でも api からは DB/Redis が見える** ✅
（同じ private ネットワーク上だから）

```powershell
docker compose exec api node -e "fetch('http://localhost:3000').catch(console.error)"
```

---

## 28.5 「DBを覗きたい…」デバッグの安全な逃げ道3選🧰🧡

![Escape Routes](./picture/docker_safe_isolation_ts_study_028_05_escape_routes.png)

### 逃げ道1：`exec` で中から触る（基本これ）🧑‍🔧✨

```powershell
docker compose exec db psql -U app -d appdb
docker compose exec redis redis-cli ping
```

* ✅ “穴を開けない” ので安全
* ✅ チーム開発でも事故りにくい

### 逃げ道2：デバッグ用ツールは **profiles** で必要時だけ起動🧪🎛️

![Profile Switch](./picture/docker_safe_isolation_ts_study_028_06_profile_switch.png)

例：`adminer` や `pgadmin` を “普段は起動しない” にする。profilesの公式解説はこちら([Docker Documentation][3])

```yaml
services:
  pgadmin:
    image: dpage/pgadmin4
    profiles: ["debug"]
    environment:
      PGADMIN_DEFAULT_EMAIL: a@b.c
      PGADMIN_DEFAULT_PASSWORD: pass
    ports:
      - "127.0.0.1:5050:80"
    networks:
      - private
```

起動するときだけ👇

```powershell
docker compose --profile debug up -d
```

* ✅ “必要なときだけ危険を増やす” ができる
* ✅ 使い終わったら `--profile debug` をやめれば元に戻る

### 逃げ道3：最終手段＝**127.0.0.1 限定で一時公開** 🧨➡️🧯

どうしてもホストのGUIツールから直に繋ぎたいときだけ。

* IPを付けないと全IFバインドの可能性があるので注意（仕様）([Docker ドキュメント][4])
* Docker自体にもポート公開の考え方の説明があります([Docker Documentation][6])

例（短い構文でもOK）：

```yaml
ports:
  - "127.0.0.1:5432:5432"
```

💡 ルール：

* “デバッグ中だけ” つける
* PRに入れない / main に入れない
* 終わったら即消す 🗑️

---

## 28.6 ありがちな事故パターン（そして直し方）😇💥

![Accident Patterns](./picture/docker_safe_isolation_ts_study_028_07_accident_patterns.png)

### 事故1：DBに `ports: "5432:5432"` を書いてしまった🫠

**症状**：ローカルPCの外部（同一LANなど）からも触れ得る
**修正**：DB/Redisは ports を消す。必要なら “127.0.0.1 限定＆一時” にする🧯

### 事故2：全部同じネットワークで、frontend からもDBが見える😱

**修正**：`public` と `private` に分離。DB/Redisは private のみ。
Composeは同ネットワーク上で名前解決できるので、分離が効きます([Docker Documentation][1])

### 事故3：`internal: true` を付けたら、なんか動かない😭

`internal: true` は “外部に出られないネットワーク” なので、
そのネットワーク上のコンテナが **外部DNS/外部API** に行こうとしてると詰みます（仕様として外部接続を遮断）([Docker Documentation][2])
**対処**：

* DB/Redisだけ internal に入れる（今回の形）
* 外に出る必要があるのは public 側に置く

---

## 28.7 AI拡張（Copilot/Codex等）を使うときの“安全チェック”🤖🔍

AIに compose を書かせると、わりと高確率で **DBに ports を開けがち** です😂🕳️
なので、生成物はこの順でチェック✅

1. `db` `redis` に `ports:` が無い？（無いのが正解）
2. `db` `redis` が `private` だけに繋がってる？
3. `public` に繋がっていいのは入口（web/api）だけ？
4. デバッグ用ツールは profiles に閉じ込めた？([Docker Documentation][3])

---

## 28.8 ミニ演習（手を動かすやつ）🏋️‍♂️✨

**演習A：わざと事故らせて直す**😈🔧

1. db に `ports: "5432:5432"` を追加
2. `Test-NetConnection 127.0.0.1 -Port 5432` が成功するのを確認
3. ports を消して、失敗に戻す（“穴を塞ぐ”）🧯

**演習B：デバッグ用GUIを profiles に閉じ込める**🧪

1. `pgadmin` サービスを追加して `profiles: ["debug"]` を付ける
2. 普段は起動しないことを確認
3. `docker compose --profile debug up -d` で起動して触る
4. 終わったら profile を無効に戻す🧹

---

## 28.9 まとめ（第28章の“合言葉”）🎉

* **DB/Redisは ports を開けない**（内部専用が基本）🍱🔐
* **ネットワーク分離**で「話せる相手」を設計する🕸️
* **覗きたい時の逃げ道**は `exec` → `profiles` → “127.0.0.1一時公開” の順🧰✨

---

次の第29章（AI拡張の被害半径）に行く前に、もし希望があれば👇

* 「web/api/db/redis の4つを題材に、**public/privateの2段＋debug profile** まで込みの“完成テンプレ”」
* 「DBを MySQL に変えた版 / Redisを Valkey にした版」
  みたいな派生も作れます😊🔥

[1]: https://docs.docker.com/compose/how-tos/networking/?utm_source=chatgpt.com "Networking in Compose"
[2]: https://docs.docker.com/reference/compose-file/networks/?utm_source=chatgpt.com "Networks | Docker Docs"
[3]: https://docs.docker.com/compose/how-tos/profiles/?utm_source=chatgpt.com "Use service profiles"
[4]: https://docs.docker.jp/compose/compose-file/?utm_source=chatgpt.com "Compose Specification（仕様） - Docker ドキュメント"
[5]: https://docs.docker.com/compose/how-tos/startup-order/?utm_source=chatgpt.com "Control startup order - Docker Compose"
[6]: https://docs.docker.com/get-started/docker-concepts/running-containers/publishing-ports/?utm_source=chatgpt.com "Publishing and exposing ports"
