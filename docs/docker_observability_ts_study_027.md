# 第27章：Dockerfile HEALTHCHECK：コンテナ自身に健康判定を持たせる 🧪📦

Dockerの「プロセスは動いてるけど、実はもう応答してない…😇」を見抜くための仕組みが **Dockerfile の `HEALTHCHECK`** です。
コンテナの中でコマンドを定期実行して、成功/失敗で **healthy / unhealthy** を付けます。([Docker Documentation][1])

---

## ① 今日のゴール 🎯✨

* `HEALTHCHECK` を Dockerfile に書ける ✍️
* `docker ps` で `(healthy)` / `(unhealthy)` を見てニヤッとできる 😎
* `docker inspect` で「なぜ失敗したか」を追える 🔎([Docker Documentation][1])

---

## ② 図（1枚）🖼️（脳内イメージでOK）

![Healthcheck Process](./picture/docker_observability_ts_study_027_01_healthcheck_process.png)

```text
Docker Engine
   │  (一定間隔で)
   ▼
[HEALTHCHECK コマンド]  ← コンテナ内で実行
   │
   ▼
http://127.0.0.1:3000/health  にアクセス
   │
   ├─ 200 OK → exit 0 → healthy ✅
   └─ 500 / タイムアウト / 例外 → exit 1 → unhealthy ❌
```

---

## ③ 手を動かす（手順 8つ）🛠️💨

以下は「第25章で `/health` がある」前提で進めます（もし無ければ、最後に最小の `/health` 例も置いておきます🧯）。

### 手順1：healthcheck 用スクリプトを作る 🧾

![Script Logic](./picture/docker_observability_ts_study_027_02_script_logic.png)

**`scripts/healthcheck.mjs`** を追加します。

```js
// scripts/healthcheck.mjs
const url = process.env.HEALTHCHECK_URL ?? "http://127.0.0.1:3000/health";

// healthcheck 自体にも timeout はあるけど、アプリ側でも短く失敗させると気持ちいい🙂
const timeoutMs = Number(process.env.HEALTHCHECK_TIMEOUT_MS ?? "2000");

const controller = new AbortController();
const t = setTimeout(() => controller.abort(), timeoutMs);

try {
  const res = await fetch(url, { signal: controller.signal });
  clearTimeout(t);

  // OKなら exit 0（healthy）
  if (res.ok) process.exit(0);

  // NGなら exit 1（unhealthy）
  console.error(`healthcheck failed: ${res.status} ${res.statusText}`);
  process.exit(1);
} catch (e) {
  clearTimeout(t);
  console.error(`healthcheck error: ${e?.message ?? e}`);
  process.exit(1);
}
```

ポイント：

* **exit code が命**：`0=healthy / 1=unhealthy / 2は予約で使うな` ([Docker Documentation][1])
* 出力（stdout/stderr）は `docker inspect` で見れる（ただし保存は最大4096 bytes）([Docker Documentation][1])

---

### 手順2：Dockerfile に `HEALTHCHECK` を足す 🧩

![Instruction Anatomy](./picture/docker_observability_ts_study_027_03_instruction_anatomy.png)

（例：Nodeの実行イメージに `scripts/` をコピーして使う）

```dockerfile
## --- runtime stage のイメージ例（あなたのDockerfileに合わせてOK） ---
## 例: FROM node:24-alpine
WORKDIR /app

## 既存：distやnode_modulesをコピーしてるはず
## COPY --from=build /app/dist ./dist
## COPY package*.json ./
## RUN npm ci --omit=dev

## ✅ 追加：healthcheck スクリプト
COPY scripts ./scripts

## ✅ 追加：Dockerfile HEALTHCHECK
HEALTHCHECK --interval=10s --timeout=3s --start-period=15s --retries=3 \
  CMD ["node", "/app/scripts/healthcheck.mjs"]

## 既存：起動コマンド
## CMD ["node", "/app/dist/server.js"]
```

`HEALTHCHECK` のオプション（超重要）👇

* `--interval`：何秒ごとにチェックするか（既定 30s）([Docker Documentation][1])
* `--timeout`：1回のチェックの制限時間（既定 30s / 超えたら失敗扱いで強制終了）([Docker Documentation][1])
* `--retries`：何回連続で失敗したら unhealthy にするか（既定 3）([Docker Documentation][1])
* `--start-period`：起動直後の猶予（この間の失敗はカウントしない）([Docker Documentation][1])
* `--start-interval`：**start-period 中だけ**チェック間隔を変える（Docker Engine 25.0+）([Docker Documentation][1])

また、Dockerfile内に書ける `HEALTHCHECK` は **1つだけ**で、複数書いたら最後だけ有効です。([Docker Documentation][1])

---

### 手順3：ビルド 🏗️

```bash
docker build -t obs-mini-api:hc .
```

---

### 手順4：起動 ▶️

```bash
docker run -d --name obs-api -p 3000:3000 obs-mini-api:hc
```

---

### 手順5：`docker ps` で health 表示を見る 👀✨

![Docker PS States](./picture/docker_observability_ts_study_027_04_docker_ps_states.png)

```bash
docker ps
```

期待する雰囲気（例）：

* 起動直後：`(health: starting)` 🐣
* 成功後：`(healthy)` ✅
* 失敗が続くと：`(unhealthy)` ❌

※ health は「通常の status」に追加で付くもの、というのがポイントです。([Docker Documentation][1])

---

### 手順6：`docker inspect` で “なぜ失敗したか” を見る 🔎🧠

![Inspect Health Logs](./picture/docker_observability_ts_study_027_05_inspect_health_logs.png)

まずはステータスだけ👇

```bash
docker inspect --format '{{.State.Health.Status}}' obs-api
```

次にログ（直近の実行結果）👇

```bash
docker inspect --format '{{range .State.Health.Log}}{{println .End " exit=" .ExitCode " " .Output}}{{end}}' obs-api
```

`docker inspect` はDockerオブジェクトの詳細をJSON等で見れるコマンドです。([Docker Documentation][2])
（この章では “Health の中身を覗く” がメイン🎁）

---

### 手順7：わざと壊して `unhealthy` を見る 😈💥

一番わかりやすいのは「/health が 500 を返す状態」にすること。

例：**`/health` が “ファイルがあったら不健康” にする**（デモ用でOK）👇
`src/server.ts` などに、こういう分岐を入れます：

```ts
import fs from "node:fs";

app.get("/health", (req, res) => {
  if (fs.existsSync("/tmp/unhealthy")) {
    return res.status(500).json({ ok: false });
  }
  return res.json({ ok: true });
});
```

起動したまま、コンテナ内でファイルを作る👇

```bash
docker exec obs-api sh -lc "touch /tmp/unhealthy"
```

しばらくして `docker ps` を見ると `unhealthy` になってるはず！😆
戻す👇

```bash
docker exec obs-api sh -lc "rm -f /tmp/unhealthy"
```

---

### 手順8：掃除 🧹

```bash
docker rm -f obs-api
```

---

## ④ つまづきポイント（3つ）🪤😵‍💫

![Curl Missing Trap](./picture/docker_observability_ts_study_027_06_curl_missing_trap.png)

1. **“curl が無い問題”**
   公式例は `curl -f http://localhost/ || exit 1` が多いけど、イメージによっては curl が入ってません。([Docker Documentation][1])
   → 今回は **Node の `fetch`** で回避（依存を増やさない👍）

2. **/health が重い（DB確認とか）**
   healthcheck は「軽く・速く」が正義💨
   重いと `timeout` で落ちて、無駄に unhealthy 連発します。

3. **start-period を入れてないせいで起動直後に即unhealthy**
   起動に時間がかかるアプリは、`--start-period` を入れて “助走時間” を確保しよう🏃‍♂️‍➡️([Docker Documentation][1])
   （Engine 25.0+なら `--start-interval` で start-period 中だけ細かく監視もできるよ）([Docker Documentation][1])

---

## ⑤ ミニ課題（15分）⏳🎮

![Start Period Shield](./picture/docker_observability_ts_study_027_07_start_period_shield.png)

**A. チューニング遊び 🎚️**

* `--interval=3s` にして、healthy/unhealthy の切り替わり速度を体感する⚡
* `--retries=5` にして「粘り強さ」を変える🧘

**B. start-period 実験 🐢**

* アプリ起動をわざと遅くする（例：起動時に `await new Promise(r=>setTimeout(r, 8000))`）
* `start-period` あり/なしで、起動直後の挙動がどう変わるか観察👀

---

## ⑥ AIに投げるプロンプト例（コピペOK）🤖📋

```text
Dockerfile HEALTHCHECK を追加したい。
Node(fetch) で /health を叩く healthcheck.mjs を作って。
- 2秒でタイムアウト
- 成功は exit 0、失敗は exit 1
- 失敗時は理由を console.error に出す
```

```text
/health エンドポイントに「/tmp/unhealthy があれば 500」を入れて、
docker exec で unhealthy を再現できるようにしたい。Express の例を書いて。
```

（AI拡張：GitHub Copilot / OpenAI Codex などにそのまま投げてOK🤖✨）

---

## おまけ：`HEALTHCHECK NONE` って何？🙋‍♂️

ベースイメージが healthcheck を持ってる時に、**継承を無効化**できます。([Docker Documentation][1])
（「このイメージの healthcheck、うちの用途だと邪魔…」って時に便利👍）

---

## 最小の `/health` がまだ無い場合（超ミニ）🧯

```ts
app.get("/health", (req, res) => res.json({ ok: true }));
```

---

次の第28章で、この health を **Compose の起動順（healthy になるまで待つ）**につなげて、「起動直後の接続失敗ログが減って気持ちいい」状態にしていきます 😆⏳

[1]: https://docs.docker.com/reference/dockerfile/ "Dockerfile reference | Docker Docs"
[2]: https://docs.docker.com/reference/cli/docker/inspect/?utm_source=chatgpt.com "docker inspect"
