# 第09章：構造化ログ（JSON）：検索しやすい形にする 🧱🔎

## ① 今日のゴール 🎯✨

* ログを「ただの文字列」じゃなく「**データ（JSON）**」として出せるようになる 🧾➡️📦
* 1行ログをコピーしても、**機械で検索・集計しやすい形**になってるのを体感する 🔎📊
* `docker compose logs` の出力を **PowerShellでJSONとして扱う**ところまでやる 💪🪟

> ここでいう構造化ログは、ざっくり言うと「**1行=1つのJSON**」のログです（NDJSONっぽいやつ）🌲
> PinoはJSONログが前提のロガーで、pino-prettyはそれを**開発時だけ読みやすく整形**する道具だよ、という立ち位置です。 ([GitHub][1])

---

## ② 図（1枚）🖼️

```text
(今まで) ただの文字列ログ
  "GET /slow 200 512ms"

(これから) JSONログ（構造化ログ）
  {"time":"...","level":"info","msg":"http","http":{"method":"GET","path":"/slow","status":200},"ms":512}

→ できること
  ✅ status=500 だけ抽出
  ✅ /slow だけ抽出
  ✅ ms が遅い順に並べる
  ✅ あとでLoki/Grafana等に入れた時に強い
```

---

## ③ 手を動かす（手順 5〜10個）🛠️🚀

### 0) まず大事な前提（超重要）📣

コンテナのログは「**ファイルに頑張って書く**」より「**標準出力に出して、Dockerに拾ってもらう**」のが基本路線です📦
Dockerはログドライバで収集する仕組みがあり、デフォルトは `json-file` です。 ([Docker Documentation][2])

---

### 1) ライブラリを入れる 📦🌲

今回は **Pino** で「JSONログ」をキレイに出します。

```bash
## APIコンテナのプロジェクト（package.jsonがある場所）で
npm i pino

## 開発中だけ “読みやすくする” 用（任意）
npm i -D pino-pretty
```

> pino-pretty は「開発時に整形して読みやすくする」用途です。ログを整形する処理は本番では負担になりがちなので、基本は開発時限定が鉄板です🧠 ([GitHub][1])

---

### 2) `/src/logger.ts` を作る 🧱🧾

`src/logger.ts` を新規作成（なければ `src/` 配下に作ってOK）👇

```ts
// src/logger.ts
import pino from "pino";

const pretty =
  process.env.LOG_PRETTY === "1"
    ? pino.transport({
        target: "pino-pretty",
        options: {
          colorize: true,
          translateTime: "SYS:yyyy-mm-dd'T'HH:MM:ss.l",
          singleLine: true,
        },
      })
    : undefined;

export const logger = pino(
  {
    level: process.env.LOG_LEVEL ?? "info",

    // 目で見ても分かりやすい ISO 時刻に（好みで epoch のままでもOK）
    timestamp: pino.stdTimeFunctions.isoTime,

    // どのサービスのログか、毎行に自動で付ける（あとで検索が楽✨）
    base: {
      service: process.env.SERVICE_NAME ?? "api",
      env: process.env.NODE_ENV ?? "development",
    },
  },
  pretty
);
```

* `LOG_PRETTY=1` のときだけ “読みやすいログ” になります（開発用）✨
* ふつうは JSON がそのまま 1行ずつ出ます 🧱
* `timestamp: isoTime` の例はこういう感じで設定できます。 ([dash0.com][3])
* そしてPinoの「トランスポート（ログ加工）」はワーカースレッド等に逃がすのが推奨、という思想がベースにあります。 ([GitHub][4])

---

### 3) HTTPアクセスログを “1行JSON” にする 🚪🧾⏱️

Expressを想定して「全リクエストを最後に1行で出す」ミドルウェアを追加します。

`src/index.ts`（または `src/app.ts`）で、`app` を作った直後あたりに👇

```ts
import express from "express";
import { logger } from "./logger";

const app = express();

// ここから追加👇（アクセスログ）
app.use((req, res, next) => {
  const start = process.hrtime.bigint();

  res.on("finish", () => {
    const end = process.hrtime.bigint();
    const ms = Number(end - start) / 1_000_000;

    logger.info(
      {
        http: {
          method: req.method,
          path: req.originalUrl,
          status: res.statusCode,
        },
        ms: Math.round(ms * 100) / 100,
      },
      "http"
    );
  });

  next();
});
```

ポイントはこれ👇😆

* **キー名を固定**する（`http.method`, `http.path`, `http.status`, `ms`）
* 1行で完結（あとで検索・集計するため）🔎
* “文章で頑張って説明しない”。データで語る 📊

---

### 4) エラーログも “オブジェクトで” 出す 🧯🔴

ルートで落ちたとき、**errを文字列にしない**のがコツです（`Error`って雑に文字列化すると情報が消えやすい😇）

Expressのエラーハンドラ（最後の方）に👇

```ts
// いちばん下に置く（他の app.use の後）
app.use((err: unknown, req: express.Request, res: express.Response, next: express.NextFunction) => {
  logger.error(
    {
      err, // ← “そのまま入れる”
      http: { method: req.method, path: req.originalUrl },
    },
    "unhandled_error"
  );

  res.status(500).json({ error: "internal_error" });
});
```

---

### 5) Dockerで動かして、JSONログを確認 👀📦

起動して、ログを見る：

```bash
docker compose up -d --build
docker compose logs -f api
```

**期待するログ例（JSONの1行）**👇

```text
{"level":30,"time":"2026-02-13T04:23:10.123Z","service":"api","env":"development","http":{"method":"GET","path":"/ping","status":200},"ms":3.12,"msg":"http"}
```

---

### 6) “JSONとして扱える” ことを体験する（超おもしろい）🪄🔎

`docker compose logs` は通常「サービス名のプレフィックス」を付けがちで、それがあると **JSONパースが壊れます**💥
なので **`--no-log-prefix`** を付けます。 ([Docker Documentation][5])

まず「プレフィックス無し」でログを流す👇

```powershell
docker compose logs -f api --no-log-prefix --since 5m
```

その出力をPowerShellで “JSONとして” 触る👇✨
（※ログがJSON1行なら、1行ずつ `ConvertFrom-Json` できます）

```powershell
docker compose logs -f api --no-log-prefix --since 5m |
  ForEach-Object { $_ | ConvertFrom-Json } |
  Select-Object time, msg, @{n="path";e={$_.http.path}}, @{n="status";e={$_.http.status}}, ms
```

`ConvertFrom-Json` は PowerShell の標準機能です。 ([Microsoft Learn][6])

---

### 7) “遅いログだけ” 抜き出す 🐢💥

例えば「500ms以上」を抜く👇

```powershell
docker compose logs api --no-log-prefix --since 5m |
  ForEach-Object { $_ | ConvertFrom-Json } |
  Where-Object { $_.ms -ge 500 } |
  Sort-Object ms -Descending |
  Select-Object time, @{n="path";e={$_.http.path}}, @{n="status";e={$_.http.status}}, ms
```

はい、これが **「ログがデータになった瞬間」**です😆🎉
“目で探す” から “条件で取る” へ進化した！🧠✨

---

## ④ つまづきポイント（3つ）🪤😵‍💫

1. **JSONなのにパースできない…** 🧨
   原因：`docker compose logs` のプレフィックスが混ざってる可能性大。
   対策：`--no-log-prefix` を付ける。 ([Docker Documentation][5])

2. **ログが読みにくい！でもJSONは崩したくない！** 😫
   対策：開発中だけ `LOG_PRETTY=1` にして pino-pretty を使う（本番はOFF）。
   pino-pretty自体が「開発向けフォーマッタ」と明言されています。 ([GitHub][1])

3. **ログ加工（整形・送信）でアプリが重くなる不安** 🐌
   対策：Pinoは “ログ処理（transports）を別スレッド/別プロセスへ” を推奨する設計思想があり、重い加工をメインスレッドに乗せない発想が基本です。 ([GitHub][4])

---

## ⑤ ミニ課題（15分）⏳✅

**課題A：キーを増やしてみよう 🧱➕**

* `logger.ts` の `base` に `version` を足す（例：`process.env.APP_VERSION`）
* ログに毎行 `version` が出ることを確認 🎉

**課題B：/slow だけ集計しよう 🐢📊**

* PowerShellで `/slow` のログだけ抽出して、`ms` の平均っぽいのを見る（まずは件数でもOK）

  * ヒント：`Where-Object { $_.http.path -eq "/slow" }`

**課題C：500系だけ抜こう 🔥**

* `Where-Object { $_.http.status -ge 500 }` でエラーだけ表示してみる

---

## ⑥ AIに投げるプロンプト例（コピペOK）🤖📋

**1) “ログのキー設計” を相談する 🧠**

```text
Node/TypeScriptのAPIで構造化ログ(JSON)にしたいです。
http.method/path/status/ms と、サービス識別(service/env)は必須にします。
初心者でも運用しやすいキー設計（命名ルールと例）を提案して。
```

**2) “既存のconsole.logを置き換え” してもらう 🔁**

```text
このプロジェクトのconsole.log/console.errorを、pinoの構造化ログに置き換えたい。
logger.ts を作って、起動ログ・アクセスログ・エラーログを1行JSONで出すようにリファクタして。
変更差分のコードを提案して。
```

**3) “PowerShellでログ抽出ワンライナー” を作らせる 🪄**

```text
docker compose logs のJSONログをPowerShellで解析したい。
/slow のログだけ抽出して、msの降順で上位10件を表示するワンライナーを書いて。
前提: docker compose logs は --no-log-prefix を使う。
```

---

## 今日のまとめ 🌈📌

* **構造化ログ（JSON）**にすると「読む」だけじゃなく「検索・抽出・集計」できるようになる 🧱🔎
* `--no-log-prefix` は **JSONパースの生命線**（ログ行を純粋なJSONにする） ([Docker Documentation][5])
* pino-pretty は便利だけど **開発専用**が基本（本番はJSONのままが強い） ([GitHub][1])

次の第10章（相関ID/reqId）に行くと、いよいよ「1リクエストを1本の糸で追う」🧵ができて、デバッグが急にRPGから攻略本になります😆📘

[1]: https://github.com/pinojs/pino-pretty "GitHub - pinojs/pino-pretty: Basic prettifier for Pino log lines"
[2]: https://docs.docker.com/engine/logging/configure/ "Configure logging drivers | Docker Docs"
[3]: https://www.dash0.com/guides/logging-in-node-js-with-pino "Production-Grade Logging in Node.js with Pino · Dash0"
[4]: https://github.com/pinojs/pino "GitHub - pinojs/pino:  super fast, all natural json logger"
[5]: https://docs.docker.com/reference/cli/docker/compose/logs/ "docker compose logs | Docker Docs"
[6]: https://learn.microsoft.com/ja-jp/powershell/module/microsoft.powershell.utility/convertfrom-json?view=powershell-7.5&utm_source=chatgpt.com "ConvertFrom-Json - PowerShell"
