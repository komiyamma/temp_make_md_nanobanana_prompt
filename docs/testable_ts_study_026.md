# 第26章：境界でエラー変換（例外→結果、結果→表示）🔁🧯

![testable_ts_study_026_exception_translation.png](./picture/testable_ts_study_026_exception_translation.png)

✨この章のテーマはシンプル👇
**「エラーは“境界”で翻訳する」**です😊📚

---

## 1) この章でできるようになること🎯🧪* 外側（HTTP/DB/ファイル等）

が投げる **例外（throw）** を、中心が扱いやすい **結果（Result）** に変換できる🧩


* 中心が返した **結果（Result）** を、UI/CLI/HTTPレスポンスなどの **表示・返し方** に変換できる🎀
* 「try/catch が散らばって地獄😵‍💫」を卒業できる✨

---

## 2) まず結論：エラーは3段階で“姿が変わる”👻➡️

📦➡️🖥️エラーは同じ“失敗”でも、置き場所で最適な形が違うよ〜って話です😊



### A. 外の世界のエラー（例外）

💥* `fetch` が落ちた、JSON壊れてた、タイムアウトした…みたいなやつ


* だいたい **例外（throw）** の形で来る

### B. 中心のエラー（扱いやすい結果）

📦* 中心は「分岐して処理したい」ので、**Result** みたいな形が強い💪



### C. 表示のエラー（人に見せる形）

🖥️💬* CLIなら「メッセージ＋終了コード」


* Webなら「HTTPステータス＋JSON」
* アプリなら「トースト表示」など✨

👉 **境界が翻訳者**です🔁🧑‍🏫

---

## 3) ハンズオン：HTTP失敗 → 中心の結果 → CLI表示 を1本でつなぐ🔗🌐🧪ここでは「ユーザー情報を取りに行って挨拶文を作る」ミニ例でいきます😊💕

---

### 3-1) まずは Result 型を用意する📦✨

```ts
// src/core/result.ts
export type Ok<T> = { ok: true; value: T };
export type Err<E> = { ok: false; error: E };
export type Result<T, E> = Ok<T> | Err<E>;

export const ok = <T>(value: T): Ok<T> => ({ ok: true, value });
export const err = <E>(error: E): Err<E> => ({ ok: false, error });

export const isOk = <T, E>(r: Result<T, E>): r is Ok<T> => r.ok;
export const isErr = <T, E>(r: Result<T, E>): r is Err<E> => !r.ok;

export const map = <T, E, U>(r: Result<T, E>, f: (v: T) => U): Result<U, E> =>
  isOk(r) ? ok(f(r.value)) : r;

export const mapErr = <T, E, F>(r: Result<T, E>, f: (e: E) => F): Result<T, F> =>
  isErr(r) ? err(f(r.error)) : r;

export const unwrapOr = <T, E>(r: Result<T, E>, fallback: T): T =>
  isOk(r) ? r.value : fallback;
```

---

### 3-2) 中心が扱う「エラー型」を決める（ドメイン＋インフラ）

🧠🧯「第25章」の分類を使って、**ドメイン由来**と**インフラ由来**を分けたまま、中心では union で扱えるようにします😊



```ts
// src/core/errors.ts
export type DomainError =
  | { kind: "UserNotFound"; userId: string }
  | { kind: "InvalidUserId"; reason: string };

export type InfraError =
  | { kind: "NetworkUnavailable"; detail: string; cause?: unknown }
  | { kind: "Timeout"; ms: number; cause?: unknown }
  | { kind: "BadResponse"; status: number; body?: string };

export type AppError = DomainError | InfraError;
```

---

### 3-3) 境界（Port）

を切る：中心は interface だけを見る👀🧩

```ts
// src/core/ports.ts
import type { Result } from "./result";
import type { AppError } from "./errors";

export type User = { id: string; name: string };

export interface UserGateway {
  fetchUser(userId: string): Promise<Result<User, AppError>>;
}
```

---

### 3-4) 外側（Adapter）

：例外をキャッチして Result に変換する🧯➡️📦ここが第26章のど真ん中✨
**外側の例外を“中心が扱える形”へ翻訳**します🔁

```ts
// src/adapters/fetchUserGateway.ts
import type { UserGateway, User } from "../core/ports";
import { ok, err, type Result } from "../core/result";
import type { AppError } from "../core/errors";

export class FetchUserGateway implements UserGateway {
  constructor(
    private readonly baseUrl: string,
    private readonly timeoutMs = 5000
  ) {}

  async fetchUser(userId: string): Promise<Result<User, AppError>> {
    const url = `${this.baseUrl}/users/${encodeURIComponent(userId)}`;

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.timeoutMs);

    try {
      const res = await fetch(url, { signal: controller.signal });

      if (res.status === 404) {
        return err({ kind: "UserNotFound", userId });
      }
      if (!res.ok) {
        const body = await safeText(res);
        return err({ kind: "BadResponse", status: res.status, body });
      }

      const data = (await res.json()) as { id: string; name: string };
      return ok({ id: data.id, name: data.name });
    } catch (e) {
      // ここで“例外”を中心に持ち込まない✨（Resultに変換！）
      const isAbort = e instanceof DOMException && e.name === "AbortError";
      if (isAbort) {
        return err({ kind: "Timeout", ms: this.timeoutMs, cause: e });
      }
      return err({ kind: "NetworkUnavailable", detail: "fetch failed", cause: e });
    } finally {
      clearTimeout(timer);
    }
  }
}

async function safeText(res: Response): Promise<string | undefined> {
  try {
    return await res.text();
  } catch {
    return undefined;
  }
}
```

> ここで `cause` を持たせておくと、「元の原因（根っこ）」をログで追いやすいよ〜ってやつです🕵️‍♀️✨（JS の `Error.cause` も同じ狙い！）([MDNウェブドキュメント][1])

---

### 3-5) 中心（UseCase）

：例外ゼロで分岐できる🥰🧪

```ts
// src/core/usecase.ts
import type { UserGateway } from "./ports";
import { err, ok, type Result } from "./result";
import type { AppError } from "./errors";

export async function buildGreeting(
  userId: string,
  gateway: UserGateway
): Promise<Result<string, AppError>> {
  if (!userId || userId.trim().length < 3) {
    return err({ kind: "InvalidUserId", reason: "3文字以上にしてね" });
  }

  const r = await gateway.fetchUser(userId);

  if (!r.ok) {
    // 中心は “型で分岐” できるのが最高✨
    return r;
  }

  return ok(`こんにちは、${r.value.name}さん😊🌸`);
}
```

---

### 3-6) 表示（Presentation）

：Result を “見せる形” に変換する🖥️🎀ここが「結果→表示」の翻訳ポイント💡



```ts
// src/presentation/cliView.ts
import type { AppError } from "../core/errors";
import type { Result } from "../core/result";

export function renderCli(result: Result<string, AppError>): { message: string; exitCode: number } {
  if (result.ok) {
    return { message: result.value, exitCode: 0 };
  }

  const e = result.error;
  switch (e.kind) {
    case "InvalidUserId":
      return { message: `IDが変かも…👉 ${e.reason} 😵‍💫`, exitCode: 2 };

    case "UserNotFound":
      return { message: `そのユーザーは見つからなかったよ…😢（${e.userId}）`, exitCode: 1 };

    case "Timeout":
      return { message: `通信がタイムアウトしたよ…⏰💦 もう一回やってみて🙏`, exitCode: 3 };

    case "NetworkUnavailable":
      return { message: `ネットワークが不安定かも…📶💭 少し待って再挑戦してね🙏`, exitCode: 3 };

    case "BadResponse":
      return { message: `サーバーが変な返事した😵（status=${e.status}）`, exitCode: 4 };

    default: {
      // exhaustivenessチェック（型が増えたらここで気づける✨）
      const _never: never = e;
      return { message: `予期しないエラー🧯 ${String(_never)}`, exitCode: 99 };
    }
  }
}
```

---

### 3-7) main：つなぐだけ（組み立て場所）

🏗️🔗

```ts
// src/main.ts
import { FetchUserGateway } from "./adapters/fetchUserGateway";
import { buildGreeting } from "./core/usecase";
import { renderCli } from "./presentation/cliView";

async function main() {
  const gateway = new FetchUserGateway("https://example.com/api");
  const result = await buildGreeting("komi", gateway);

  const view = renderCli(result);
  console.log(view.message);
  process.exitCode = view.exitCode;
}

main().catch((e) => {
  // “最終防衛線”だけは置いてOK（ここに落ちるのはバグ寄り）
  console.error("Unexpected crash 🧯", e);
  process.exitCode = 99;
});
```

---

## 4) テスト：中心は Result だからめっちゃ書きやすい🧪💖Vitest だと `expect` が素直で気持ちいいです😊（`expect` API は公式にもまとまってるよ）

([Vitest][2])



```ts
// src/core/usecase.test.ts
import { describe, expect, test } from "vitest";
import { buildGreeting } from "./usecase";
import { err, ok } from "./result";
import type { UserGateway } from "./ports";

test("ユーザーが見つからないときはUserNotFoundになる😢", async () => {
  const stub: UserGateway = {
    fetchUser: async () => err({ kind: "UserNotFound", userId: "nope" }),
  };

  const r = await buildGreeting("nope", stub);
  expect(r.ok).toBe(false);
  if (!r.ok) expect(r.error.kind).toBe("UserNotFound");
});

test("成功すると挨拶文が返る😊🌸", async () => {
  const stub: UserGateway = {
    fetchUser: async () => ok({ id: "a", name: "こみやんま" }),
  };

  const r = await buildGreeting("aaa", stub);
  expect(r.ok).toBe(true);
  if (r.ok) expect(r.value).toContain("こんにちは");
});
```

---

## 5) この章の「設計のコツ」まとめ💡✨### ✅ 例外→結果（外側でやる）* `try/catch` は **外側（Adapter）

に寄せる**


* 例外は **Result の Err に変換**して中心に渡す
* 原因追跡したいなら **cause を残す**（ログで神になる🕵️‍♀️）([MDNウェブドキュメント][1])

### ✅ 結果→表示（表示層でやる）* 中心の `AppError` を見て、**メッセージ/ステータス/終了コード**に変換


* 中心に「HTTP 404 とか exitCode」とかを持ち込まない🙅‍♀️✨

---

## 6) よくある事故ポイント😵‍💫🧨* 中心で `throw` し始めて、また try/catch が増える（逆戻り）

🔙


* 例外を握りつぶして「よくわからん」で返す（デバッグ不能）🫥
* 表示用メッセージを中心で作る（UI都合が侵入）🚫
* エラー型が巨大になりすぎる（粒度は“必要最小”でOK）✂️

---

## 7) AI（Copilot/Codex）

に頼ると速いところ🤖💨そのままコピペで使えるプロンプト例👇✨



* 「`AppError` の union に対して、`renderCli()` の switch を exhaustiveness チェック付きで作って」
* 「`FetchUserGateway` の `fetch` 例外を `Timeout/NetworkUnavailable/BadResponse` にマッピングして」
* 「`buildGreeting()` のテストケースを5個列挙して、Vitestで雛形を書いて」

※ただし「どこが境界か」「どこで翻訳するか」は、あなたが決めるところだよ〜🧠💖

---

## 8) ちょい最新メモ（2026年っぽさ）

📌🪄* TypeScript は **5.9 系**が最新として配布されていて、GitHub でも 5.9.3 が “Latest” 扱いになってるよ📦✨ ([GitHub][3])


* Node.js は **v24 が Active LTS**で、2026-01-13 に **v24.13.0 (LTS)** のセキュリティリリースが出てるよ🛡️([Node.js][4])

---

## 9) 次章につながる“ひとこと予告”🍱🧪第27章は「どこをユニットで守って、どこを結合で確認する？」の**粒度設計**だよ〜😊
今日作った「中心＝Resultで安定」構造が、そのまま最強の土台になります💪✨

[1]: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Error/cause?utm_source=chatgpt.com "Error: cause - JavaScript - MDN Web Docs"
[2]: https://vitest.dev/api/expect.html?utm_source=chatgpt.com "expect"
[3]: https://github.com/microsoft/typescript/releases?utm_source=chatgpt.com "Releases · microsoft/TypeScript"
[4]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
