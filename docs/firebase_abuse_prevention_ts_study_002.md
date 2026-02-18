# 第02章：App Checkの仕組み（トークン・TTL・段階導入）⌛🧠

## この章でできるようになること🎯

* App Check が **何を証明して、何を証明しないか** が言える🙂
* App Check トークンの **流れ（どこで生まれて、どこに付いていくか）** が図で説明できる🗺️
* **TTL（有効期限）** の意味と、短く/長くしたときのトレードオフがわかる⚖️
* **段階導入**（まず見守る→あとで強制）が“怖くない手順”として整理できる👀🎛️

---

## 読む📖（仕組みを「1枚」で理解する🧩）

## 1) App Check は何をしてる？（3ステップだけ）🧿

App Check はざっくり **この3手** です👇 ([Firebase][2])

1. ✅ アプリが「私は正規のアプリだよ」を証明（証明プロバイダで判定）
2. ✅ Firebase がそれを信じて **App Check トークン（JWT）** を発行
3. ✅ 以後、アプリの通信にそのトークンが付いていき、**正規アプリ以外を弾ける**

イメージ図（超ざっくり）👇

* ブラウザ（React）

  * ↓（証明プロバイダで判定）
* App Check

  * ↓（トークン発行）
* Firebase各サービス（Firestore/Storage/Functions/AI…）

  * ↑（リクエストにトークンが乗る）

---

## 2) 「トークン」って結局なに？🪪

**App Check トークン**は「このリクエストは、登録済みの正規アプリから来たっぽいよ」という“入場スタンプ”です🧿
Firebase SDK 経由で通信している分は、基本的に **裏で勝手に付けてくれる**感じになります（※強制のON/OFFは別の話）([Firebase][1])

⚠️ここ大事：

* App Check は **“誰が何をできるか”を決めるものじゃない**（それは Auth / Rules の仕事）
* App Check は **“正規アプリかどうか”のレイヤー**

---

## 3) トークンはどこに付くの？（Firebase内 / 自前バックエンド）📦

### ✅ Firebaseのサービスに行く通信

Firebase SDK がやってくれる（Firestore / Storage / Functions / など）🧠

### ✅ 自前バックエンドに行く通信（自作APIとか）

この場合は **自分でヘッダーに乗せる**のが王道です📮
トークンは URL（クエリパラメータ等）に入れないのが推奨です（漏れやすいので😱）([Firebase][3])

---

## 4) TTL（有効期限）ってなに？⌛

App Check トークンには **有効期限（TTL）** があって、設定で変えられます🎛️
WebのreCAPTCHA系だと、

* 設定できる範囲：**30分〜7日**
* デフォルト：**1日（多くのアプリに妥当）**
* だいたい **TTLの半分くらい経つとリフレッシュ**される
* ただしWebは **自動リフレッシュがデフォルトOFF** なので、明示ONが推奨 ([Firebase][1])

### TTLを短くすると…🔒（強いけど重い）

* ✅ 盗まれても使える時間が短い（安全）
* ❌ 再証明が増えて遅延・回数・コストが増えやすい ([Firebase][1])

### TTLを長くすると…🚀（軽いけどリスク増）

* ✅ 再証明が減って軽い
* ❌ もし漏れたら“使える時間”が長い ([Firebase][1])

---

## 5) 「段階導入」が超重要（いきなり強制しない）👀➡️🔒

導入の流れはこれが鉄板です👇

1. クライアントに App Check を入れる
2. まずは **メトリクス監視（見守り）**
3. 問題ないのを確認してから **強制（enforcement）** をON

ポイント：クライアントはトークンを送り始めても、**強制をONにするまでは必須扱いにならない** ので、まず安全に観測できます👀 ([Firebase][1])

---

## 6) ちょい先取り：Limited-use token（リプレイ耐性）♻️🚫

「トークンを盗まれて使い回される（リプレイ）」が怖いケースでは、**使い捨て寄りのトークン**もあります🧨

* **limited-use token** は **TTL 5分固定（変更不可）**
* その代わり **毎回取りに行くので遅くなる**（追加の往復が増える）
* Firebase AI Logic でも、状況によって **limited-use tokens を使う**選択があり、段階的に切り替えるアイデアとして Remote Config が挙げられています ([Firebase][4])

※ここは後半章（リプレイ対策/AI保護）で本格的に触れるけど、**“存在だけ”今知っておく**と設計がラクです🙂

---

## 手を動かす🛠️（この章は「観測」と「方針決め」が主役✨）

## 実験1：TTL方針メモを作る✍️（1枚でOK）

下のテンプレをメモアプリに貼って埋めてください📝✨
（まだ実装してなくてもOK！）

* 守りたいもの：

  * Firestore：＿＿＿（例：メモ一覧/検索）
  * Storage：＿＿＿（例：画像アップロード）
  * Functions：＿＿＿（例：管理者処理）
  * AI：＿＿＿（例：整形ボタン）
* 予想アクセス頻度：

  * 低/中/高（どれ？）
* まずのTTL案：

  * いったん **デフォルト（1日）** でスタート or もっと短く？
* “短くしたい理由” or “長くしたい理由”：

  * 例：AIはコストが怖い→短め寄りにしたい、など🤖💸

> TTLのデフォルト1日は「多くのアプリに妥当」と明記されています。([Firebase][1])

---

## 実験2：トークンの残り寿命を“見える化”する👀⌛

App Check が入ったあと（第5章で初期化したあと）に、これを走らせると理解が一気に進みます🔥
「JWTのexpを読むだけ」の安全な観測です（※本番でトークンをログに出すのは避けてね😇）

```ts
// appCheckInspector.ts
// App Check tokenの「残り時間」を表示する観測用ユーティリティ🧿⌛
// ※デバッグ用途。トークン本文をログに出しっぱなしにしないこと！

import { getAppCheck, getToken } from "firebase/app-check";
import type { FirebaseApp } from "firebase/app";

function base64UrlDecode(input: string): string {
  const pad = "=".repeat((4 - (input.length % 4)) % 4);
  const b64 = (input + pad).replace(/-/g, "+").replace(/_/g, "/");
  return decodeURIComponent(
    Array.prototype.map
      .call(atob(b64), (c: string) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
      .join("")
  );
}

export async function logAppCheckTtl(app: FirebaseApp) {
  const appCheck = getAppCheck(app);

  // forceRefresh=false: まずはキャッシュ優先で観測（基本はこれ）🧠
  const res = await getToken(appCheck, /* forceRefresh= */ false);

  const token = res.token;
  const [, payload] = token.split(".");
  const json = JSON.parse(base64UrlDecode(payload));

  const nowSec = Math.floor(Date.now() / 1000);
  const expSec = Number(json.exp);
  const remainSec = expSec - nowSec;

  console.log("🧿 App Check token exp:", new Date(expSec * 1000).toLocaleString());
  console.log("⌛ remain:", Math.max(0, remainSec), "sec");
}
```

`getToken(appCheck, false)` の形で取れる例は、公式のカスタムバックエンド連携ページにも載っています。([Firebase][3])

---

## 実験3：自前APIに付ける“ヘッダー名”だけ先に固定する📮

自前バックエンドに送るときはヘッダーに👇

* `X-Firebase-AppCheck: <token>`

URLに入れない（漏れやすい）という注意も公式にあります。([Firebase][3])

---

## ミニ課題🧩（1分でOK🙂）

**「トークンが漏れたら何が起きる？」を一言で** 書いてください✍️

例：

* 「AI整形を勝手に叩かれてコストが溶ける」🤖💸
* 「画像アップロード連打でストレージと転送料が燃える」📷🔥
* 「管理者Callableを狙われる」🧑‍💼💥

そして次に、**漏れた場合に“効く要素”**を丸で囲む⭕

* TTL（短いほど被害時間が短い）([Firebase][1])
* 強制ON（未検証を拒否）([Firebase][1])
* limited-use token（リプレイ耐性）([Firebase][4])

---

## チェック✅（言えたら勝ち🎉）

* [ ] App Check の流れを **3ステップ**で説明できる ([Firebase][2])
* [ ] TTLを短くすると **安全↑ / 性能↓ / コスト影響** があると言える ([Firebase][1])
* [ ] Webは自動更新がデフォルトOFFなので、ONにする必要があると言える ([Firebase][1])
* [ ] いきなり強制せず、まず **監視→段階的に強制** の順が自然と言える ([Firebase][1])

---

## つまずきポイント集（先に踏んでおく😆）🧯

* 😵 **自動更新をONにしてなくてトークン期限切れ** → なんか通信が不安定に…
  → Webは明示ONが推奨です ([Firebase][1])
* 😱 **debug token をうっかり公開**
  → debug token は超強いので、漏れたらコンソールで即 revoke（取り消し）推奨 ([Firebase][5])
* 🙃 **いきなり強制ONしてユーザーが死ぬ**
  → まず観測してから強制が安全 ([Firebase][1])

---

## AI活用🚀🤖（Antigravity / Gemini CLI で“設計の迷い”を潰す）

ここ、AIがめちゃ役立ちます🔥

* Antigravity は “エージェントにタスクを渡して計画→実装→調査”みたいな流れが意識されてます ([Google Codelabs][6])
* Gemini CLI はターミナル統合のAIエージェントとして紹介され、OSSとしても公開されています ([Google Cloud][7])

## 使い方（プロンプト例）💬

* 「このアプリ（メモ＋画像＋AI整形）だと TTL は1日でOK？30分に寄せるべき？理由も」
* 「強制ONの順番（Firestore→Storage→AI→Functions）って妥当？監視ポイントもセットで」
* 「App Checkを初期化する場所がFirebaseアクセスより前になってるか、リポジトリを見て指摘して」🔎

---

次は **第3章（reCAPTCHA v3：スコアとしきい値）** に行くと、
「じゃあ“正規っぽさ”をどう判定してるの？」がつながって超気持ちいいです🤖📊🔥

[1]: https://firebase.google.com/docs/app-check/web/recaptcha-provider "Get started using App Check with reCAPTCHA v3 in web apps  |  Firebase App Check"
[2]: https://firebase.google.com/docs/app-check "Firebase App Check"
[3]: https://firebase.google.com/docs/app-check/web/custom-resource?utm_source=chatgpt.com "Protect custom backend resources with App Check in web apps"
[4]: https://firebase.google.com/docs/ai-logic/app-check "Implement Firebase App Check to protect APIs from unauthorized clients  |  Firebase AI Logic"
[5]: https://firebase.google.com/docs/app-check/web/debug-provider "Use App Check with the debug provider in web apps  |  Firebase App Check"
[6]: https://codelabs.developers.google.com/getting-started-google-antigravity "Getting Started with Google Antigravity  |  Google Codelabs"
[7]: https://cloud.google.com/blog/ja/topics/developers-practitioners/introducing-gemini-cli "Gemini CLI : オープンソース AI エージェント | Google Cloud 公式ブログ"
