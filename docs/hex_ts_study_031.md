# 第31章：HTTP導入③：ユースケースはHTTPを知らない🙅‍♀️

![hex_ts_study_031[(./picture/hex_ts_study_031_usecase_blindness_to_http.png)

## 1) この章のゴール 🎯💕

ここまで作ってきた **中心（ドメイン＋ユースケース）** を、HTTPを足しても **1行も直さずに** 動かせるようにするよ〜😊✨
できるようになることはこの3つ👇

* ✅ 「中心がHTTPを知らない」状態か、チェックできる
* ✅ HTTPの入口（Inbound Adapter）を追加しても中心が無傷でいける
* ✅ “変更するときに触る場所”を迷わない（＝保守が怖くなくなる！）🛡️

---

## 2) まず結論：ユースケースは「HTTP語」をしゃべらない🧠🚫

ユースケースが知っていいのは **アプリのルール** だけ。
HTTPの都合（ステータスコードとかヘッダとか）は **全部、入口側で翻訳** するよ🧩✨

### ありがちNG（中心が汚れてるサイン）😱

* `req` / `res` / `reply` がユースケースに入ってくる
* `statusCode` をユースケースが返す
* `express` / `fastify` の型を `app/` や `domain/` が import してる
* `Request` / `Response` をDTOとして使ってる

### 正しいOK（中心の言葉）😊✅

* 入力：`AddTodoInput` みたいな **素朴なDTO**
* 出力：`AddTodoOutput` みたいな **素朴なDTO**
* 失敗：`DomainError` / `ValidationError` みたいな **仕様のエラー**

---

## 3) ミッション：HTTPを足しても中心を1ミリも動かさない✅🔁

やることはシンプルに5ステップだよ〜😊

1. 🕵️‍♀️ 中心がHTTPを参照してないかチェック
2. 🌐 HTTP Adapter（入口）を作る
3. 🔁 Request→DTO、DTO→Responseに“翻訳”する
4. 🧩 Composition Rootで合体（依存の組み立て）
5. 🧪 テストで「中心が無傷」を証明する

---

## 4) ステップ1：中心の“汚染チェック”🧹🕵️‍♀️

VS Codeの検索でOK！
`src/domain` と `src/app` を対象に、こういう単語が **出てきたら黄色信号** 🚥

* `fastify`, `express`
* `Request`, `Response`, `IncomingMessage`, `ServerResponse`
* `reply`, `res`, `req`
* `statusCode`, `headers`, `cookie`

> 出ないのが理想✨ 出たら「それ、Adapter側に追い出せない？」って考えよ😊

---

## 5) ステップ2：Inbound Port（ユースケースの入口）は“HTTP抜き”で定義する🔌✨

ユースケースのインターフェースは、HTTPを一切含めないよ🙅‍♀️

```ts
// src/app/ports/in/AddTodoUseCase.ts
export type AddTodoInput = { title: string };
export type AddTodoOutput = { id: string; title: string; completed: boolean };

export interface AddTodoUseCase {
  execute(input: AddTodoInput): Promise<AddTodoOutput>;
}
```

この時点で、ユースケースは「ただの関数っぽい入口」になる😊💕

---

## 6) ステップ3：HTTP Adapterは“翻訳係”に徹する🧩🌐

ここが第31章の主役！
HTTP Adapterは **薄いほど正義** 🥗✨（太ると中心が汚れる…！）

例として Fastify でいくね（TS相性よし＆型の話がしやすい）😊
FastifyのTypeScript周りの公式ドキュメントもあるよ。([Fastify][1])

```ts
// src/adapters/inbound/http/buildServer.ts
import Fastify from "fastify";
import type { AddTodoUseCase } from "../../../app/ports/in/AddTodoUseCase";

export function buildServer(addTodo: AddTodoUseCase) {
  const fastify = Fastify({ logger: true });

  fastify.post("/todos", async (req, reply) => {
    // ① Request → 入口用の形に取り出す（ここは“翻訳”）
    const body = (req.body ?? {}) as { title?: unknown };
    const rawTitle = typeof body.title === "string" ? body.title : "";

    // ② 境界で軽くバリデーション（ユーザーに優しいエラーにする）
    const title = rawTitle.trim();
    if (title.length === 0) {
      return reply.code(400).send({ error: "title is required" });
    }

    try {
      // ③ DTOにしてユースケースへ（中心はHTTPを知らない）
      const out = await addTodo.execute({ title });

      // ④ 出力DTO → Response（ここも“翻訳”）
      return reply.code(201).send(out);
    } catch (e) {
      // ⑤ 中心のエラーをHTTPに“翻訳”
      // 例：ValidationErrorなら422、DomainErrorなら409…みたいに
      return reply.code(422).send({ error: "invalid input" });
    }
  });

  return fastify;
}
```

ポイントはこれ👇😊✨

* **ユースケースを呼ぶ前後だけ** で完結してる
* ここに「業務ルール（完了の二重適用禁止とか）」を書き始めたら危険⚠️
* 入口のバリデーションは“見た目の親切”としてOKだけど、**最終防衛線はドメイン側** にも残してね🛡️

---

## 7) ステップ4：確認！ユースケース側はHTTPと無関係🙅‍♀️💖

ユースケースの実装例（HTTPの気配ゼロ！）

```ts
// src/app/usecases/AddTodoService.ts
import type { AddTodoUseCase, AddTodoInput, AddTodoOutput } from "../ports/in/AddTodoUseCase";
import type { TodoRepository } from "../ports/out/TodoRepository";
import { Todo } from "../../domain/Todo";
import type { IdGeneratorPort } from "../ports/out/IdGeneratorPort";

export class AddTodoService implements AddTodoUseCase {
  constructor(
    private readonly repo: TodoRepository,
    private readonly idGen: IdGeneratorPort
  ) {}

  async execute(input: AddTodoInput): Promise<AddTodoOutput> {
    const todo = Todo.create({ id: this.idGen.newId(), title: input.title });
    await this.repo.save(todo);
    return { id: todo.id, title: todo.title, completed: todo.completed };
  }
}
```

ここが気持ちいいところ〜〜〜😊💕
HTTPに変えても、GraphQLに変えても、CLIに戻しても、中心は同じまま🔁✨

---

## 8) ステップ5：Composition Rootで合体（ここだけが“newの場所”）🧩🏗️

最後に「どのAdapterを使うか」を決めて合体させるよ！

```ts
// src/main.ts
import { buildServer } from "./adapters/inbound/http/buildServer";
import { AddTodoService } from "./app/usecases/AddTodoService";
import { InMemoryTodoRepository } from "./adapters/outbound/InMemoryTodoRepository";
import { RandomUuidGenerator } from "./adapters/outbound/RandomUuidGenerator";

const repo = new InMemoryTodoRepository();
const idGen = new RandomUuidGenerator();

const addTodo = new AddTodoService(repo, idGen);

const server = buildServer(addTodo);
await server.listen({ port: 3000, host: "127.0.0.1" });
```

依存の向きはこう👇

* 外側（HTTP）が中心（UseCase）を知っていい👌
* 中心（UseCase）は外側（HTTP）を知らない🙅‍♀️

---

## 9) 動作確認：PowerShellから叩いてみよ〜🙌✨

Windowsならこれがラクだよ😊（JSONも扱いやすい✨）

```ps1
Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:3000/todos" `
  -ContentType "application/json" `
  -Body '{"title":"Buy milk"}'
```

返ってきたJSONが `AddTodoOutput` の形ならOK✅🎉

---

## 10) 「中心が無傷」をテストで証明する🧪✨

### ① ユースケース単体テスト（最優先）💪

ここはHTTPが一切いらないのが最高😊💕

```ts
import { describe, it, expect } from "vitest";
import { AddTodoService } from "./AddTodoService";
import { InMemoryTodoRepository } from "../../adapters/outbound/InMemoryTodoRepository";

describe("AddTodoService", () => {
  it("タイトルが入ったTodoを追加できる", async () => {
    const repo = new InMemoryTodoRepository();
    const idGen = { newId: () => "id-1" };
    const uc = new AddTodoService(repo, idGen);

    const out = await uc.execute({ title: "hello" });

    expect(out).toEqual({ id: "id-1", title: "hello", completed: false });
  });
});
```

### ② HTTP Adapterテスト（“翻訳”だけを見る）🌐🧩

Fastifyは `inject` があって便利だよ😊（ネットワーク不要）

```ts
import { describe, it, expect } from "vitest";
import { buildServer } from "./buildServer";

describe("HTTP adapter /todos", () => {
  it("POSTで201とTodoを返す", async () => {
    const fakeAddTodo = { execute: async () => ({ id: "1", title: "a", completed: false }) };
    const app = buildServer(fakeAddTodo);

    const res = await app.inject({
      method: "POST",
      url: "/todos",
      payload: { title: "a" },
    });

    expect(res.statusCode).toBe(201);
  });
});
```

---

## 11) ここで“第31章クリア”のチェックリスト✅🎀

これが全部YESなら、めちゃ良い感じ！😊✨

* ✅ `domain/` と `app/` に `fastify` / `express` の import がない
* ✅ ユースケースの入出力DTOに `statusCode` や `headers` がいない
* ✅ HTTPのエラー表現（400/404/500）はAdapterで決めてる
* ✅ 入口（HTTP）を追加してもユースケースのテストはそのまま通る
* ✅ 「翻訳」と「ルール」が混ざってない（Adapterが薄い🥗）

---

## 12) おまけ：2026の“今どき”メモ📝✨

* Node.js は v24 が Active LTS になっていて、セキュリティリリースも継続中だよ🛡️([nodejs.org][2])
* TypeScriptは “ネイティブ移植（TypeScript 7のプレビュー）” の話も進んでて、ビルド高速化が大きなテーマになってるよ🚀([Microsoft Developer][3])

---

## まとめ 🎁💖

第31章の合言葉はこれっ✨

* 🛡️ **中心を守る**
* 🧩 **HTTPは翻訳（Adapterの仕事）**
* 🔌 **中心はDTOとPortだけを見る**

次は「テストが一気に楽になる」ゾーン（ユースケース単体テストの強化）に入ると、さらに気持ちよくなるよ〜😊🧪✨

[1]: https://fastify.io/docs/latest/Reference/TypeScript/?utm_source=chatgpt.com "TypeScript"
[2]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[3]: https://developer.microsoft.com/blog/typescript-7-native-preview-in-visual-studio-2026?utm_source=chatgpt.com "TypeScript 7 native preview in Visual Studio 2026"
