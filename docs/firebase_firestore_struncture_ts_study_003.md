# 第3章：ID設計（自動ID vs 意味のあるID）🆔

この章は「**ドキュメントIDをどう決めるか**」を、事故りにくい判断軸で身につける回です😊✨
FirestoreのIDは“検索”じゃなくて“参照”を強くする道具…ここがポイントです🔗

---

## まず超重要：IDは“検索キー”じゃないよ🔎🙅‍♂️

![ID as Reference vs Search Key](./picture/firebase_firestore_struncture_ts_study_003_01_id_search_vs_ref.png)

Firestoreで「このデータ欲しい！」ってなる場面は大きく2種類👇

* **(A) 参照で1件ピンポイント**：`doc(db, "posts", postId)` みたいに **IDで直に取りに行く** 💨
* **(B) 条件で探す**：`where("slug", "==", "foo")` みたいに **フィールドで検索する** 🔍

(A)を気持ちよくするのがID設計、(B)は**フィールド設計＋インデックス**の話になります📚
「タイトルで探すから、IDをタイトルにしよ！」はだいたい罠です😇

---

## 自動ID（Auto ID）って何がうれしいの？🎲✨

![Auto ID Load Balancing](./picture/firebase_firestore_struncture_ts_study_003_02_auto_id_load_balance.png)

Firestoreは「意味のあるIDが無いなら、自動でID作っていいよ」って公式でも言ってます。([Firebase][1])
しかも自動IDは、書き込みが偏って遅くなるのを避けやすい（散らす仕組み）ので、**高頻度で増えるデータに強い**です💪([Firebase][2])

✅ 自動IDが向くやつ（だいたいコレ）

* 記事 `posts`、コメント `comments`、いいねログ、アクセスログ、AIログ…など「どんどん増える」系📈🤖
* “作成が多い”＝自動IDが安定しやすい✨([Firebase][2])

---

## 意味のあるID（Custom ID）はいつ使う？🧩

![Custom ID Use Cases](./picture/firebase_firestore_struncture_ts_study_003_03_custom_id_cases.png)

「このIDに意味があると、運用がラク！」って場面もあります😊

✅ 意味のあるIDが向くやつ

* **1ユーザーにつき必ず1個**：`users/{uid}`（超定番）👤
* **1日につき必ず1個**：`reports/{YYYY-MM-DD}` みたいな “日別ドキュメント” 📅
* **固定の設定**：`settings/public` とか（ドキュメント数が少なく固定）⚙️

ただし注意点も多いです⚠️

* 連番や日付だけなど「増え方が偏る」IDは、高負荷で詰まりやすい設計になりがちです（※とくに大量作成時）😵‍💫([Firebase][2])
* さらに、**推測しやすいIDは“事故った時に被害が増えやすい”**（ルールが甘い/バグる等）ので、守りもセットで考えます🛡️([Firebase][3])

---

## FirestoreのIDにできない文字・制限（地味に大事）📏

ドキュメントID（コレクションIDも）には制限があります👇

* `/` は使えない
* `.` や `..` だけのIDはダメ
* `__.*__` に一致するIDはダメ
* 文字列の長さ上限（バイト上限）あり
  などが公式に明記されています🧯([Firebase][4])

なので、カッコよく「メールアドレスをIDにする」みたいなのは避けるのが無難です✉️💥（`@`はOKでも、変更・個人情報・運用がつらい）

---

## この教材の題材（User / Report / Post / Comment）でのおすすめID案🧠✨

![Recommended ID Patterns](./picture/firebase_firestore_struncture_ts_study_003_04_recommended_ids.png)

ここは“勝ちパターン”でいきます👇

## 1) ユーザー

* `users/{uid}` ✅（Authのuidをそのまま使う）👤

  * 1ユーザー1ドキュメントにピッタリ
  * ルールも書きやすい（後で楽）🛡️

## 2) 日報（1日1回なら）

* `users/{uid}/reports/{YYYY-MM-DD}` ✅📅

  * “その日の日報は1つだけ”が自然に担保できる
  * URLに載せる必要はたいてい無い（自分専用画面でOK）🙈

## 3) 記事

* `posts/{postId(auto)}` ✅📰

  * 記事は増えやすいので自動IDが安定
  * URLは `/posts/{postId}` でOK（まずこれが最強にラク）🔗

## 4) コメント

* `posts/{postId}/comments/{commentId(auto)}` ✅💬

  * これも増えやすいので自動IDでOK

---

## URLに載せるID / 載せないID の考え方🌐🔐

ミニ原則いきます👇

✅ URLに載せてもOKになりやすい

* `postId`（自動ID）📰
* 公開プロフィールにするなら `uid` も「載せてもいい」ケースはある（でも慎重に）👤

🙅‍♂️ URLに載せないほうがいい寄り

* メール、電話、社員番号、注文番号など **個人情報っぽいもの**
* 連番 `1,2,3...` や `20260216` だけみたいな **推測しやすいもの**（公開ページだと特に）🕵️‍♂️

そして超大事：
**「推測しにくいID」＝セキュリティではない**です⚠️
最終的に守るのはSecurity Rulesなので、甘いルールは普通にアウトです🛡️([Firebase][3])

---

## 手を動かす（TypeScript）🧪✨

## (1) 記事を “自動ID” で作る（王道）📰🎲

```ts
import { addDoc, collection, serverTimestamp } from "firebase/firestore";
import { db } from "./firebase";

export async function createPost(input: {
  title: string;
  body: string;
  authorUid: string;
}) {
  const ref = await addDoc(collection(db, "posts"), {
    title: input.title,
    body: input.body,
    authorUid: input.authorUid,
    createdAt: serverTimestamp(),
    updatedAt: serverTimestamp(),
  });

  return ref.id; // ← これがURLに使える postId ✅
}
```

## (2) ユーザーを “意味のあるID（uid）” で作る👤🆔

```ts
import { doc, setDoc, serverTimestamp } from "firebase/firestore";
import type { User } from "firebase/auth";
import { db } from "./firebase";

export async function createUserDoc(user: User) {
  await setDoc(doc(db, "users", user.uid), {
    displayName: user.displayName ?? "",
    photoURL: user.photoURL ?? "",
    createdAt: serverTimestamp(),
    updatedAt: serverTimestamp(),
  });
}
```

## (3) 日報を “意味のあるID（YYYY-MM-DD）” で作る📅📝

```ts
import { doc, setDoc, serverTimestamp } from "firebase/firestore";
import { db } from "./firebase";

export async function upsertDailyReport(input: {
  uid: string;
  dateId: string; // "2026-02-16" みたいな形式
  text: string;
}) {
  await setDoc(doc(db, "users", input.uid, "reports", input.dateId), {
    text: input.text,
    dateId: input.dateId,
    updatedAt: serverTimestamp(),
  }, { merge: true });
}
```

---

## セキュリティルール（ID設計と相性がいい最小形）🛡️✨

![Security Rules Matching](./picture/firebase_firestore_struncture_ts_study_003_05_security_rules_match.png)

`users/{uid}` にすると、**「自分のuidだけアクセスOK」**が超書きやすいです😊
（ルールの条件式の考え方は公式でも解説されています）([Firebase][5])

```rules
service cloud.firestore {
  match /databases/{database}/documents {

    match /users/{uid} {
      allow read, write: if request.auth != null && request.auth.uid == uid;

      match /reports/{dateId} {
        allow read, write: if request.auth != null && request.auth.uid == uid;
      }
    }
  }
}
```

※そして「とりあえず全部公開」みたいなルールは危険なので、ありがちなダメ例も公式の注意喚起で一度目を通すのおすすめです😇([Firebase][3])

---

## ミニ課題🎯（この章のゴールに直結）

## ミニ課題1：ID設計を“1枚表”にする📝✨

下の表をあなたのプロジェクト向けに埋めてください👇

| エンティティ  | パス案                                | IDタイプ | URLに載せる？ | 理由         |
| ------- | ---------------------------------- | ----- | -------- | ---------- |
| User    | `users/{uid}`                      | 意味あり  | たぶん載せない  | 1人1個・ルール簡単 |
| Report  | `users/{uid}/reports/{YYYY-MM-DD}` | 意味あり  | 載せない     | 1日1個・自分専用  |
| Post    | `posts/{autoId}`                   | 自動    | 載せる      | 公開ページに便利   |
| Comment | `posts/{postId}/comments/{autoId}` | 自動    | 載せない     | 増える・参照用    |

## ミニ課題2：危険IDを3つ挙げて、なぜダメか書く💥

例：

* `users/{email}`：変更されるし個人情報つらい😵
* `posts/1,2,3...`：推測される＆事故ったら総ナメの入口🚪
* `posts/2026-02-16`：公開系だと推測しやすい📅

---

## チェック✅（ここまで来たら勝ち🎉）

* [ ] 「検索」は基本フィールドでやる、IDは参照用と理解できた🔎
* [ ] 増えるデータ（posts/comments/logs）は自動IDを選べる🎲
* [ ] `users/{uid}` のように “意味のあるIDが強い場面” を言語化できた👤
* [ ] IDの制限（`/`禁止など）を知っている📏([Firebase][4])
* [ ] 「推測しにくさ」をセキュリティにしない（Rulesで守る）🛡️([Firebase][3])

---

## AIで“ID設計レビュー”を爆速にする🤖⚡（Antigravity / Gemini CLI / Firebase AI Logic）

## Antigravity（エージェントで計画→実行→検証）🛰️

Antigravityは “Mission Controlでエージェントを動かす” みたいな思想の開発環境として説明されています🤖🧭([Google Codelabs][6])
ID設計は「案を複数出して比較」するのが強いので、相性いいです✨

## Gemini CLI（ターミナルのAIエージェント）⌨️🤖

Gemini CLIはターミナルで動くオープンソースのAIエージェントで、ReActループやツール連携で作業を進められる、と説明されています🛠️([Google for Developers][7])
例えば「この設計表を読ませて、危険なIDや運用上の穴を洗って」みたいな使い方ができます👀✨

## Firebase AI Logic（アプリからGemini/Imagenを使う）🔥

Firebase AI LogicはアプリからGemini/Imagenモデルにアクセスする仕組みとして公式に案内されています🤖📱([Firebase][8])
たとえば、**設計レビュー結果やAI生成物の監査ログ**を `aiLogs/{autoId}` で保存する、みたいな設計にも自然につながります🧾✨

## コピペ用プロンプト例📎

* 「User/Report/Post/CommentのID案がこれ。**推測されやすさ・運用のつらさ・ホットスポット**観点で赤入れして」
* 「URLに載せるIDが `postId` だけでOKか、`slug` も欲しい。**slugのユニーク制約**をFirestoreで実現する案を3つ」
* 「このSecurity Rulesで、**ID推測→不正閲覧**が起きないかチェックして。危険なルール例も教えて」([Firebase][3])

---

次の章（第4章）では、ここで決めたID設計を踏まえて「サブコレの使いどころ」を、`posts/{postId}/comments` を題材にスパッと判断できるようにしていきます🧩🔥

[1]: https://firebase.google.com/docs/firestore/manage-data/add-data?utm_source=chatgpt.com "Add data to Cloud Firestore - Firebase - Google"
[2]: https://firebase.google.com/docs/firestore/best-practices?utm_source=chatgpt.com "Best practices for Cloud Firestore - Firebase - Google"
[3]: https://firebase.google.com/docs/rules/insecure-rules?utm_source=chatgpt.com "Avoid insecure rules | Firebase Security Rules - Google"
[4]: https://firebase.google.com/docs/firestore/quotas?utm_source=chatgpt.com "Usage and limits: Firestore - Firebase"
[5]: https://firebase.google.com/docs/firestore/security/rules-conditions?utm_source=chatgpt.com "Writing conditions for Cloud Firestore Security Rules - Firebase"
[6]: https://codelabs.developers.google.com/getting-started-google-antigravity?utm_source=chatgpt.com "Getting Started with Google Antigravity"
[7]: https://developers.google.com/gemini-code-assist/docs/gemini-cli?utm_source=chatgpt.com "Gemini CLI | Gemini Code Assist"
[8]: https://firebase.google.com/docs/ai-logic?utm_source=chatgpt.com "Gemini API using Firebase AI Logic - Google"