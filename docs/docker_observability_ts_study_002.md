# 第02章：“よくある障害”を3パターンに分ける 🧩😵‍💫

## ① 今日のゴール 🎯✨

* 何かが壊れたときに、まず **「アプリ起因」or「依存起因」or「環境起因」** のどれっぽいかを、3分で当てにいけるようになる 🕵️‍♂️💨
* さらに「原因候補を“短いリスト”にする癖」を身につける ✍️✅
* おまけで、わざと落とすエンドポイント（/boom）を作って、ログで「どのルートで落ちたか」を追えるようにする 💥👀

---

## ② 図（1枚）🖼️📦

![Three Failure Sources](./picture/docker_observability_ts_study_002_01_three_failure_sources.png)

障害の原因って、だいたいここに落ちます👇

```text
  [あなたのHTTPリクエスト] 
            |
            v
   +------------------+
   |     アプリ        |  ← ①アプリ起因（バグ/例外/実装ミス）
   +------------------+
        |        |
        |        +--------------------+
        |                             |
        v                             v
+------------------+          +------------------+
|   依存サービス     |          |      環境         |
| (DB/外部API等)     |          | (Docker/設定/ポート|
| ←②依存起因         |          |  env/権限/ネット等)|
+------------------+          +------------------+
         ←────────────── ③環境起因は全体に影響しがち
```

---

## ③ まず覚える「3分類」🧠🔖

### A. アプリ起因 🧑‍💻💣

![App Failure Characteristics](./picture/docker_observability_ts_study_002_02_app_failure_characteristics.png)

**特徴**

* あるURL（ある操作）で **毎回** だいたい同じ感じで落ちる
* ログに **スタックトレース** や「どのファイル・何行」みたいな情報が出がち 📌

**よくある例**

* null/undefined を想定してなくて落ちた
* 例外を投げた／投げられたのに拾ってない
* 型は合ってるけど、値の前提が壊れてた（空文字OKだと思ってた…等）

---

### B. 依存起因 🔌💥

![Dependency Failure Characteristics](./picture/docker_observability_ts_study_002_03_dependency_failure_characteristics.png)

**特徴**

* アプリ自体は起動するけど、特定の機能で失敗する
* エラー文に **ECONNREFUSED / ETIMEDOUT / DNS / 502** など“ネットワーク臭”が出がち 🌐💦

**よくある例**

* DBが落ちてる
* 外部APIが遅い/落ちてる
* 接続先ホスト名やURLを間違えた

---

### C. 環境起因 📦🧨

![Environment Failure Characteristics](./picture/docker_observability_ts_study_002_04_environment_failure_characteristics.png)

**特徴**

* そもそも起動しない／起動してもすぐ落ちる
* 「ポートが使われてる」「環境変数が無い」「権限が無い」みたいな“設定臭”が出がち ⚙️😇
* 複数コンテナ構成だと「起動順」でも事故る（依存が先に準備できてない）⏳
  ※ Compose は依存関係（depends_on）で起動順を制御できるよ、という話が公式にもあります 📚([Docker Documentation][1])

---

## ④ “短いリスト”にする癖 ✍️🪄（これ超大事）

![Short List Strategy](./picture/docker_observability_ts_study_002_05_short_list_strategy.png)

障害対応でありがちなのが「可能性が無限にあって脳が死ぬ」やつ…😵‍💫
そこで、**まず候補を5個以内**に潰していきます。

おすすめテンプレ👇

```text
【短い候補リスト（最大5つ）】
1) どのルート？（/boom なのか /ping なのか）
2) 入力は？（クエリ/JSON/ヘッダ）
3) 依存呼び出しは？（DB/API）
4) 設定は？（env/URL/キー/ポート）
5) いつから？（変更点：直近の差分）
```

これを作るだけで、対応が一気に「作業」になります 👍✨

---

## ⑤ 手を動かす（ハンズオン）🛠️🔥

## やること：/boom を作って “落ちた場所”をログで特定する 💥👀

ここでは Express 5 を使います（async で投げたエラーも、エラーハンドラへ流れてくれるのが嬉しいやつ）✨([expressjs.com][2])
あと TypeScript 実行は tsx を使うとラクです（watch もできる）⚡([GitHub][3])

---

## 1) ファイル構成 📁

```text
your-app/
  compose.yml
  Dockerfile
  package.json
  tsconfig.json
  src/
    server.ts
```

---

## 2) package.json 🧾

```json
{
  "name": "obs-mini-api",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "tsx watch src/server.ts",
    "build": "tsc -p tsconfig.json",
    "start": "node dist/server.js"
  },
  "dependencies": {
    "express": "^5.1.0"
  },
  "devDependencies": {
    "tsx": "^4.0.0",
    "typescript": "^5.0.0"
  }
}
```

---

## 3) tsconfig.json 🧠

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "skipLibCheck": true
  },
  "include": ["src"]
}
```

---

## 4) src/server.ts 🚀

ポイントは2つ！

* ルートに「わざと落ちる」/boom を作る 💥
* 最後に **エラーハンドラ（引数4つのやつ）** を置く 🧯
  ※ Express の公式も「エラーハンドリングは最後」「4引数」と言ってます 📚([expressjs.com][4])

```ts
import express, { Request, Response, NextFunction } from "express";

const app = express();
app.use(express.json());

/**
 * 超ミニなアクセスログ（第7章で本格化するけど、今は最低限でOK）
 */
app.use((req, _res, next) => {
  console.log(`[REQ] ${req.method} ${req.path}`);
  next();
});

app.get("/ping", (_req, res) => {
  res.json({ ok: true, at: new Date().toISOString() });
});

/**
 * わざと落とす 💥
 */
app.get("/boom", (_req, _res) => {
  throw new Error("boom! わざと例外を投げました 💥");
});

/**
 * 依存起因っぽい雰囲気を出す（存在しないホストへアクセス）
 * ※ Express 5 は async/Promise の失敗もエラーハンドラへ流してくれる 😇
 */
app.get("/dep-broken", async (_req, _res) => {
  const r = await fetch("http://doesnotexist.invalid/");
  const t = await r.text();
  return t;
});

/**
 * 環境起因っぽいやつ（必須envが無い）
 */
app.get("/need-env", (_req, res) => {
  const v = process.env.MY_REQUIRED;
  if (!v) {
    throw new Error("MY_REQUIRED が無いよ 😭（環境起因っぽい）");
  }
  res.json({ ok: true, MY_REQUIRED: v });
});

/**
 * エラーハンドラ（必ず最後）
 */
app.use((err: unknown, req: Request, res: Response, _next: NextFunction) => {
  console.error(`[ERR] ${req.method} ${req.path}`, err);
  res.status(500).json({ error: "Internal Server Error", route: req.path });
});

const port = Number(process.env.PORT ?? "3000");
app.listen(port, () => {
  console.log(`[BOOT] listening on :${port}`);
});
```

---

## 5) Dockerfile 🐳

```dockerfile
FROM node:current-slim

WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install

COPY tsconfig.json ./
COPY src ./src

RUN npm run build

ENV PORT=3000
EXPOSE 3000
CMD ["npm", "run", "start"]
```

---

## 6) compose.yml 📦

```yaml
services:
  api:
    build: .
    ports:
      - "3000:3000"
    environment:
      - PORT=3000
```

---

## 7) 起動して叩く ▶️👊

```bash
docker compose up --build
```

別ターミナルで👇

```bash
curl http://localhost:3000/ping
curl http://localhost:3000/boom
curl http://localhost:3000/dep-broken
curl http://localhost:3000/need-env
```

---

## 8) 期待するログ例 👀🧾（雰囲気）

```text
[BOOT] listening on :3000
[REQ] GET /ping
[REQ] GET /boom
[ERR] GET /boom Error: boom! わざと例外を投げました 💥
[REQ] GET /dep-broken
[ERR] GET /dep-broken TypeError: fetch failed
[REQ] GET /need-env
[ERR] GET /need-env Error: MY_REQUIRED が無いよ 😭（環境起因っぽい）
```

ここで大事なのはこれ👇

* **「どのルートで落ちたか」** が 1秒でわかる ✅
* /dep-broken は “依存（ネットワーク）臭”、/need-env は “設定臭” がする ✅

（補足）Promise/async の失敗がエラーハンドラに流れるのは Express 5 の嬉しい改善ポイントだよ 🙌([expressjs.com][2])

---

## ⑥ つまづきポイント（3つ）🪤😭

1. **エラーハンドラを最後に置いてない**
   ルートより上に置くと、想定通り拾えないことがあるよ〜🧯
   （公式も「最後に定義」って言ってる）([expressjs.com][4])

2. **“環境起因”のときにアプリを疑い続けて沼る**
   起動しない／即死する系は、まず「ポート」「env」「権限」「ファイル」「依存の起動順」あたりを疑うのが近道 😇📦

3. **“依存起因”のエラー文を見落とす**
   ECONNREFUSED / ETIMEDOUT / DNS っぽい単語が出たら、だいたい依存か環境（ネットワーク設定）方面 🧠🔌

---

## ⑦ ミニ課題（15分）⏳🎮

## 課題A：3分類クイズ 🧩

次の症状を、Aアプリ / B依存 / C環境 に分類して、理由を一言で書いてね ✍️

1. /boom だけ毎回 500、ログに server.ts の行番号が出る
2. /dep-broken が “fetch failed” で落ちる
3. コンテナが起動直後に落ち続け、ログに “PORT is already in use” が出る
4. /need-env が “MY_REQUIRED が無い” で落ちる

## 課題B：短い候補リストを作る ✍️

「/slow が遅い（まだ作ってない想定でOK）」と聞いたら、候補を最大5個に絞って書いてみてね 🐢💭

---

## ⑧ AIに投げるプロンプト例（コピペOK）🤖📋

## 1) 3分類の当てにいく 🧠

```text
次のログ/症状を「アプリ起因・依存起因・環境起因」のどれが濃厚か判定して。
理由を1行、次に確認するコマンドや観測ポイントを3つ出して。

症状:
- （ここにログや状況を書く）
```

## 2) “短い候補リスト”を作らせる ✍️

```text
この障害の原因候補を最大5つに絞って。
各候補について「確認方法」を1つずつ書いて。

状況:
- （例）/boom は500、/pingはOK、最近変更したのは○○
```

## 3) Expressのエラーハンドリングの見直し 🧯

```text
この server.ts のエラーハンドリングで足りない点を指摘して。
初心者にもわかるように、修正案を最小差分で提案して。
（コードを貼る）
```

---

## ちょい予告 👀✨

この章で「どこが怪しいか」を当てられるようになったら、次の章以降で

* ログを “標準出力に寄せる” 📣
* ログを “揃えて読みやすくする” 🧾
* さらにメトリクス📈とヘルス💚で「影響」と「復旧判断」もできるようにする
  …って感じで強化していくよ 💪🌈

（補足）Promise が未処理のまま落ちる系は Node 側にも “unhandledRejection” みたいなイベントがあるので、後半で「逃さない」作りに進化させます 🧯⚡([nodejs.org][5])

[1]: https://docs.docker.com/compose/how-tos/startup-order/?utm_source=chatgpt.com "Control startup order - Docker Compose"
[2]: https://expressjs.com/2024/10/15/v5-release.html?utm_source=chatgpt.com "Introducing Express v5: A New Era for the Node. ..."
[3]: https://github.com/privatenumber/tsx?utm_source=chatgpt.com "privatenumber/tsx: ⚡️ TypeScript Execute | The easiest ..."
[4]: https://expressjs.com/en/guide/error-handling.html?utm_source=chatgpt.com "Error handling"
[5]: https://nodejs.org/api/process.html?utm_source=chatgpt.com "Process | Node.js v25.2.1 Documentation"
