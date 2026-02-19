# 第7章：ユーザー別データ設計（uid基準の王道）👤📁✨

この章のゴールはコレ👇
**「ログインした人が“自分のデータだけ”読める/書ける」状態を、Rulesでカチッと作る**ことです🔐💪
そして…**他人のuidをURLみたいに指定しても、ちゃんと弾ける**ようにします🚫😤

---

## 1) まず“王道”を1枚で理解しよう🗺️✨

FirestoreのRulesは、基本 **「パス（場所）＋条件」**で守ります🧱
つまり、データの置き方がキレイだと、Rulesもキレイになります🙂✨

## ✅ 王道の設計（超おすすめ）👑

![User Data Model Structure](./picture/firebase_security_role_ts_study_007_01_user_data_model.png)

* **users/{uid}** … そのユーザー本人の“マイページの本体”📄
* **users/{uid}/(subcollections)** … その人の個別データ（メモ、設定、下書き…）📦
* **publicProfiles/{uid}** … 公開プロフィール（読むのは全員OK、書くのは本人だけ）🌍🧑‍💻

ここで大事なのがコレ👇
**uidを「ドキュメントID」にする**こと！
そうするとRulesが「本人かどうか」を判断しやすいんです😆

Rules側では、認証情報として **`auth.uid`（ユーザー固有ID）** が使えます。([Firebase][1])
（Rules言語の基本構造は `match` と `allow` で作ります🧩）([Firebase][2])

---

## 2) ありがちな失敗パターン（先に踏んで回避😂💥）

## ❌ 失敗A：uidを“フィールド”に入れて所有者判定しようとする

![Vulnerable Field-Based Security](./picture/firebase_security_role_ts_study_007_02_field_id_antipattern.png)

例：`posts/{postId}` の中に `ownerUid: "xxx"` を入れて、Rulesで `request.auth.uid == resource.data.ownerUid` みたいにするやつ。

これ、**正しく書けば可能**なんだけど、初心者がやると事故りやすいです😇
理由は👇

* 「作成時に ownerUid を好きに書かれる」事故が起きる💣
* 「更新で ownerUid を書き換えられる」事故が起きる💣💣

👉 まずは **パスにuidを埋める設計**から入るのが安全です🛡️✨

## ❌ 失敗B：`auth != null` だけでOKにしちゃう

![Auth Only Risk (Too Permissive)](./picture/firebase_security_role_ts_study_007_03_auth_only_risk.png)

「ログインしてればOK」だけだと、**“全ログインユーザーが他人のデータ触れる”**状態になりがち😱
公式にも「authだけチェックして満足してない？」って注意があります⚠️([Firebase][3])

---

## 3) Hands-on：データ構造を作る🧑‍💻📁

今回はこの形にします👇

* `users/{uid}`（非公開・本人だけ）

  * `displayName`
  * `photoURL`
  * `createdAt`
  * `updatedAt`

* `publicProfiles/{uid}`（公開・読むのは全員OK、更新は本人だけ）

  * `displayName`
  * `photoURL`
  * `updatedAt`

* `users/{uid}/notes/{noteId}`（非公開メモ・本人だけ）

  * `text`
  * `updatedAt`

---

## 4) Rulesを書こう（まずは“最小で強い”やつ）🛡️✨

![isOwner Security Logic](./picture/firebase_security_role_ts_study_007_04_is_owner_logic.png)

ポイントはこれだけ👇
**「ログインしていて、かつ uid が一致する」**＝本人✅

```txt
rules_version = '2';

service cloud.firestore {
  match /databases/{database}/documents {

    function signedIn() {
      return request.auth != null;
    }

    function isOwner(uid) {
      return signedIn() && request.auth.uid == uid;
    }

    // ✅ 本人だけのデータ（超王道）
    match /users/{uid} {
      allow read, write: if isOwner(uid);
    }

    // ✅ 本人だけが書けて、読むのは全員OK（公開プロフィール）
    match /publicProfiles/{uid} {
      allow read: if true;
      allow create, update: if isOwner(uid);
      allow delete: if false;
    }

    // ✅ 本人だけのサブコレ（メモなど）
    match /users/{uid}/notes/{noteId} {
      allow read, write: if isOwner(uid);
    }
  }
}
```

`rules_version = '2'`（v2が最新）も忘れずにね🙂([Firebase][2])

---

## 5) React(TypeScript)で「自分のusers/{uid}」を触る👆✨

![React UID Reference Logic](./picture/firebase_security_role_ts_study_007_05_react_uid_ref.png)

「ドキュメントID＝uid」にするのがコツです👑
（自動IDにしない！）

```ts
import { getAuth } from "firebase/auth";
import { getFirestore, doc, getDoc, setDoc, serverTimestamp } from "firebase/firestore";

const auth = getAuth();
const db = getFirestore();

export async function upsertMyUserProfile(displayName: string, photoURL?: string) {
  const user = auth.currentUser;
  if (!user) throw new Error("Not signed in");

  const ref = doc(db, "users", user.uid);

  await setDoc(
    ref,
    {
      displayName,
      photoURL: photoURL ?? null,
      updatedAt: serverTimestamp(),
      createdAt: serverTimestamp(), // 初回以外は上書きされちゃうのが気になるなら後で改善OK🙂
    },
    { merge: true }
  );
}

export async function readMyUserProfile() {
  const user = auth.currentUser;
  if (!user) throw new Error("Not signed in");

  const ref = doc(db, "users", user.uid);
  const snap = await getDoc(ref);
  return snap.exists() ? snap.data() : null;
}
```

---

## 6) “他人のuidで読めない”を確認しよう（ここが本番😤🧪）

![Unauthorized Access Attempt](./picture/firebase_security_role_ts_study_007_06_attack_simulation.png)

## 手で確認（超シンプル）🖱️

1. Aユーザーでログインして `users/{Aのuid}` を読む ✅
2. コードをわざと改造して `users/{Bのuid}` を読もうとする
3. **Permission denied** になったら勝ち🏆✨

---

## 7) Emulatorでテスト（安全開発の必殺技）🧪🧯

Rulesは「書いて終わり」じゃなくて、**テストしてから出す**が正解です✅
公式もEmulatorでの検証＆単体テストを推しています🧪([Firebase][4])

## まずEmulator起動🚀

```sh
firebase emulators:start --only firestore,auth
```

（Emulatorのセットアップや起動はこの流れが基本です）([Firebase][5])

## Rulesの単体テスト例（Jest想定）🧪

![Unit Test Scenarios](./picture/firebase_security_role_ts_study_007_07_unit_test_cases.png)

「Aliceは自分のusers/Aliceは読める、Bobのusers/Bobは読めない」を機械で保証します🤖✅

```ts
import fs from "node:fs";
import { initializeTestEnvironment, assertFails, assertSucceeds } from "@firebase/rules-unit-testing";
import { doc, getDoc, setDoc } from "firebase/firestore";

test("users/{uid} is private to the owner", async () => {
  const testEnv = await initializeTestEnvironment({
    projectId: "demo-rules-ch7",
    firestore: {
      rules: fs.readFileSync("firestore.rules", "utf8"),
    },
  });

  const alice = testEnv.authenticatedContext("aliceUid");
  const bob = testEnv.authenticatedContext("bobUid");

  const aliceDb = alice.firestore();
  const bobDb = bob.firestore();

  // ✅ Aliceは自分のドキュメントを書ける
  await assertSucceeds(setDoc(doc(aliceDb, "users", "aliceUid"), { displayName: "Alice" }));

  // ✅ Aliceは自分のドキュメントを読める
  await assertSucceeds(getDoc(doc(aliceDb, "users", "aliceUid")));

  // ❌ BobはAliceのドキュメントを読めない
  await assertFails(getDoc(doc(bobDb, "users", "aliceUid")));

  await testEnv.cleanup();
});
```

（単体テストの考え方と環境づくりは公式ガイドが一番確実です）([Firebase][6])

---

## 8) AI活用：Rulesとテストの“叩き台”を爆速で作る🤖⚡

## ✅ 使い分けのコツ（超大事）🧠

* AI：**叩き台を作る**（構造、ルールの候補、テストの雛形）🧱
* 人間：**最終判断＆レビュー**（漏れ、意図、事故ポイント）👀🧑‍⚖️

## Gemini CLI（Firebase拡張）でRules生成🛠️

FirebaseのAI支援では、**Gemini CLI の拡張がプロジェクト状態を見てRulesを“1回生成”**できます。
ただし **自動追従で更新されるわけじゃない**ので、更新は自分でやる必要ありです⚠️([Firebase][7])

さらに、AIプロンプト集も用意されていて、MCP対応のAIアシスタントから使える流れになっています📚✨([Firebase][8])

👉 AIに投げるおすすめ指示（そのままコピペOK）👇

* 「`users/{uid}` は本人だけ read/write」
* 「`publicProfiles/{uid}` は read=全員、write=本人」
* 「`users/{uid}/notes/{noteId}` は本人だけ」
* 「Emulator用の単体テスト（owner/other/unauth）も作って」🧪

## Antigravity + Firebase MCP で、状況を見ながら相談＆整備🧲✨

Antigravityに **Firebase MCP server** を入れると、エージェントがFirebase手順や状態に沿って作業しやすくなります（導入手順も公式で案内あり）([The Firebase Blog][9])

## Gemini in Firebase の立ち位置🙂

Gemini in Firebase はRulesの相談はできるけど、**コードベースにアクセスできないのでRulesを“生成”する用途はGemini CLI推奨**、という整理です🧠([Firebase][10])

---

## 9) ミニ課題🎯✨（10〜20分想定）

## 課題A：非公開プロフィール（users/{uid}）

* `displayName` を更新できるUIを作る🖊️
* devtools等で“他人uid”に差し替えて読みに行って、弾かれるのを確認🚫😤

## 課題B：公開プロフィール（publicProfiles/{uid}）

* 一覧画面（全員のpublicProfilesを読む）を作る🌍
* でも更新は本人だけ（他人のpublicProfiles/{uid}更新が弾かれる）✅

---

## 10) チェック✅（ここまでできたら勝ち🏆）

* [ ] `users/{uid}` が **本人以外は読めない/書けない**🔒
* [ ] `publicProfiles/{uid}` が **読むのは全員OK、更新は本人だけ**🌍✍️
* [ ] “uidを差し替える攻撃”を試しても **Permission denied** になる💥
* [ ] Emulatorテストで ✅/❌ が自動で確認できる🧪

---

必要なら、次の一歩として「users/{uid} の中でも **フィールドごとに更新可否を分ける**（例：createdAtは絶対変更不可）」みたいな“事故りにくさMAX”設計も、この章の続きとして作れます😆🛡️

[1]: https://firebase.google.com/docs/rules/rules-and-auth "Security Rules and Firebase Authentication  |  Firebase Security Rules"
[2]: https://firebase.google.com/docs/rules/rules-language "Security Rules language  |  Firebase Security Rules"
[3]: https://firebase.google.com/docs/firestore/security/insecure-rules?utm_source=chatgpt.com "Fix insecure rules | Firestore - Firebase"
[4]: https://firebase.google.com/docs/emulator-suite?utm_source=chatgpt.com "Introduction to Firebase Local Emulator Suite"
[5]: https://firebase.google.com/docs/rules/emulator-setup?utm_source=chatgpt.com "Set up the Local Emulator Suite | Firebase Security Rules"
[6]: https://firebase.google.com/docs/rules/unit-tests?utm_source=chatgpt.com "Build unit tests | Firebase Security Rules - Google"
[7]: https://firebase.google.com/docs/ai-assistance/prompt-catalog/write-security-rules?utm_source=chatgpt.com "AI Prompt: Write Firebase Security Rules | Develop with AI assistance"
[8]: https://firebase.google.com/docs/ai-assistance/prompt-catalog?utm_source=chatgpt.com "AI prompt catalog for Firebase | Develop with AI assistance"
[9]: https://firebase.blog/posts/2025/11/firebase-mcp-and-antigravity/?utm_source=chatgpt.com "Antigravity and Firebase MCP accelerate app development"
[10]: https://firebase.google.com/docs/ai-assistance/gemini-in-firebase?utm_source=chatgpt.com "Gemini in Firebase - Google"
