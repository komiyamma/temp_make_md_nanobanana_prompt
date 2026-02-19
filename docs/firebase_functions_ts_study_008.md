# 第08章：CORSとセキュリティの最初の壁🧱🔒

この章は「**React（ブラウザ）からHTTP関数を呼んだ瞬間に出る、あの謎エラー**」を倒す回です😇🌪️
そして大事な本音：**CORSは“セキュリティ”じゃなくて、ブラウザの交通整理**です🚦（ここを勘違いすると事故ります）

---

## この章でできるようになること🎯

* ✅ CORSエラーの正体を“一言で”説明できる🗣️
* ✅ Functions（HTTP / onRequest）に**許可Originを絞ったCORS設定**を入れられる🔧
* ✅ 「CORSを直した＝安全になった」じゃない理由がわかる🧠
* ✅ AI（Genkit / Firebase AI Logic）を呼び出す前に、**課金事故を防ぐ入口の守り**を作れる🛡️💸

---

## キーワード📚

* CORS / Origin / Same-Origin Policy
* Preflight（事前通信）/ OPTIONS
* Allowlist（許可リスト）
* Auth（IDトークン）/ App Check（アプリ正当性）
* “CORSはブラウザ限定の壁”🧱

---

## 1) まず結論：CORSって何？🤔

![CORS Traffic Controller](./picture/firebase_functions_ts_study_008_01_cors_traffic.png)

CORSは、ざっくり言うと——
**ブラウザが「そのWebページは、そのAPIを呼んでいい？」をチェックする仕組み**です🌐✅

* ブラウザは、勝手に他ドメインのAPIを呼ぶのを嫌がります（ユーザー保護）🧯
* だからサーバー側（Functions）が「このOriginならOKだよ」と返す必要があります🧩

Firebase公式のHTTP関数ドキュメントにも、HTTP関数は**デフォルトでCORS未設定**で、クロスオリジンだとエラーになる、と明記されています。([Firebase][1])

---

## 2) つまずきポイント：Preflight（OPTIONS）って何👀？

![Preflight (OPTIONS) Flow](./picture/firebase_functions_ts_study_008_02_preflight_flow.png)

「GETなら動くのに、POSTしたら死ぬ😇」みたいな時、だいたいこれです。

ブラウザは、条件によって**本番のPOSTの前に**「この送信していい？」って確認の **OPTIONS** を投げます（= preflight）🧪
HTTP関数は `OPTIONS` もサポート対象に含まれます。([Firebase][1])

なので、**CORS設定がない** or **許可条件が合わない**と、ブラウザ側がブロックします🚫

---

## 3) 一番ラクで堅い解決：onRequest の `cors` オプションを使う🛠️✨

ここが2026時点の“正攻法”です。
Firebase公式は、HTTP関数（onRequest）で `cors` オプションを提供していて、

* `true`：全Origin許可（公開API向け）
* `string / regex / array`：許可したいOriginだけ指定（アプリ向け）
* デフォルトは `false`（CORSなし）

…と説明しています。([Firebase][1])

---

## ✅ ハンズオン：許可Originを“限定”してCORSを通す（推奨）🔒

例：自分のフロントが

* `https://YOUR-PROJECT.web.app`
* `https://example.com`（独自ドメイン）

だけから呼べるようにする✋

```ts
import { onRequest } from "firebase-functions/v2/https";

const ALLOWED_ORIGINS = [
  "https://YOUR-PROJECT.web.app",
  "https://example.com",
];

export const apiEcho = onRequest(
  { cors: ALLOWED_ORIGINS },
  async (req, res) => {
    // JSONを返すだけの超ミニAPI
    res.status(200).json({
      ok: true,
      method: req.method,
      body: req.body ?? null,
    });
  }
);
```

✅ これで **preflight（OPTIONS）も含めて**ブラウザが通しやすくなります🧠✨
（自前で `Access-Control-Allow-*` を書くより事故が減ります）

---

## ⚠️ あるある注意：Originは「スキーム＋ドメイン＋ポート」🎯

![Origin Components](./picture/firebase_functions_ts_study_008_03_origin_components.png)

* `http://localhost:5173` と `http://localhost:3000` は**別Origin**です😵‍💫
* `https://` と `http://` も別です
* “プレビューURL”も別Originになります（プレビュー運用するなら、そこも許可リストに入れる）🧪

---

## 4) 超重要：CORSは“セキュリティ”ではない🙅‍♂️🔐

![CORS is Not Security](./picture/firebase_functions_ts_study_008_04_cors_not_security.png)

ここ、テストに出ます（マジで）📣

* CORSは **ブラウザだけ**が守る壁🧱
* curl / Postman / 悪いスクリプトは、**CORS関係なく叩けます**🔫（ブラウザじゃないので）

つまり、CORSを直しただけだと…

> 「“誰でも”叩けるAPIが、ブラウザからも叩けるようになった」

になりがちです😇

---

## 5) “本当の守り”の基本セット：Auth + App Check 🛡️✨

![Three Layers of Defense](./picture/firebase_functions_ts_study_008_05_defense_layers.png)

AI（Genkit / Firebase AI Logic）を裏側で呼ぶなら、ここ超大事💸🔥
**守らないと、勝手に叩かれて課金が溶ける**系の事故が起きます。

## 5-1) Auth（ログインした人だけ）🔐

Firebase Admin SDKで **IDトークン検証**できます。公式に「検証・デコードできる」説明があります。([Firebase][2])

## 5-2) App Check（“本物のアプリ”からだけ）🧿

App Checkは「あなたのアプリから来た通信か」を見る仕組みで、Authと相互補完って公式も言っています。([Firebase][3])

---

## 6) ここが落とし穴：onRequest は `enforceAppCheck` が使えない😇

Callable（onCall）なら `enforceAppCheck: true` が公式手順としてあります。([Firebase][4])
でも **onRequest（HTTP）には同じノリで付けられません**。

実際、2nd genの `HttpsOptions`（onRequest用オプション）は `enforceAppCheck` を含まない形で定義されています。([Firebase][5])

👉 なのでHTTP関数でApp Checkをやるなら、**自分でトークン検証**が基本になります（次節）🧠

---

## 7) ハンズオン：HTTP関数で「CORS + Auth + App Check」を最低限いれる🧰🛡️

![Manual Token Verification](./picture/firebase_functions_ts_study_008_06_manual_verification.png)

## 守りの設計（この章のゴール形）🏁

* ✅ CORS：許可Originだけ通す
* ✅ Auth：`Authorization: Bearer <ID_TOKEN>` を検証
* ✅ App Check：`X-Firebase-AppCheck` を検証

App Checkのトークン検証は、公式が「`X-Firebase-AppCheck` ヘッダを取り、Admin SDKで verify する」例を出しています。([Firebase][6])

---

## ✅ 例コード：守り入りのHTTP関数テンプレ🧱🔒

```ts
import { onRequest } from "firebase-functions/v2/https";
import { initializeApp } from "firebase-admin/app";
import { getAuth } from "firebase-admin/auth";
import { getAppCheck } from "firebase-admin/app-check";

initializeApp();

const ALLOWED_ORIGINS = [
  "https://YOUR-PROJECT.web.app",
  "https://example.com",
];

export const apiSecureEcho = onRequest(
  { cors: ALLOWED_ORIGINS },
  async (req, res) => {
    try {
      // 1) Auth（IDトークン）チェック 🔐
      const authHeader = req.header("Authorization") || "";
      const match = authHeader.match(/^Bearer (.+)$/);
      if (!match) {
        return res.status(401).json({ ok: false, error: "Missing Bearer token" });
      }
      const idToken = match[1];
      const decoded = await getAuth().verifyIdToken(idToken);

      // 2) App Checkチェック 🧿
      const appCheckToken = req.header("X-Firebase-AppCheck") || "";
      if (!appCheckToken) {
        return res.status(401).json({ ok: false, error: "Missing App Check token" });
      }
      await getAppCheck().verifyToken(appCheckToken);

      // 3) ここから先が“本処理”（AI呼び出し等）🤖✨
      return res.status(200).json({
        ok: true,
        uid: decoded.uid,
        method: req.method,
        body: req.body ?? null,
      });
    } catch (e) {
      return res.status(401).json({ ok: false, error: "Unauthorized" });
    }
  }
);
```

📌 この形にしておくと、次の章以降で

* GenkitでAI処理
* Slack通知
* Firestore書き込み
  みたいな“お金が動く処理”を安全に足せます💸🧯

---

## 8) React側はどう呼ぶ？（超ミニ例）⚛️📡

イメージだけ掴めればOKです🙂

* AuthのIDトークンを取って `Authorization` に入れる
* App Checkトークンを取って `X-Firebase-AppCheck` に入れる
* それで `fetch()` する

（App Checkトークンをカスタムバックエンドに送って検証する流れ自体が公式の前提です）([Firebase][6])

---

## 9) AIでデバッグを爆速にする（Antigravity / Gemini CLI）🛸🤖

![AI Debugging CORS](./picture/firebase_functions_ts_study_008_07_ai_debugging.png)

CORSって、正直「1文字違い」で沼ります😇
そんな時は **Gemini CLI + Firebase拡張**に“症状から原因を当てさせる”のが強いです💪

Firebase拡張は、Gemini CLIにFirebase向けの能力を足して、MCPサーバー設定なども面倒を見てくれます。([Firebase][7])

## 使い方の雰囲気🧰

* 「ブラウザのNetworkタブのスクショ or エラーメッセージ」を貼る📎
* 「許可したいOriginはこれ」「本番とプレビューはこれ」って添える
* 「`cors` の許可リストを最小で提案して」って頼む🤖

（拡張の導入・更新コマンドも公式に載ってます）([Firebase][7])

---

## 10) ミニ課題🎓✨（10〜15分）

## 課題A：CORSだけ直す🧱

1. `apiEcho` を作る
2. 許可Originを **1つだけ**にしてデプロイ
3. Reactから叩いて成功させる🎉

✅ チェック

* 「CORSはデフォルト無効で、許可しないとブラウザが止める」と言える([Firebase][1])

---

## 課題B：守りを入れて“安全な入口”にする🔐🧿

1. `apiSecureEcho` を作る
2. `Authorization` が無い時に 401 になる
3. `X-Firebase-AppCheck` が無い時に 401 になる

✅ チェック

* 「HTTP関数はCallableみたいに `enforceAppCheck` で一発、ではない」と言える([Firebase][5])

---

## まとめ🎁

* CORSは「**ブラウザの壁**」であって「**サーバーの防御**」じゃない🧱
* `onRequest({ cors: [...] })` で、許可Originを絞るのが最短ルート🚀 ([Firebase][1])
* 本当に守るなら **Auth + App Check** をセットで考える🔐🧿 ([Firebase][2])
* AI（Genkit / Firebase AI Logic）を裏で呼ぶほど、入口の守りが重要になる🤖💸
* Gemini CLI拡張＋MCPで、沼（CORS）を早めに脱出しよう🛸✨ ([Firebase][7])

---

次の第9章（Callable / onCall）は、この章の地獄（CORS）をかなり回避しつつ、Auth/App Checkを“楽に”やる王道に入っていきます🔐✨

[1]: https://firebase.google.com/docs/functions/http-events "Call functions via HTTP requests  |  Cloud Functions for Firebase"
[2]: https://firebase.google.com/docs/auth/admin/verify-id-tokens "Verify ID Tokens  |  Firebase Authentication"
[3]: https://firebase.google.com/docs/app-check?utm_source=chatgpt.com "Firebase App Check - Google"
[4]: https://firebase.google.com/docs/app-check/cloud-functions "Enable App Check enforcement for Cloud Functions  |  Firebase App Check"
[5]: https://firebase.google.com/docs/reference/functions/2nd-gen/node/firebase-functions.https.httpsoptions "https.HttpsOptions interface  |  Cloud Functions for Firebase"
[6]: https://firebase.google.com/docs/app-check/custom-resource-backend "Verify App Check tokens from a custom backend  |  Firebase App Check"
[7]: https://firebase.google.com/docs/ai-assistance/gcli-extension "Firebase extension for the Gemini CLI  |  Develop with AI assistance"
