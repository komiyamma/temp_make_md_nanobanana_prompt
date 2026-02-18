# 第05章：ReactにApp Checkを入れる（v3版）⚛️🧿

この章は「**React アプリが App Check トークンを付けて Firebase にアクセスできる状態**」を作ります😊
ここができると、次の章以降で **Firestore / Storage / Functions / Firebase AI Logic** を“段階的に守る”準備が整います🛡️✨

---

## この章でできるようになること 🎯

* React アプリ起動時に **App Check を初期化**できる🧿
* トークンが **自動更新**されるようにできる♻️（これ重要！）([Firebase][1])
* Firebase Console の **App Check メトリクス**で「Verified が増えてる」ことを確認できる👀📈([Firebase][2])

---

## ざっくり図解っぽく 🧠🖼️

![App Check Pass](./picture/firebase_abuse_prevention_ts_study_005_01_concept.png)

App Check は「アプリが正規っぽいか」を証明する **通行証** です🎫

* ✅ 正規アプリ（React + App Check） → 通行証つきで Firebase にアクセス
* ❌ 不正スクリプト / API キー盗用 → 通行証なし（または偽造）で弾けるようになる

ポイント：**Rules の代わりじゃない**です🙅‍♂️
Rules は「誰が何できるか」、App Check は「正規アプリ経由か」を見るイメージ👍

---

## まずは準備チェック ✅🧩

ここまでの章でやってる想定だけど、最低限これが揃ってればOKです👌

* Firebase Console で対象の **Web アプリ**が登録済み
* App Check で **reCAPTCHA v3** を選んで、**site key** と **secret key** を用意済み（secret は Console に登録）([Firebase][1])

⚠️ ローカル開発で `localhost` を reCAPTCHA の許可ドメインに入れたくなるけど、**Web は Debug Provider を使うのが公式の筋**です（この教材だと第13章でやるやつ）🧪🧿([Firebase][3])

---

## 手を動かす その1 依存関係を入れる 📦🖱️

![Setup Dependencies](./picture/firebase_abuse_prevention_ts_study_005_02_setup.png)

React + Vite だとして（今いちばん自然な構成）、プロジェクト内で：

```bat
npm i firebase
```

（Node は LTS を使うのが安心です。たとえば v24 系が LTS として継続アップデートされています）([Node.js][4])

---

## 手を動かす その2 環境変数に site key を置く 🔑✨

Vite なら `.env.local` を作って：

```env
VITE_RECAPTCHA_SITE_KEY=あなたの_site_key
```

site key は公開されても致命傷ではないけど、**コードに直書きより管理しやすい**のでここに置くのがラクです🙂

---

## 手を動かす その3 Firebase 初期化を 1か所に集約する 📦🧠

![Centralized Initialization](./picture/firebase_abuse_prevention_ts_study_005_03_structure.png)

React で App Check を踏むときの事故で多いのがこれ👇

* `useEffect` に書いて **二重初期化**（React StrictMode や HMR のせい）😇
* Firestore/Storage を先に触ってしまって **App Check の初期化が間に合わない**💥([Firebase][1])
* `isTokenAutoRefreshEnabled` を入れ忘れて、気づいたらトークン期限切れ🍂([Firebase][1])

なので、この教材では **「firebase.ts 1枚に全部寄せる」**作戦でいきます👍

## `src/lib/firebase.ts` を作る ✍️

```ts
// src/lib/firebase.ts
import { getApp, getApps, initializeApp } from "firebase/app";
import {
  initializeAppCheck,
  ReCaptchaV3Provider,
  getToken,
  type AppCheck,
} from "firebase/app-check";

// ✅ ここはあなたの Firebase プロジェクトの設定（Console からコピペ）
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY as string,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN as string,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID as string,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET as string,
  appId: import.meta.env.VITE_FIREBASE_APP_ID as string,
};

// ✅ React + HMR 対策：Firebase App を多重生成しない
export const app = getApps().length ? getApp() : initializeApp(firebaseConfig);

// ✅ App Check は “1アプリにつき1回だけ” 初期化できるので、HMR 対策も入れる
const APP_CHECK_KEY = "__appCheckInstance__";

export const appCheck: AppCheck =
  (globalThis as any)[APP_CHECK_KEY] ??
  (() => {
    const siteKey = import.meta.env.VITE_RECAPTCHA_SITE_KEY as string;

    const instance = initializeAppCheck(app, {
      provider: new ReCaptchaV3Provider(siteKey),
      // ✅ Web は自動更新が「明示的に ON 推奨」
      isTokenAutoRefreshEnabled: true,
    });

    (globalThis as any)[APP_CHECK_KEY] = instance;
    return instance;
  })();

// 🧪 動作確認用（本番ではログを減らすのがおすすめ）
export async function debugLogAppCheckToken() {
  // getToken で “いまのトークン取れる？” を確認できる
  const { token } = await getToken(appCheck);
  console.log("App Check token (head):", token.slice(0, 20) + "...");
}
```

**大事ポイント**✅

* `initializeAppCheck()` は **1つの Firebase App につき1回**だけです（だから HMR 対策が効きます）([Firebase][5])
* `ReCaptchaV3Provider` は **ブラウザ向け**です（Node 環境では動きません）([Firebase][5])
* そして何より、**Firestore/Storage を触る前に App Check を初期化**が基本です([Firebase][1])

---

## 手を動かす その4 React 側で “最初に” 読み込ませる 🚀⚛️

![Startup Sequence](./picture/firebase_abuse_prevention_ts_study_005_04_init_flow.png)

`src/main.tsx`（または `src/main.jsx`）のかなり上のほうで import します👇

```ts
// src/main.tsx
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

// ✅ ここで firebase.ts を読み込ませる（= App Check が先に初期化される）
import { debugLogAppCheckToken } from "./lib/firebase";

debugLogAppCheckToken().catch(console.error);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

これで「アプリ起動 → App Check 初期化 → トークン取得」までの流れができます🧿✨

---

## 動作確認 👀✅

## 1) ブラウザコンソールを見る 🔎

* `App Check token (head): xxxx...` が出れば第一関門突破🎉
  （出ないなら、site key / ドメイン / ブロッカー系を疑う）

## 2) Firebase Console の App Check メトリクスを見る 📈

![Metrics Overview](./picture/firebase_abuse_prevention_ts_study_005_05_metrics.png)

App Check SDK を入れたら、**強制を ON にする前に**メトリクスで様子見するのが公式の流れです👀([Firebase][2])

メトリクスにはだいたいこんな分類が出ます👇

* Verified（通ってる）✅
* Outdated client（古いクライアント）🕰️
* Unknown origin（怪しい直叩き）👿
* Invalid（偽トークン等）🚫([Firebase][2])

---

## よくある詰まりポイント集 😵‍💫🧯

![Troubleshooting](./picture/firebase_abuse_prevention_ts_study_005_06_pitfalls.png)

## 1) `initializeAppCheck` を2回呼んで落ちる

* 原因：React StrictMode / HMR / 複数箇所 import
* 対策：この章の `globalThis` ガード方式でOK
  （App Check は 1回だけ、が仕様）([Firebase][5])

## 2) Firestore などを先に触ってる

* 原因：`firebase.ts` を分散してしまった
* 対策：**App Check を先に初期化**が基本です([Firebase][1])

## 3) トークンの自動更新を入れ忘れた

* Web の reCAPTCHA v3 は **自動更新を明示 ON** が推奨です([Firebase][1])
* トークンには TTL があり、デフォルトは **1日**で、半分経つと更新が走ります🕒([Firebase][1])

## 4) ローカルで reCAPTCHA ドメイン設定に悩む

* 公式は「`localhost` を reCAPTCHA の許可ドメインに入れるより **Debug Provider を使う**」の流れです🧪🧿([Firebase][3])

---

## AI 機能と App Check を最初から結びつける 🤖🧿💸

![Protecting AI](./picture/firebase_abuse_prevention_ts_study_005_07_ai_shield.png)

この教材の題材は「メモ＋画像＋AI整形」なので、AI が特に狙われやすいです（= お金が燃えやすい🔥）

## Firebase AI Logic 側の現実ポイント 💰

* Firebase AI Logic は「プロジェクト全体の制限」だけでなく、**“per user” 的に扱える quota 設計**も案内されています
* しかもデフォルトが **100 RPM/ユーザー**と高めなので、実運用では下げるのが推奨です🎛️([Firebase][6])

App Check と合わせるとこうなります👇

* **App Check**：正規アプリ以外を入れない🧿
* **Rate limit**：正規ユーザーでも連打で破産しない💸🚫([Firebase][6])

さらに、App Check は **Firebase AI Logic も“強制対象”に含まれる**ので、段階導入ができます🛡️([Firebase][7])

---

## Antigravity と Gemini CLI を使って実装を爆速チェック 🚀🤖

「初学者あるあるのミス（初期化順、重複、漏れ）」は AI がめっちゃ得意です🔎✨

しかも最近は Firebase 側が **MCP サーバー**を用意していて、**Antigravity / Gemini CLI / Firebase Studio** などから Firebase を“道具として”触れる流れが公式で整ってます🧰([Firebase][8])
Gemini CLI には **Firebase 公式拡張**もあります🧩([Firebase][9])

## 使わせ方の例 📝（プロンプト案）

* 「React + Vite の構成で、App Check 初期化が複数回起きないかレビューして」👀
* 「Firestore/Storage/AI Logic を触ってる箇所を列挙して、App Check 初期化より後になってないか確認して」✅
* 「App Check が動かない時の原因候補（site key / ドメイン / ブロッカー）を優先度つきで出して」🧯

---

## ミニ課題 🧩✨

**課題：初期化を“1か所”に固定して、動作確認できる状態にする！**

1. `src/lib/firebase.ts` に App Check 初期化をまとめる📦
2. `main.tsx` で最初に import する🚀
3. Console にトークンっぽいログが出ることを確認する🔎
4. Firebase Console の App Check メトリクスで **Verified が出る**のを確認する👀📈([Firebase][2])

---

## チェック ✅🧾

* [ ] `initializeAppCheck` が 1回だけ呼ばれてる（HMR でも落ちない）([Firebase][5])
* [ ] `isTokenAutoRefreshEnabled: true` を入れた([Firebase][1])
* [ ] App Check 初期化が “Firestore/Storage/AI” より先になってる([Firebase][1])
* [ ] メトリクスで Verified が確認できた([Firebase][2])

---

## 次章への伏線 🔁🏢

reCAPTCHA v3 はまず入り口として最高なんだけど、公式ドキュメントでも **新規は Enterprise 推奨**の文脈が強いです📌([Firebase][1])
Enterprise は **TTL が短め（デフォルト 1時間）**で、運用寄りのコントロールがしやすい方向です⏱️

次の第6章では、今日作った実装を “差し替え可能” にして、Enterprise へスムーズ移行できる設計にしていきます🔥

[1]: https://firebase.google.com/docs/app-check/web/recaptcha-provider "Get started using App Check with reCAPTCHA v3 in web apps  |  Firebase App Check"
[2]: https://firebase.google.com/docs/app-check/monitor-metrics "Monitor App Check request metrics  |  Firebase App Check"
[3]: https://firebase.google.com/docs/app-check/web/debug-provider "Use App Check with the debug provider in web apps  |  Firebase App Check"
[4]: https://nodejs.org/en/blog/release/v24.13.1?utm_source=chatgpt.com "Node.js 24.13.1 (LTS)"
[5]: https://firebase.google.com/docs/reference/js/app-check "app-check package  |  Firebase JavaScript API reference"
[6]: https://firebase.google.com/docs/ai-logic/quotas "Rate limits and quotas  |  Firebase AI Logic"
[7]: https://firebase.google.com/docs/app-check/enable-enforcement "Enable App Check enforcement  |  Firebase App Check"
[8]: https://firebase.google.com/docs/ai-assistance/mcp-server?utm_source=chatgpt.com "Firebase MCP server | Develop with AI assistance - Google"
[9]: https://firebase.google.com/docs/ai-assistance/gcli-extension?utm_source=chatgpt.com "Firebase extension for the Gemini CLI"
