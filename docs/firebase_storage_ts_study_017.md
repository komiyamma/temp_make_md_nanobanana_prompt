### 第17章：App Check（“正規アプリ”以外を通しにくくする）🧿🛡️

この章は「画像アップロード（Cloud Storage）を、野良スクリプトやコピーアプリから叩かれにくくする」回です📷💥
**App Check** は、リクエストに“正規アプリっぽい証明（トークン）”を付けて、Firebase側でチェックできる仕組みです✨
ただし万能バリアではなく、**Auth と Storage Rules の代わりにはならない**（併用が前提）という立ち位置です🧠([Firebase][1])

---

## 1) まず腹落ち：App Check で何が変わるの？🤔

### App Check なしだと…😇

* Webアプリの設定情報（firebaseConfig）は基本的に見えてしまうので、悪意ある人が **“それっぽいクライアント”** を作れてしまう😈
* Storage Rules が強ければ守れるけど、それでも **大量アクセス・不正利用の圧** は来る可能性がある💣

### App Check を入れると…🧿

* アプリが毎回のアクセスに **App Check トークン** を付けるようになる
* さらに「強制（Enforce）」をONにすると、**トークンが正しくないリクエストを拒否**できる🚫([Firebase][2])

---

## 2) 今日のゴール🎯✨

* ✅ Web（React）で App Check を初期化して、Storage の通信にトークンが乗るようにする
* ✅ ローカル開発は **debug token** で安全に回す
* ✅ 監視（メトリクス）→ 強制（Enforce）の順で “事故らず” 移行する📈🔥([Firebase][3])

---

## 3) 手順（コンソール → コード → ローカル → 監視 → 強制）🛠️🚀

### Step A：プロバイダはどれにする？（迷ったら Enterprise 推し）🧩

Web の App Check は、主に **reCAPTCHA Enterprise** を使う流れが強いです（スコア型でユーザーに見えない）🕵️‍♂️✨([Firebase][3])

* ✅ **reCAPTCHA Enterprise**：基本おすすめ（不可視・スコア型）([Firebase][3])
* ✅ **reCAPTCHA v3**：従来の選択肢（プロジェクト事情で使うことも）

> Enterprise は「スコアしきい値」や「トークンTTL（30分〜7日）」も調整できます⚙️
> ただししきい値を上げると正規ユーザーも落ちる可能性があるので、**いきなり強制しない**のがコツです🧯([Firebase][3])

---

### Step B：Firebase コンソール側で登録する🧾

1. Firebase コンソール → **App Check** に行く
2. Webアプリを **App Check に登録**（reCAPTCHA Enterprise の site key を入力）([Firebase][3])
3. （任意）TTL やリスクしきい値（スライダー）をデフォルトのままにしてまず開始でOK👌([Firebase][3])

---

### Step C：クライアント（React/TS）に App Check を組み込む💻✨

2026-02 時点の Node は **v24 が Active LTS** として案内されています（新しめでOK）🧠([Node.js][4])
Firebase JS SDK は npm / GitHub の最新を入れればOK（例：firebase@12.9.0 が “Latest” として出ています）📦([GitHub][5])

#### 1) インストール

```bash
npm i firebase@latest
```

#### 2) `firebase.ts`（最小セット）

* **ポイント：App Check 初期化は「Firebaseサービスを触る前」に置く**✨([Firebase][3])
* Enterprise を使う例です（迷ったらこれでOK）👍

```ts
// src/lib/firebase.ts
import { initializeApp } from "firebase/app";
import {
  initializeAppCheck,
  ReCaptchaEnterpriseProvider,
} from "firebase/app-check";
import { getStorage } from "firebase/storage";

// いつもの firebaseConfig
const firebaseConfig = {
  // apiKey, authDomain, projectId, storageBucket, ...
};

export const app = initializeApp(firebaseConfig);

/**
 * ✅ ローカル開発は debug provider を使う
 * - self.FIREBASE_APPCHECK_DEBUG_TOKEN を true にすると
 *   DevToolsに debug token が出る → Consoleで safelist する流れ
 */
if (import.meta.env.DEV) {
  (self as any).FIREBASE_APPCHECK_DEBUG_TOKEN = true; // initializeAppCheckより前！
}

export const appCheck = initializeAppCheck(app, {
  provider: new ReCaptchaEnterpriseProvider(
    import.meta.env.VITE_RECAPTCHA_ENTERPRISE_SITE_KEY
  ),
  isTokenAutoRefreshEnabled: true,
});

export const storage = getStorage(app);
```

> `isTokenAutoRefreshEnabled` はデフォルトで自動更新されないので、`true` にするのが安心です🔁([Firebase][3])

---

### Step D：ローカル開発（localhost）は debug token でやる🧪🔐

ここが超重要ポイントです⚠️
**“localhost で動かすために、reCAPTCHA の許可ドメインに localhost を足す”のはダメ**です（誰でもローカルで回せてしまう）🚫([Firebase][6])

手順はこう👇([Firebase][6])

1. `self.FIREBASE_APPCHECK_DEBUG_TOKEN = true;` を **初期化より前**に置く
2. `localhost` でアプリを開く → DevTools の Console に **AppCheck debug token** が出る
3. Firebase コンソール（App Check）→ **Manage debug tokens** で、そのトークンを登録（safelist）
4. 以後、そのブラウザ/マシンでは debug token が使われる🎮

> debug token は「強力な通行証」なので、**公開リポジトリに絶対入れない**でね🧨（漏れたら revoke！）([Firebase][6])

---

### Step E：まずは“監視”してから、強制（Enforce）へ📈➡️🚨

アプリをデプロイすると、**クライアントはトークンを送るようになる**けど、Firebase側は **まだ必須にはしない**状態です🫶
この段階で **メトリクスを見て安全確認**します👀([Firebase][3])

* App Check メトリクスで、Cloud Storage の **受理/拒否**の雰囲気を確認する([Firebase][3])
* ここで拒否が多いなら「古いクライアント」「設定ミス」「debug token 未登録」などが濃厚🕵️‍♂️

#### Enforce をONにする🔥

App Check → Cloud Storage のメトリクスを開いて **Enforce** を押すだけです✅
反映は最大15分くらいかかることがあります⏳([Firebase][2])

---

## 4) “動いた？”確認ポイント✅🔍

* ✅ ローカル（localhost）でアップロードできる

  * できない場合：debug token が safelist されてない可能性大
* ✅ 本番URLでアップロードできる

  * できない場合：site key のドメイン設定やキー取り違えが多い
* ✅ Enforce 後に「知らんクライアント」からのアクセスは弾かれる

  * これが本来の狙い🎯([Firebase][2])

---

## 5) よくある詰まりポイント集🧯😵‍💫

* **App Check 初期化が遅い**：Storage を触った後に `initializeAppCheck()` してる → トークンが乗らない
* **debug token が未登録**：ローカルで token が出たのに safelist してない
* **localhost を許可ドメインに入れたくなる病**：それはダメ！🚫（debug token でやる）([Firebase][6])
* **Enforce を急にON**：既存ユーザー（古い版）が落ちる → まずメトリクス確認から📈([Firebase][3])
* **しきい値を上げすぎ**：正規ユーザーまで落ちる → いったんデフォルト運用がおすすめ🎛️([Firebase][3])

---

## 6) AIで爆速にする（Antigravity / Gemini CLI / Console AI）🤖⚡

ここ、めちゃ効きます🔥

### Gemini CLI（Firebase拡張）で“設定〜調査”を短距離化🏃‍♂️💨

Firebase は Gemini CLI 連携（Firebase extension）があって、**Firebase MCP server を自動セットアップ**して Firebase向けのツールやプロンプトが増えます🧰([Firebase][7])
インストール例も公式に載ってます🧩([Firebase][7])

* 使い方イメージ（お願い例）💬

  * 「App Check を Cloud Storage に入れたけど、Enforce 後に 403 が出る。原因切り分け手順をチェックリスト化して」
  * 「debug token の safelist 手順を、コンソールのどこを押すかまで箇条書きにして」
  * 「今の `firebase.ts` の初期化順序、危ないところある？」

### Firebase Studio で“再現性”を固める🧪📦

Firebase Studio はブラウザ上の開発環境で、Nix で環境を揃えたり、Firebase エミュレータも含めて統合的に扱えます🧰✨([Firebase][8])
「手元PCの差で詰まる」を減らすのに便利です🙂([Firebase][8])

---

## 7) ミニ課題🎯📝

1. localhost で debug token を出して、Firebase コンソールで safelist できた？🧿
2. 本番URLで動かして、App Check メトリクスが増えてるのを見た？📈
3. Cloud Storage の Enforce をONにする前に、影響範囲（旧バージョン利用者がいるか）をメモした？🧾([Firebase][3])

---

## 8) チェック✅（この章の合格ライン）

* ✅ 「App Check は Auth/Rules の代わりじゃなく、乱用対策の追加レイヤー」って説明できる🧠([Firebase][1])
* ✅ localhost は debug token で回せる（そして `localhost` を許可ドメインに入れない）🚫([Firebase][6])
* ✅ “監視してから Enforce” の順で移行できる📈➡️🚨([Firebase][3])

---

次は第18章（エミュレーター＆切り替え）で「本番を汚さず安全に壊して学ぶ🧪💥」に行くと、App Check も Rules も一気に理解が固まります💪😆

[1]: https://firebase.google.com/docs/app-check "Firebase App Check"
[2]: https://firebase.google.com/docs/app-check/enable-enforcement "Enable App Check enforcement  |  Firebase App Check"
[3]: https://firebase.google.com/docs/app-check/web/recaptcha-enterprise-provider "Get started using App Check with reCAPTCHA Enterprise in web apps  |  Firebase App Check"
[4]: https://nodejs.org/en/about/previous-releases "Node.js — Node.js Releases"
[5]: https://github.com/firebase/firebase-js-sdk/releases "Releases · firebase/firebase-js-sdk · GitHub"
[6]: https://firebase.google.com/docs/app-check/web/debug-provider "Use App Check with the debug provider in web apps  |  Firebase App Check"
[7]: https://firebase.google.com/docs/ai-assistance/gcli-extension "Firebase extension for the Gemini CLI  |  Develop with AI assistance"
[8]: https://firebase.google.com/docs/studio "Firebase Studio"
