# 第10章：Firebaseの接続口を1ファイルにまとめる 🔌🔥

## 今日のゴール 🎯

「Firebaseを使うための入口」を **1つのファイル（例：`firebase.ts`）に集約**して、どこからでも同じインスタンスを使える状態にします🙂✨
これができると、Auth/Firestore/Storage/Functions/AI などを **安全にスッキリ追加**していけます！🚀

---

## まず理解：なんで1ファイルにするの？🧠

## ✅ 理由1：初期化は“1回だけ”が基本

Firebaseは `initializeApp()` を **何回も呼ばない**のが基本です。
入口が散らばると「どこで初期化したっけ？😵」になりがちです。

## ✅ 理由2：必要なものだけ import して軽くできる（Tree Shaking）🌲

Firebase Web SDK は “モジュール式（v9以降）” が、バンドラ最適化（Tree Shaking）に向いてます。必要な関数だけ import するほど、最終ビルドが軽くなります🏃‍♂️💨 ([Firebase][1])

## ✅ 理由3：環境切り替え（開発/本番）がラクになる 🔁

設定（Firebase config）を env に寄せておくと、`.env.production` などで切り替えがしやすいです📦
Vite は env を `import.meta.env` で扱います。 ([vitejs][2])

## ✅ 理由4：AIも“同じ入口”からつなげる 🤖✨

Firebase AI Logic（Webだと `firebase/ai`）も **同じ `firebaseApp` を元に初期化**します。ここを1本化しておくと、AIボタン追加が一瞬になります⚡ ([Firebase][3])

---

## 手を動かす：`firebase.ts` を作る 🛠️🔥

ここでは例として、こんな構成にします👇（名前は好みでOK！）

* `src/lib/firebase.ts`  ← Firebaseの入口（本章の主役）⭐
* `src/vite-env.d.ts`   ← envの型補完（あると超快適）✨

---

## 1) env を用意する（Vite流）🌱

## ✅ `.env.local` を作る（Gitには入れないのが定番🙈）

プロジェクト直下に `.env.local` を作って、Firebaseコンソールの「Webアプリ設定」の値を入れます✍️

```env
VITE_FIREBASE_API_KEY=xxxxxxxxxxxxxxxx
VITE_FIREBASE_AUTH_DOMAIN=xxxxxx.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=xxxxxx
VITE_FIREBASE_STORAGE_BUCKET=xxxxxx.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=1234567890
VITE_FIREBASE_APP_ID=1:1234567890:web:xxxxxxxxxxxx
```

### 🔎 ここ重要ポイント

* Vite は **`VITE_` で始まる env だけ**をブラウザ側コードに公開します（それ以外は `undefined` になります）🧠 ([vitejs][2])
* FirebaseのAPIキーは、Firebaseでは “アクセス権限そのもの” ではなく **プロジェクト識別**に使われます（本当の防御は Security Rules / App Check）🔐 ([Firebase][4])
  なので「入れちゃダメな秘密鍵」扱いではないですが、**他のGoogle Cloud API用のキー**を混ぜるのは別問題なので注意です⚠️（Firebase以外は別キー推奨） ([Firebase][4])

---

## 2) envをTypeScriptで補完する（地味に神）✨

Viteは `import.meta.env` の型定義を持っていますが、**自分で追加した `VITE_...` の補完は自前で足す**のがラクです🧠 ([vitejs][2])

`src/vite-env.d.ts` を作成：

```ts
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_FIREBASE_API_KEY: string;
  readonly VITE_FIREBASE_AUTH_DOMAIN: string;
  readonly VITE_FIREBASE_PROJECT_ID: string;
  readonly VITE_FIREBASE_STORAGE_BUCKET: string;
  readonly VITE_FIREBASE_MESSAGING_SENDER_ID: string;
  readonly VITE_FIREBASE_APP_ID: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
```

---

## 3) `src/lib/firebase.ts` を作る（本体）🔌🔥

ポイントはココ👇

* `initializeApp()` を **1回にする**
* `auth/db/storage/functions` を **ここで作って export**
* env が空なら、**早めにわかりやすく落とす**（初心者ほど大事）🧯

```ts
// src/lib/firebase.ts
import { initializeApp, getApp, getApps, type FirebaseApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";
import { getStorage } from "firebase/storage";
import { getFunctions } from "firebase/functions";

// （任意）AI Logic を後で使うならここも入口にまとめられる
// import { getAI, GoogleAIBackend } from "firebase/ai";

function mustEnv(name: keyof ImportMetaEnv): string {
  const v = import.meta.env[name];
  if (!v) {
    // ここで落とすと「設定ミス」がすぐ分かって最高🙂
    throw new Error(`Missing env: ${name}（.env.local を確認してね）`);
  }
  return v;
}

const firebaseConfig = {
  apiKey: mustEnv("VITE_FIREBASE_API_KEY"),
  authDomain: mustEnv("VITE_FIREBASE_AUTH_DOMAIN"),
  projectId: mustEnv("VITE_FIREBASE_PROJECT_ID"),
  storageBucket: mustEnv("VITE_FIREBASE_STORAGE_BUCKET"),
  messagingSenderId: mustEnv("VITE_FIREBASE_MESSAGING_SENDER_ID"),
  appId: mustEnv("VITE_FIREBASE_APP_ID"),
};

// ✅ 初期化は1回だけ（ViteのHMRでも二重初期化を避ける）
export const firebaseApp: FirebaseApp =
  getApps().length > 0 ? getApp() : initializeApp(firebaseConfig);

// ✅ 使うサービスをここで “生成して export”
export const auth = getAuth(firebaseApp);
export const db = getFirestore(firebaseApp);
export const storage = getStorage(firebaseApp);
export const functions = getFunctions(firebaseApp);

// （任意）AI Logic も“同じ入口”に乗せられる
// export const ai = getAI(firebaseApp, { backend: new GoogleAIBackend() });
```

> 「モジュール式で必要なものだけ import」するのが、Firebase公式でも推されている方向性です🌲 ([Firebase][1])

---

## 4) どこからでも使えるか確認する ✅

例えば `src/main.tsx` や任意のページで import して、起動確認します🙂

```ts
import { auth, db } from "./lib/firebase";

console.log("Firebase OK!", { auth, db });
```

---

## ミニ課題 🎯✨（10〜15分）

## 課題A：環境切り替えを体験する 🔁

* `.env.development` と `.env.production` を作ってみる
* build 時に `.env.production` が使われるのを体験する
  Vite はモードによって読み込む env ファイルが変わります🧠 ([vitejs][2])

## 課題B：`.env.example` を作る 🧾

中身はダミーでOK。チーム開発や未来の自分が助かるやつです😂✨

---

## チェック ✅（できた？）

* `firebase.ts` 以外に `initializeApp()` が存在しない ✅
* `import.meta.env.VITE_...` が `undefined` になってない ✅（なってたら env 名か prefix ミス）
* `auth/db/storage/functions` をどこからでも import できる ✅
* 「設定ミス」したら、エラーが分かりやすく出る ✅（`Missing env: ...`）

---

## つまずきポイント集 🧯😵‍💫

## 😵 `process.env` を使ってしまった

Vite は基本 `import.meta.env` です。`process.env` はそのままだと期待通り動かないことが多いです🧠 ([vitejs][2])

## 😵 env を書いたのに反映されない

env は **開発サーバ起動時に読み込まれる**ので、`.env.local` を変えたら一度 dev server を再起動すると安定です🙂（「あ、これか！」率めちゃ高い）

## 😵 APIキーが漏れるのが怖い

FirebaseのAPIキーは、Firebaseの仕組み上「それ自体でDBへ侵入できる鍵」ではなく、実データ防御は Security Rules / App Check が主役です🔐 ([Firebase][4])
ただし、**他のGoogle Cloud API用のキー**を同じように扱うのは危険なので、そこは分けるのが安全です⚠️ ([Firebase][4])

## 😵 `API_KEY_SERVICE_BLOCKED` / 403 が出た

API key restrictions（許可リスト）の設定ミスで起こることがあります。Firebase関連APIの許可リストを削りすぎるとエラーになるよ、という注意が公式にあります🧯 ([Firebase][4])

---

## Antigravity / Gemini CLI 活用（この章で効くやつ）🤖⚡

## ✅ 1発で “envの型定義” を作らせる

* やりたいこと：`.env.local` のキーから `vite-env.d.ts` を自動生成
* 効果：タイポ地獄（`VITE_FIREBASE_PROJCT_ID` とか）を即死させられる😂

## ✅ `firebase.ts` のレビュー観点をAIに出させる

* 例：

  * 「二重初期化を避けてる？」
  * 「env 未設定時に分かりやすく落ちる？」
  * 「サービスの export が増えても破綻しない？」
    みたいなチェックリストを作らせると強いです💪✨

## ✅ AI Logic を“後で足す”前提の設計にする

この章の `firebase.ts` を整えておくと、AI Logic はこの形で **入口に追加できる**イメージです👇
（`firebase/ai` を使う例が公式にあります）([Firebase][3])

---

次の章（第11章）で、この `auth` を使って「ログイン状態で画面をガードする🚧🔐」に突入できます。
ここまでできたら、もう管理画面アプリの背骨が立ってますよ〜！😆🏗️✨

[1]: https://firebase.google.com/docs/web/module-bundling "Using module bundlers with Firebase  |  Firebase for web platforms"
[2]: https://ja.vite.dev/guide/env-and-mode "環境変数とモード | Vite"
[3]: https://firebase.google.com/docs/ai-logic/get-started "Get started with the Gemini API using the Firebase AI Logic SDKs  |  Firebase AI Logic"
[4]: https://firebase.google.com/docs/projects/api-keys "Learn about using and managing API keys for Firebase  |  Firebase Documentation"
