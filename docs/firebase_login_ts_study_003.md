# 第03章：React側のAuth土台：SDK導入＆初期化（モジュラー流儀）🧩

この章でやるのはシンプル！
**「Firebaseをアプリに組み込む“配線”」**を作って、次章以降でログイン処理をガンガン足せる状態にします💪✨

---

![Project Structure](./picture/firebase_login_ts_study_003_05_file_structure.png)

## 0) 今日できあがるもの 🎯

* `firebase` SDK を入れる 📦
* `.env.local` に設定値を入れる 🔐
* `src/lib/firebase.ts` を作って
  `app` と `auth` を **export** する 🚀
* 起動してエラーゼロを確認✅

（FirebaseのWeb導入は “npmで入れて initialize して使う” の流れが公式です）([Firebase][1])

---

![NPM Install](./picture/firebase_login_ts_study_003_01_install.png)

## 1) SDKをインストール 📦✨

ターミナルでプロジェクトのルートへ移動して👇

```bash
npm i firebase
```

2026-02時点だと、`firebase` の最新版は **12.9.0** が見えてます（公開日表示も出ます）。([npm][2])

確認したければ👇

```bash
npm ls firebase
```

---

![Config Source](./picture/firebase_login_ts_study_003_02_config_source.png)

## 2) Firebase設定（firebaseConfig）を用意する 🔧

Firebaseコンソールの「Webアプリ」の設定で出てくる **firebaseConfig** を使います。
この `firebaseConfig` は “公開してOKな識別子の塊” で、公式もその前提で案内しています。([Firebase][3])

> ただし！
> **Gemini用に生成される「Gemini API key」はアプリコードに入れないでね**（ここは別扱いで超重要⚠️）([Firebase][4])

---

![Env Var Injection](./picture/firebase_login_ts_study_003_03_env_injection.png)

## 3) `.env.local` に設定値を入れる（Vite想定）🧪

プロジェクト直下に `.env.local` を作って、こういう感じで入れます👇
（値はコンソールからコピペでOK✂️）

```env
VITE_FIREBASE_API_KEY=xxxxxxxxxxxxxxxxxxxx
VITE_FIREBASE_AUTH_DOMAIN=xxxxxx.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=xxxxxx
VITE_FIREBASE_STORAGE_BUCKET=xxxxxx.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=1234567890
VITE_FIREBASE_APP_ID=1:1234567890:web:xxxxxxxxxxxx
```

---

![Singleton Guard](./picture/firebase_login_ts_study_003_04_singleton_guard.png)

## 4) `firebase.ts` を作る（ここが“背骨”🦴）🧩

`src/lib/firebase.ts` を作って👇

```ts
// src/lib/firebase.ts
import { initializeApp, getApp, getApps } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY as string,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN as string,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID as string,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET as string,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID as string,
  appId: import.meta.env.VITE_FIREBASE_APP_ID as string,
};

// ✅ 開発中(HMR)にimportが複数回走っても落ちないようにガードする
export const app = getApps().length ? getApp() : initializeApp(firebaseConfig);

// ✅ 認証の入口（次章からここを使い倒す！）
export const auth = getAuth(app);
```

ポイントはこれ👇

* `getApps().length ? ...` がないと、開発中に **“[DEFAULT] もうあるよ！”** で怒られがち😇（Hot Reload あるある）

---

## 5) 動作確認（エラーゼロを勝ち取る🏆）✅

起動！

```bash
npm run dev
```

画面が出て、コンソールが真っ赤じゃなければOK🙆‍♂️✨
“Authの初期化に成功してる” 状態です。

---

## 6) つまずきポイント集（ここで9割救われる🛟）😵‍💫➡️😊

## A. `Firebase App named '[DEFAULT]' already exists`

原因：`initializeApp()` が複数回呼ばれてる
対策：さっきの `getApps()` ガードを入れる✅

---

## B. `import.meta.env` が `undefined` っぽい

原因：

* `.env.local` が **プロジェクト直下**にない
* 変数名が `VITE_` で始まってない
  対策：
* 位置と名前を見直す🔍
* **devサーバー再起動**（envは再起動しないと読まれないこと多い）🔁

---

## C. `Module not found: firebase/auth` みたいなやつ

原因：インストールできてない / 依存が壊れてる
対策：

* `npm ls firebase` で入ってるか確認
* だめなら `node_modules` 消して入れ直し（最終手段）💥

---

![Firebase AI Integration](./picture/firebase_login_ts_study_003_06_ai_integration.png)

## 7) 🤖AIサービスも“同じ配線”でつながる（超うれしいポイント）✨

FirebaseのAI（Firebase AI Logic）は、Webだと `firebase/ai` から使います。([Firebase][4])
この章では「将来すぐ足せる形」にだけしておくのが気持ちいい👍

## 7-1) AI Logic の初期化イメージ（置いておくだけOK）🧠✨

`src/lib/firebase-ai.ts` を作るイメージ👇（あとで有効化したら動かす）

```ts
// src/lib/firebase-ai.ts
import { app } from "./firebase";
import { getAI, getGenerativeModel, GoogleAIBackend } from "firebase/ai";

// Gemini Developer API を使う例（Firebase AI Logic側のガイドに沿った形）
export const ai = getAI(app, { backend: new GoogleAIBackend() });

// モデルは用途に合うものを選ぶ（例）
export const model = getGenerativeModel(ai, { model: "gemini-2.5-flash" });
```

モデル名の例は公式サンプルにも出ています。([Firebase][4])
それと、**Gemini 2.0 Flash/Flash-Lite は 2026-03-31 にリタイア予定**が明記されてるので、古い指定のままにしないのが安全です🧯([Firebase][4])

そして超重要⚠️
**Gemini API key はアプリコードに入れない**（これは公式が強く注意してます）([Firebase][4])

---

## 8) Antigravity / Gemini CLI に“任せる”と爆速になる🚀🤖

## Antigravity ミッション例 🧑‍🚀

* 「`.env.local` から設定を読み、`firebase.ts` を作って、HMRでも落ちないようにして」
  みたいに投げると、**配線作業が一瞬**になります🧩✨（Antigravityはエージェント主導で計画→実装→検証まで回す思想）([Google Codelabs][5])

## Gemini CLI でセルフレビュー 🔎

* `firebase.ts` を見せて「初期化の二重実行の可能性ある？」「安全に直して」みたいに聞くと、**構成チェック**が速いです⚡（Gemini CLIはターミナルから使えるAIエージェントとして案内されています）([Google Cloud Documentation][6])

---

![Debugging Init](./picture/firebase_login_ts_study_003_07_debugger.png)

## 9) ミニ課題 🎮✅

1. `src/lib/firebase.ts` を作ったら、どこかの画面で一回だけ👇を入れてみる（動作確認）

   * `console.log("firebase app ok", app.name);`
2. `auth` を import して👇を出してみる

   * `console.log("currentUser", auth.currentUser);`（今は `null` で普通🙂）

---

## 10) チェック問題（理解が固まるやつ🧠✅）

**Q1.** `getApps()` ガードは何のため？
**Q2.** `.env.local` のキー名が `VITE_` で始まらないとダメなのはなぜ？
**Q3.** Firebaseの `apiKey` と、Geminiの `API key` の扱いが違うのはなぜ？

**答え（サクッと）**

* **A1.** 開発中の再読み込み等で `initializeApp()` が複数回呼ばれても落ちないようにするため🙂
* **A2.** Viteが “クライアントへ公開してよい env” を `VITE_` 接頭辞で判定してるから🔑
* **A3.** Firebaseの `apiKey` は公開前提の識別子として扱われる一方、Gemini用キーは **コードに入れない**よう公式が注意しているから⚠️([Google Cloud Documentation][6])

---

次の第4章では、この `auth` を使って **ログイン状態監視（onAuthStateChanged）でアプリの背骨を通す🦴** に進めるよ！🚀

[1]: https://firebase.google.com/docs/web/setup "Add Firebase to your JavaScript project  |  Firebase for web platforms"
[2]: https://www.npmjs.com/package/firebase?utm_source=chatgpt.com "firebase"
[3]: https://firebase.google.com/docs/projects/api-keys "Learn about using and managing API keys for Firebase  |  Firebase Documentation"
[4]: https://firebase.google.com/docs/ai-logic/get-started "Get started with the Gemini API using the Firebase AI Logic SDKs  |  Firebase AI Logic"
[5]: https://codelabs.developers.google.com/getting-started-google-antigravity?utm_source=chatgpt.com "Getting Started with Google Antigravity"
[6]: https://docs.cloud.google.com/gemini/docs/codeassist/gemini-cli "Gemini CLI  |  Gemini for Google Cloud  |  Google Cloud Documentation"
