# 第5章：Rules言語の基本②（request / resource / 変更差分）🔍🛡️✨

この章のテーマはこれ👇
**「今あるデータ（resource）と、これから書き込まれようとしてるデータ（request.resource）を区別して、更新の“差分”で安全に制御する」**です😆💡

---

## 1) まずは超重要3点セットを覚える📌😺

![Resource vs Request.Resource](./picture/firebase_security_role_ts_study_005_01_resource_vs_request.png)

## ✅ resource（今DBにある“既存データ”）

* `resource` は **対象ドキュメントそのもの**
* `resource.data` は **ドキュメントの中身（Map）** ([Firebase][1])
* `resource.id` は **ドキュメントID** ([Firebase][1])

---

## ✅ request（リクエストの情報）

![Request Object Anatomy](./picture/firebase_security_role_ts_study_005_02_request_object.png)

* `request.method` は操作の種類（`get/list/create/update/delete`） ([Firebase][2])
* `request.time` はサーバーが受け取った時刻（サーバー時刻チェックに使える） ([Firebase][2])

---

## ✅ request.resource（“書き込まれた後”の新しい姿）✨

* `request.resource` は **書き込み系（create/update/delete）で使える「新しいresource」** ([Firebase][2])
* ルールを書くときの感覚はこう👇

  * `resource.data` = “変更前”
  * `request.resource.data` = “変更後（こうしたい！）”

---

## 2) create / update / delete で「見えるもの」が違う⚠️🧠

![Data Visibility by Operation](./picture/firebase_security_role_ts_study_005_03_operation_visibility.png)

ここ、事故りやすいので丁寧にいくよ〜😊

## 🟦 create（新規作成）

* だいたい **resource（既存）が無い**（まだ作られてないから）
* なので **入力検証は `request.resource.data` が主役**✨

## 🟨 update（更新）

* **resource.data（変更前）も request.resource.data（変更後）も両方ある**
* “差分”で制御できるから、ここが一番テクい＆強い💪🔥

## 🟥 delete（削除）

* 削除は **クライアントから「新しいデータ」が送られてこない**ので、`request.resource.data` を使ったバリデーションができない（＝できても意味が薄い）ことが多いよ、という注意が広く共有されてる⚠️ ([Qiita][3])
* 削除時に見るべきは基本 **resource.data（消される側の既存データ）** 👀

---

## 3) “差分”を取る最強ワザ：Map.diff() 🧩✨

![Map Diff Logic](./picture/firebase_security_role_ts_study_005_04_map_diff.png)

Firestore Rules では **Map同士の差分**が取れるよ！
`request.resource.data.diff(resource.data)` みたいに書くと、**MapDiff** が返る💡 ([The Firebase Blog][4])

MapDiff にはこういう便利メソッドがある👇 ([Firebase][5])

* `changedKeys()`：値が変わったキー
* `addedKeys()`：追加されたキー
* `removedKeys()`：消されたキー
* `affectedKeys()`：追加/変更/削除の全部入り（影響を受けたキー）

---

## 4) 手を動かす🧑‍💻🔥：更新で“触っていいフィールドだけ”許す

ここでは例として `posts/{postId}` を守るよ📮✨
「本文は編集OK。でも `ownerId` と `createdAt` は絶対いじれない」みたいなやつ！

## 4-1. まずはサンプルデータ設計（イメージ）🧠🧱

* `ownerId`（投稿者の uid）
* `title`（タイトル）
* `body`（本文）
* `createdAt`（作成時刻）
* `updatedAt`（更新時刻）
* `isLocked`（ロック中フラグ：trueなら編集不可）

---

## 4-2. ルールを書いてみる（差分で update を縛る）🔒✍️

![Secure Update Filtering](./picture/firebase_security_role_ts_study_005_05_secure_update.png)

```rules
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    match /posts/{postId} {

      // ✅ create: 必須フィールドが揃っていること（例）
      allow create: if
        request.auth != null
        && request.resource.data.ownerId == request.auth.uid
        && request.resource.data.title is string
        && request.resource.data.body is string
        && request.resource.data.createdAt == request.time
        && request.resource.data.updatedAt == request.time;

      // ✅ update: ロック中はダメ + 変更できるキーを限定
      allow update: if
        request.auth != null
        && resource.data.ownerId == request.auth.uid
        && resource.data.isLocked != true
        // 変更して良いのは title, body, updatedAt だけ！
        && request.resource.data.diff(resource.data)
             .affectedKeys()
             .hasOnly(["title", "body", "updatedAt"].toSet())
        // updatedAt はサーバー時刻で更新されていること
        && request.resource.data.updatedAt == request.time;

      // ✅ delete: 基本は resource 側の情報で判断
      allow delete: if
        request.auth != null
        && resource.data.ownerId == request.auth.uid
        && resource.data.isLocked != true;
    }
  }
}
```

ポイント解説だよ😊👇

![Update Validation Checklist](./picture/firebase_security_role_ts_study_005_06_update_checklist.png)

* `request.resource.data.diff(resource.data).affectedKeys()` で「変えたキーの集合」を取る ([Firebase][5])
* `hasOnly(...)` で「このキー以外は絶対変えるな！」ができる✨ ([The Firebase Blog][4])
* `request.time` を使うと「時刻を勝手に書き換える」系を防ぎやすい⌚ ([Firebase][2])

---

## 5) すぐ試す（超かんたん検証）🧪😺

## ✅ 試す操作（頭の中でOK→できればEmulatorで）

1. **create**：`title/body/createdAt/updatedAt` を入れて作る → 通る🙆‍♂️
2. **update**：`title` だけ変更 + `updatedAt=request.time` → 通る🙆‍♂️
3. **update**：`ownerId` を自分→他人に変えようとする → **弾かれる**🙅‍♂️💥
4. **update**：`isLocked` を勝手に `false` にする → **弾かれる**🙅‍♂️💥
5. **delete**：`isLocked=true` の投稿を消す → **弾かれる**🙅‍♂️💥

---

## 6) ミニ課題🎯🧠（更新時だけ禁止するルールを作ろう）

次の仕様を満たす `notes/{noteId}` を守ってね📝✨

* create：ログインしてたらOK
* update：**完全に禁止**（編集させない）🚫
* delete：本人だけOK（owner一致）🗑️

ヒント：`allow update: if false;` でもOKだよ😂（ルールは正義）

---

## 7) チェック✅（ここ答えられたら勝ち！🏆🎉）

* `resource.data` と `request.resource.data` の違いを、1行で言える？🙂
* update のとき、**“差分”で守る**と何が嬉しい？（改造クライアント対策✨）
* delete で `request.resource.data` を前提にすると危ない理由、説明できる？ ([Qiita][3])

---

## 8) AI活用コーナー🤖✨（Rulesづくりを爆速にする）

## 8-1. “叩き台”はAI、決定は人間🧑‍⚖️✅

![AI Rules Drafting & Human Review](./picture/firebase_security_role_ts_study_005_07_ai_review_workflow.png)

Firebase の **AIプロンプトカタログ**には、Rules作成用のプロンプトが用意されてるよ📚✨
しかも **Antigravity / Gemini CLI などのエージェント**向けに使える前提で整備されてる！ ([Firebase][6])

その中の「Security Rulesを書かせる」プロンプトは、**プロジェクト状態を元に1回生成する（自動追従ではない）**と明記されてるので、運用の注意点もバッチリ👌 ([Firebase][7])

---

## 8-2. Antigravity × Firebase MCP で「今の設計」を見ながら相談🧠🔧

Firebase MCP サーバーを Antigravity に入れる導線が公式に用意されてるよ（設定手順も公開） ([Firebase][8])
背景として、Firebase側も Antigravity や Gemini CLI で MCP をうまく動かす話をブログで出してる📣 ([The Firebase Blog][9])

**この章の使い方（おすすめ）**👇

* AIに「posts の update で変更できるキーを title/body/updatedAt に限定したい。Rulesを書いて」って叩き台を作らせる
* 出てきたRulesに対して、人間がチェックする✅

  * “ownerId 変えられない？”
  * “isLocked を解除できない？”
  * “updatedAt を request.time で縛ってる？”

---

## 9) この章のまとめ📦✨

* `resource.data` は **今あるデータ**、`request.resource.data` は **変更後のデータ** ([Firebase][2])
* update は **差分（diff）で守ると最強**🛡️✨ ([The Firebase Blog][4])
* delete は **基本 resource 側で判断**（送信データ前提にしない）⚠️ ([Qiita][3])
* AIはRules作りを速くするけど、**最終レビューは人間**🧑‍⚖️✅ ([Firebase][7])

---

次の章（第6章）に行くと、ここで触れた `request.auth` を「ログイン必須の守り」に育てていくよ🔐😆

[1]: https://firebase.google.com/docs/reference/rules/rules.firestore.Resource "Interface: Resource  |  Firebase"
[2]: https://firebase.google.com/docs/reference/rules/rules.firestore.Request "Interface: Request  |  Firebase"
[3]: https://qiita.com/KosukeSaigusa/items/18217958c581eac9b245?utm_source=chatgpt.com "Firestore Security Rules の書き方と守るべき原則"
[4]: https://firebase.blog/posts/2020/06/new-firestore-security-rules-features/ "New improvements to Firestore Security Rules"
[5]: https://firebase.google.com/docs/reference/rules/rules.MapDiff "Interface: MapDiff  |  Firebase"
[6]: https://firebase.google.com/docs/ai-assistance/prompt-catalog?utm_source=chatgpt.com "AI prompt catalog for Firebase | Develop with AI assistance"
[7]: https://firebase.google.com/docs/ai-assistance/prompt-catalog/write-security-rules?utm_source=chatgpt.com "AI Prompt: Write Firebase Security Rules"
[8]: https://firebase.google.com/docs/ai-assistance/mcp-server?utm_source=chatgpt.com "Firebase MCP server | Develop with AI assistance - Google"
[9]: https://firebase.blog/posts/2025/11/firebase-mcp-and-antigravity/?utm_source=chatgpt.com "Antigravity and Firebase MCP accelerate app development"
