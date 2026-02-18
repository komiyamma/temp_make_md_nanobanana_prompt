# 第11章：再生攻撃（リプレイ）対策：トークン使い回しを防ぐ♻️🚫

この章はひとことで言うと、**「同じApp Checkトークンを“何回も使い回して”叩かれるのを止める」**ための章です🧿✨
特に **AI機能（＝お金が燃えやすい🔥）** や **管理者操作（＝事故ったら終わる😇）** に効きます。

---

## 0) まず「リプレイ」って何？😈📼

![Replay Attack](./picture/firebase_abuse_prevention_ts_study_011_01_replay_concept.png)

App Check を入れて **enforcement（強制）** までONにすると、雑に `curl` で叩く“未検証リクエスト”は落ちます👍
でも…もし攻撃者が何らかの方法で **「正規ユーザーのトークン（App Checkトークン）」を1回ぶん入手**できたら？

* そのトークンを **期限が切れるまで使い回して**
* 同じAPIを **連打／自動化** して
* 画像生成・要約・変換みたいな **高コストAPIを“財布攻撃”** できちゃう可能性があります💸💥

そこで出てくるのが **Replay protection（β）** です🛡️
これは **「トークンを“1回使ったら無効化（consume）”する」** 仕組みです。([Firebase][1])

---

## 1) Replay protection（β）の全体像🧠🧩

![Token Consumption](./picture/firebase_abuse_prevention_ts_study_011_02_consume_mechanism.png)

Replay protection は、やることが2つだけです👇

## A. サーバ側（Functions側）で「消費（consume）する」♻️✅

Callable Functions なら、**関数定義に `consumeAppCheckToken: true` を付ける**だけです。([Firebase][1])

* これで **検証後にトークンが消費**され、**同じトークンの再利用ができなくなる**イメージです。([Firebase][1])

## B. クライアント側（React側）で「使い捨てトークンを取る」🧾✨

Callable を呼ぶときに、`limitedUseAppCheckTokens: true` を付けます。([Firebase][1])
（カスタムバックエンドへ `fetch` する場合は `getLimitedUseToken()` を使います。([Firebase][2])）

---

## 2) 超重要な注意⚠️（この章でハマりがちなところ）

## ✅ ① これは β です🧪

公式ドキュメントでも **Replay protection (beta)** と明記されています。([Firebase][1])

## ✅ ② 「CallableのReplay protection」は Node.js のFunctions SDKだけ対応🍃

ドキュメントに **“Node.js の Cloud Functions SDK のみ対応”** とあります。([Firebase][1])
つまり、**Python（preview）や他言語のCallable** では同じやり方はできません（この章では Node/TS で固めるのが安全ルートです🚶‍♂️）。

## ✅ ③ 速度コストがある（追加の往復が増える）🐢

![Security vs Speed](./picture/firebase_abuse_prevention_ts_study_011_03_latency_tradeoff.png)

Replay protection をONにすると **App Checkバックエンドへの追加通信が発生して遅延が増える**ので、普通は **重要なエンドポイントだけ**に使います。([Firebase][1])

---

## 3) このミニアプリだと「どこに入れる？」🎯🤖

![Selecting Targets](./picture/firebase_abuse_prevention_ts_study_011_04_target_selection.png)

題材アプリ「メモ＋画像＋AI整形」だと、Replay protection はここが鉄板です👇

* **AI整形ボタン（Firebase AI Logic / Gemini呼び出し）**
  → 連打・自動化されると **コストが燃える🔥**
* **管理者専用のCallable（削除/凍結/大量処理）**
  → 事故が怖い😱

逆に、**毎回呼ばれる高頻度API** に雑に入れると、体感が遅くなってUXが死にます🪦
（“全部ONにしない”が正解です💡）

---

## 4) ハンズオン：Callable FunctionsでReplay protectionを有効化☎️🧿

ここでは **2nd gen（v2）** の書き方でいきます✍️
第10章で `enforceAppCheck: true` を入れている前提で、そこに **`consumeAppCheckToken: true` を追加**します。

## ✅ 4-1. Functions側：`consumeAppCheckToken: true` を付ける

![Server Configuration](./picture/firebase_abuse_prevention_ts_study_011_05_server_code.png)

```ts
// functions/src/index.ts
import { onCall, HttpsError } from "firebase-functions/v2/https";

export const aiFormatMemo = onCall(
  {
    enforceAppCheck: true,          // App Checkが無い/無効なら拒否 🧿
    consumeAppCheckToken: true,     // ★ 使い捨て（リプレイ防止）♻️🚫
  },
  async (request) => {
    // request.app に App Check情報（appIdなど）が入るよ 🧩
    // request.auth にはAuth情報（ログインしていれば）👤

    if (!request.auth) {
      throw new HttpsError("unauthenticated", "ログインしてね🙂");
    }

    // ここでAI整形（例：Firebase AI Logic / Gemini）を呼ぶ想定 🤖
    // ...（第12章でガッツリやる）
    return { ok: true };
  }
);
```

この `consumeAppCheckToken` が、公式で案内されている “Replay protection のスイッチ” です。([Firebase][1])

---

## ✅ 4-2. 役割（IAMロール）を付ける🔑👮

Replay protection を使うには、**トークンを検証するサービスアカウント**に
`Firebase App Check Token Verifier` ロールが必要です。([Firebase][1])

どのサービスアカウントかは構成で変わります👇（公式に分岐が書かれています）

* 1st gen のデフォルト構成 → **App Engine default service account**
* 2nd gen のデフォルト構成 → **Default compute service account** ([Firebase][1])

（Admin SDK を明示初期化していて、専用のサービスアカウントキーを使ってるなら、最初から付与済みのこともあります。([Firebase][1])）

---

## ✅ 4-3. React側：Callable呼び出しで “limited-use” を要求する⚛️🧾

![Client Request](./picture/firebase_abuse_prevention_ts_study_011_06_client_code.png)

Web（React）から呼ぶときは、`httpsCallable` のオプションに
**`{ limitedUseAppCheckTokens: true }`** を付けます。([Firebase][1])

```ts
// src/lib/functions.ts
import { getFunctions, httpsCallable } from "firebase/functions";

export async function callAiFormatMemo() {
  const fn = httpsCallable(
    getFunctions(),
    "aiFormatMemo",
    { limitedUseAppCheckTokens: true } // ★ 使い捨てトークンで呼ぶ🧿♻️
  );

  const res = await fn({ text: "こんにちは！" });
  return res.data;
}
```

これを付けないと、サーバ側で「使い捨て前提」になってるのに、クライアントが通常トークンで来て **401/Permission denied っぽい挙動**になって詰まりがちです😵‍💫
（“サーバだけON” はだいたい事故ります）

---

## 5) 仕組みを腹落ちさせる：流れを図解っぽく🧿➡️♻️➡️🚫

* 通常モード

  1. クライアント：トークンを取る
  2. サーバ：検証してOKなら処理
  3. 同じトークンでも、期限内ならまた通る可能性あり

* Replay protection モード（この章）

  1. クライアント：**limited-useトークン**を取る
  2. サーバ：検証して **consume（消費）**
  3. 同じトークンで再実行 → **“もう使ったよ”で拒否**🚫

この「サーバが consume する」がポイントです。([Firebase][1])

---

## 6) “AI機能”と絡めた現実の防御線🤖🛡️

![Complete Defense](./picture/firebase_abuse_prevention_ts_study_011_07_full_defense.png)

Replay protection は強いけど、万能ではないです🙂
**「同じトークンの使い回し」を止める**だけなので、

* 攻撃者が毎回あらたにトークンを取って
* 何回も正規っぽく叩く

みたいなケースは別対策も必要です🧯

Firebase公式ブログのAIエンドポイント例でも、Replay protection（consume）に加えて
**認証（Auth）**や **レート制限**も一緒にやっています。([The Firebase Blog][3])

> つまり結論：
> **Replay protection + Auth + レート制限（/クォータ）** が “お財布防衛ライン” です💸🛡️

---

## 7) Antigravity / Gemini CLI で爆速チェックするアイデア🚀🤖🔎

ここ、AIと相性めちゃ良いです👇

* **Gemini CLI** にリポジトリを見せて

  * `httpsCallable(` を全部探させる
  * 「どの呼び出しだけ `limitedUseAppCheckTokens: true` にするべき？」を分類させる🎯
* **Antigravity のエージェント**に

  * “管理者操作・AI操作・課金が絡む操作” を洗い出し
  * 「Replay protection 対象リスト」を作らせる🧾✨
* さらに「ONにしたら遅くなる箇所」も候補に出させて、UX事故を予防🙂⚖️

（AIにやらせるのは “洗い出し・提案・差分作成” まで。最終判断は人間が握るのが安全です👍）

---

## 8) ミニ課題📝🔥

1. あなたのミニアプリで **「絶対に使い回しされたくないCallable」** を2つ選ぶ🎯

   * 例：AI整形、管理者削除、課金に近い操作…など
2. その2つだけに `consumeAppCheckToken: true` を付ける♻️
3. React側もその2つだけ `limitedUseAppCheckTokens: true` にする⚛️

---

## 9) チェック✅（ここまでできたら勝ち！🏁）

* `consumeAppCheckToken: true` を **重要なCallableだけ**に入れた♻️🚫 ([Firebase][1])
* React側で、そのCallableだけ `limitedUseAppCheckTokens: true` を付けた⚛️🧾 ([Firebase][1])
* IAMの `Firebase App Check Token Verifier` ロールの話を理解した🔑👮 ([Firebase][1])
* 「全部ONにしない（遅延が増える）」が説明できる🐢⚖️ ([Firebase][1])
* 「Replayだけじゃ財布攻撃は止まらない→Auth/レート制限も必要」が言える💸🧯 ([The Firebase Blog][3])

---

次の第12章（AIを守る）では、この章で作った **“AI整形Callable”** を本当にAI接続して、
**App Check + （必要なら）ユーザー単位の回数制御**までセットで「破産しないAI」に仕上げます🤖💸🛡️

[1]: https://firebase.google.com/docs/app-check/cloud-functions "Enable App Check enforcement for Cloud Functions  |  Firebase App Check"
[2]: https://firebase.google.com/docs/app-check/web/custom-resource "Protect custom backend resources with App Check in web apps  |  Firebase App Check"
[3]: https://firebase.blog/posts/2025/11/securing-ai-endpoints-from-abuse/ "Securing a retail AI endpoint from abuse for virtual try on"
