# 第49章：fetch境界（ネット無しでテスト）🌐

![オフラインテスト](./picture/tdd_ts_study_049_offline.png)

## 🎯この章でできるようになること

* `fetch` を **そのまま直呼びせず**、差し替え可能な「境界」にできるようになる🔌✨
* **ネット無し**で、成功/404/500/通信失敗 をテストできるようになる🧪💪
* 「HTTPの失敗」を **設計として整理**して、呼び出し側が扱いやすい形にできる🧩💡

> ちなみに Node の `fetch` は内部で Undici が使われる前提で説明するよ🫶（だから“ネットワーク層は別物”として分けると、テストが安定しやすい！） ([Node.js][1])

---

## 🧠まずイメージ：なぜ `fetch` 直呼びがツラいの？😵‍💫

![画像を挿入予定](./picture/tdd_ts_study_049_fetch_bypass.png)

`fetch` をビジネスロジックの真ん中で呼ぶと…

* テストがネット状況に左右される（落ちる/遅い/たまに失敗）💥
* 404/500 の扱いが **各所に散らかる**（if地獄）🌀
* テストで「APIが返す値」を作るのが大変（毎回 Response 作るのしんどい）🫠

なのでこの章は、**`fetch` を“境界”に追い出して**、ロジック中心を守るよ🏰✨

---

## ✅今回の方針：`fetch` を注入（DI）して差し替える🔁

ポイントはこれだけ👇💗

* 本番：`new HttpClient(fetch)`（本物の `fetch` を渡す）
* テスト：`new HttpClient(fakeFetch)`（偽物 `fetch` を渡す）

これで **ネット無しで回る**ようになるよ〜！🚀

---

## 🧪ハンズオン：HTTPラッパーをTDDで作ろう（成功/404/500/通信失敗）

ここでは「取得してJSONを返す」最小の `HttpClient` を作るよ🧁
戻り値は **Result型**（成功/失敗を値で返す）にするね✨

---

### 0) ファイル構成📁

こんな感じでOK！（名前は好みで👍）

```txt
src/
  http/
    httpClient.ts
tests/
  httpClient.test.ts
```

---

## 1) まずテストを書く（Red）🔴🧪

「200ならJSONが取れる」からいくよ〜！

```ts
// tests/httpClient.test.ts
import { describe, it, expect, vi } from "vitest";
import { HttpClient, type FetchLike } from "../src/http/httpClient";

const makeResponse = (status: number, body: unknown) => ({
  ok: status >= 200 && status < 300,
  status,
  json: async () => body,
  text: async () => JSON.stringify(body),
});

describe("HttpClient.getJson", () => {
  it("200ならokでJSONを返す😊", async () => {
    const fetcher: FetchLike = vi.fn().mockResolvedValue(
      makeResponse(200, { name: "Alice" })
    );

    const client = new HttpClient(fetcher);
    const result = await client.getJson<{ name: string }>("https://example.test/users/1");

    expect(result).toEqual({ ok: true, value: { name: "Alice" } });
  });
});
```

🔎 ここで大事：`fetcher` は **Responseっぽいもの**を返せばOK！
本物の `Response` を頑張って作らなくていいよ🥹✨（テストが軽い！）

---

## 2) 最小実装（Green）🟢✨

次に実装するよ！

```ts
// src/http/httpClient.ts
export type Result<T, E> =
  | { ok: true; value: T }
  | { ok: false; error: E };

export type HttpProblem =
  | { kind: "not_found"; status: 404; url: string }
  | { kind: "server_error"; status: number; url: string }
  | { kind: "http_error"; status: number; url: string }
  | { kind: "network_error"; url: string; message: string };

export type ResponseLike = {
  ok: boolean;
  status: number;
  json(): Promise<unknown>;
  text(): Promise<string>;
};

export type FetchInit = {
  method?: string;
  headers?: Record<string, string>;
  body?: string;
};

export type FetchLike = (url: string, init?: FetchInit) => Promise<ResponseLike>;

export class HttpClient {
  constructor(private readonly fetcher: FetchLike) {}

  async getJson<T>(url: string): Promise<Result<T, HttpProblem>> {
    try {
      const res = await this.fetcher(url, { method: "GET" });

      if (res.ok) {
        const data = (await res.json()) as T;
        return { ok: true, value: data };
      }

      if (res.status === 404) {
        return { ok: false, error: { kind: "not_found", status: 404, url } };
      }

      if (res.status >= 500) {
        return { ok: false, error: { kind: "server_error", status: res.status, url } };
      }

      return { ok: false, error: { kind: "http_error", status: res.status, url } };
    } catch (e) {
      const message = e instanceof Error ? e.message : String(e);
      return { ok: false, error: { kind: "network_error", url, message } };
    }
  }
}
```

💡これで「ネットが落ちたら例外で落ちる」じゃなくて、**失敗も値で返る**から呼び出し側が扱いやすいよ🫶✨

---

## 3) 404のテスト追加（Red→Green）🔴🟢

「見つからない」はよくあるから、仕様として固定しよ🎯

```ts
it("404ならnot_foundになる🥺", async () => {
  const fetcher: FetchLike = vi.fn().mockResolvedValue(
    makeResponse(404, { message: "not found" })
  );

  const client = new HttpClient(fetcher);
  const result = await client.getJson("https://example.test/users/999");

  expect(result).toEqual({
    ok: false,
    error: { kind: "not_found", status: 404, url: "https://example.test/users/999" },
  });
});
```

---

## 4) 500のテスト追加（Red→Green）🔥

サーバ側が死ぬのも、現実では普通にある😇

```ts
it("500ならserver_errorになる💥", async () => {
  const fetcher: FetchLike = vi.fn().mockResolvedValue(
    makeResponse(500, { message: "oops" })
  );

  const client = new HttpClient(fetcher);
  const result = await client.getJson("https://example.test/users/1");

  expect(result).toEqual({
    ok: false,
    error: { kind: "server_error", status: 500, url: "https://example.test/users/1" },
  });
});
```

---

## 5) 通信失敗（fetchがthrow）も固定する（Red→Green）📡💔

Wi-Fi切れた、DNS死んだ、タイムアウト…などなど😭
ここも「たまに落ちる」を潰す大事ポイント！

```ts
it("fetchが例外を投げたらnetwork_errorになる📡💔", async () => {
  const fetcher: FetchLike = vi.fn().mockRejectedValue(new Error("ECONNRESET"));

  const client = new HttpClient(fetcher);
  const result = await client.getJson("https://example.test/users/1");

  expect(result.ok).toBe(false);
  if (!result.ok) {
    expect(result.error.kind).toBe("network_error");
    expect(result.error.message).toContain("ECONNRESET");
  }
});
```

---

## ✨ここまでの“境界”が作れたら勝ち！🏆

この `HttpClient` があると、呼び出し側はこう書けるよ👇💕

```ts
const http = new HttpClient(fetch); // 本物fetchを注入
const r = await http.getJson<{ name: string }>("https://api.example.com/me");

if (r.ok) {
  console.log("こんにちは", r.value.name);
} else {
  switch (r.error.kind) {
    case "not_found":
      // 404のUIとか
      break;
    case "server_error":
      // リトライ候補
      break;
    case "network_error":
      // オフライン案内
      break;
  }
}
```

---

## 🧷補足：どうしても global `fetch` を差し替えたい時（任意）

「既存コードが `fetch(...)` 直呼びで、今すぐ注入に直せない…🥺」って時は、Vitest の `vi.stubGlobal` で一時的に差し替えもできるよ。 ([Vitest][2])

```ts
import { vi, afterEach } from "vitest";

afterEach(() => {
  vi.unstubAllGlobals(); // 戻す
});

vi.stubGlobal("fetch", vi.fn().mockResolvedValue(/* Responseっぽいもの */));
```

ただしこれ、**依存が見えにくくなりがち**だから、基本は「注入」に寄せるのがおすすめだよ〜🙂‍↕️✨ ([Vitest][2])

---

## 🌐もう一段リアルに：MSWで“ネットっぽく”テスト（任意）

「fetchの注入テスト」は超速いけど、
**“実際のHTTPリクエストの形（URL/クエリ/ヘッダ）”も含めて確かめたい**時があるよね👀

その場合は MSW みたいに **リクエストを横取りして返す**方法が便利✨（Node+Vitest向けの案内もあるよ） ([mswjs.io][3])

> 使い分けの目安🍀
>
> * ユニット（速い）：**注入**（この章）
> * 統合（ちょいリアル）：**MSW**（必要なところだけ）

---

## 🤖AIの使いどころ（この章のテンプレ）💬✨

コピペで使えるやつ置いとくね🫶

* 「404/500/通信失敗」をどう扱うべき？（UI/ログ/リトライ方針も含めて）🧭
* `HttpProblem` の union 設計、他に分けるべき種類ある？💡
* テストケースの抜け（例えば 401/403/429）ってどれが優先？🎯
* “やりすぎない”リトライ戦略案を3つ（弱/中/強）で出して⚡️

---

## ✅チェックリスト（できてたら合格🎉）

* [ ] テストが **ネット無し**で全部通る🌈
* [ ] 200/404/500/通信失敗 を **仕様として固定**できた🧪
* [ ] 呼び出し側が `switch (error.kind)` で迷わず分岐できる🧩
* [ ] 例外ログを貼り付けなくても、失敗の種類が見える👀✨

---

## 🧩次章へのつなぎ（第50章）

この章は「HTTPとして成功か失敗か」を整理しただけで、**JSONの中身が正しいか**までは守ってないよ〜！🙈
次は「壊れたデータを入口で弾く」＝**バリデーション/スキーマ**で、型と現実を一致させにいくよ🧷💖（第50章へGO！）

[1]: https://nodejs.org/en/learn/getting-started/fetch?utm_source=chatgpt.com "Node.js Fetch"
[2]: https://vitest.dev/api/vi.html?utm_source=chatgpt.com "Vitest"
[3]: https://mswjs.io/docs/quick-start/?utm_source=chatgpt.com "Quick start"
