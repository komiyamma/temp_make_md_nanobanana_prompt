# 第16章：Custom Claims × RulesでRBAC（王道パターン）👑🛡️

この章のゴールはこれ👇✨
**「一般ユーザーは自分のデータだけ」＆「管理者は全部」** を、**Security Rulesだけで機械的に守れる**状態にするよ🙂🔐
（UIで隠すだけ、は卒業〜！🙅‍♂️💦）

---

## 0) まず“RBACの王道”って何？🗺️

**RBAC = Role Based Access Control（役割で権限を分ける）** だよ👮‍♂️👩‍💻

今回の王道パターンはこれ👇

* 役割（例：admin）を **AuthenticationのIDトークンに埋め込む** 🎫
* その中身を **Rulesの `request.auth.token` で見て分岐** 🧠
  （custom claims が `auth.token` に入る）([Firebase][4])

✅ これで「クライアント改造されたら終わり😱」を潰せる！
（サーバー側で“役割”を確定させるからね）

---

## 1) 読む📖：Custom Claimsの超重要ポイント3つ⚠️

## 1-1. Custom Claimsは“権限のためだけ”に使う🎫

* **サイズ上限は1000 bytes**、しかも **JSON化できる値だけ**（boolean / string / number / array / object など）([Firebase][5])
* 予約語（OIDC / Firebase reserved names）もあるので、変なキー名は避ける([Firebase][5])
* 「プロフィール」みたいな頻繁に変わる情報は **DBに置く**のが正解🧺（claimsは“権限”専用）

## 1-2. 付与は“特権サーバー環境”だけでやる🧨

Custom claims は **機密になり得る**ので、**Firebase Admin SDKが動く特権環境でのみ設定すべき**、と公式に書いてあるよ([Firebase][5])
→ つまり **クライアントから直接付与は絶対NG** 🙅‍♀️🔥

## 1-3. 付与しても、すぐ反映されないことがある⏳

claims は **次に新しいIDトークンが発行**されたタイミングで反映されるよ([Firebase][5])
ただし、クライアント側で **強制リフレッシュ**できる👇
`currentUser.getIdToken(true)` でトークン更新できる([Firebase][5])

---

## 2) 手を動かす🧑‍💻：やること全体図（今日の作業）🧩

やる順番はこれでOK👇✨

1. **（初回だけ）自分を admin にする** 🎫👑
2. admin が使える **「権限付与Function」** を作る⚙️
3. Firestore Rules で **admin / 一般ユーザーを分岐** 🛡️
4. React側で **admin UI を出し分け** 🖥️✨
5. Emulatorで **admin/user/未ログインをテスト** 🧪

---

## 3) 例のデータ構造（いつもの `privateNotes` をRBAC化）🗂️

このシリーズで使ってる例に合わせて進めるね🙂

* `privateNotes/{uid}/notes/{noteId}`

  * 一般ユーザー：自分の `{uid}` 配下だけ
  * admin：誰の `{uid}` 配下でもOK

* `adminOnlyLogs/{logId}`

  * admin だけ読み書きOK

---

## 4) 実装①：Admin付与の“入口”を作る（Cloud Functions）⚙️🔐

## 4-1. Nodeランタイムは 22 or 20 を選ぶ🧠

Cloud Functions for Firebase の Node.js は **22 / 20 がサポート**、18は非推奨だよ([Firebase][6])

## 4-2. 管理者だけが実行できる callable function（TypeScript例）📞

「adminが、別ユーザーに admin=true を付与/解除する」関数を作るよ🙂
ポイントはこれ👇

* 呼び出し側が admin じゃなきゃ拒否🙅‍♂️
* 既存claimsを **マージ**して上書き事故を防ぐ🧯（incremental更新例が公式にある）([Firebase][5])

```ts
// functions/src/index.ts
import { initializeApp } from "firebase-admin/app";
import { getAuth } from "firebase-admin/auth";
import { onCall, HttpsError } from "firebase-functions/v2/https";

initializeApp();

type SetAdminRequest = { targetUid: string; admin: boolean };

export const setAdmin = onCall(async (req) => {
  // 1) ログインしてない人は無理
  if (!req.auth) throw new HttpsError("unauthenticated", "ログインしてね🙂");

  // 2) 呼び出し側がadminじゃないと無理
  if (req.auth.token.admin !== true) {
    throw new HttpsError("permission-denied", "管理者だけが実行できます👑");
  }

  const { targetUid, admin } = req.data as SetAdminRequest;

  if (!targetUid) throw new HttpsError("invalid-argument", "targetUid が必要です🧩");

  const auth = getAuth();
  const user = await auth.getUser(targetUid);

  // 3) 既存claimsを保ったまま更新（上書き事故を防ぐ）
  const current = user.customClaims ?? {};
  await auth.setCustomUserClaims(targetUid, { ...current, admin: !!admin });

  return { ok: true };
});
```

> ✅ Custom claims は **特権サーバー環境のAdmin SDKからのみ設定すべき**([Firebase][5])
> なので、こういうFunctions経由が王道だよ🙂✨

---

## 5) 実装②：（初回だけ）最初のadminをどう作る？👑🧨

ここだけは現実的に **“プロジェクト管理者が1回だけ”** やる必要があるよ🙂
理由：まだ admin が誰もいないから、4章の `setAdmin` を呼べない🤣💦

やり方は色々あるけど、教材として安全で分かりやすいのは👇

* **ローカルの一回限りスクリプト**で自分に `admin: true` を付与
* その後は **`setAdmin` で運用**（管理画面から操作できる）

※ここでの注意：サービスアカウント鍵は超重要なので、Gitに入れない＆漏らさないでね🧯🔑（“権限の根っこ”だから）

（カスタムクレーム設定自体はAdmin SDKでこうやる、が公式）([Firebase][5])

---

## 6) 実装③：RulesでRBAC（admin / owner 分岐）🛡️✨

`request.auth.token` で custom claims を見て分岐できるよ([Firebase][4])
（公式例も `request.auth.token.admin == true` って書き方！）([Firebase][4])

```rules
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    function isSignedIn() {
      return request.auth != null;
    }

    function isAdmin() {
      return isSignedIn() && request.auth.token.admin == true;
    }

    function isOwner(uid) {
      return isSignedIn() && request.auth.uid == uid;
    }

    // ✅ 例：adminだけが見れるログ
    match /adminOnlyLogs/{logId} {
      allow read, write: if isAdmin();
    }

    // ✅ 例：privateNotes は「本人だけ」or「adminなら全部」
    match /privateNotes/{uid}/notes/{noteId} {
      allow read: if isOwner(uid) || isAdmin();
      allow create: if isOwner(uid) || isAdmin();
      allow update, delete: if isOwner(uid) || isAdmin();
    }
  }
}
```

🎉 これで完成！
クライアントでURLを書き換えて他人の `{uid}` を読もうとしても、**Rulesが門番して落とす**🚪🛡️

---

## 7) 実装④：React側でadmin UIを出し分ける🖥️👑

Rulesが本体だけど、UX的に **adminだけ管理画面を見せる**のは大事🙂✨
IDトークンのclaimsは **リフレッシュで最新化**できるよ([Firebase][5])

```ts
import { useEffect, useState } from "react";
import { getAuth, onAuthStateChanged } from "firebase/auth";

export function useIsAdmin() {
  const [isAdmin, setIsAdmin] = useState(false);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const auth = getAuth();
    return onAuthStateChanged(auth, async (user) => {
      if (!user) {
        setIsAdmin(false);
        setReady(true);
        return;
      }

      // claims取得（必要なら true で強制更新もできる）
      const tokenResult = await user.getIdTokenResult();
      setIsAdmin(tokenResult.claims.admin === true);
      setReady(true);
    });
  }, []);

  return { isAdmin, ready };
}
```

💡「admin付与したのに反映されない😭」って時は、対象ユーザー側で
`getIdToken(true)`（強制更新）を挟むと直ることが多いよ([Firebase][5])

---

## 8) 実装⑤：Emulatorで“3者テスト”（未ログイン / user / admin）🧪🧯

ここ、めっちゃ大事！！！🔥
Rulesは **テストが本体**🙂

ユニットテスト環境では、`authenticatedContext()` に **tokenOptions（= custom claims）** を渡せるよ([Firebase][7])

イメージ👇（要点だけ）

```ts
import { initializeTestEnvironment, assertFails, assertSucceeds } from "@firebase/rules-unit-testing";
import fs from "node:fs";
import { doc, getDoc, setDoc } from "firebase/firestore";

test("RBAC: adminだけadminOnlyLogsに書ける", async () => {
  const testEnv = await initializeTestEnvironment({
    projectId: "demo-project",
    firestore: { rules: fs.readFileSync("firestore.rules", "utf8") },
  });

  const anon = testEnv.unauthenticatedContext();
  const user = testEnv.authenticatedContext("user1");
  const admin = testEnv.authenticatedContext("admin1", { token: { admin: true } }); // ←ここが肝！

  await assertFails(setDoc(doc(anon.firestore(), "adminOnlyLogs/log1"), { x: 1 }));
  await assertFails(setDoc(doc(user.firestore(), "adminOnlyLogs/log1"), { x: 1 }));
  await assertSucceeds(setDoc(doc(admin.firestore(), "adminOnlyLogs/log1"), { x: 1 }));
});
```

---

## 9) AI活用🤖✨：Rules＆テストの叩き台を一瞬で作る（でも最後は人間）🧑‍⚖️✅

## 9-1. Gemini CLIで「Rules＋テスト」を生成できる🧠

Firebase公式の AI Prompt（Preview）として、**Rules生成＆改善**が案内されてるよ([Firebase][8])
重要ポイント👇

* 自動更新じゃない（毎回手で更新が必要）([Firebase][8])
* 生成AIは間違えるので必ずレビュー＆テスト([Firebase][8])
* Admin SDK経由のアクセスはRulesが呼ばれない（別途バックエンドで認可が必要）([Firebase][8])

Gemini CLI拡張の導入〜実行例👇([Firebase][8])

```bash
gemini extensions install https://github.com/gemini-cli-extensions/firebase
gemini
```

（プロジェクトルートで）生成👇([Firebase][8])

```text
/firestore:generate_security_rules
```

## 9-2. Antigravityでも同系の“プロンプト資産”を使える🧩

Firebase MCP server のプロンプト群は、Antigravity や Gemini CLI など複数AIアシスタントで使える、って整理されてるよ([Firebase][9])
→ 「RBACにしたい」「privateNotesをadmin/ownerで分岐したい」みたいに、仕様を日本語で投げて叩き台を作るのが超効率的🙂✨

---

## 10) ミニ課題🎯（10〜20分）：RBACを“本当に使える”形にする💪✨

やること👇😊

1. `adminOnlyLogs` に

* admin：書ける✅
* user/未ログイン：書けない❌
  を **Emulatorテストで保証**🧪

2. `privateNotes/{uid}/notes/{noteId}` に

* user：自分のuidだけ✅
* admin：誰のuidでも✅
  を **Rules simulator でも軽く確認**（Consoleのシミュレータで認証あり/なしを試せる）([Firebase][10])

---

## 11) チェック✅（この章を終えたらここが言える！）

* `request.auth.token` で **claimsを見て分岐できる**🙂([Firebase][4])
* custom claims は **Admin SDKの特権環境でだけ付与**するべき🔥([Firebase][5])
* 反映が遅い時は **トークン強制更新**で追いつかせられる🎫🔁([Firebase][5])
* Emulatorで **admin/user/未ログイン**の3者テストを書ける🧪([Firebase][7])

---

次の第17章（Firestore内でロール管理するパターン）に行くと、
「claimsが向いてる範囲／DBが向いてる範囲」の線引きがもっとクリアになるよ🙂📦✨

[1]: https://chatgpt.com/c/6992f8ee-fedc-83a3-a90f-8746d566cf64 "Firebaseセキュリティルール"
[2]: https://chatgpt.com/c/6992f61a-962c-83a5-8413-d0c320868184 "Rules言語の基本②"
[3]: https://chatgpt.com/c/6993016c-3a30-83a6-8c8d-b8b3765f684b "Firestore セキュリティルール"
[4]: https://firebase.google.com/docs/rules/rules-and-auth "Security Rules and Firebase Authentication  |  Firebase Security Rules"
[5]: https://firebase.google.com/docs/auth/admin/custom-claims "Control Access with Custom Claims and Security Rules  |  Firebase Authentication"
[6]: https://firebase.google.com/docs/functions/1st-gen/manage-functions-1st?hl=ja "関数を管理する（第 1 世代）  |  Cloud Functions for Firebase"
[7]: https://firebase.google.com/docs/rules/unit-tests "Build unit tests  |  Firebase Security Rules"
[8]: https://firebase.google.com/docs/ai-assistance/prompt-catalog/write-security-rules "AI Prompt: Write Firebase Security Rules  |  Develop with AI assistance"
[9]: https://firebase.google.com/docs/ai-assistance/prompt-catalog "AI prompt catalog for Firebase  |  Develop with AI assistance"
[10]: https://firebase.google.com/docs/firestore/security/get-started "Get started with Cloud Firestore Security Rules  |  Firebase"
