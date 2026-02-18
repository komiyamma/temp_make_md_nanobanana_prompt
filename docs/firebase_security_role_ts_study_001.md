# 第1章：なぜRulesが必要？「公開しちゃった😱」事故の構造を知る💥🛡️

この章のテーマはズバリ👇
**「Firestoreは“ネットに繋がったDB”だから、守りを決めないと“普通に漏れる”」**です😱💦
（悪意あるハッカーじゃなくても、設定ミスだけで事故ります…）

---

## この章でできるようになること🎯✨

* 「公開しちゃった😱」が **どういう仕組みで起きるか** を説明できる
* **危ないRules**を見て「何がヤバいか」を言葉にできる
* 「Rulesは入口の審査🚪」という発想が腹落ちする

---

## 1) まず結論：Firestoreは“誰でも叩ける入口”がある🔓🌍

Firestoreは、Web/モバイルのクライアントSDKから **直接アクセス**できます。
そして、そのリクエストは **毎回Security Rulesで判定**されます。([Firebase][1])

つまりこうです👇

* アプリ（Reactなど）の中のコードは、ユーザーに見られる・改造される前提🧑‍🔧💻
* だから「画面でボタンを隠す🙈」だけじゃ守れない
* **最後の砦がRules**（入口の審査員🚪👮‍♂️）

---

## 2) 「公開事故😱」が起きる典型パターン（構造で理解）🧠💥

事故はだいたい次の流れで起きます👇

1. 開発中に「とりあえず動かす」ためにルールを緩める🛠️
2. そのまま本番に出す（または期限付き公開を忘れる）📤😇
3. 誰かが **一覧取得（list）** や **総当たり** でデータに触れる
4. 「え、ログインしてないのに読める…？」で発覚😱

Firebase公式も「よくある脆弱な設定と直し方」をガイド化してます。([Firebase][2])

---

## 3) “危ないRules”の代表例を見て、ヤバさを言語化しよう🧯🗣️

ここからは **わざと危ない例** を見ます（本番で使わないでね！）⚠️🙅‍♂️

## 危険例A：全公開（最悪）☠️

```js
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if true;
    }
  }
}
```

**何がヤバい？😱**

* 全コレクション・全ドキュメントが **誰でも読み書き** できる
* 「ユーザー一覧」「メール」「課金情報」「下書き」全部アウトの可能性💥
* 改ざん・削除もできる（荒らされ放題）🧨

## 危険例B：期限付き公開（“忘れる”やつ）⏳😇→😱

```js
match /{document=**} {
  allow read, write: if request.time < timestamp.date(2026, 4, 1);
}
```

**何がヤバい？😱**

* 「あとで閉めるつもり」が一番危ない
* 期限切れ前に漏れても、ログに残らず気づきにくいことも…😵‍💫
* “開発中だけ”のつもりが本番に混ざるあるある💣
  こういう「危険なルール」パターンも公式で注意喚起されています。([Firebase][2])

## 危険例C：「ログインしてれば何でもOK」も実は危ない🔓👤

```js
match /{document=**} {
  allow read, write: if request.auth != null;
}
```

**何がヤバい？😱**

* “ログイン済みなら全員が全データを触れる”＝他人のデータも触れる可能性💥
* さらに入力検証が無いと「role=adminを書き換える」みたいな権限昇格も起きがち🧨
  （この教材の後半で「入力検証」「書いていい項目だけ許す」をしっかりやります🛡️）

---

## 4) 超重要な勘違い：Admin SDKはRulesの対象外⚠️🧱

ここ、初心者がハマりがちです😵‍💫

* **クライアントSDK（Web/モバイル）** → Rulesで守れる✅
* **Firebase Admin SDK（サーバー側）** → Rulesで守れない（基本フル権限）⚠️

Firebase公式ブログでも「Admin SDKのリクエストはRulesでゲートされない」ことが明確に書かれています。([The Firebase Blog][3])

なので将来的に👇

* サーバー側（Functionsなど）は **IAM / サービスアカウント / サーバー側の認可** が別途必要
  という発想になります（ここは第2章以降で丁寧にやります🙂）

---

## 5) 手を動かす🧑‍💻：Rules Playgroundで“事故を再現”してみよう🧪🔥

この章では「安全に体験」したいので、まずは **FirebaseコンソールのRules Playground** を使います🙂
（ローカルの自動テストは後半章でEmulatorを使います🧪）

Rules Playgroundの公式ガイドはこちらです。([Firebase][4])

## やること（5〜10分）⏱️

1. Firebaseコンソールで Firestore を開く
2. **Rules** タブを開く
3. ルールを上の「危険例A」に一旦してみる（※あとで戻す前提）⚠️
4. **Rules Playground**（シミュレーター）でリクエストを試す🧪

   * 未ログイン（authなし）で read / write が通るか？
   * どのパスでも通っちゃうか？

## 観察ポイント👀

* 「未ログインでも通る」＝公開事故確定😱
* ルールが `match /{document=**}` になってると、**守りが全消し**になりやすい💥

> 終わったら、必ずルールを戻すか、次の章へ進む前に“閉める”こと！🚪🔒

---

## 6) ミニ課題🎯：「このルールだと誰が何できちゃう？」を3つ書く📝

危険例Aを見て、次の3つを自分の言葉で書いてみてください🙂✨

* ① 誰が読める？（未ログインは？）
* ② 誰が書ける？（追加・更新・削除は？）
* ③ 一番マズい被害は何？（例：個人情報漏えい、改ざん、全消し…）

---

## 7) チェック✅（ここまででOKなら次へ！）

* Rulesが「入口の審査🚪」だと説明できる
* `allow read, write: if true;` を見た瞬間に「それ最悪☠️」って言える
* 「ログインしてればOK」でも危ないケースがあるとわかった
* Admin SDKはRulesの外側だと理解できた([The Firebase Blog][3])

---

## 8) AI活用🤖✨：Rulesの“危険臭チェック”をAIにやらせる（ただし最終判断は人間）🧑‍⚖️✅

2026-02-16時点では、Firebase公式の **AIプロンプトカタログ**があり、Antigravity / Gemini CLI などのエージェントから使う前提で整備されています。([Firebase][5])
さらに「Security Rulesを書く」専用プロンプトも用意されています。([Firebase][6])

## 使い方イメージ（この章では“レビュー役”が便利）🔍

AIにRulesファイルを貼って、こう聞きます👇

* 「このRulesで **公開事故になりうる箇所** を箇条書きで指摘して」
* 「`match /{document=**}` や `if true` みたいな **危険パターン** がある？」([Firebase][2])
* 「未ログイン・一般ユーザー・管理者の3者で、何ができるか表にして」

最後に **Rules Playgroundで自分でも再現**して確かめる、が鉄板です🧪✅ ([Firebase][4])

---

次の第2章では、「Firestoreのアクセス経路の整理（Rulesが効く/効かない）」に入って、**守れる範囲を取り違えない**ようにしていきます🧭✨

[1]: https://firebase.google.com/docs/firestore/security/get-started?utm_source=chatgpt.com "Get started with Cloud Firestore Security Rules - Firebase"
[2]: https://firebase.google.com/docs/rules/insecure-rules?utm_source=chatgpt.com "Avoid insecure rules | Firebase Security Rules - Google"
[3]: https://firebase.blog/posts/2019/03/firebase-security-rules-admin-sdk-tips/?utm_source=chatgpt.com "7 tips on Firebase security rules and the Admin SDK"
[4]: https://firebase.google.com/docs/rules/simulator?utm_source=chatgpt.com "Quickly validate Firebase Security Rules - Google"
[5]: https://firebase.google.com/docs/ai-assistance/prompt-catalog?hl=ja&utm_source=chatgpt.com "Firebase の AI プロンプト カタログ | Develop with AI assistance"
[6]: https://firebase.google.com/docs/ai-assistance/prompt-catalog/write-security-rules?utm_source=chatgpt.com "AI Prompt: Write Firebase Security Rules"
