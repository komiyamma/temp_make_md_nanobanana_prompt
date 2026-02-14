# 第29章：レジリエンス基礎（タイムアウト/キャンセル/リトライ）⏳🛑🔁

> 今日のゴール🎯：**「外部が遅い/落ちる/混む」**の“現実”に、アプリが負けないようにする✨
> ここを押さえると、急にプロっぽい安定感が出るよ〜😊💪

---

## 0. レジリエンスってなに？🌧️→🌈

レジリエンス（Resilience）は、ざっくり言うと…

* 外部APIが遅い😵‍💫
* ネットワークが切れる📶💥
* サービスが混んでる🐏🐏🐏
* たまに落ちる🌩️

…みたいな“よくある現実”が起きても、**アプリが固まらず、ユーザーが迷子にならず、運用も追える**状態にすることだよ😊✨

そして、レジリエンスの基本三種の神器がこれ👇

* **タイムアウト**⏳：待ちすぎない
* **キャンセル**🛑：もう要らない処理を止める
* **リトライ**🔁：条件つきで再挑戦する

![リトライ時計：タイミングを見計らって再挑戦[(./picture/err_model_ts_study_029_retry_clock.png)

---

## 1. まず大事な結論💡「リトライは正義じゃない」😇❌

リトライって便利そうだけど、雑にやると地獄になる😱

* **二重注文**🛒🛒（POSTを2回送っちゃった）
* **同時リトライ祭り**🎆（混雑がさらに悪化）
* **ユーザーがずっと待たされる**🫠

だからこの章は、「リトライを増やす」じゃなくて
**“安全にやる条件”を決める**章だよ😊🧠

---

## 2. タイムアウト⏳：待ちすぎないのが優しさ💗

### 2-1. なぜ必要？🧐

外部通信って、失敗しなくても **「ずっと返ってこない」**があるんだよね😵‍💫
だから「○秒待ったら諦める」を設計に入れるのが大事！

### 2-2. いちばん簡単：`AbortSignal.timeout()` ✅

最近の環境だと、`AbortSignal.timeout(ms)` がすごく便利！
指定した時間で自動キャンセルしてくれるよ⏳🛑 ([MDN Web Docs][1])

```ts
export async function fetchWithTimeout(url: string, ms: number): Promise<Response> {
  // ms 経ったら自動で abort される AbortSignal
  const signal = AbortSignal.timeout(ms);
  return fetch(url, { signal });
}
```

### 2-3. フォールバック：`AbortController + setTimeout`（超定番）🧰

`AbortSignal.timeout()` が使えない場面がゼロとは言えないので、
“王道”の書き方も覚えておくと強いよ😊

```ts
export async function fetchWithTimeoutFallback(url: string, ms: number): Promise<Response> {
  const controller = new AbortController();
  const timerId = setTimeout(() => controller.abort(), ms);

  try {
    return await fetch(url, { signal: controller.signal });
  } finally {
    clearTimeout(timerId); // 成功でも失敗でもタイマーお掃除🧹
  }
}
```

### 2-4. タイムアウトになると何が起きる？（超重要）🚨

`fetch` は abort されると、Promise が **`AbortError` で reject** されるよ。([MDN Web Docs][2])
つまり「通信失敗」と同じ流れで例外っぽく来ることがある。

ここでの設計ポイントは👇

* タイムアウトは **インフラ寄りの失敗**（InfraError）になりがち🌩️
* でも、**キャンセルと区別したい**（次でやるよ）🙂

---

## 3. キャンセル🛑：「失敗」じゃないこともある🙂✨

たとえば…

* 検索中に、別のキーワードを打ち直した⌨️💨
* 画面遷移した➡️
* モーダル閉じた❌

このとき、前の通信は「失敗」ってより **“不要になった”** だよね🙂

### 3-1. `AbortController` でキャンセルする📎

```ts
export function startSearch(query: string) {
  const controller = new AbortController();

  const promise = fetch(`/api/search?q=${encodeURIComponent(query)}`, {
    signal: controller.signal,
  });

  return {
    promise,
    cancel: () => controller.abort(), // ユーザー操作で止める🛑
  };
}
```

### 3-2. キャンセルを「例外」扱いしない設計にする🎀

`AbortError` で来るから、うっかりすると…

* ログにエラー大量📛
* 画面に「エラー！」トースト連発🍞💥

になりがち😱

なのでおすすめは👇

* **キャンセルは“第3の結果”として扱う**（Ok/Err とは別）🙂

例：`Outcome<T>` を作るパターン👇

```ts
type Outcome<T, E> =
  | { kind: "ok"; value: T }
  | { kind: "err"; error: E }
  | { kind: "cancelled" };

function isAbortError(e: unknown): boolean {
  return e instanceof DOMException && e.name === "AbortError";
}
```

> Abort での reject や `AbortController.abort()` は仕様として普通に起きるものだよ、って理解でOK🙂🛑 ([MDN Web Docs][3])

---

## 4. リトライ🔁：やっていい条件・ダメな条件を決めよう🧠

### 4-1. リトライしていいことが多いパターン✅

だいたいこういうやつ👇（※代表例）

* 一時的なネットワーク失敗📶
* タイムアウト⏳（ただし回数と総時間に上限！）
* サーバが混雑（`429` や `503`）🚦

  * `Retry-After` が付いてたら **待ってから再試行**が基本 ([MDN Web Docs][4])

`Retry-After` は「何秒待つか」か「日時」で来ることがあるよ🕰️ ([IETF HTTP Working Group][5])

### 4-2. リトライしちゃダメ寄り❌

* **入力ミス**（ドメインエラー）🙅‍♀️
* **認証エラー**🔑（トークン切れなら更新→再試行は別設計）
* **バグ（不変条件違反）**🧱⚡（直すべき）
* **キャンセル**🛑（ユーザーが止めたのに再開は迷惑🙂）

### 4-3. いちばん大事：副作用がある操作は危険⚠️

たとえば `POST /orders` みたいな「作る」操作をリトライすると…

* 1回目はサーバに届いて注文作成🛒
* でも返事が途中で途切れてクライアントは「失敗」と誤解😵
* 2回目のリトライで **もう1個注文**🛒🛒

これを防ぐ考え方が **Idempotency Key（冪等キー）** だよ✨
`POST` や `PATCH` みたいな非冪等操作を“安全に再試行”できるようにする仕組みとして、IETFでも仕様が進んでる🧠 ([IETF Datatracker][6])
実運用でも Stripe などが「安全なリトライには冪等キー」って明言してるよ🙂 ([Stripe Documentation][7])

---

## 5. バックオフ（間隔を空ける）🧊：リトライの作法✨

リトライは **すぐ連打しない**！
「指数バックオフ + 上限 + jitter（ゆらぎ）」が定番だよ🔁📈✨ ([Amazon Web Services, Inc.][8])

### 5-1. サンプル：指数バックオフ + jitter

```ts
function sleep(ms: number) {
  return new Promise<void>((resolve) => setTimeout(resolve, ms));
}

function computeBackoffMs(attempt: number, baseMs = 200, capMs = 5_000): number {
  // 0,1,2... で 200,400,800... みたいに増える
  const exp = Math.min(capMs, baseMs * 2 ** attempt);

  // jitter: 0.5x〜1.0x でゆらす（同時リトライ祭りを避ける）🎲
  const jitter = 0.5 + Math.random() * 0.5;
  return Math.floor(exp * jitter);
}
```

---

## 6. 実装パターン：安全な `retryFetch` を作る🧰🔁

### 6-1. “再試行していい？”を関数に分ける🧠

ポイントは「条件を1箇所に集める」こと✨

```ts
type RetryDecision =
  | { kind: "no" }
  | { kind: "yes"; waitMs: number };

function parseRetryAfterSeconds(value: string | null): number | null {
  if (!value) return null;

  // Retry-After: 120 みたいな秒数形式だけ先に対応（日時形式は必要になったら追加でOK🙂）
  const secs = Number(value);
  return Number.isFinite(secs) && secs >= 0 ? Math.floor(secs * 1000) : null;
}

function decideRetry(params: {
  attempt: number;
  maxAttempts: number;
  error: unknown;
  response?: Response;
}): RetryDecision {
  const { attempt, maxAttempts, error, response } = params;

  // 回数上限🔚
  if (attempt >= maxAttempts - 1) return { kind: "no" };

  // キャンセルはリトライしない🛑
  if (error instanceof DOMException && error.name === "AbortError") {
    return { kind: "no" };
  }

  // HTTPレスポンスがある場合（=通信自体はできた）🌐
  if (response) {
    // 429/503 あたりは Retry-After を尊重しがち
    if (response.status === 429 || response.status === 503) {
      const wait = parseRetryAfterSeconds(response.headers.get("Retry-After"));
      if (wait != null) return { kind: "yes", waitMs: wait };

      // ヘッダ無ければバックオフ
      return { kind: "yes", waitMs: computeBackoffMs(attempt) };
    }

    // 502/504 みたいな“ゲートウェイ系”も一時的なことが多い（例）
    if (response.status === 502 || response.status === 504) {
      return { kind: "yes", waitMs: computeBackoffMs(attempt) };
    }

    // それ以外は基本リトライしない（必要ならここを増やす）🙂
    return { kind: "no" };
  }

  // レスポンスが無い＝ネットワーク断/タイムアウト等の可能性📶💥
  return { kind: "yes", waitMs: computeBackoffMs(attempt) };
}
```

`Retry-After` の意味は「次のリクエストまでどれくらい待つべきか」だよ🕰️ ([MDN Web Docs][4])

### 6-2. 本体：`retryFetch`

```ts
export async function retryFetch(
  input: RequestInfo | URL,
  init: RequestInit & { timeoutMs?: number } = {},
  options: { maxAttempts?: number } = {},
): Promise<Response> {
  const maxAttempts = options.maxAttempts ?? 3;

  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    // 1回ごとに AbortSignal を作り直す（abort済みsignalは再利用できない）🧠
    // ※AbortSignalはabort後に使い回すと即rejectされるよ :contentReference[oaicite:9]{index=9}
    const timeoutMs = init.timeoutMs ?? 5_000;
    const signal = AbortSignal.timeout(timeoutMs);

    try {
      const res = await fetch(input, { ...init, signal });

      if (res.ok) return res;

      // HTTPエラーの場合も条件次第でリトライ
      const d = decideRetry({ attempt, maxAttempts, error: null, response: res });
      if (d.kind === "no") return res;

      await sleep(d.waitMs);
      continue;
    } catch (e) {
      const d = decideRetry({ attempt, maxAttempts, error: e });
      if (d.kind === "no") throw e;

      await sleep(d.waitMs);
      continue;
    }
  }

  // ここには来ない設計だけど保険🧯
  throw new Error("retryFetch: unreachable");
}
```

---

## 7. 失敗種類ごとの「再試行OK/NG・ユーザー表示」表を作ろう📋✨（ミニ演習）

ここが今日のメイン演習だよ🎓💖
あなたのアプリを想像して、こんな表を作ってみてね😊

| 失敗の種類     | 具体例         |    再試行 | ユーザー表示                | 裏でやること         |
| --------- | ----------- | -----: | --------------------- | -------------- |
| キャンセル🛑   | 画面遷移/検索打ち直し |     NG | 何も出さない or 小さく「中止」🙂   | ログ不要 or debug  |
| タイムアウト⏳   | 5秒待っても返らない  | 条件つきOK | 「時間がかかってるよ。再試行できるよ」🔁 | retry回数・総時間に上限 |
| ネット断📶💥  | オフライン       | 条件つきOK | 「通信が不安定みたい」📶         | オフライン検知/導線     |
| 429🚦     | レート制限       |     OK | 「混雑中。少し待ってね」🐏        | Retry-After尊重  |
| 503🌩️    | サービス一時停止    |     OK | 「ただいま混み合ってるよ」         | Retry-After尊重  |
| ドメインエラー💗 | 在庫なし        |     NG | 「在庫がないよ」              | そのまま表示         |
| バグ🧱⚡     | 不変条件違反      |     NG | 「問題が起きた」              | 監視/通知/調査用ログ    |

> `Retry-After` が 429/503 で使われるのは定番だよ📌 ([MDN Web Docs][9])

---

## 8. 反例（リトライすると地獄）をAIに出させよう😱🤖（AI活用）

AIに「事故例」を出させると、ルール作りが一気にラクになるよ✨

おすすめプロンプト👇

* 「**HTTPのリトライで二重実行が起きる例**を、初心者向けに5つ挙げて」😱
* 「**キャンセルとタイムアウトを同じ扱いにしたときのUX事故**を教えて」🛑💥
* 「**429/503のとき Retry-After を尊重しないと何が起きる？**」🐏🐏🐏
* 「この表（再試行OK/NG・表示方針）に**穴がないか監査して**」👮‍♀️🔎

---

## 9. まとめ😊📌

この章で一番えらいのはこれ！✨

* **タイムアウト**で「待ちすぎ」を防ぐ⏳
* **キャンセル**を“失敗扱いしない”設計にする🛑🙂
* **リトライ**は条件つき（特に 429/503 は `Retry-After`）🚦
* **指数バックオフ + jitter**で混雑を悪化させない🔁🎲 ([Amazon Web Services, Inc.][8])
* **副作用のある操作は冪等キーが超重要**🛒🛡️ ([Stripe Documentation][7])

次の総合演習（第30章）では、ここで作った「表」と「retryFetch」みたいな部品が、そのまま武器になるよ〜🎓💖

[1]: https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal/timeout_static?utm_source=chatgpt.com "AbortSignal: timeout() static method - Web APIs | MDN"
[2]: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch?utm_source=chatgpt.com "Using the Fetch API - MDN Web Docs"
[3]: https://developer.mozilla.org/en-US/docs/Web/API/AbortController?utm_source=chatgpt.com "AbortController - Web APIs | MDN"
[4]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Retry-After?utm_source=chatgpt.com "Retry-After header - HTTP - MDN Web Docs"
[5]: https://httpwg.org/specs/rfc9110.html?utm_source=chatgpt.com "RFC 9110 - HTTP Semantics"
[6]: https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/?utm_source=chatgpt.com "The Idempotency-Key HTTP Header Field"
[7]: https://docs.stripe.com/api/idempotent_requests?utm_source=chatgpt.com "Idempotent requests | Stripe API Reference"
[8]: https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/?utm_source=chatgpt.com "Timeouts, retries and backoff with jitter"
[9]: https://developer.mozilla.org/ja/docs/Web/HTTP/Reference/Headers/Retry-After?utm_source=chatgpt.com "Retry-After - HTTP - MDN Web Docs"
