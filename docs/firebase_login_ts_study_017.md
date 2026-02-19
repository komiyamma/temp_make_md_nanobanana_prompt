# 第17章：“uid基準”でデータを持つ準備：ユーザードキュメントの型🧠

この章は「Authでログインできた！」の次に来る、**アプリの背骨づくり**です💪🙂
やることはシンプルで、**ログインした人の `uid` をキーにして、`users/{uid}` に“その人のプロフィール箱”を作る**だけ📦✨
ここが固まると、次のFirestore章で「ユーザー別データ」「権限制御」が一気にラクになります🚀

---

## 0) まず考え方：AuthとFirestoreの役割分担🧠🔐🗂️

![Auth vs Firestore Role](./picture/firebase_login_ts_study_017_01_auth_vs_firestore.png)

* **Auth（認証）**は「本人かどうか」を管理する場所🔐
* **Firestore（データ）**は「アプリとして必要なプロフィール/設定/状態」を置く場所🗂️

Authの `user` だけでも動くけど、現実のアプリはだいたいこうなります👇

* ニックネーム、アイコン、初回チュートリアル済みフラグ、テーマ設定…などなど🎨🧑‍💻
  → これを **`users/{uid}` に集約**すると強い💥

そしてセキュリティ的にも、**`users/{uid}` は “本人だけ読める/書ける”** ルールにしやすいです✅
（`request.auth.uid == uid` の形が基本になります）([Firebase][1])

---

## 1) この章のゴール🎯✨

できあがりはこう👇

1. ログインしたら、`users/{uid}` が無ければ作る（あれば更新だけ）🧱
2. `users/{uid}` に、最低限のプロフィール初期値を入れる🧾
3. “本人だけアクセスできる” ルールの形を知る🛡️
4. （おまけ）AIで「プロフィール初期文」や「歓迎メッセージ」を作って入れる🤖💬

---

## 2) “ユーザードキュメントの型” を決めよう📐🧾

![User Document Schema](./picture/firebase_login_ts_study_017_02_data_schema.png)

まずは最小でOK！おすすめの最小セット👇（あとで増やせる前提👍）

* `uid: string`（固定）🆔
* `displayName: string | null`（名前）🙂
* `photoURL: string | null`（アイコン）🖼️
* `email: string | null`（必要なら）📧
* `providerIds: string[]`（google/password など）🌈
* `createdAt: serverTimestamp()`（作成時刻）⏱️
* `updatedAt: serverTimestamp()`（更新時刻）🔁
* `lastLoginAt: serverTimestamp()`（最終ログイン）🚪
* `profileVersion: number`（将来の移行用）🧬

> ⚠️ **パスワードやトークンは絶対保存しない**でOKです🙅‍♂️（Authが管理する領域）

---

## 3) Firestoreの準備（最小だけ）🧰🔥

Firestoreがまだならコンソールで有効化して、データベースを作ります🗂️
クライアント（ブラウザ）からFirestoreへ書き込む場合、**Security Rulesで許可しないと弾かれる**のが普通です（＝安全側がデフォ）🛡️([Firebase][1])

---

## 4) 実装：`users/{uid}` を“初回だけ作る”関数を作る🧱🧠

![Ensure Logic (Transaction)](./picture/firebase_login_ts_study_017_03_transaction_logic.png)

ここが本章のメインです💪🙂
ポイントは2つ：

* `onAuthStateChanged` は何度も走ることがある（リロード/復帰でも）🔁
* だから **“何回呼ばれても壊れない（冪等）”** にするのが勝ち✨

そこでおすすめは **トランザクション**です（「無ければ作る、あれば更新」）🧩

## 4-1) 型（TypeScript）🧾

```ts
// src/types/userDoc.ts
import type { Timestamp } from "firebase/firestore";

export type UserDoc = {
  uid: string;

  displayName: string | null;
  photoURL: string | null;
  email: string | null;
  emailVerified: boolean;

  providerIds: string[];

  profileVersion: number;

  createdAt: Timestamp;   // serverTimestampで入れる
  updatedAt: Timestamp;   // serverTimestampで入れる
  lastLoginAt: Timestamp; // serverTimestampで入れる
};
```

## 4-2) “ユーザードキュメントを保証する”関数🧱

```ts
// src/lib/ensureUserDoc.ts
import type { User } from "firebase/auth";
import { doc, runTransaction, serverTimestamp } from "firebase/firestore";
import { db } from "./firebase"; // 既に作ってる db を使う想定

export async function ensureUserDoc(user: User): Promise<void> {
  const ref = doc(db, "users", user.uid);

  await runTransaction(db, async (tx) => {
    const snap = await tx.get(ref);

    const providerIds = user.providerData
      .map((p) => p.providerId)
      .filter((v): v is string => !!v);

    // 毎回更新してOKなもの（lastLoginAt と updatedAt など）
    const common = {
      uid: user.uid,
      displayName: user.displayName ?? null,
      photoURL: user.photoURL ?? null,
      email: user.email ?? null,
      emailVerified: user.emailVerified,
      providerIds,
      updatedAt: serverTimestamp(),
      lastLoginAt: serverTimestamp(),
      profileVersion: 1,
    };

    if (!snap.exists()) {
      // 初回だけ作る
      tx.set(ref, {
        ...common,
        createdAt: serverTimestamp(),
      });
      return;
    }

    // 2回目以降は「上書き事故」を避けて merge
    tx.set(ref, common, { merge: true });
  });
}
```

---

## 5) どこで呼ぶ？おすすめは `onAuthStateChanged` の中📌🔁

![Auth Hook Integration](./picture/firebase_login_ts_study_017_04_hook_integration.png)

ログイン状態が変わったときに、ユーザードキュメントを整えちゃいます💪

```ts
// 例：AuthProvider 内
import { onAuthStateChanged } from "firebase/auth";
import { auth } from "./firebase";
import { ensureUserDoc } from "./ensureUserDoc";

useEffect(() => {
  const unsub = onAuthStateChanged(auth, async (user) => {
    if (user) {
      await ensureUserDoc(user);
    }
    // setUser / setLoading とかは今まで通り
  });

  return () => unsub();
}, []);
```

> ✅ これで「ログインできた人は、必ず `users/{uid}` がある」状態を作れます✨

---

## 6) （発展）“初回ログインだけ” を検出したいとき🌈👀

![New User Detection](./picture/firebase_login_ts_study_017_05_new_user.png)

例えば「初回だけチュートリアル出したい！」みたいな時は、Googleログイン（Popup/Redirect）で返る `UserCredential` から **`getAdditionalUserInfo()`** を使うと便利です🧠
公式のAPIリファレンスにもあります([Firebase][2])
`AdditionalUserInfo` には `isNewUser` がいます([Firebase][3])

```ts
import { GoogleAuthProvider, signInWithPopup, getAdditionalUserInfo } from "firebase/auth";
import { auth } from "./firebase";

export async function signInWithGoogle() {
  const provider = new GoogleAuthProvider();
  const cred = await signInWithPopup(auth, provider);

  const info = getAdditionalUserInfo(cred);
  const isNewUser = info?.isNewUser ?? false;

  return { user: cred.user, isNewUser };
}
```

---

## 7) Security Rules：`users/{uid}` は本人だけ🛡️🔐

![Security Match](./picture/firebase_login_ts_study_017_06_security_rules.png)

まずは “超基本形” を入れておくと、事故りにくいです✅
「本人の `uid` と一致するドキュメントだけ read/write 許可」みたいな形です🧷([Firebase][1])

```
// Firestore Security Rules（例）
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{uid} {
      allow read, write: if request.auth != null && request.auth.uid == uid;
    }
  }
}
```

> 🔥 よくあるエラー：`Missing or insufficient permissions`
> だいたい「ルールがまだ」「uidの一致条件が違う」「ログインしてない」のどれかです🙂

---

## 8) おまけ：AIでプロフィール初期値を“気持ちよく”する🤖✨

![AI Welcome Message](./picture/firebase_login_ts_study_017_07_ai_welcome.png)

たとえば、初回ログイン時に👇

* 「ようこそメッセージ」🎉
* 「プロフィールの自己紹介テンプレ」📝
* 「使い方の一言」💡
  を生成して `users/{uid}` に入れると、UXがグッと良くなります😊

Firebaseの **AI Logic（Gemini）** は、アプリからGeminiを呼ぶ導線として整理されています([Firebase][4])
しかも注意点として、**特定モデルが 2026-03-31 にリタイア予定**の記載もあるので、使うモデル名は新しめを選ぶのが安心です🧠([Firebase][5])

例（“歓迎メッセージ”生成イメージ）👇

```ts
import { getAI, getGenerativeModel } from "firebase/ai";
import { app } from "./firebase";

export async function generateWelcomeText(displayName: string | null) {
  const ai = getAI(app);
  const model = getGenerativeModel(ai, { model: "gemini-2.5-flash-lite" });

  const name = displayName ?? "あなた";
  const prompt = `${name}さん向けに、短い歓迎メッセージを日本語で1つ。絵文字多め。`;

  const result = await model.generateContent(prompt);
  return result.response.text();
}
```

> ⚠️ AIに渡す情報は最小でOK（メール全文とか個人情報をモリモリ渡さない）🙆‍♂️

---

## 9) Antigravity / Gemini CLI の使いどころ🚀🧑‍💻🤖

## Antigravity（エージェント開発）🛰️

Antigravityは「エージェントが計画→実装→検証までやる」タイプの開発支援で、Mission Control 的に扱えるよ、という説明が公式Codelabにあります([Google Codelabs][6])

この章で投げると強い“ミッション例”👇

* 「`ensureUserDoc` を冪等にして、AuthProviderに組み込んで」🧱
* 「`users/{uid}` の型を作って、参照側コンポーネントも生成して」🧾
* 「Firestore Rules の最小形を提案して」🛡️

## Gemini CLI（ターミナルのAIエージェント）⌨️

Gemini CLIは、ターミナルから使えるオープンソースのAIエージェントで、MCPやWeb検索などにも触れられています([Google Cloud Documentation][7])
この章だと👇みたいな使い方が刺さります🎯

* 「このリポジトリで `onAuthStateChanged` の呼び出し箇所を探して、最適な場所に `ensureUserDoc` を差し込んで」🔎
* 「`users/{uid}` を読む画面を追加して、型安全にして」🧩

---

## 10) ミニ課題🎒✅

## ミニ課題A：プロフィール表示ページを作る👤🖼️

* `users/{uid}` をリアルタイム購読（`onSnapshot`）して表示
* `displayName / email / providerIds / lastLoginAt` を出す

## ミニ課題B：初回だけ“ようこそ🎉”を出す

* `getAdditionalUserInfo().isNewUser` を使って
* 初回ログインならAIで歓迎文生成 → Firestoreに保存 → 画面表示✨

---

## 11) チェック問題（サクッと）✅🧠

1. `users/{uid}` の `uid` に **メールアドレス**を使わない理由は？
2. `onAuthStateChanged` で `ensureUserDoc()` を呼ぶメリットは？
3. `Missing or insufficient permissions` が出たとき、真っ先に疑う場所は？
4. `merge: true` を使うと何が嬉しい？
5. “初回ログインだけ” を検出するヒントは？

（答えの例：1は変更/プライバシー/ID設計的に微妙、2は復帰でも保証、3はRules、4は上書き事故防止、5は `getAdditionalUserInfo().isNewUser` など🙂）

---

## 次につながる話🔗🔥

ここまでで、**アプリのデータ設計が「uid中心」に切り替わりました**👏✨
次のFirestore章では、この `users/{uid}` を起点にして

* ユーザーごとのデータ（例：`users/{uid}/posts`）🗂️
* 一覧表示・検索・ページング📜
* Rulesの本格設計🛡️

に自然に入れます🚀

必要なら、この第17章の流れに合わせて「プロフィール表示コンポーネント」「購読フック（`useUserDoc`）」「AI歓迎文の保存」まで、まるごと教材として続きも書くよ🙂✨

[1]: https://firebase.google.com/docs/rules/basics "Basic Security Rules  |  Firebase Security Rules"
[2]: https://firebase.google.com/docs/reference/js/auth "auth package  |  Firebase JavaScript API reference"
[3]: https://firebase.google.com/docs/reference/js/auth.additionaluserinfo "AdditionalUserInfo interface  |  Firebase JavaScript API reference"
[4]: https://firebase.google.com/docs/ai-logic/get-started "Get started with the Gemini API using the Firebase AI Logic SDKs  |  Firebase AI Logic"
[5]: https://firebase.google.com/docs/ai-logic "Gemini API using Firebase AI Logic  |  Firebase AI Logic"
[6]: https://codelabs.developers.google.com/getting-started-google-antigravity "Getting Started with Google Antigravity  |  Google Codelabs"
[7]: https://docs.cloud.google.com/gemini/docs/codeassist/gemini-cli "Gemini CLI  |  Gemini for Google Cloud  |  Google Cloud Documentation"
