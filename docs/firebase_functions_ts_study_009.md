# 第09章：Callable（onCall）で“認証つきAPI”を楽にする🔐✨

この章は「フロント（React）から呼べる、**認証つきの安全なAPI**」を最短で作る回です😊
Callable（onCall）は、ふつうのHTTP API（onRequest）より“アプリ向け”に作られていて、**ログイン情報（Auth）やApp CheckのトークンをSDKがよしなに付けてくれる**のが強みです🚀
しかも後で「AIを呼ぶ処理（課金が絡む）💸🤖」を置くときの“王道の入口”になります。

---

## 0) まずイメージ図🧠✨

![Callable Overview](./picture/firebase_functions_ts_study_009_01_callable_overview.png)

* React（Web）🖥️ → `httpsCallable()` 📦
* 自動で添付されるもの✅

  * Firebase Authentication トークン
  * App Check トークン（設定していれば）
  * ほか（FCMなど、環境により）
* Functions（onCall）⚙️

  * `request.auth` で「誰？」が取れる
  * App Checkを強制すると、怪しい呼び出しをブロックできる🛡️

この「トークン自動添付」＆「サーバ側で検証」こそCallableの気持ちよさです😆
([Firebase][1])

---

## 1) 今日のゴール🎯

* ✅ **ログインしてる人だけ**実行できるCallableを作る
* ✅ エラーを“アプリ向け”に返す（`HttpsError`）📛
* ✅ **App Check も必須化**して、雑な直叩きを減らす🧱🔒

---

## 2) Callableは「AuthつきAPI」を作る最短ルート💡

![Server-Side Checks](./picture/firebase_functions_ts_study_009_02_server_check.png)

Callableは「Firebaseアプリ（SDK）」から呼ばれる前提のAPIです。なので……

* 認証チェックがラク（`request.auth` を見るだけ）🙂
* エラーもラク（`HttpsError` を投げるだけ）🙂
* CORSも“Callable流”で設定できる（v2）🌍
  ([Firebase][1])

---

## 3) 実装：ログイン必須のCallableを作る🛠️✨

ここでは例として、**「AI整形リクエスト（ダミー）」**を受け取って返すCallableを作ります🤖
（この章では“認証・防御の枠”を完成させるのが主役。AI本体は後で差し込める形にします👌）

### 3-1) Functions側（TypeScript）⚙️

![Callable Logic Flow](./picture/firebase_functions_ts_study_009_03_logic_flow.png)

* ポイント🧠

  * `request.auth` が無ければ弾く（未ログイン）
  * 入力バリデーションする（変なの来たら弾く）
  * 失敗は `HttpsError` を投げる（クライアントが読みやすい）

```ts
// functions/src/callables/formatNote.ts
import { onCall, HttpsError } from "firebase-functions/v2/https";
import { logger } from "firebase-functions";

type Input = {
  text: string;
};

type Output = {
  formatted: string;
  uid: string;
};

export const formatNote = onCall(
  // まずは Auth を主役に。App Check 強制は次の手順で ON にするよ！
  // （下で enforceAppCheck: true に切り替える）
  async (request): Promise<Output> => {
    // 1) Authチェック 🔐
    if (!request.auth) {
      throw new HttpsError("unauthenticated", "ログインが必要です🙇‍♂️");
    }

    // 2) 入力チェック 📦
    const data = request.data as Partial<Input>;
    if (typeof data.text !== "string" || data.text.trim().length === 0) {
      throw new HttpsError("invalid-argument", "text は必須です📝");
    }

    const uid = request.auth.uid;

    // 3) ここが将来：AI処理の差し込みポイント 🤖✨
    // 今はダミーで「整形したっぽい」文字列を返す
    const formatted =
      `✨整形結果✨\n` +
      `- uid: ${uid}\n` +
      `- text: ${data.text.trim()}`;

    logger.info("formatNote called", { uid });

    return { formatted, uid };
  }
);
```

`HttpsError` を投げると、クライアント側で `error.code / error.message / error.details` として受け取れます📛
([Firebase][1])

---

## 4) React側：`httpsCallable()` で呼ぶ📞✨

![HttpsError Handling](./picture/firebase_functions_ts_study_009_04_error_handling.png)

Callableは `fetch()` じゃなくて、**SDKの `httpsCallable()`** で呼ぶのが基本です🙂

```ts
// src/lib/functions.ts
import { getFunctions, httpsCallable } from "firebase/functions";
import { app } from "./firebaseApp"; // initializeApp 済みのやつ

const functions = getFunctions(app);
// もし Functions を特定リージョンにしてるなら：getFunctions(app, "asia-northeast1") みたいに揃える

export const formatNote = httpsCallable(functions, "formatNote");
```

呼び出し例👇

```ts
// どこかの React コンポーネント / handler
import { formatNote } from "../lib/functions";

async function onClickFormat(text: string) {
  try {
    const res = await formatNote({ text });
    // res.data が Functions の戻り値
    const data = res.data as { formatted: string; uid: string };
    console.log(data.formatted);
  } catch (e: any) {
    // Callable は code/message/details を持ってくる
    console.error("Callable error:", e.code, e.message, e.details);
  }
}
```

この “クライアントのエラー形” は公式サンプルのパターンです📦
([Firebase][1])

---

## 5) 「未ログインだと弾かれる」を確認する✅🔐

テスト観点はシンプル👇

* ✅ ログイン状態 → 成功して `formatted` が返る
* ✅ 未ログイン → `unauthenticated` で落ちる

`request.auth` が無い場合に弾くのは、公式サンプルでも王道です🙂
([Firebase][1])

---

## 6) App Checkも必須化して“直叩き”を減らす🧱🔒

Authだけでも大事だけど、現実の運用だと👇が起きがちです😇

* ログインできるユーザーが、スクリプトで叩きまくる（AIや外部APIだと課金が怖い💸）
* 認証の前に、そもそも“アプリ以外”から来る通信を減らしたい🛡️

そこで **App Check 強制**です🔥

### 6-1) Functions側：`enforceAppCheck: true` を付ける（v2）✅

![App Check Enforcement](./picture/firebase_functions_ts_study_009_05_enforce_app_check.png)

```ts
import { onCall, HttpsError } from "firebase-functions/v2/https";

export const formatNote = onCall(
  {
    enforceAppCheck: true, // ← App Check トークンが無い/無効なら即Reject🧱
  },
  async (request) => {
    // request.app に App Check 情報（app ID など）が入る
    // Authも引き続き request.auth で見れる
    if (!request.auth) {
      throw new HttpsError("unauthenticated", "ログインが必要です🙇‍♂️");
    }
    // ...
    return { formatted: "ok", uid: request.auth.uid };
  }
);
```

`enforceAppCheck: true` を入れるだけで「無効なApp Checkは拒否」になります。`request.app` にApp Check由来の情報も来ます🛡️
([Firebase][2])

> ここ、めちゃ大事：CallableはクライアントSDKが App Check トークンを自動で付けます（設定していれば）📎
> ([Firebase][2])

---

### 6-2) React側：App Check を初期化する（reCAPTCHA v3 / Enterprise）🧩

**Web**はまず reCAPTCHA v3 か reCAPTCHA Enterprise が定番です🙂
（要件が強いなら Enterprise が便利なことも多いです✨）
([Firebase][3])

例：reCAPTCHA v3

```ts
// src/lib/appCheck.ts
import { initializeAppCheck, ReCaptchaV3Provider } from "firebase/app-check";
import { app } from "./firebaseApp";

export const appCheck = initializeAppCheck(app, {
  provider: new ReCaptchaV3Provider("あなたのサイトキー（公開鍵）"),
  isTokenAutoRefreshEnabled: true,
});
```

この初期化コードの形は公式の案内どおりです🧩
([Firebase][3])

---

### 6-3) 開発中は「Debug token」で詰まりを回避🧯🧪

![Debug Token Usage](./picture/firebase_functions_ts_study_009_06_debug_token.png)

ローカル開発・CIだと、App Check がうまく通らないことがあります。そんなときは **debug provider** を使います🙂
ブラウザのコンソールに出る debug token を Firebase コンソールで登録してOK、という流れです🧪
([Firebase][4])

---

## 7) CORSどうするの？🌍（Callableの考え方）

Callableは基本「SDKから呼ぶ」前提なので、CORSも“Callable流”です🙂

* v2 の `onCall` は `cors` オプションで許可originを設定できます
* すべて禁止したいなら `cors: false` も可能
  ([Firebase][1])

さらに、Callableはデフォルトで “all origins 許可” の方向で動く前提が書かれています（GenkitのonCallでも同様の説明）👀
([Firebase][5])

---

## 8) AI開発（Antigravity / Gemini CLI）でここを爆速にする🤖🛸

![AI Acceleration](./picture/firebase_functions_ts_study_009_07_ai_acceleration.png)

Callable周りは「雛形生成」「エラー原因の切り分け」「設定チェック」が地味に時間を食います😇
そこで **Firebase MCP server** を使うと、AI側が Firebase CLI と同じ認証で情報を見に行けて、作業がかなりスムーズになります🧰✨

* Firebase MCP server は Antigravity や Gemini CLI などのMCPクライアントで使える
* Gemini CLI は Firebase拡張を入れるのが推奨（自動設定＋コンテキスト付）
  ([Firebase][6])

やること（超ざっくり）👇

* `gemini extensions install .../firebase/` を入れる
* 「CallableでAuth/AppCheckを必須にしたい。必要なコード差分と落とし穴を列挙して」みたいに依頼
* 出てきた差分を人間がレビューして反映✅
  ([Firebase][6])

---

## ミニ課題🧩🔥（20〜30分）

## 課題A：Callableを“プロフィール更新API”にする👤✨

* 入力：`displayName: string`
* 出力：`{ ok: true }`
* 条件：未ログインなら `unauthenticated`
* 追加：空文字は `invalid-argument`

## 課題B：App Check を強制にする🧱

* Functions：`enforceAppCheck: true` をON
* Web：App Check を初期化（v3 or Enterprise）
* ローカル：debug tokenで通す

---

## チェックテスト✅🧠

* ✅ Callableは `httpsCallable()` で呼ぶ（fetchで雑に叩くものじゃない）
* ✅ `request.auth` が無ければ未ログイン（即 `unauthenticated`）
* ✅ 入力チェックは “最初に” やる（`invalid-argument`）
* ✅ App Check は `enforceAppCheck: true` で強制できる（v2）
* ✅ 開発中は debug token で詰まり回避できる

---

次の章（第10章）で「Secret Manager / defineSecret」へ進むと、Callableはそのまま **Slack通知やAIキー管理**の土台になります🔔🗝️🤖
「Callable＝認証つきの入口」って感覚が掴めてたら大成功です😆✨

[1]: https://firebase.google.com/docs/functions/callable "Call functions from your app  |  Cloud Functions for Firebase"
[2]: https://firebase.google.com/docs/app-check/cloud-functions "Enable App Check enforcement for Cloud Functions  |  Firebase App Check"
[3]: https://firebase.google.com/docs/app-check/web/recaptcha-provider "Get started using App Check with reCAPTCHA v3 in web apps  |  Firebase App Check"
[4]: https://firebase.google.com/docs/app-check/web/debug-provider "Use App Check with the debug provider in web apps  |  Firebase App Check"
[5]: https://firebase.google.com/docs/functions/oncallgenkit "Invoke Genkit flows from your App  |  Cloud Functions for Firebase"
[6]: https://firebase.google.com/docs/ai-assistance/mcp-server "Firebase MCP server  |  Develop with AI assistance"
