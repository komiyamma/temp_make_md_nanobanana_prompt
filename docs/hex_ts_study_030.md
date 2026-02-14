# 第30章：HTTP導入②：Request→DTO変換、Response整形 🔁📮

![hex_ts_study_030[(./picture/hex_ts_study_030_request_processing_flow.png)
![hex_ts_study_030[(./picture/hex_ts_study_030_request_response_dtos.png)

この章は「HTTPの入口（Inbound Adapter）」がやるべき **翻訳** を、ちゃんと“型”と“ルール”で固める回だよ〜😊💖
やることはシンプル！

* リクエスト（params/query/body）→ **UseCase入力DTO** に変換する 🔁
* 返り値（UseCase出力DTO）→ **HTTPレスポンス** に整形する 📦
* 失敗（バリデーション/仕様エラー）→ **標準っぽいエラー形式** に変換する 🧯

---

## 0) 2026/01/23 時点の“最新版メモ”🆕📝

* Node.js は **v24 が Active LTS**（新規ならこれが安心寄り）で、v22/v20 は Maintenance LTS だよ 📌 ([nodejs.org][1])
* TypeScript の安定版は **5.9.3**（npmのlatest）🧩 ([npm][2])
* Zod は **v4系**が安定で、npmのlatestは **4.3.5**（2026/01時点）🔍 ([npm][3])
* エラー形式は **RFC 9457（Problem Details）** が “標準の軸” として使いやすいよ 🧯 ([RFCエディタ][4])

---

## 1) 今回のゴール 🎯✨

この章を終えると…

* 「HTTPの生データ」→「UseCaseが欲しい形」に **迷わず変換**できる 🔁😊
* **入口でバリデーション**して、中心へゴミを持ち込まない 🚯🛡️
* エラー時も、レスポンスが **いつも同じ形** で返せる 📦✨

---

## 2) まず“流れ”を1枚で理解しよ 🗺️🏃‍♀️💨

```text
HTTP Request
  ↓ (params/query/body を読む)
Inbound Adapter（この章）
  ↓ ① validate（入口で！）
  ↓ ② map（UseCase Input DTOへ）
UseCase（中心）
  ↓ Output DTO or Domain/App Error
Inbound Adapter（この章）
  ↓ ③ present（HTTP Responseへ）
HTTP Response
```

ポイントはこれ👇
**中心（UseCase）は “HTTPを1ミリも知らない”** こと！🙅‍♀️🌐

---

## 3) 入口（HTTP Adapter）が「やること / やらないこと」🚪🧩

### やること ✅

* params/query/body を読む 👀
* 文字列→number/boolean などに変換する 🔁
* バリデーションする（空文字NG、UUID形式、長さ制限…）🧪
* UseCase入力DTOを作る 📮
* UseCaseの結果をHTTPレスポンスへ整形する 📦
* エラーをHTTP向けに変換する（ステータス、形）🧯

### やらないこと ❌

* 業務ルール判断（「完了は二重適用禁止」みたいな本体ルール）🚫
  → それは UseCase / Domain の仕事だよ 🧠🛡️

---

## 4) 今回の方針：Zodで“入口を固める” 🔒🧪✨

TypeScriptの型だけだと、実行時に「変なJSON」が来たとき守れないの🥲
だから入口で **ランタイム検証**するよ！

* Zodは **スキーマ＝型** を作れて便利（v4系が安定）🔍 ([npm][3])

---

## 5) 実装の配置（迷子防止）📁🧭

こんな感じで分けるとスッキリするよ〜😊

* `src/adapters/http/`

  * `todo.schemas.ts`（Zodスキーマ置き場）🧪
  * `todo.mapper.ts`（Request→InputDTO、OutputDTO→Response）🔁
  * `todo.presenter.ts`（成功レスポンス整形）📦
  * `problem.ts`（エラーレスポンス整形）🧯

---

## 6) コード：スキーマ（入口の検問所）🧪🚧

```ts
// src/adapters/http/todo.schemas.ts
import { z } from "zod";

export const AddTodoBodySchema = z.object({
  title: z.string().trim().min(1, "title は必須だよ").max(200, "title は200文字までだよ"),
});

export const TodoIdParamSchema = z.object({
  id: z.string().uuid("id は UUID 形式でね"),
});

export const ListTodosQuerySchema = z.object({
  // 例：?completed=true
  completed: z
    .string()
    .optional()
    .transform((v) => {
      if (v === undefined) return undefined;
      if (v === "true") return true;
      if (v === "false") return false;
      return "INVALID";
    })
    .refine((v) => v !== "INVALID", "completed は true/false だけだよ"),
});
```

ここが気持ちいいポイント💖

* `.trim().min(1)` で「空白だけ」も弾ける ✂️
* queryの `"true"/"false"` を boolean に翻訳できる 🔁

---

## 7) コード：Request → UseCase入力DTO へ変換 🔁📮

UseCase側に、例えばこういうDTOがある想定ね👇（すでに前章までで作ってる感じ）

```ts
// src/app/dto/todo.ts（例）
export type AddTodoInputDto = { title: string };
export type CompleteTodoInputDto = { id: string };
export type ListTodosInputDto = { completed?: boolean };
```

HTTP側で “翻訳関数” を作るよ😊

```ts
// src/adapters/http/todo.mapper.ts
import { ZodError } from "zod";
import {
  AddTodoBodySchema,
  TodoIdParamSchema,
  ListTodosQuerySchema,
} from "./todo.schemas";
import type { AddTodoInputDto, CompleteTodoInputDto, ListTodosInputDto } from "../../app/dto/todo";

export function toAddTodoInput(body: unknown): AddTodoInputDto {
  const parsed = AddTodoBodySchema.parse(body);
  return { title: parsed.title };
}

export function toCompleteTodoInput(params: unknown): CompleteTodoInputDto {
  const parsed = TodoIdParamSchema.parse(params);
  return { id: parsed.id };
}

export function toListTodosInput(query: unknown): ListTodosInputDto {
  const parsed = ListTodosQuerySchema.parse(query);
  return { completed: parsed.completed };
}

// ZodError かどうか判定したい時用（便利）
export function isZodError(err: unknown): err is ZodError {
  return err instanceof ZodError;
}
```

超だいじ📌
**ここで作ったDTOだけ** を UseCase に渡すの。
`request.body` をそのまま投げるのは卒業〜🎓✨

---

## 8) レスポンス整形：成功時の“見せ方”📦✨

成功時も「UseCaseの返り値」をそのまま返すんじゃなく、**HTTPの形**に整えると未来が楽😊💕

```ts
// src/adapters/http/todo.presenter.ts
export type TodoHttpResponse = {
  todo: {
    id: string;
    title: string;
    completed: boolean;
  };
};

export function presentTodo(todo: { id: string; title: string; completed: boolean }): TodoHttpResponse {
  return {
    todo: {
      id: todo.id,
      title: todo.title,
      completed: todo.completed,
    },
  };
}

export type TodosHttpResponse = {
  todos: Array<{ id: string; title: string; completed: boolean }>;
};

export function presentTodos(todos: Array<{ id: string; title: string; completed: boolean }>): TodosHttpResponse {
  return { todos: todos.map((t) => ({ id: t.id, title: t.title, completed: t.completed })) };
}
```

「いまは同じ形じゃん？」って思ってもOK👌
**将来**（フィールド追加/削除、レスポンス互換）で守られるよ🛡️

---

## 9) エラー整形：RFC 9457（Problem Details）で統一 🧯📦

エラーの形が毎回バラバラだと、クライアント側が泣く😭
そこで “標準の型” に寄せるのが強い✨（RFC 9457） ([RFCエディタ][4])

```ts
// src/adapters/http/problem.ts
export type ProblemDetails = {
  type: string;     // エラー種別URI（自分のドメインでOK）
  title: string;    // 人間向け短いタイトル
  status: number;   // HTTP status
  detail?: string;  // 具体説明
  instance?: string;// そのエラーの発生箇所（任意）
  // extension fields: 追加情報も入れてOK（RFC的に許可される）
  errors?: Array<{ path: string; message: string }>;
};

export function problem(params: ProblemDetails): ProblemDetails {
  return params;
}
```

---

## 10) “入口バリデーションエラー”を ProblemDetails にする 🧪➡️🧯

Zodのエラーは情報がたっぷりあるから、それを “整形して返す” と超親切😊💖

```ts
// src/adapters/http/zodProblem.ts
import type { ZodError } from "zod";
import { problem, type ProblemDetails } from "./problem";

export function zodToProblem(err: ZodError, instance?: string): ProblemDetails {
  return problem({
    type: "https://example.com/problems/validation-error",
    title: "Validation Error",
    status: 400,
    detail: "リクエストの形式が正しくないよ",
    instance,
    errors: err.issues.map((i) => ({
      path: i.path.join(".") || "(root)",
      message: i.message,
    })),
  });
}
```

---

## 11) “UseCaseのエラー”を HTTP に翻訳する 🧠➡️🌐

ここがヘキサゴナルの気持ちよさポイント💖
中心が投げるエラー（仕様）を、HTTP向けに **ここでだけ** 変換する！

例：

* `TodoNotFound` → 404
* `AlreadyCompleted` → 409
* `BusinessRuleViolation` → 400 など

```ts
// src/adapters/http/appErrorMap.ts
import { problem, type ProblemDetails } from "./problem";

// 例：中心が返すエラー型（プロジェクトの実体に合わせてね）
export type AppError =
  | { kind: "TodoNotFound"; id: string }
  | { kind: "TodoAlreadyCompleted"; id: string }
  | { kind: "Unexpected"; message: string };

export function appErrorToProblem(err: AppError, instance?: string): ProblemDetails {
  switch (err.kind) {
    case "TodoNotFound":
      return problem({
        type: "https://example.com/problems/todo-not-found",
        title: "Todo Not Found",
        status: 404,
        detail: `Todo が見つからないよ (id=${err.id})`,
        instance,
      });

    case "TodoAlreadyCompleted":
      return problem({
        type: "https://example.com/problems/todo-already-completed",
        title: "Todo Already Completed",
        status: 409,
        detail: `すでに完了してるよ (id=${err.id})`,
        instance,
      });

    default:
      return problem({
        type: "https://example.com/problems/unexpected",
        title: "Unexpected Error",
        status: 500,
        detail: err.message,
        instance,
      });
  }
}
```

---

## 12) ルートで使う：Controllerは“薄く”👩‍🍳✨

フレームワークは何でもいいけど、例として Fastify で書くね（TSとの相性も良い）。
Fastifyは Type Providers など型推論の仕組みもあるよ〜📌 ([Fastify][5])

```ts
// src/adapters/http/todo.routes.ts
import type { FastifyInstance } from "fastify";
import { toAddTodoInput, toCompleteTodoInput, toListTodosInput, isZodError } from "./todo.mapper";
import { presentTodo, presentTodos } from "./todo.presenter";
import { zodToProblem } from "./zodProblem";
import { appErrorToProblem, type AppError } from "./appErrorMap";

export async function registerTodoRoutes(app: FastifyInstance, deps: {
  addTodo: (input: { title: string }) => Promise<{ id: string; title: string; completed: boolean } | AppError>;
  completeTodo: (input: { id: string }) => Promise<{ id: string; title: string; completed: boolean } | AppError>;
  listTodos: (input: { completed?: boolean }) => Promise<Array<{ id: string; title: string; completed: boolean }> | AppError>;
}) {
  app.post("/todos", async (req, reply) => {
    const instance = "/todos";
    try {
      const input = toAddTodoInput(req.body);
      const result = await deps.addTodo(input);

      if (isAppError(result)) {
        const p = appErrorToProblem(result, instance);
        return reply.code(p.status).type("application/problem+json").send(p);
      }

      return reply.code(201).send(presentTodo(result));
    } catch (e) {
      if (isZodError(e)) {
        const p = zodToProblem(e, instance);
        return reply.code(p.status).type("application/problem+json").send(p);
      }
      const p = appErrorToProblem({ kind: "Unexpected", message: "なにか変なことが起きたよ…" }, instance);
      return reply.code(p.status).type("application/problem+json").send(p);
    }
  });

  app.post("/todos/:id/complete", async (req, reply) => {
    const instance = "/todos/:id/complete";
    try {
      const input = toCompleteTodoInput(req.params);
      const result = await deps.completeTodo(input);

      if (isAppError(result)) {
        const p = appErrorToProblem(result, instance);
        return reply.code(p.status).type("application/problem+json").send(p);
      }

      return reply.code(200).send(presentTodo(result));
    } catch (e) {
      if (isZodError(e)) {
        const p = zodToProblem(e, instance);
        return reply.code(p.status).type("application/problem+json").send(p);
      }
      const p = appErrorToProblem({ kind: "Unexpected", message: "なにか変なことが起きたよ…" }, instance);
      return reply.code(p.status).type("application/problem+json").send(p);
    }
  });

  app.get("/todos", async (req, reply) => {
    const instance = "/todos";
    try {
      const input = toListTodosInput(req.query);
      const result = await deps.listTodos(input);

      if (isAppError(result)) {
        const p = appErrorToProblem(result, instance);
        return reply.code(p.status).type("application/problem+json").send(p);
      }

      return reply.code(200).send(presentTodos(result));
    } catch (e) {
      if (isZodError(e)) {
        const p = zodToProblem(e, instance);
        return reply.code(p.status).type("application/problem+json").send(p);
      }
      const p = appErrorToProblem({ kind: "Unexpected", message: "なにか変なことが起きたよ…" }, instance);
      return reply.code(p.status).type("application/problem+json").send(p);
    }
  });
}

function isAppError(v: unknown): v is AppError {
  return typeof v === "object" && v !== null && "kind" in v;
}
```

ここでの美しさ😍✨

* 変換（Request→DTO）✅
* 例外・エラー翻訳（→ProblemDetails）✅
* 表示（Output→Response）✅
* ルール判断は中心へ ✅

---

## 13) 動作チェック（手で叩く）🧪🔨

例：ToDo追加

```bash
curl -X POST http://localhost:3000/todos ^
  -H "Content-Type: application/json" ^
  -d "{\"title\":\"Buy milk\"}"
```

タイトル空で叩くと、入口で 400 ＆ `application/problem+json` が返ってくるはず🧯✨
（この “いつも同じ形” が超大事！）

---

## 14) AI活用：この章での“安全な頼り方”🤖💖

### ✅ 使ってOK（速くなる）

* 「このエンドポイントのZodスキーマ作って」🧪
* 「ProblemDetailsのerrors配列の整形案ちょうだい」🧯
* 「presenterのレスポンス例もっと増やして」📦

### ⚠️ ちょい注意（芯がブレやすい）

* 「UseCaseの責務をHTTPに寄せる提案」→ やめとく🙅‍♀️
* 「domainにrequest型を置こう」→ 全力で拒否🛡️🔥

AIに投げるテンプレ（コピペOK）📝✨

* 「HTTP adapter でやるべきなのは変換と呼び出しだけ。業務ルールは入れない。Request→InputDTO、OutputDTO→Response、Error→ProblemDetails の設計をレビューして」🤖✅

---

## 15) チェックリスト（合格ライン）✅🎀

* [ ] `request.body/params/query` を **直接** UseCaseに渡してない？🙅‍♀️
* [ ] バリデーションは入口で完結してる？🧪
* [ ] エラー時レスポンスが **毎回同じ形**？📦
* [ ] `application/problem+json` を使えてる？🧯 ([RFCエディタ][4])
* [ ] presenterで “見せ方” を固定できてる？✨

---

## 16) 自主課題（ミニ）📝💖

1. `GET /todos?limit=10&offset=20` を追加して、queryをDTOへ変換してみよ🔁
2. Zodのエラーに `errors: [{path,message}]` を入れて返すの、もっと親切にしてみよ😊
3. `TodoNotFound` の `type` を “自分のプロジェクトURL” に寄せて整理してみよ📌

---

次の章（HTTP導入③）で、**「中心コードが1行も変わらない」快感**を確認しに行こうね😊💕

[1]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[2]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "typescript"
[3]: https://www.npmjs.com/package/zod?utm_source=chatgpt.com "Zod"
[4]: https://www.rfc-editor.org/rfc/rfc9457.html?utm_source=chatgpt.com "RFC 9457: Problem Details for HTTP APIs"
[5]: https://fastify.io/docs/latest/Reference/Type-Providers/?utm_source=chatgpt.com "Type-Providers"
