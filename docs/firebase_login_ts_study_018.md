# 第18章：サーバー側で守る：IDトークン検証の入口（Node/.NET/Python）🔐

この章でやることはシンプルです🙂
**「ログインしてる“っぽい”」を、サーバー側で“本当にログインしてる”に変える**のがゴールです💪✨
（IDトークン＝JWTをサーバーで検証して、`uid` を確定させます）([Firebase][1])

---

## 0) まずはイメージ図（これができると強い）🧠✨

```text
React(ブラウザ) ── getIdToken() ──▶  Authorization: Bearer <IDトークン>
        │                                                │
        └──────────────▶  Functions(HTTP)  ── verifyIdToken() ──▶ uid確定 ✅
```

* **クライアントは“自己申告”し放題**になりがち😈
* サーバーで **`verifyIdToken()`** して初めて「この人は本当にこのユーザーだね」が確定します✅([Firebase][1])

---

## 1) 読む（5分）📚👀

この章の要点はこのへんに全部まとまってます👇

* IDトークンの検証の考え方（Admin SDKで検証して `uid` を取り出す）([Firebase][1])
* HTTP関数（CORSの`cors`オプションの考え方）([Firebase][2])
* Nodeのサポート状況（Node 20 / 22がフルサポート、18はdeprecated）([Firebase][3])
* デプロイにBlaze必須（「あれ？デプロイできない」原因になりがち）([Firebase][3])
* Callable（`onCall`）は**バックエンドがAuthorizationトークンを自動検証**して`context`に入れてくれる（楽！）([Firebase][4])

---

## 2) 手を動かす：まず “whoAmI API” を作る🛠️👤

## 2-1) Functionsを用意する（TypeScript）📦✨

まだ `functions/` がなければ、作ります。

```bash
npm install -g firebase-tools
firebase login
firebase init functions
```

* 言語は **TypeScript** を選ぶのがおすすめ🙂
* Nodeは **20か22** を選ぶのが安全です（公式がフルサポートを明言）([Firebase][3])
* デプロイするなら、Firebaseプロジェクトは **Blaze** が必要です（まずここで詰まりやすい）([Firebase][3])

---

## 2-2) “HTTP + IDトークン検証” を最小で書く✍️🔐

`functions/src/index.ts` に **「Authorization: Bearer …」を検証して uid を返す**関数を作ります。

```ts
import { onRequest } from "firebase-functions/v2/https";
import * as logger from "firebase-functions/logger";
import { initializeApp } from "firebase-admin/app";
import { getAuth } from "firebase-admin/auth";

initializeApp();

export const whoAmI = onRequest(
  // Authorization ヘッダーを使うとプリフライトが起きやすいので、まずCORSを許可しておく🙂
  { cors: true },
  async (req, res) => {
    try {
      const authHeader = req.header("Authorization") ?? "";
      const m = authHeader.match(/^Bearer (.+)$/);

      if (!m) {
        res.status(401).json({ error: "missing_bearer_token" });
        return;
      }

      const idToken = m[1];

      // ここが“背骨”🦴：トークンが正しい・期限切れでない・署名OKなら decoded が返る
      const decoded = await getAuth().verifyIdToken(idToken);

      res.json({
        uid: decoded.uid,
        email: decoded.email ?? null,
      });
    } catch (e) {
      logger.warn("verifyIdToken failed", e as any);
      res.status(401).json({ error: "invalid_or_expired_token" });
    }
  }
);
```

* `cors: true` は「CORS未設定でブロックされる😇」を避けるための保険です
  HTTP関数は `cors` オプションでCORSを制御できます([Firebase][2])
* `verifyIdToken()` は「形式OK・期限OK・署名OK」ならデコード結果が返ります([Firebase][1])
* ただし **“失効（revoked）チェックは別”** なので、強くやるなら失効検知も検討します（後述）([Firebase][1])

---

## 2-3) ローカルで軽く動作確認する🧪✨

```bash
firebase emulators:start --only functions
```

起動ログに `http://127.0.0.1:...` みたいなURLが出ます。
（このURLに、あとでReactから叩きます🙂）

---

## 3) React側：IDトークンを付けて呼ぶ📨🌈

ログイン済みユーザーから `getIdToken()` して、`Authorization` に付けます。

```ts
import { getAuth } from "firebase/auth";

export async function callWhoAmI(apiUrl: string) {
  const user = getAuth().currentUser;
  if (!user) throw new Error("未ログインだよ🙂");

  const idToken = await user.getIdToken(); // たまに強制更新したいなら getIdToken(true)

  const res = await fetch(apiUrl, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${idToken}`,
    },
  });

  if (res.status === 401) {
    // ここが重要：トークン期限切れ・ログアウト状態などを“丁寧に”扱う
    throw new Error("ログインが切れたっぽい！もう一回ログインしてね🙏");
  }

  return res.json() as Promise<{ uid: string; email: string | null }>;
}
```

**ポイント🧠**

* 401が返るのは「悪」じゃなくて“正常な守り”です🛡️
* 401を受けたら、UIで「再ログイン導線」を出すのが優しさ🙂✨

---

## 4) もっと楽にする：Callable（onCall）で“自動検証”に寄せる🚀

HTTP（onRequest）は自由度が高い代わりに、**CORSやBearer処理を自分で書く**ことが多いです。
Callable（onCall）は、**Authorizationトークンをバックエンドが自動検証**して、`context`に入れてくれます（ラク！）([Firebase][4])

## 4-1) Functions側（onCall）

```ts
import { onCall, HttpsError } from "firebase-functions/v2/https";
import { initializeApp } from "firebase-admin/app";

initializeApp();

export const whoAmICallable = onCall((request) => {
  if (!request.auth) {
    throw new HttpsError("unauthenticated", "ログインしてね🙂");
  }

  return {
    uid: request.auth.uid,
    email: request.auth.token.email ?? null,
  };
});
```

## 4-2) React側（httpsCallable）

```ts
import { getFunctions, httpsCallable } from "firebase/functions";

export async function callWhoAmICallable() {
  const fn = httpsCallable(getFunctions(), "whoAmICallable");
  const result = await fn();
  return result.data as { uid: string; email: string | null };
}
```

Callableは **プリフライトも自動処理**してくれます（地味に助かるやつ）([Firebase][4])
さらに **App Check トークンも自動検証**して `context` に注入されます（条件が揃うと強い）([Firebase][4])

---

## 5) Node / Python / .NET の“選び方”ざっくり🧭

## Node（Functions）🟩

* Node **20 / 22** がフルサポート（18はdeprecated）([Firebase][3])
* TypeScriptで最短ルート✨

## Python（Functions）🐍

* Functionsのランタイムとして **Python 3.10〜3.13** がサポート、**デフォルトは3.13** と明記されています([Firebase][3])
* IDトークン検証は Admin SDK で `auth.verify_id_token()`（公式例あり）([Firebase][1])

## .NET（Cloud Run functions）🟦

* .NETは **Cloud Run functions** のランタイム側で選べます
* **.NET 8** が安定ラインとして載っていて、**.NET 10** はPreview扱いで示されています([Google Cloud Documentation][5])
* C# でも Admin SDK で `VerifyIdTokenAsync` の公式例があります([Firebase][1])

> つまり：
> **Functionsで最短＝Node/TS**、**Pythonもいける**、**.NETはCloud Run functionsが主戦場**、って感じです🙂✨

---

## 6) つまずきポイント集（ここ超重要）🧨➡️🧯

## 6-1) CORSで詰む😇

* `Authorization` を付けるとブラウザが **OPTIONS（プリフライト）** を投げがち
* HTTP関数は `cors` オプションで解決しやすいです([Firebase][2])
* Callableはプリフライトも自動でうまくやってくれます([Firebase][4])

## 6-2) 「検証OK＝完全に安全」ではない🙅‍♂️

* `verifyIdToken()` は署名や期限は見ますが、**失効（revoked）チェックは別**と公式に注意があります([Firebase][1])

  * “強制ログアウトさせたい”運用をするなら、失効検知もセットで考えると安心🙂

## 6-3) サーバーは“ルールを無視できる”👻

* Admin SDKでFirestoreを読むと、セキュリティルールを素通りします
* だから **「uidでアクセス制御するコード」** をサーバー側でちゃんと書くのが大事🛡️

---

## 7) AIでスピード上げる🤖💨（実戦向け）

## 7-1) Antigravityで“ミッション化”する🚀

Antigravityは「エージェントに計画→実装→検証まで任せる」思想の開発プラットフォームとして紹介されています([Google Codelabs][6])

**ミッション例（コピペ用）🧾**

* 「`whoAmI`（onRequest）を追加して、Authorization Bearerの検証まで実装して」
* 「CORSでブラウザから叩けるようにして」
* 「401/200のレスポンス例をREADMEに追記して」
* 「（余裕あれば）onCall版も追加して比較して」

## 7-2) Gemini CLIで“抜け漏れ監査”🔎

Gemini CLIはターミナル上で動くオープンソースAIエージェントとして説明されています([Google Cloud Documentation][7])

**投げると強い指示🧠**

* 「Authorizationヘッダー周りのセキュリティ穴ない？」
* 「401の扱い、UI/UXとして破綻してない？」
* 「ログにトークン文字列を出してない？」（これ地雷🔥）

## 7-3) Firebase AI Logicで“やさしい説明文”を作る💬✨

Firebase AI Logicは、モバイル/ウェブからGemini/Imagenを呼ぶ用途に最適化されたSDK＆セキュリティ統合（App Checkなど）を提供しています([Firebase][8])

**使いどころ例🙂**

* 401が返った時に「何が起きたか」を、ユーザー向けにやさしく説明する文を生成

  * 例：「ログインが切れたかも。もう一回ログインしてね🙏」みたいな文章を状況に応じて出す✨

---

## 8) ミニ課題🎯：`/private/profile` を作って “uidで守る” を完成させよう🧩👤

**やること**

1. サーバーでIDトークン検証 → `uid` を取り出す ✅
2. `users/{uid}` を読み、プロフィールを返す（返す項目は最低限）
3. 未ログイン（401）時のUIを整える（再ログイン導線）🚪

---

## 9) チェック問題✅📝（答えつき）

1. IDトークン検証をサーバーでやる目的は？
   → **“このリクエストのuidを確定させる”ため**（自己申告を信じない）([Firebase][1])

2. HTTP関数でAuthorizationヘッダーを使うと起きがちな問題は？
   → **CORSプリフライト**。`cors`オプションで対処([Firebase][2])

3. Callable（onCall）の嬉しい点は？
   → **バックエンドがBearerトークンを自動検証**して`context`で使える([Firebase][4])

4. `verifyIdToken()` で注意するべき公式の注記は？
   → **失効（revoked）チェックは別**([Firebase][1])

5. FunctionsのNodeランタイムは何が安全？
   → **Node 20 / 22**（18はdeprecated）([Firebase][3])

6. Python Functionsのデフォルトバージョンは？
   → **3.13**（3.10〜3.13サポート）([Firebase][3])

---

次の章（第19章）でMFAの話に進む前に、この第18章ができると「守りの基礎体力」が一気に上がります💪🛡️
もしよければ、今の構成（Hosting/App Hosting/Functionsどれ中心か）に合わせて、**呼び出しURLの組み立て方**や**エミュレータでのフロント接続**も“あなたの形”に最適化した手順で書き換えますよ🙂✨

[1]: https://firebase.google.com/docs/auth/admin/verify-id-tokens "Verify ID Tokens  |  Firebase Authentication"
[2]: https://firebase.google.com/docs/functions/http-events "Call functions via HTTP requests  |  Cloud Functions for Firebase"
[3]: https://firebase.google.com/docs/functions/get-started "Get started: write, test, and deploy your first functions  |  Cloud Functions for Firebase"
[4]: https://firebase.google.com/docs/functions/callable-reference "Protocol specification for https.onCall  |  Cloud Functions for Firebase"
[5]: https://docs.cloud.google.com/functions/docs/runtime-support "Runtime support  |  Cloud Run functions  |  Google Cloud Documentation"
[6]: https://codelabs.developers.google.com/getting-started-google-antigravity "Getting Started with Google Antigravity  |  Google Codelabs"
[7]: https://docs.cloud.google.com/gemini/docs/codeassist/gemini-cli "Gemini CLI  |  Gemini for Google Cloud  |  Google Cloud Documentation"
[8]: https://firebase.google.com/docs/ai-logic "Gemini API using Firebase AI Logic  |  Firebase AI Logic"
