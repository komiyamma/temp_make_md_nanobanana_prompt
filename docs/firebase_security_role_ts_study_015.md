# 第15章：Custom Claims入門（ロールを“トークンに埋める”）🎫🔐

この章はひとことで言うと👇
**「管理者フラグ（ロール）を“ユーザーのIDトークン”に刻印して、アプリ全体の門番に使えるようにする」**回です✨
（UIでボタンを隠すだけ🙈じゃなく、**仕組みで弾く🛡️**のが目的！）

---

## 1) まずは超イメージ図🧠✨

* ユーザーがログインすると…
  **IDトークン🎫**（身分証みたいなもの）が発行される
* **Custom Claims** は、その身分証に「あなたはadminです✅」みたいな**追加情報**を入れる仕組み
* Firestore Security Rules は、その身分証を見て **「通す/止める」** を決められる🚪

Rules側での参照はこんな感じ👇
`request.auth.token.admin`（adminというクレームを見に行く） ([Firebase][1])
![Concept of Custom Claims.](./picture/firebase_security_role_ts_study_015_01_custom_claims_concept.png)

---

## 2) 重要ポイントだけ先に⚠️（ここを外すと事故る😱）

## ✅ Custom Claimsは「クライアントから付けられない」

Custom Claims を付与できるのは **Admin SDK（サーバー側の特権環境）だけ**です。
つまり、**Reactアプリ（ブラウザ）にAdmin SDKを入れて付与**みたいなのはNG🙅‍♂️（危険すぎ） ([Firebase][2])
![Where to apply Custom Claims.](./picture/firebase_security_role_ts_study_015_02_client_vs_server.png)

## ✅ 付与しても、すぐ反映されない（トークン更新が必要）🔄

Custom Claimsは **次に発行されるIDトークン**に入ります。
なので付与直後は、ユーザー側で **トークンの強制更新**が必要になることが多いです（後で手を動かします） ([Firebase][2])
![The necessity of Token Refresh.](./picture/firebase_security_role_ts_study_015_03_token_refresh.png)

## ✅ 入れられるサイズに上限がある（1000バイト）📦

Custom Claimsは **最大1000バイト**。大きいデータやプロフィール全部を入れる場所じゃないです🙅‍♀️
「admin: true」みたいな **小さいフラグ**向き！ ([Firebase][2])
![1000 Byte Limit on Claims.](./picture/firebase_security_role_ts_study_015_04_size_limit.png)

## ✅ 予約語っぽいクレーム名は使えない🧨

勝手に `sub` とか `iat` とか、JWTの標準っぽい名前を使うとトラブルになりやすいです。
Firebase側でも「予約されてるクレーム名がある」注意が出ています（Custom Claimsのドキュメントに記載あり） ([Firebase][2])

---

## 3) 手を動かす🧑‍💻✨：Custom Claims を付けて、Reactで確認する

ここからは **最短で体験**します🔥
ゴールは👇
**「自分のUIDに admin=true を付けて、React側で『付いた！』を確認」**です✅

---

## Step A：React側に「クレーム確認パネル」を作る🔍🪪

ログイン後に、今のユーザーが持つクレームを表示します。
（ポイント：`getIdTokenResult()` で `claims` が見えます）

```ts
// claimsDebug.ts (どこでもOK：コンポーネント内でも可)
import { getAuth, getIdTokenResult } from "firebase/auth";

export async function loadClaims(forceRefresh = false) {
  const auth = getAuth();
  const user = auth.currentUser;
  if (!user) return { uid: null, claims: null };

  // forceRefresh=true で「新しいトークンを取り直す」🌀
  const tokenResult = await getIdTokenResult(user, forceRefresh);
  return { uid: user.uid, claims: tokenResult.claims };
}
```

表示例（どこかの画面で）👇

* uid: `xxxxx`
* claims: `{ admin: true, ... }` みたいになったら成功🎉

> 「付与したのに表示されない😢」ときは、あとで出てくる **forceRefresh=true** を試します🔄 ([Firebase][2])

---

## Step B：Admin SDKで「admin=true」を付与する（最短の1回作業）🔧👑

ここは **サーバー側の特権**です。初心者でもやりやすいのは👇
✅ **Windows上で、1回だけ“管理者付与スクリプト”を実行**（ローカルのNodeでOK）

Admin SDKの前提（2026の目安）：

* Admin Node.js SDK：**Node.js 18+** ([Firebase][3])
  （Cloud Functions側のNodeは **20 / 22 が選べて、18はdeprecated**） ([Firebase][4])
* Admin Python SDK：Python 3.9+（推奨3.10+、3.9 deprecated） ([Firebase][3])
* Admin .NET SDK：.NET 6+（推奨 .NET 8+、6/7 deprecated） ([Firebase][3])

## 1) 必要なもの📌

* Firebase Admin SDK用の **サービスアカウント認証情報（JSON）**
  （Admin SDKはこれでFirebaseと特権通信します） ([Firebase][3])

## 2) スクリプト例（TypeScript）🧩

```ts
// tools/grant-admin.ts
import fs from "node:fs";
import { initializeApp, cert } from "firebase-admin/app";
import { getAuth } from "firebase-admin/auth";

const serviceAccountPath = "./serviceAccountKey.json"; // 置いた場所に合わせてね
const serviceAccount = JSON.parse(fs.readFileSync(serviceAccountPath, "utf8"));

initializeApp({ credential: cert(serviceAccount) });

const uid = process.argv[2];
if (!uid) {
  console.error("使い方: node tools/grant-admin.ts <UID>");
  process.exit(1);
}

await getAuth().setCustomUserClaims(uid, { admin: true });
console.log("✅ admin=true を付与しました:", uid);

// 全削除したいとき（全部のCustom Claimsを消す）👇
// await getAuth().setCustomUserClaims(uid, null);
```

> `setCustomUserClaims(uid, null)` で「そのユーザーのCustom Claimsを全消し」できます🧹 ([Firebase][2])

※ `firebase-admin` のセットアップや「認証情報ファイルが必要」という話は Admin SDKの公式手順にあります ([Firebase][3])
![Executing Admin SDK script.](./picture/firebase_security_role_ts_study_015_05_admin_sdk_script.png)

---

## Step C：React側で「トークン強制更新」して確認する🔄✅

付与直後は、React側でこうします👇

```ts
import { loadClaims } from "./claimsDebug";

const before = await loadClaims(false);
console.log("before", before);

const after = await loadClaims(true); // 👈 ここが大事！
console.log("after", after);
```

`after.claims.admin === true` になったら勝ち🎉🎉🎉
この「強制更新が必要」って話は公式にも書かれてます ([Firebase][2])

---

## 4) （プレビュー）Rules側でどう見える？🛡️👀

次の章（第16章）でガッツリやりますが、Custom ClaimsはRulesでこう見えます👇

```js
// firestore.rules（プレビュー用）
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    match /adminOnly/{docId} {
      allow read, write: if request.auth != null
                         && request.auth.token.admin == true;
    }
  }
}
```

`request.auth.token` でトークンの中身（claims）を参照できます ([Firebase][1])

---

## 5) よくある事故パターン集😂💥（先に踏んでおこう）

![Common pitfalls with Custom Claims.](./picture/firebase_security_role_ts_study_015_06_common_accidents.png)

## 事故①：付与したのに admin が見えない😱

原因トップはこれ👇

* **トークン更新してない**（forceRefreshしてない） ([Firebase][2])

対策✅

* `getIdTokenResult(user, true)` を使う（または再ログイン）

---

## 事故②：クレームに色々入れすぎる📦💣

Custom Claimsは **1000バイト上限**。
「表示名」「設定」「権限リスト全部」みたいなのは入れない🙅‍♂️ ([Firebase][2])

対策✅

* **最小フラグだけ**（例：`admin: true`, `role: "editor"` 程度）
* それ以上は Firestoreに置いて、Rulesは“入口の判定”だけに使う（第17章で比較します）

---

## 事故③：クレーム名で地雷を踏む🧨

JWTの標準クレームっぽい名前や予約されてる名前を使うと危険。
公式も「予約されているクレーム名がある」注意をしています ([Firebase][2])

対策✅

* `admin`, `roles`, `tier`, `staff` みたいな **素朴な名前**にする

---

## 6) AI活用コーナー🤖✨（Antigravity / Gemini CLI）

Custom Claimsは「仕組み」はシンプルだけど、**実装のミスが致命傷**になりがち😇
だからAIはめちゃ便利。ただし…**最終レビューは人間の仕事👀✅**

## ✅ Antigravityでやると強いこと🧠⚡

Firebase MCP server を Antigravity に追加して、エージェントに「作業計画→実装→手順の説明」までやらせられます ([The Firebase Blog][5])

おすすめ依頼文（コピペOK）👇

* 「Custom Claimsで `admin: true` を付与する“安全な運用”を作りたい。

  1. 付与はAdmin SDKだけ、2) 付与後のトークン更新、3) 権限付与の監査ログ案、まで含めて設計して」

---

## ✅ Gemini CLI（Firebase拡張）で“叩き台”を速攻で作る💨

Firebase拡張を入れると、Firebase MCP serverの機能が使えます ([Firebase][6])
さらにプロンプトカタログのコマンド（例：`/firebase:init`）も使えます ([Firebase][7])

そして特にセキュリティルール生成は便利だけど、重要注意⚠️

* **Rulesは自動追従で更新されない**（1回実行の生成）
* **必ずテストしてからデプロイ**
* Admin SDK利用時はRulesが効かないので、バックエンド側で認可が必要 ([Firebase][8])

Custom ClaimsまわりでAIに頼むなら👇

* 「React側でclaimsを表示するコンポーネントを書いて」
* 「Admin SDKで `setCustomUserClaims` を使う最小スクリプトを書いて（JSON鍵の扱い注意も入れて）」
* 「“付与→トークン更新→反映確認”のチェックリストを作って」

---

## 7) ミニ課題🎯（10分）

1. 自分のUIDを表示できる✅
2. Admin SDKで `admin=true` を付ける✅
3. Reactで `forceRefresh=true` して、`claims.admin === true` を確認✅
4. できたら `setCustomUserClaims(uid, null)` で削除して、再び `admin` が消えるのも確認🧹 ([Firebase][2])

---

## 8) チェック✅（合格ライン）

* [ ] Custom Claimsは「サーバー（Admin SDK）だけ」から付与できると説明できる ([Firebase][2])
* [ ] 「付与直後に反映されない＝トークン更新が必要」を体で理解した ([Firebase][2])
* [ ] Claimsに“大量の情報”を入れない理由（1000バイト）を言える ([Firebase][2])
* [ ] 次章で `request.auth.token.admin` をRulesに組み込める準備ができた ([Firebase][1])

---

次の第16章では、ここで作った `admin` を使って **RulesでRBAC（ロール制御）を完成**させます👑🛡️
「adminだけ見えるコレクション」「一般ユーザーは自分の分だけ」みたいな王道パターンを一気に組みますよ🔥

[1]: https://firebase.google.com/docs/rules/rules-and-auth "Security Rules and Firebase Authentication  |  Firebase Security Rules"
[2]: https://firebase.google.com/docs/auth/admin/custom-claims "Control Access with Custom Claims and Security Rules  |  Firebase Authentication"
[3]: https://firebase.google.com/docs/admin/setup "Add the Firebase Admin SDK to your server"
[4]: https://firebase.google.com/docs/functions/manage-functions "Manage functions  |  Cloud Functions for Firebase"
[5]: https://firebase.blog/posts/2025/11/firebase-mcp-and-antigravity/ "Antigravity and Firebase MCP accelerate app development"
[6]: https://firebase.google.com/docs/ai-assistance/gcli-extension "Firebase extension for the Gemini CLI  |  Develop with AI assistance"
[7]: https://firebase.google.com/docs/ai-assistance/prompt-catalog "AI prompt catalog for Firebase  |  Develop with AI assistance"
[8]: https://firebase.google.com/docs/ai-assistance/prompt-catalog/write-security-rules "AI Prompt: Write Firebase Security Rules  |  Develop with AI assistance"
