# 第24章：サーバ側の例外境界（APIルートで受け止める）🧱🚪

この章は「**サーバのAPIルートで起きた例外（throw）を、どこで・どうやって最後に受け止めるか**」を決めて、**毎回ブレない形**にする回だよ〜😊💕

---

## 0) この章でできるようになること🎯✨

* APIの「最後のcatch地点」を**ルート（入口）に固定**できる🚪
* どんな変なthrowが来ても、**unknown → アプリ標準エラー**に寄せられる🧼
* 返すレスポンス（成功/失敗）を**統一**できる📦
* ログの出し方も統一できて、**あとから追跡**できる🔎🧵

※環境の最新状況として、Node.jsは **v24がActive LTS**で、v25がCurrentとして更新が続いてるよ（2026-01頃の更新もあり）🟢 ([Node.js][1])
TypeScriptはnpm上のlatestが **5.9.3**（本日時点の表示）で、次の大きな節目として **TypeScript 6.0は“既存JS実装の最後のメジャー”**になる方針が公式ブログで語られているよ📌 ([npmjs.com][2])

---

## 1) なんで「最後のcatch地点」を決めるの？😵‍💫💥

APIを作ってると、失敗の扱いがこうなりがち👇

* ルートAは try/catch してる
* ルートBはしてない
* ルートCはしてるけど握りつぶす
* ルートDは返す形がバラバラ

結果…
**クライアント側が地獄**😇（毎回違う失敗形式）
**運用も地獄**😇（ログもバラバラで追えない）

だから、ここでルールを一個にするよ！

> ✅ **「例外は最終的にAPIルート境界で受け止め、正規化して、統一形式で返す」**

この“最終受付”が **例外境界**（Exception Boundary）だよ🧱🚪

---

## 2) 例外境界の責務：やること／やらないこと🧠✨

### ✅ やること（境界の仕事）🧱

1. **try/catchで最後に受け止める**
2. catchしたものを **unknown → 標準エラーへ正規化**🧼
3. **分類**（domain / infra / bug）を信じられる形にする🏷️
4. **レスポンスへ変換**（HTTPステータスとボディ）📦
5. **ログ出力**（安全に・追跡できるように）🔎🧵

### ❌ やらないこと（境界に入れない）🙅‍♀️

* ルート固有のビジネス判断（例：在庫引当の細かい分岐）
* DBや外部APIの例外の解釈を“その場で”増やしていく
* その場しのぎの文言作り（ログもレスポンスも）

境界は **「変換工場」**みたいなもの🏭✨
中身の処理（ドメイン/インフラ）は別の場所で整えるよ🙂

---

## 3) 統一フロー（これが完成形の流れ）🗺️✨

イメージはこう👇

* リクエストが来る📩
* ルート内部で処理する🧠
* 失敗したら throw / Result.Err / 変なunknown が来るかも😱
* **境界で一回ぜんぶ受け止める**🧱
* **正規化**して、**統一レスポンス**にして返す📦

図にするとこんな感じ〜😊

```text
[HTTP Request]
      |
      v
  (API Route)
   try {
      doWork()
      return 200
   } catch (e) {
      appErr = normalize(e)
      log(appErr)
      return toHttpResponse(appErr)
   }
```

![ミドルウェアフィルター：不純物（例外）を取り除いて綺麗なレスポンスにする[(./picture/err_model_ts_study_024_middleware_filter.png)

---

## 4) 実装の最小セット（まずこれだけ）🧰✨

この章では「ルート境界」を作るので、必要な部品は4つ！

1. **AppError（標準エラーの形）**
2. **normalize（unknown→AppError）**
3. **toHttp（AppError→HTTPレスポンス）**
4. **route wrapper（各ルートを包む関数）**

次章でProblem Details（RFC7807）を本格導入するけど、ここでは“入口の形”だけ作っておくよ🧾✨
Problem Detailsの仕様自体はRFCとして定義されているよ（status/type/title/detail/instance など）📌 ([RFCエディタ][3])

---

## 5) まずは“標準エラー”の形を決めよう🏷️🎁

ポイントはこれ👇

* **クライアントに見せてOKな情報**と
* **ログだけに残す情報**を分ける🙈🔒

```ts
// エラーの分類
export type ErrorKind = "domain" | "infra" | "bug";

// クライアントに返してOKな“安全な”情報
export type PublicError = {
  kind: ErrorKind;
  code: string;       // 例: "USER_EMAIL_TAKEN"
  message: string;    // 表示してOKな説明（やさしめ）
  status: number;     // HTTP status（仮でOK）
};

// ログ用に持っておく追加情報（外に出さない）
export type AppError = PublicError & {
  cause?: unknown;    // 元の例外
  debug?: unknown;    // スタックや詳細（PII注意！）
};
```

---

## 6) unknown を正規化する（復習＋ルート境界向けのコツ）🧼✨

ルート境界で大事なのはこれ！

* catchした値は **基本unknown**😳
* “とりあえず Error にする”だけだと、分類もHTTP変換もできない
* だから **AppErrorへ寄せる**🧼

```ts
export function normalizeUnknown(e: unknown): AppError {
  // すでにAppErrorならそのまま
  if (isAppError(e)) return e;

  // Errorっぽいなら、infra扱いに寄せる例（方針はチームでOK）
  if (e instanceof Error) {
    return {
      kind: "infra",
      code: "UNEXPECTED_ERROR",
      message: "通信やサーバの都合で失敗しちゃったみたい…🙏 もう一度試してね。",
      status: 500,
      cause: e,
      debug: { name: e.name, message: e.message, stack: e.stack },
    };
  }

  // それ以外（string/objectなど）も全部吸収
  return {
    kind: "infra",
    code: "THROWN_NON_ERROR",
    message: "サーバ側で想定外の失敗が起きちゃった…🙏",
    status: 500,
    cause: e,
    debug: { thrown: e },
  };
}

function isAppError(x: unknown): x is AppError {
  if (!x || typeof x !== "object") return false;
  const a = x as any;
  return (
    (a.kind === "domain" || a.kind === "infra" || a.kind === "bug") &&
    typeof a.code === "string" &&
    typeof a.message === "string" &&
    typeof a.status === "number"
  );
}
```

💡コツ：

* **ルート境界は“最後の砦”**なので、どんな入力でも落ちないようにする（＝例外を例外で返さない）🧱✨

---

## 7) AppError を HTTPレスポンスに変換する📦🌐

次章でProblem Detailsに寄せるんだけど、今は簡易版でOK😊
（形を統一するのが最優先！）

```ts
export type ApiErrorResponse = {
  error: {
    code: string;
    message: string;
    kind: "domain" | "infra" | "bug";
  };
};

export function toApiErrorResponse(err: AppError): { status: number; body: ApiErrorResponse } {
  return {
    status: err.status,
    body: {
      error: {
        code: err.code,
        message: err.message,
        kind: err.kind,
      },
    },
  };
}
```

---

## 8) ルートを包む“境界ラッパー”を作る（ここが主役）🧱🚪✨

### パターン：Route Handler を高階関数で包む🎁

**目的：** 各ルートに同じtry/catchを書かない！✍️❌
**代わりに：** ルートを“包む”関数を1個作る！🪄

---

### 8-A) Express風（req/res）ラッパー例🧩

```ts
type ExpressLikeReq = { headers: Record<string, string | undefined>; body?: unknown; };
type ExpressLikeRes = {
  status: (code: number) => ExpressLikeRes;
  json: (body: unknown) => void;
};

type RouteFn = (req: ExpressLikeReq) => Promise<unknown>;

export function withApiBoundary(fn: RouteFn) {
  return async (req: ExpressLikeReq, res: ExpressLikeRes) => {
    const requestId = req.headers["x-request-id"] ?? cryptoRandomId();

    try {
      const data = await fn(req);
      res.status(200).json({ data, requestId });
    } catch (e) {
      const appErr = normalizeUnknown(e);

      safeLogError(appErr, { requestId });

      const { status, body } = toApiErrorResponse(appErr);
      res.status(status).json({ ...body, requestId });
    }
  };
}

function safeLogError(err: AppError, ctx: { requestId: string }) {
  // 例：本番ではPIIに注意して最小限に！
  console.error("API_ERROR", {
    requestId: ctx.requestId,
    kind: err.kind,
    code: err.code,
    debug: err.debug,
  });
}

function cryptoRandomId() {
  // Node 24/25ならcryptoは標準で使えるよ（環境依存のため短めに）
  return Math.random().toString(16).slice(2);
}
```

---

### 8-B) Hono風（Responseを返す）ラッパー例🌿

Honoは **app.onError** で“未捕捉エラー”をまとめて処理できるよ😊
ドキュメントにも **onErrorでカスタムResponseを返す**例がある✨ ([Hono][4])

```ts
type HonoContextLike = {
  req: { header: (name: string) => string | undefined };
  json: (body: unknown, status?: number) => Response;
};

type HonoHandler = (c: HonoContextLike) => Promise<Response>;

export function withHonoBoundary(fn: HonoHandler) {
  return async (c: HonoContextLike) => {
    const requestId = c.req.header("x-request-id") ?? cryptoRandomId();

    try {
      return await fn(c);
    } catch (e) {
      const appErr = normalizeUnknown(e);
      safeLogError(appErr, { requestId });

      const { status, body } = toApiErrorResponse(appErr);
      return c.json({ ...body, requestId }, status);
    }
  };
}
```

---

### 8-C) Next.js Route Handler っぽい例（Responseを返す）🧩✨

Next.jsは“内部で投げるものがある”系があるので、むやみにcatchして握りつぶさない配慮が必要な場面があるよ（たとえば redirect は try の外に置くのが推奨されてる）📌 ([Next.js][5])
なので方針としては👇

* **基本は境界でcatch**
* ただしフレームワークが“制御のために投げるもの”は、**再throw**する場合もある（必要な時だけ）

（※ここは利用フレームワークに合わせて調整でOK😊）

---

## 9) 例：ユーザー登録ルートを“境界で受け止める”👤📝✨

「登録処理」が失敗するパターンっていっぱいあるよね😳

* すでにメールが使われてる（domain）
* DBが落ちた（infra）
* ありえない状態（bug）

まず、ドメイン側は「ドメインエラー」を投げる（またはResult.Err）方針を決めておいて👇

```ts
export function emailAlreadyUsed(email: string): AppError {
  return {
    kind: "domain",
    code: "USER_EMAIL_TAKEN",
    message: "そのメールアドレスは、すでに使われているみたい…🥺",
    status: 409,
  };
}
```

ルートは“境界”に任せるから、内部はスッキリ✨

```ts
const registerRoute = withApiBoundary(async (req) => {
  const body = req.body as any;

  // 例：すでに使われてたら domain error を投げる
  if (body.email === "taken@example.com") {
    throw emailAlreadyUsed(body.email);
  }

  // ここでDB保存…（失敗すれば例外でもResultでもOK）
  return { userId: "u_123" };
});
```

✅ポイント：ルート内で“毎回” try/catchしない。
**最後は境界で必ず揃う**からね😊🧱

---

## 10) よくある地雷💣（初心者がハマりやすいTOP7）😱

1. **catchして握りつぶす**（ログもレスポンスも無し）🙈
2. **500なのに200で返す**（クライアントが成功扱いして事故）😇
3. **クライアントにstackを返す**（情報漏えい）🧨
4. **ルートごとにエラー形式が違う**（フロントが死ぬ）⚰️
5. **ログに個人情報をそのまま出す**（超危険）🔒💥
6. **エラーを二重にラップして原因が追えない**🌀
7. 「とりあえずthrow new Error("...")」乱発で、分類が崩壊🏷️💣

---

## 11) ミニ演習📝✨：「APIルートのエラー方針」を1枚にまとめよう📄💖

ここ、めっちゃ効くよ😊
下のテンプレを埋めてみて〜✨

### ✅ エラー方針シート（テンプレ）📄

* 例外境界の場所：**APIルートの入口**🚪
* ルート内でtry/catchする？：基本しない（境界に寄せる）🧱
* catchしたunknownの扱い：**normalizeUnknown**でAppError化🧼
* クライアントへ返す失敗形式：**統一フォーマット**📦
* ログ：requestId付き、PIIは出さない🔎🔒
* domain / infra / bug のHTTPステータス方針：

  * domain：4xx中心（例：409/422など）
  * infra：基本 503/500（リトライの可能性）
  * bug：500固定（開発者向け）

---

## 12) AI活用🤖✨（Copilot / Codexに投げると強いプロンプト集）

### ① 境界ラッパー作り🧱

* 「APIルート用の高階関数を作って。成功は {data, requestId}、失敗は {error:{code,message,kind}, requestId} に統一。catch unknown は normalizeUnknown を使う」

### ② “握りつぶし”検出🙈

* 「このコードで握りつぶしてる箇所を指摘して、統一境界に寄せるリファクタ案を出して」

### ③ 例外境界の責務レビュー👀

* 「このエラーハンドラの責務が薄い/厚いところをレビューして、境界がやるべきこと/やらないことに分けて提案して」

### ④ 危ないログ添削🔒

* 「このログ出力に個人情報や秘密が混ざる可能性を指摘して、安全なログ項目に直して」

---

## まとめ🎀✨

* 例外境界は「最後の受付」🧱🚪
* APIルートで受け止めると、**レスポンスもログも統一**できる📦🔎
* unknownは必ず正規化🧼
* 境界は“変換工場”で、ビジネス判断は入れない🏭💡

次章はここで作った **統一エラー**を、RFC7807の **Problem Details** に寄せて「API契約」として固めていくよ🧾🌐✨ ([RFCエディタ][3])

[1]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[2]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "TypeScript"
[3]: https://www.rfc-editor.org/rfc/rfc7807.html?utm_source=chatgpt.com "RFC 7807: Problem Details for HTTP APIs"
[4]: https://hono.dev/docs/api/hono?utm_source=chatgpt.com "App"
[5]: https://nextjs.org/docs/app/guides/redirecting?utm_source=chatgpt.com "Guides: Redirecting"
