# 第29章：HTTP導入①：ルーティング→ユースケース呼ぶだけ 🚪🌐

![hex_ts_study_029[(./picture/hex_ts_study_029_http_adapter_express.png)

この章は「**HTTPの入口を増やす**」回だよ😊
CLIで動いてる中心（ユースケース/ドメイン）はそのままに、**HTTPを“差し込み口”として追加**します💖

---

## 1 この章のゴール 🎯✨

できるようになること👇

* `/todos` みたいなURLにアクセスされたら、**ユースケースを呼ぶ**だけにできる🙌
* **Controllerを薄く保つ**コツがわかる🥗✨
* 「中心はHTTPを知らない」を体験できる🛡️🔌

---

## 2 今回の方針 合言葉はこれ 🗣️✨

* **Controllerは翻訳係**🧩
  「HTTPの世界 → DTO → ユースケース呼ぶ → 返す」だけ！
* **中心は静かに**🧠🌿
  中心（usecase/domain）は `express` も `Request` も知らない🙅‍♀️

---

## 3 使うHTTPフレームワークは Express v5 にするよ 🚀🧰

理由はシンプルで安心だから😊

* Express v5 は正式リリース済みで、現在も更新が続いてるよ📈 ([expressjs.com][1])
* **async/await の例外がそのままエラーハンドラに流れる**（Promiseのrejectを自動で拾う）ので、Controllerがさらに薄くできる✨ ([expressjs.com][2])
* `express.json()` も **標準ミドルウェア**として使えるよ🧴 ([expressjs.com][3])
* TypeScript の型は `@types/express` が v5 系で提供されてるよ🧷 ([npm][4])

---

## 4 まずはインストール 📦✨

（npm例）

```bash
npm i express
npm i -D @types/express tsx
```

* `tsx` は **TypeScriptをそのまま実行**しやすい定番枠だよ⚡ ([GitHub][5])
* Nodeは安定運用なら **LTS系**が基本で、2026-01時点だと v24 が Active LTS 側だよ🧱 ([nodejs.org][6])

---

## 5 ルーティングの形を決めよう 🗺️✨

今回のAPIは超ミニでOK🙆‍♀️

* `GET /todos` 👉 一覧
* `POST /todos` 👉 追加
* `POST /todos/:id/complete` 👉 完了

「RESTっぽい形」にしておくと、あとで育てやすいよ🌱💕

---

## 6 フォルダ配置はここに置く 📁🧭

この章で増えるのは「HTTPの入口」だけ！

```txt
src/
  adapters/
    inbound/
      http/
        createHttpApp.ts
        todoRoutes.ts
        errorMiddleware.ts
        server.ts
```

---

## 7 コード 入口の本体を作る 🧩🌐

### 7.1 ルーター todoRoutes.ts 🚪➡️🧠

ポイント：**ルートの中でやるのは3つだけ**
① 受け取る → ② ユースケース呼ぶ → ③ 返す

```ts
// src/adapters/inbound/http/todoRoutes.ts
import { Router, type Request, type Response } from "express";

type AddTodoUseCase = {
  execute(input: { title: string }): Promise<{ id: string; title: string; completed: boolean }>;
};

type ListTodosUseCase = {
  execute(): Promise<{ items: Array<{ id: string; title: string; completed: boolean }> }>;
};

type CompleteTodoUseCase = {
  execute(input: { id: string }): Promise<{ id: string; title: string; completed: boolean }>;
};

export function createTodoRouter(deps: {
  addTodo: AddTodoUseCase;
  listTodos: ListTodosUseCase;
  completeTodo: CompleteTodoUseCase;
}) {
  const router = Router();

  router.get("/todos", async (_req: Request, res: Response) => {
    const output = await deps.listTodos.execute();
    res.json(output);
  });

  router.post("/todos", async (req: Request, res: Response) => {
    // ここは次章で本格バリデーションするよ😊
    const title = String(req.body?.title ?? "");
    const output = await deps.addTodo.execute({ title });
    res.status(201).json(output);
  });

  router.post("/todos/:id/complete", async (req: Request, res: Response) => {
    const id = String(req.params.id ?? "");
    const output = await deps.completeTodo.execute({ id });
    res.json(output);
  });

  return router;
}
```

> Express v5 は async handler の例外をエラーハンドラへ流してくれるので、ここで `try/catch` を増やさなくても運用しやすいよ✨ ([expressjs.com][2])

---

### 7.2 アプリ組み立て createHttpApp.ts 🧩🏗️

```ts
// src/adapters/inbound/http/createHttpApp.ts
import express from "express";
import { createTodoRouter } from "./todoRoutes";
import { errorMiddleware } from "./errorMiddleware";

export function createHttpApp(deps: Parameters<typeof createTodoRouter>[0]) {
  const app = express();

  // JSONボディ受け取り（標準ミドルウェア）🧴
  app.use(express.json()); // Express 5.x API にあるよ :contentReference[oaicite:7]{index=7}

  // ルーティング（入口は薄く）🚪✨
  app.use(createTodoRouter(deps));

  // エラーは最後でまとめて変換 🧯
  app.use(errorMiddleware);

  return app;
}
```

---

### 7.3 エラーミドルウェア errorMiddleware.ts 🧯✨

ここも「薄く」ね🥗
（本格エラー設計は後の章でやるけど、最低限あると安心）

```ts
// src/adapters/inbound/http/errorMiddleware.ts
import type { Request, Response, NextFunction } from "express";

export function errorMiddleware(err: unknown, _req: Request, res: Response, _next: NextFunction) {
  // とりあえず最小：詳細は後の章で育てる🌱
  const message = err instanceof Error ? err.message : "Unknown error";
  res.status(500).json({ message });
}
```

Express v5 のエラーハンドリングの基本は公式ガイドにまとまってるよ🧭 ([expressjs.com][2])

---

### 7.4 起動ファイル server.ts 🚀🌐

```ts
// src/adapters/inbound/http/server.ts
import { createHttpApp } from "./createHttpApp";

// ここは仮の依存注入：あなたのプロジェクトのusecase達に差し替えてね😊
// 例：compositionRoot から { addTodo, listTodos, completeTodo } を受け取る感じ✨
import { buildTodoUseCases } from "../../compositionRoot/buildTodoUseCases";

const port = Number(process.env.PORT ?? 3000);

const deps = buildTodoUseCases();
const app = createHttpApp(deps);

app.listen(port, () => {
  console.log(`HTTP server listening on http://localhost:${port}`);
});
```

---

## 8 起動コマンド 🏃‍♀️💨

```json
// package.json
{
  "scripts": {
    "dev:http": "tsx watch src/adapters/inbound/http/server.ts"
  }
}
```

`tsx` は TypeScriptを実行しやすい定番ツールとして使われてるよ⚡ ([GitHub][5])

---

## 9 動作チェック まずは3発だけ撃とう 💥😊

PowerShellだと `curl` が別物なことがあるので、`curl.exe` を使うと安定🙆‍♀️

### 9.1 追加 POST /todos 📝

```powershell
curl.exe -X POST http://localhost:3000/todos `
  -H "Content-Type: application/json" `
  -d "{\"title\":\"牛乳を買う\"}"
```

### 9.2 一覧 GET /todos 📋

```powershell
curl.exe http://localhost:3000/todos
```

### 9.3 完了 POST /todos/:id/complete ✅

```powershell
curl.exe -X POST http://localhost:3000/todos/123/complete
```

---

## 10 Controllerが薄いかチェックする ✅🥗✨

ControllerでやってOK👇

* ✅ `req` から必要情報を拾う
* ✅ DTOを作る
* ✅ usecaseを呼ぶ
* ✅ `res.json()` で返す

Controllerでやったら太るやつ👇

* ❌ 業務ルール（「空文字禁止」など）をガッツリ書く
* ❌ 状態遷移（完了二重適用の判断）をする
* ❌ Repositoryを直接触る

「太った瞬間に中心が汚れる」って覚えてね😱🧼

---

## 11 AIに頼るならここが安全 🤖💖

### 11.1 ルーティング雛形を作らせるプロンプト 📝

```txt
Express v5 + TypeScript で Router を作ってください。
制約：
- ルート内は「reqから値→DTO→usecase.execute→res.json」のみ
- ドメイン/ユースケース側は express を import しない
- ルートは GET /todos, POST /todos, POST /todos/:id/complete
```

### 11.2 自爆防止チェック質問 🔍⚠️

```txt
このHTTPアダプタのコードは「usecase/domainがHTTPを知らない」を守れていますか？
express型(Request/Response)が中心へ漏れていないかも確認して。
```

---

## 12 まとめ 🎁💕

* HTTPは **Inbound Adapter** として追加するだけ🌐🔌
* ルーティングは **ユースケース呼ぶだけ**にして薄く🥗✨
* Express v5 は async/await の扱いが楽で、エラーハンドラへ流せるのが嬉しい🧯 ([expressjs.com][2])
* 次章で **Request→DTO変換とレスポンス整形**をキレイにするよ🔁📮💖

次の「第30章」も、この流れのまま気持ちよくいけるよ〜！😊🌸

[1]: https://expressjs.com/2024/10/15/v5-release.html?utm_source=chatgpt.com "Introducing Express v5: A New Era for the Node. ..."
[2]: https://expressjs.com/en/guide/error-handling.html?utm_source=chatgpt.com "Error handling"
[3]: https://expressjs.com/en/5x/api.html?utm_source=chatgpt.com "Express 5.x - API Reference"
[4]: https://www.npmjs.com/package/%40types/express?utm_source=chatgpt.com "types/express"
[5]: https://github.com/privatenumber/tsx?utm_source=chatgpt.com "privatenumber/tsx: ⚡️ TypeScript Execute | The easiest ..."
[6]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
