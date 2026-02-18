# 第13章：ローカル開発：Debug Provider（ローカルでも詰まらない）🧪🧿

この章は「App Check の **強制（enforce）** をONにした途端、`localhost` 開発が止まる😇」を **スムーズに解決**する回です✨
結論：**ローカルでは Debug Provider を使う**のが公式ルートです✅ ([Firebase][1])

---

## 1) まず全体像を1枚で🧠🗺️

![Debug Provider Flow](./picture/firebase_abuse_prevention_ts_study_013_01_debug_workflow.png)

* 本番：`reCAPTCHA v3 / Enterprise` で **正規クライアント証明**🧿
* ローカル：`Debug Provider` で **例外的に通す**🧪

  * その代わり、**デバッグトークンを Firebase Console に登録（allowlist）**する🔐 ([Firebase][1])

⚠️ 超大事：`localhost` を reCAPTCHA の許可ドメインに入れて回避しようとしないでね（それやると、他人のPCの localhost からでも動かせちゃう＝危険😱） ([Firebase][1])

---

## 2) 手を動かす：ローカルで Debug Provider を有効化🧪🛠️

## 2-1. App Check 初期化コードに「ローカル時だけ」デバッグONを足す🧿

![Conditional Logic](./picture/firebase_abuse_prevention_ts_study_013_02_code_setup.png)

ポイントはこれ👇
**`initializeAppCheck()` より前に** `self.FIREBASE_APPCHECK_DEBUG_TOKEN` をセットすること！ ([Firebase][1])

例：React + Vite 想定（TypeScript）⚛️

```ts
// src/services/firebase.ts
import { initializeApp } from "firebase/app";
import { initializeAppCheck, ReCaptchaV3Provider } from "firebase/app-check";

const firebaseConfig = {
  // いつものやつ（apiKeyとか）
};

export const app = initializeApp(firebaseConfig);

// ✅ ローカル(dev)だけ Debug Provider を有効化
if (import.meta.env.DEV) {
  (self as any).FIREBASE_APPCHECK_DEBUG_TOKEN = true;
}

// ✅ App Check 初期化（本番は reCAPTCHA、ローカルは Debug Provider が使われる）
export const appCheck = initializeAppCheck(app, {
  provider: new ReCaptchaV3Provider(import.meta.env.VITE_RECAPTCHA_SITE_KEY),
  isTokenAutoRefreshEnabled: true,
});
```

> 「ローカルなのに reCAPTCHA の Provider を書いていいの？」
> → OK。デバッグモードをONにすると、ローカルでは Debug Provider 側の挙動になるのが公式の流れです。 ([Firebase][1])

---

## 2-2. ローカル起動して、ブラウザのConsoleで「デバッグトークン」を拾う👀🧪

![Token Extraction](./picture/firebase_abuse_prevention_ts_study_013_03_browser_console.png)

1. `npm run dev` で起動（例：`http://localhost:5173`）
2. Chrome/Edge で DevTools を開く（Windows：`F12` or `Ctrl + Shift + I`）🪟
3. Console にこれが出る👇
   `AppCheck debug token: "xxxx-...."`
4. その `"..."` をコピー✂️ ([Firebase][1])

---

## 2-3. Firebase Console に登録（allowlist）する🔐🧿

![Whitelisting](./picture/firebase_abuse_prevention_ts_study_013_04_console_registration.png)

Firebase Console → App Check → 対象アプリ（Web）→ メニュー → **Manage debug tokens** → さっきのトークンを登録✅ ([Firebase][1])

登録できたら、**Firebase 側がそのトークンを有効扱い**してくれます。 ([Firebase][1])

---

## 3) ここまで出来たら動作チェック🎯（Firestore/Storage/Functions/AI）

![Service Check](./picture/firebase_abuse_prevention_ts_study_013_05_verification.png)

ローカルで次を順に押してみて、全部通れば勝ちです🏆✨

* Firestore：メモ一覧を読む📄
* Storage：画像アップロード📷
* Functions：管理者Callableを叩く🧑‍💼
* AI：**「AI整形ボタン」**を押して、応答が返る🤖✨

特に AI は「直叩きAPI」が悪用されやすいので、**開発の早い段階から App Check を入れるのが強く推奨**されてます。
そして **“開発中でも” App Check 前提で進める**のが推奨、って明言されています✅ ([Firebase][2])

---

## 4) Debug Provider の“運用ルール”🔐（ミスると事故るやつ）

![Security Rules](./picture/firebase_abuse_prevention_ts_study_013_06_best_practices.png)

Debug Provider は便利だけど、**「本人確認なしで通れる鍵」**みたいなものです🔑😱
公式も「本番で使うな」「漏れたら即 revoke」と強く言ってます。 ([Firebase][1])

おすすめルール👇

* ✅ デバッグトークンは **Git に絶対入れない**（コミット禁止） ([Firebase][1])
* ✅ トークンが漏れた疑いがあったら **Console で revoke**（削除） ([Firebase][1])
* ✅ “デバッグON” のコードは **ローカル時だけ**（`import.meta.env.DEV` など） ([Firebase][1])
* ✅ チームなら **人ごと・端末ごと** にトークン発行（共有しないのが安全）🔐

---

## 5) よくある詰まりポイント集😵‍💫➡️🙂

## A. 「トークン登録したのに 401 / invalid」になる

だいたいこれ👇

* `self.FIREBASE_APPCHECK_DEBUG_TOKEN = true;` を **初期化より後**に書いてる（順番ミス） ([Firebase][1])
* 別ブラウザ / シークレットで開いた（保存場所が別なので、別トークン扱いになりがち） ([Firebase][1])
* `localhost` と `127.0.0.1` を行き来してる（別物なのでトークンが変わることがある）
* Firebase の **プロジェクト / Webアプリ** を間違えて登録してる（あるある）

## B. 「permission-denied」になる（でも App Check の問題じゃない）

これは **Security Rules** の拒否の可能性大です🛡️
App Check を通しても、Rules で止まったら普通に落ちます🙂

## C. 古い書き方でハマる

古い Web SDK だと「import 時に読む」制約があって `index.html` に書く必要がありました。
でも今どきは v9+ を使うのが前提で、そこは回避できるよ、という注意書きがあります。 ([Firebase][1])

---

## 6) もっとラクする：Antigravity / Gemini CLI で“詰まり潰し”🤖🧰

![AI Debugging](./picture/firebase_abuse_prevention_ts_study_013_07_ai_troubleshooting.png)

最近は **Firebase MCP server** があって、いろんなAIツールから Firebase を触れる/調べられる世界になってます。
しかも対応クライアントに **Antigravity** や **Gemini CLI** が明記されています✅ ([Firebase][3])

さらに **Gemini CLI 用の Firebase 拡張**を入れると、MCP server の設定も自動でやってくれて、Firebase向けのプリセットプロンプトも使えます。 ([Firebase][4])

使いどころ（この章向け）👇

* 🔎「`initializeAppCheck` が呼ばれてる場所を全部洗い出して、ローカル時だけ debug token が先にセットされてるか確認して」
* 🔎「App Check 初期化が複数回走ってない？Reactの起動経路を見て」
* 🔎「AI整形ボタンのエラーが App Check 由来か Rules 由来か、ログ/例外から切り分けて」

（ここ、AIにやらせると体感10倍ラクです😆）

---

## 7) ミニ課題🎒✨（10〜20分）

## やること

1. ローカルで Debug Provider をON
2. Console に出たデバッグトークンを allowlist 登録
3. ミニアプリでこの4つが全部通ることを確認✅

   * Firestore read/write📝
   * Storage upload📷
   * Functions callable☎️
   * AI整形🤖✨

## 追加ミッション（できたら強い💪）

* `localhost` と `127.0.0.1` で挙動が変わるのを観察して、**開発用URLを1つに固定**する🧷

---

## 8) チェック✅（この章のゴール）

* Debug Provider の流れを、口で説明できる（取得→Console登録→通る）🗣️ ([Firebase][1])
* 「`localhost` を reCAPTCHA 許可ドメインに入れる」は危険だと理解してる😱 ([Firebase][1])
* AI機能も含めて、**開発段階から App Check 前提で進める理由**が腹落ちしてる🤖🔒 ([Firebase][2])

---

次の第14章（CIでもApp Check🏗️🔒）に行くと、**「PRで動いたのに本番で死ぬ😇」**を防げるようになります。
第13章ができてると第14章はめちゃ楽ですよ〜😆✨

[1]: https://firebase.google.com/docs/app-check/web/debug-provider "Use App Check with the debug provider in web apps  |  Firebase App Check"
[2]: https://firebase.google.com/docs/ai-logic/app-check "Implement Firebase App Check to protect APIs from unauthorized clients  |  Firebase AI Logic"
[3]: https://firebase.google.com/docs/ai-assistance/mcp-server "Firebase MCP server  |  Develop with AI assistance"
[4]: https://firebase.google.com/docs/ai-assistance/gcli-extension "Firebase extension for the Gemini CLI  |  Develop with AI assistance"
