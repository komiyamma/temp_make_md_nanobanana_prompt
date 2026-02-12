# 第46章：非同期テスト基礎（async/await）⏳

![非同期の砂時計](./picture/tdd_ts_study_046_async_hourglass.png)

## 🎯 目的

* Promise（非同期）の処理でも、TDDをいつも通り **Red→Green→Refactor** で回せるようになる💪💕
* **成功（resolve）/ 失敗（reject）** のテストを、ブレずに書けるようになる✅
* 「await忘れでテストが“嘘のGreen”になる事故」を防げるようになる🚑💥

---

## 📚 学ぶこと（今日の超重要ポイント3つ）🔑

### 1) Vitestは「テスト関数がPromiseを返したら、解決まで待つ」⏳

つまり `async () => { ... }` にして `await` すればOK、ってことだよ🙂✨ ([vitest.dev][1])

### 2) `expect(...).resolves / rejects` は **await（またはreturn）必須** 🙅‍♀️

`resolves/rejects` は “Promiseをほどいてから matcher をつなげる” 機能。
ただし matcher 自体も Promise になるので、**awaitしないと事故りやすい**よ⚠️ ([vitest.dev][2])

### 3) Vitestは基本「doneコールバック」方式を推奨しない（= 使わない方が安全）🧨

Jestの `done` みたいな書き方は、Vitestでは **async/await に寄せる**のが基本だよ✅ ([vitest.dev][3])

---

## 🧪 手を動かす：Promiseの成功/失敗を2本で固定しよう💞

### お題：UserService（ユーザー表示名を返す）👤✨

* ユーザーがいれば表示名を返す（resolve）✅
* ユーザーがいなければ `USER_NOT_FOUND` で失敗（reject）❌

---

### Step 1：まずテストを書く（Red）🚦🔴

`tests/userService.test.ts`

```ts
import { describe, it, expect } from "vitest";
import { InMemoryUserRepo, UserService } from "../src/userService";

describe("UserService.getDisplayName", () => {
  it("ユーザーが見つかると表示名を返す（resolve）😊", async () => {
    const repo = new InMemoryUserRepo([{ id: "u1", name: "Alice" }]);
    const service = new UserService(repo);

    await expect(service.getDisplayName("u1")).resolves.toBe("Alice");
  });

  it("ユーザーがいないと USER_NOT_FOUND で失敗する（reject）😵‍💫", async () => {
    const repo = new InMemoryUserRepo([]);
    const service = new UserService(repo);

    await expect(service.getDisplayName("missing")).rejects.toThrow("USER_NOT_FOUND");
  });
});
```

ここでポイント💡

* `await expect(...).resolves...` ✅（awaitが要る） ([vitest.dev][2])
* `await expect(...).rejects...` ✅（rejectも同じくawaitが要る） ([vitest.dev][2])

---

### Step 2：最小実装で通す（Green）🚦🟢

`src/userService.ts`

```ts
export type User = { id: string; name: string };

export interface UserRepo {
  getById(id: string): Promise<User | null>;
}

export class InMemoryUserRepo implements UserRepo {
  constructor(private readonly users: User[]) {}

  async getById(id: string): Promise<User | null> {
    return this.users.find((u) => u.id === id) ?? null;
  }
}

export class UserService {
  constructor(private readonly repo: UserRepo) {}

  async getDisplayName(id: string): Promise<string> {
    const user = await this.repo.getById(id);
    if (!user) throw new Error("USER_NOT_FOUND");
    return user.name;
  }
}
```

---

### Step 3：整理（Refactor）🧹✨（“例外を仕様にする”の第一歩）

いきなり凝らなくてOKだけど、軽く「意味のあるエラー」にして読みやすくしよう💗

```ts
export class UserNotFoundError extends Error {
  constructor() {
    super("USER_NOT_FOUND");
  }
}
```

そして `throw new UserNotFoundError()` にすると、意図が伝わりやすいよ🙂✨
（テストは `toThrow("USER_NOT_FOUND")` のままでもOK）

---

## ⚠️ あるある事故集（ここ超大事）💥🚨

### 事故①：await/return を忘れて “嘘Green” 😇（一番こわい）

❌ダメ例（これ、テストが先に終わってしまう可能性があるよ）

```ts
it("ダメ例", async () => {
  expect(service.getDisplayName("u1")).resolves.toBe("Alice"); // awaitしてない！
});
```

✅直す

```ts
await expect(service.getDisplayName("u1")).resolves.toBe("Alice");
```

`resolves/rejects` は await（またはreturn）しようね💪 ([vitest.dev][2])

---

### 事故②：asyncに「toThrow」を使ってしまう🙅‍♀️

❌これはダメ（asyncは“投げる”んじゃなくて“rejectする”）

```ts
expect(() => service.getDisplayName("missing")).toThrow();
```

✅こうする

```ts
await expect(service.getDisplayName("missing")).rejects.toThrow("USER_NOT_FOUND");
```

---

### 事故③：done方式に逃げてカオス化😵‍💫（やめよう）

Vitestは `done` を基本サポートしない/推奨しないので、**async/await に寄せよう**ね✅ ([vitest.dev][3])

---

## 🧪 追加ミニ練習（すぐ強くなる）💪✨

### 練習A：resolve側を「return派」で書いてみる🧁

`async` を付けないなら、`return` でもOKだよ（“Promiseを返す＝待ってくれる”） ([vitest.dev][1])

```ts
it("return派（async無し）🙂", () => {
  const repo = new InMemoryUserRepo([{ id: "u1", name: "Alice" }]);
  const service = new UserService(repo);

  return expect(service.getDisplayName("u1")).resolves.toBe("Alice");
});
```

---

### 練習B：reject理由をもう少し厳密にする🎯

たとえば「エラー型も確認する」とかね✨
（ここはやりすぎ注意だけど、覚えておくと便利💗）

```ts
await expect(service.getDisplayName("missing")).rejects.toBeInstanceOf(Error);
```

---

## 🤖 AIの使い方（“テストが仕様”を守るプロンプト）🪄💞

コピペで使えるやつ置いとくね😍👇

* **テスト分割を手伝わせる**
  「この仕様を “成功/失敗” の2テストに分けて。テスト名はGiven/When/Thenの雰囲気で3案」

* **await忘れ検査**
  「このVitestテストコード、await/return忘れで嘘Greenになる箇所がないかチェックして、理由つきで直して」

* **rejectの書き方を相談**
  「このasync関数の失敗を、rejectsで最小限にテストしたい。`toThrow` との違いも含めて提案して」

---

## ✅ チェック（合格ライン）🎓✨

* `resolves/rejects` を **await or return** できてる✅ ([vitest.dev][2])
* asyncの失敗は `rejects` で書けてる✅
* 「await忘れ」のダメ例を見て、危険性を説明できる✅
* done方式に逃げずに書けてる✅ ([vitest.dev][3])

---

## おまけ：今日のひとこと（覚え方）🧠💡

**「asyncは throw じゃなくて reject としてテストする！」**
**「resolves/rejects は await を添える！」**
これだけで非同期テスト、かなり安定するよ〜〜😍🧪✨

[1]: https://vitest.dev/api/?utm_source=chatgpt.com "Test API Reference"
[2]: https://vitest.dev/api/expect.html?utm_source=chatgpt.com "expect"
[3]: https://vitest.dev/guide/migration.html?utm_source=chatgpt.com "Migration Guide"
