# 第18章：自前バックエンドを守る（X-Firebase-AppCheck を検証）🧱🛡️

この章はひとことで言うと **「Firebaseの外にある“自分のAPI”も、App Checkで“正規アプリだけ”にする」** 回です🙂✨
（たとえば：Cloud Run のAPI、コンテナで動くExpress、社内API、AI処理専用APIなど）

---

## まず結論：守りの“最小セット”はこれ🧿✅

自前APIを守るとき、最低限の型はこう👇

1. **フロント（React）**：App Check トークンを取って、HTTPヘッダ `X-Firebase-AppCheck` に載せて送る📮
2. **バック（自前API）**：ヘッダのトークンを **Admin SDKで検証**（成功したらOK、失敗は401）🚫
   → これで「あなたのFirebaseプロジェクトに属する“正規アプリ”から来た」ことが確認できます✅ ([Firebase][1])

さらに強くするなら（おすすめ！）👇

* **ユーザー本人確認もセット**：`Authorization: Bearer <Firebase Auth ID token>` も一緒に送り、バックで `verifyIdToken()` する🙋‍♂️🔐 ([Firebase][2])
* **超重要APIはリプレイ対策**：*limited-use token* ＋ サーバ側で “consume” して使い回しを潰す♻️🚫 ([Firebase][3])

---

## しくみ（超ざっくり図）🗺️

![Custom Backend Architecture](./picture/firebase_abuse_prevention_ts_study_018_01_backend_arch.png)

* React（ブラウザ）
  → App Check SDKでトークン取得
  → `X-Firebase-AppCheck: <token>` を付けて `fetch()`
* 自前API（Express / Cloud Run 等）
  → ヘッダを見てトークン検証
  → OKなら処理（Firestore読書き、画像処理、AI呼び出し等）
  → NGなら 401

---

## 読むパート（今日の公式仕様の“肝”だけ）📖✨

## 1) フロント：ヘッダに載せる（URLに埋めない！）🚫🔗

![Header vs URL](./picture/firebase_abuse_prevention_ts_study_018_02_header_vs_url.png)

Webアプリでは App Check トークンを取って、**`X-Firebase-AppCheck` ヘッダ**で送ります📮
トークンは **URL（クエリ）に入れない** のが推奨です（ログや参照元で漏れやすい…😇）。([Firebase][3])

さらに、リプレイ対策をしたい場合は **`getLimitedUseToken()`** を使う方法が案内されています。([Firebase][3])

## 2) バック：Admin SDKで検証して、ダメなら落とす🧱🔍

自前API側はやることが明確👇

* **トークンが付いてるかチェック**
* **Admin SDKで検証**（成功なら続行、失敗なら401）([Firebase][1])

---

## 手を動かす（React側）：トークンを付けて自前APIを叩く⚛️📮

![React Header Code](./picture/firebase_abuse_prevention_ts_study_018_03_react_header.png)

App Check が初期化済みの前提で、API呼び出し関数を1つ作ります🙂
（※ここでやってるのは「ヘッダに載せる」だけ。シンプル！）

```ts
import { getAppCheck, getToken /*, getLimitedUseToken */ } from "firebase/app-check";

/**
 * 自前APIを叩く共通関数（App Check トークンを自動付与）
 */
export async function callMyApi(path: string, body: unknown) {
  const appCheck = getAppCheck();

  // 通常トークン（まずはこれでOK）
  const { token } = await getToken(appCheck, /* forceRefresh */ false);

  // リプレイ対策を強くしたいAPIだけ、こっちを検討👇
  // const { token } = await getLimitedUseToken(appCheck);

  const res = await fetch(`/api${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Firebase-AppCheck": token,
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    // 401 なら「App Check通ってない」可能性が高い
    const text = await res.text().catch(() => "");
    throw new Error(`API error: ${res.status} ${text}`);
  }

  return res.json();
}
```

ポイントは2つだけ！✨

* `X-Firebase-AppCheck` にトークンを載せる ([Firebase][3])
* トークンをURLに埋めない ([Firebase][3])

---

## 手を動かす（Node/Express側）：ミドルウェアで検証する🧰🛡️

![Middleware Gate](./picture/firebase_abuse_prevention_ts_study_018_04_middleware_gate.png)

公式ドキュメントの Express ミドルウェア例がそのまま使えます👍
「まずは通す／落とす」だけ作って、あとで本処理を足すのが安全🙂

```ts
import express from "express";
import { initializeApp } from "firebase-admin/app";
import { getAppCheck } from "firebase-admin/app-check";

const app = express();
app.use(express.json());

// Cloud Run / Functions / サーバなどで、権限のあるサービスアカウントで動く想定
initializeApp();

/**
 * App Check 検証ミドルウェア
 */
async function requireAppCheck(req: express.Request, res: express.Response, next: express.NextFunction) {
  const appCheckToken = req.header("X-Firebase-AppCheck");
  if (!appCheckToken) {
    return res.status(401).send("Unauthorized");
  }

  try {
    const claims = await getAppCheck().verifyToken(appCheckToken);
    // 必要なら claims を req に載せてもOK（例: appId をログ用に）
    (req as any).appCheckClaims = claims;

    return next();
  } catch {
    return res.status(401).send("Unauthorized");
  }
}

app.post("/api/ai/formatMemo", requireAppCheck, async (req, res) => {
  // ここに「AI整形処理」など好きなロジックを書く🤖✨
  res.json({ ok: true });
});

app.listen(8080, () => console.log("server on :8080"));
```

この流れ（ヘッダ必須→verify→失敗は拒否）は公式が明示しています。([Firebase][1])

---

## さらに強く：Authも一緒に検証して「誰が叩いたか」まで確定🙋‍♂️🔐

![Dual Keys](./picture/firebase_abuse_prevention_ts_study_018_05_dual_keys.png)

App Check は「正規アプリか？」で、Auth は「ユーザー本人か？」です。
自前APIで“課金に直結するAI”をやるなら **両方やる** のが鉄板🙂

フロント側：`Authorization` も付ける（例）

* `Authorization: Bearer <ID token>`

バック側：Firebase Admin SDK で `verifyIdToken()` する流れが公式にあります。([Firebase][2])

（ここまでできると、**ユーザー別レート制限**とか、**管理者のみ許可**とかが作りやすいです💪✨）

---

## 超重要APIだけ：リプレイ対策（使い回し攻撃）を潰す♻️🚫

![Consume Token](./picture/firebase_abuse_prevention_ts_study_018_06_consume_token.png)

「AI実行」「購入」「招待コード発行」みたいな **一発が重いAPI** は、次の合わせ技が強いです👇

* フロント：`getLimitedUseToken()` を使う ([Firebase][3])
* バック：`verifyToken(token, { consume: true })` で “消費” する ([Firebase][4])

Admin SDK側は “consume” を指定できて、結果に **すでに消費済みか** の情報も返ります。([Firebase][5])

---

## ＋発展：.NET（公式Admin SDKが無い言語）で検証したい場合🧩🟣

![JWT Manual Check](./picture/firebase_abuse_prevention_ts_study_018_07_jwt_check.png)

自前バックエンドが “別言語” のときは、公式が「JWTライブラリで検証する手順」を出しています👇

* 公開鍵（JWKS）を `https://firebaseappcheck.googleapis.com/v1/jwks` から取得
* 署名検証
* ヘッダ `alg` が **RS256**、`typ` が **JWT**
* issuer（発行者）が自分のプロジェクト配下
* 期限切れじゃない
* audience が自分のプロジェクト
* （任意）subject がアプリの App ID と一致 ([Firebase][1])

しかも鍵はローテするので **ハードコードしない**、ただし **最大6時間くらいはキャッシュしてOK** とまで書いてあります。([Firebase][1])

バージョン目安：.NET は **.NET 10（LTS）** が現行の安定ど真ん中です。([Microsoft][6])

## .NETで作るならチェックリスト（コピペ用）✅

* [ ] `X-Firebase-AppCheck` ヘッダがある
* [ ] JWKS取得（キャッシュあり）
* [ ] RS256 / typ=JWT
* [ ] 署名OK
* [ ] issuer OK（自分の project number 配下）([Firebase][1])
* [ ] audience OK（自分の project number）([Firebase][1])
* [ ] exp（期限）OK
* [ ] （任意）subject == App ID

---

## AI活用：Antigravity / Gemini CLI で“守り実装”を爆速にする🚀🤖

ここ、AIがめちゃ効きます😆🔥
特にこの章は「いつものWeb API」なので、雛形生成が速い！

## Antigravity（Mission Control）でやらせると強い🛰️

Antigravityは「エージェントが計画して、コード書いて、必要ならWebも見て進める」思想が明記されています。([Google Codelabs][7])
ミッション例👇

* 「`/api/ai/formatMemo` を作る。App Check検証必須。失敗は401。ログはトークンを出さない」
* 「重要APIは limited-use token + consume 対応」

## Gemini CLI（ターミナルで）でやらせると楽🔧

Gemini CLI は **ターミナルで使えるオープンソースAIエージェント**として案内されています。([Google Cloud][8])
お願いのコツ👇

* 「このファイルに `requireAppCheck` ミドルウェア追加して」
* 「`X-Firebase-AppCheck` がURLに入ってたら指摘して」
* 「401のとき、UI側でどう見せるべき？」（第15章につながる🙂）

（Firebase Studioを使うなら `.idx/dev.nix` でツール環境を揃えられるので、チームでも再現しやすいです🧰）([Firebase][9])

---

## ミニ課題🎯（10〜20分）

1. Reactから自前APIを叩くボタンを作る🔘
2. `X-Firebase-AppCheck` を付けたときだけ成功するのを確認👀
3. 401のときに「再読み込み」「時間を置く」「問い合わせ導線」表示を入れる🙂🧯
4. （余裕あれば）重要APIだけ `getLimitedUseToken()` ＋ `consume: true` にして、再送で弾けるか試す♻️🚫 ([Firebase][3])

---

## チェック✅（言えたら勝ち🎉）

* App Checkトークンは **`X-Firebase-AppCheck` ヘッダ**で送る（URLに入れない）📮🚫 ([Firebase][3])
* 自前API側は **ヘッダ確認→Admin SDKでverify→失敗は拒否**🧱🛡️ ([Firebase][1])
* “本人”まで確定したいなら **Auth ID token も verify** する🙋‍♂️🔐 ([Firebase][2])
* 重要APIは **limited-use token + consume** でリプレイ耐性を上げられる♻️🚫 ([Firebase][3])

---

次の第19章は、今作った“守り付き自前API”を、**Antigravity / Gemini CLI で自動レビュー＆改善**して「漏れを潰す」フェーズにできます😆🔎
（例：App Check初期化漏れ、直叩き経路、ログにトークン出ちゃってないか、など）

[1]: https://firebase.google.com/docs/app-check/custom-resource-backend "Verify App Check tokens from a custom backend  |  Firebase App Check"
[2]: https://firebase.google.com/docs/auth/admin/verify-id-tokens "Verify ID Tokens  |  Firebase Authentication"
[3]: https://firebase.google.com/docs/app-check/web/custom-resource "Protect custom backend resources with App Check in web apps  |  Firebase App Check"
[4]: https://firebase.google.com/docs/reference/admin/node/firebase-admin.app-check.verifyappchecktokenoptions.md "VerifyAppCheckTokenOptions interface  |  Firebase Admin SDK"
[5]: https://firebase.google.com/docs/reference/admin/node/firebase-admin.app-check.verifyappchecktokenresponse.md "VerifyAppCheckTokenResponse interface  |  Firebase Admin SDK"
[6]: https://dotnet.microsoft.com/en-us/platform/support/policy?utm_source=chatgpt.com "The official .NET support policy"
[7]: https://codelabs.developers.google.com/getting-started-google-antigravity?utm_source=chatgpt.com "Getting Started with Google Antigravity"
[8]: https://cloud.google.com/blog/products/ai-machine-learning/choose-the-right-google-ai-developer-tool-for-your-workflow "Choose the right Google AI developer tool for your workflow | Google Cloud Blog"
[9]: https://firebase.google.com/docs/studio/devnix-reference?utm_source=chatgpt.com "dev.nix Reference: Firebase Studio"
