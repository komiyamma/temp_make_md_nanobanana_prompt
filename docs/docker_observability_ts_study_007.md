# 第07章：アクセスログ：1行で“何が起きたか”を書く 🚪🧾

## ① 今日のゴール 🎯✨

この章が終わったら、こうなってます👇

* アクセスログを **「1リクエスト＝1行」** で出せる 🧾✅
* 最低限の項目 **method / path / status / ms** が揃ってる 🧩
* `/slow` を叩いたあと、ログだけで **「遅いルートはこれ！」** が言える 🐢🔍

---

## ② まず結論：アクセスログは “短く・揃える” が正義 🧠✨

![Basic Access Log Fields](./picture/docker_observability_ts_study_007_01_access_log_fields.png)

アクセスログの目的は超シンプル👇
**「何が起きたか」を、あとから最短で説明できること** 🏃‍♂️💨

だから、まずはこの4つを **必ず出す** のが基本セットです👇

* `method=GET`（何した？）
* `path=/slow`（どこに？）
* `status=200`（結果どうだった？）
* `ms=812.3`（どれくらい時間かかった？）⏱️

> 2026-02-13時点だと、安定運用向けは **Node v24（Active LTS）** がど真ん中の扱いです（v25はCurrent）。([Node.js][1])
> **Express v5** は既に公式リリース済みで、**npmのデフォルト（latest）もv5系** になっています。([expressjs.com][2])
> そして **TypeScript 6.0 Beta** も直近で案内が出ています（移行の話題も含むので「最新の空気感」を知るのにちょうどいいです）。([Microsoft for Developers][3])

---

## ③ 図（1枚）🖼️📦

![Middleware Lifecycle](./picture/docker_observability_ts_study_007_02_middleware_lifecycle.png)

```text
リクエスト → Express middleware（開始）→ handler → レスポンス
                      ↓（finishイベント）
               1行アクセスログ → stdout/stderr → Docker が拾う → docker compose logs
```

Dockerはコンテナの **stdout / stderr** を標準で取り込んでログとして保持します。([Docker Documentation][4])
（なので「ファイルに書く」より「標準出力に出す」がまず強い、という流れになります📣）

---

## ④ 手を動かす（手順 5〜10個）🛠️🚀

ここでは **Express用のアクセスログ middleware** を作って、`/ping` と `/slow` で動きを見ます👀

### Step 1) middleware を1ファイル作る 📄✨

![Access Log Logic Details](./picture/docker_observability_ts_study_007_03_access_log_logic.png)

`src/middleware/accessLog.ts`

```ts
import type { NextFunction, Request, Response } from "express";

/**
 * アクセスログ：1リクエスト=1行
 * 最低限：method / path / status / ms
 *
 * ルール：
 * - 遅延(ms)はレスポンス完了(finish)のタイミングで計測する
 * - status>=500 は stderr に出す（あとで絞り込みやすい）
 * - path は query を含めない（個人情報/ノイズ対策）
 */
export function accessLog(req: Request, res: Response, next: NextFunction) {
  const start = process.hrtime.bigint();

  res.on("finish", () => {
    const end = process.hrtime.bigint();
    const ms = Number(end - start) / 1_000_000;

    const line =
      `access ` +
      `ts=${new Date().toISOString()} ` +
      `method=${req.method} ` +
      `path=${req.path} ` +
      `status=${res.statusCode} ` +
      `ms=${ms.toFixed(1)}`;

    if (res.statusCode >= 500) {
      console.error(line);
    } else {
      console.log(line);
    }
  });

  next();
}
```

ポイントはここ👇

* **開始時刻を取る** → **レスポンスが終わったら（finish）** msを計算 ⏱️
* `req.path` を使う（`?token=...` みたいな地雷をログに混ぜない🙈）

---

### Step 2) サーバーに middleware を挿す 🧩🚪

![Middleware Gate Placement](./picture/docker_observability_ts_study_007_04_middleware_gate.png)

`src/server.ts`（例）

```ts
import express from "express";
import { accessLog } from "./middleware/accessLog.js";

const app = express();

app.use(accessLog);

app.get("/ping", (_req, res) => {
  res.status(200).send("pong");
});

app.get("/slow", async (_req, res) => {
  await new Promise((r) => setTimeout(r, 800));
  res.status(200).send("slow ok");
});

// 例：エラー確認用（第2章の /boom があるならそれでOK）
app.get("/boom", () => {
  throw new Error("boom!");
});

const port = Number(process.env.PORT ?? 3000);
app.listen(port, () => {
  console.log(`boot ts=${new Date().toISOString()} port=${port}`);
});
```

---

### Step 3) Dockerで起動してログを見る 🐳👀

アクセスログが stdout/stderr に出ると、Docker が拾って `docker compose logs` で見れます。([Docker Documentation][4])

ログを見るコマンド（超よく使う3つ）👇

* 末尾だけ：`--tail`
* 追いかける：`--follow`
* 時刻も出す：`--timestamps`

これらのオプションは `docker compose logs` の公式オプションにあります。([Docker Documentation][5])

PowerShell例（サービス名が `api` の想定）👇

```bash
docker compose up --build
```

別ターミナルで👇

```bash
docker compose logs api --tail 50 --timestamps
```

リアルタイム追跡👇

```bash
docker compose logs api --follow --tail 20 --timestamps
```

プレフィックス（`api-1 |` みたいなやつ）を消したい時👇

```bash
docker compose logs api --no-log-prefix --tail 50
```

---

### Step 4) リクエストを投げて、ログが “1行で揃う” のを確認 🧪✨

Windowsなら `curl.exe` が分かりやすいです👇

```bash
curl.exe http://localhost:3000/ping
curl.exe http://localhost:3000/slow
```

---

## ⑤ 期待する出力（ログ1行見本）🧾👀

だいたいこんな雰囲気になります👇（順番が揃ってるのが大事！）

```text
access ts=2026-02-13T04:12:33.123Z method=GET path=/ping status=200 ms=2.4
access ts=2026-02-13T04:12:38.901Z method=GET path=/slow status=200 ms=803.6
```

これで、`/slow` が遅いのが **ログだけで即バレ** します 🐢💥

---

## ⑥ つまづきポイント（3つ）🪤😵‍💫

![Access Log Traps](./picture/docker_observability_ts_study_007_05_access_log_traps.png)

1. **ログが出ない**

   * `app.use(accessLog);` を `app.get(...)` より前に置いた？🧩

2. **ms が0っぽい / 変**

   * `finish` で計測してる？（handlerの手前でログ出すと“処理時間”にならないよ）⏱️

3. **`/slow?x=...` のクエリがログに出てうるさい or 危険**

   * `req.path` を使う（`req.originalUrl` は query まで入る）🙈

---

## ⑦ ミニ課題（15分）⏳🎮

**「遅いのが混ざる」** をログで当てるゲーム！😆

1. `/maybe-slow` を作って、50%で800ms遅延、50%で即返す
2. 10回叩く
3. ログの `ms` を見て「遅い回」だけ数える 🧮✨

ヒント：ログが揃ってると、人間でも数えやすいし、将来は検索もしやすいよ〜🔎

---

## ⑧ AIに投げるプロンプト例（コピペOK）🤖📋

**A. middleware生成（安全に短く）**

* 「Express v5 + TypeScriptで、`method/path/status/ms` の1行アクセスログmiddlewareを書いて。`finish`で計測、status>=500はstderrに出して。」

**B. ログ行のフォーマット改善**

* 「アクセスログのフォーマットを“人が読みやすいkey=value”で、順番固定にしたい。追加するなら何が最小？（例：reqIdは次章でやる前提）」

**C. 例外時も最後にログを残したい**

* 「Expressでエラー時もアクセスログが1行出るように、エラーハンドラ設計の注意点を教えて（初心者向けに）。」

---

ここまでできたら第7章はクリアです！🏁🎉
次の章（ログレベル）に進むと、「同じアクセスログでも本番では量を絞る」みたいな話ができるようになって一気に運用っぽくなります 🎚️🟢🟡🔴

[1]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[2]: https://expressjs.com/2024/10/15/v5-release.html?utm_source=chatgpt.com "Introducing Express v5: A New Era for the Node. ..."
[3]: https://devblogs.microsoft.com/typescript/announcing-typescript-6-0-beta/?utm_source=chatgpt.com "Announcing TypeScript 6.0 Beta"
[4]: https://docs.docker.com/engine/logging/drivers/json-file/?utm_source=chatgpt.com "JSON File logging driver"
[5]: https://docs.docker.com/reference/cli/docker/compose/logs/?utm_source=chatgpt.com "docker compose logs"
