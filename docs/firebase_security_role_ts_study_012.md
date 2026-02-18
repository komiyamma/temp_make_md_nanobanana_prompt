# 第12章：入力検証③ “書いていい項目だけ許す”（権限昇格を防ぐ）🛡️🚫👑

この章はひとことで言うと👇
**「ユーザーが“勝手に強くなる”書き込みを、Rulesで物理的に止める」**回です😎✨

---

## 1) まず怖い話：クライアントは“改造できる前提”😈🪛

Reactの画面で「role欄なんて出してないし大丈夫でしょ🙂」
…って思っても、攻撃者は **画面を通さずに** Firestoreへリクエストを投げられます💥

たとえば👇みたいな“追加フィールド”を混ぜてきます。

* `role: "admin"` を勝手に書く👑
* `isAdmin: true` を勝手に足す🚨
* `average_score` / `rating_count` みたいな集計項目を勝手に上書き📈
* `createdAt` / `updatedAt` を好きな値に偽装🕒

だから **「書いていいキーだけ許す（allowlist）」** が超重要です🧱✨
（Firestoreはスキーマレスなので、DB側が勝手に守ってくれることはありません）([Firebase][1])

---

## 2) この章の結論：allowlistは2種類つくる✌️🔑

## A. create（新規作成）→ `request.resource.data.keys().hasOnly(...)` ✅

「新しく作るドキュメントに、余計なフィールドが混ざってたら拒否！」🚫

Firestore公式も、**keys + hasOnly / hasAll** で allowlist を作るパターンを推奨しています🧠([Firebase][1])

---

## B. update（更新）→ `diff(resource.data).affectedKeys().hasOnly(...)` ✅✅

ここがこの章の“いちばん大事”ポイントです🔥

updateでは、`request.resource.data` は **更新後の完成形**（= 既存フィールドも含まれる）になります。
だから「キー一覧で hasOnly」すると、**サーバーが後から付けたフィールド**（例：`role`, `createdAt`）まで含まれてしまい、事故ります😱

そこで使うのが👇
**`request.resource.data.diff(resource.data).affectedKeys()`**
= 「今回の更新で“変更されたキーだけ”の集合」✨([Firebase][1])

---

## 3) “隠したいフィールド”は、そもそも別ドキュメントに分ける🙈📄

重要な注意点：Firestoreのreadは **ドキュメント単位**です。
**フィールドだけ見せない**みたいな“部分取得”は Rules だけではできません❌
隠したい情報は `private` サブコレクションなどに分離が定石です🧩([Firebase][1])

---

## 4) 手を動かす：プロフィール更新で「許可キー以外は拒否」を実装🧑‍💻🔥

## 想定データ（例）📦

`users/{uid}/profile` に、将来的にこういうフィールドが入ることを想定します👇

* ユーザーが編集してOK：`displayName`, `bio`, `photoURL`
* ユーザーが触っちゃダメ：`role`, `createdAt`, `updatedAt`（サーバー側で管理したい）

この章の目標は👇
**ユーザーが `role` を勝手に書こうとしても、絶対に通らない**状態にする🛡️✨

---

## 実装例（Rules）🧱🔐

```rules
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    function signedIn() {
      return request.auth != null;
    }

    function isOwner(uid) {
      return signedIn() && request.auth.uid == uid;
    }

    // create: 「作成時に入れていいキー」だけ許す（allowlist）
    function profileCreateOk() {
      let required = ['displayName'];
      let optional = ['bio', 'photoURL'];
      let allowed = required.concat(optional);

      return request.resource.data.keys().hasAll(required) &&
             request.resource.data.keys().hasOnly(allowed) &&
             request.resource.data.displayName is string;
    }

    // update: 「変更していいキー」だけ許す（超重要！）
    function profileUpdateOk() {
      return request.resource.data
               .diff(resource.data)
               .affectedKeys()
               .hasOnly(['displayName', 'bio', 'photoURL']);
    }

    match /users/{uid}/profile {
      allow read: if isOwner(uid);

      allow create: if isOwner(uid) && profileCreateOk();

      // role/createdAt/updatedAt が “存在していてもOK”
      // でも「変更」しようとしたら affectedKeys に載るので弾ける！
      allow update: if isOwner(uid) && profileUpdateOk();

      allow delete: if false;
    }
  }
}
```

ポイントはここ👇😎✨

* **create** は「入れていいキー」だけ（`hasOnly`）
* **update** は「変えていいキー」だけ（`affectedKeys().hasOnly`）

Firestore公式も「更新では affectedKeys を使う」例を出しています📚([Firebase][1])

---

## 5) 攻撃ごっこ（わざと悪い更新を投げる）😈➡️🧯

## ✅ 正常：プロフィール更新（OK）

* `displayName` だけ更新する
* `bio` だけ更新する
* `photoURL` だけ更新する

## ❌ 攻撃：勝手に管理者化（NG）

* `role: "admin"` を混ぜて更新
* `isAdmin: true` を追加して更新

→ **どれも `affectedKeys()` に乗るので、hasOnlyで即アウト**🎉

---

## 6) よくある落とし穴（ここで事故る）⚠️😵

## 落とし穴①：updateでも `request.resource.data.keys().hasOnly(...)` を使う

これ、**サーバーが後から追加したフィールドがあるだけで**更新が詰みます😱
updateは **「変更キーだけ」**を見るのが安全です🧯([Firebase][1])

## 落とし穴②：サーバー側（Admin SDK等）もRulesで守られていると思い込む

サーバー用ライブラリは **Rulesをバイパス**します。
その場合は **IAM** やサーバー側の認可・検証が責任範囲です🔐([Firebase][1])

---

## 7) AIで爆速にする（ただし最後は人間の目👀✅）🤖⚡

## Antigravity × Firebase MCPで「許可キー表」を作らせる🗂️✨

Google の Antigravity は **Firebase MCP server** を追加して、エージェントに実装を進めさせる流れが紹介されています🧠([The Firebase Blog][2])

おすすめ依頼（そのままコピペでOK）👇

```text
users/{uid}/profile のスキーマを確認して、
クライアントが変更してよいフィールド（allowlist）と、
サーバー側でしか触れないフィールド（denylist）を整理して。
その上で firestore.rules の create は keys().hasOnly、
update は diff(resource.data).affectedKeys().hasOnly を使って
安全に書き直して。最後に、弾くべき攻撃ケースも箇条書きで。
```

## Gemini CLI で Rules + テストの叩き台を作る🧪⚙️

FirebaseのAI支援ドキュメントでは、**Gemini CLI拡張が Rules とテストの叩き台を生成**し、反復的な“攻撃シミュレーション”も試みる、と説明されています🤖🧯([Firebase][3])
さらに「勝手に継続監視して更新してくれるわけじゃない」ので、変更のたびに見直しが必要です⚠️([Firebase][3])

プロジェクトのルートで Gemini CLI を起動して、コマンドを実行する流れが案内されています👇([Firebase][3])

```text
## 例：Gemini CLI を開いて
/firestore:generate_security_rules
```

※コンソール内の「Gemini in Firebase」は Rules 生成ができない、と明記されています（ここ勘違いしやすい！）😵‍💫([Firebase][3])

---

## 8) ミニ課題🎯（10分）

次のコレクションを想像して、allowlist を作ってみてください👇😆

`posts/{postId}`

* ユーザーが編集OK：`title`, `body`
* ユーザーが編集NG：`authorId`, `likeCount`, `status`, `roleToEdit`

やること✅

1. create 用：`keys().hasAll([...])` + `keys().hasOnly([...])`
2. update 用：`diff().affectedKeys().hasOnly([...])`
3. 「NGフィールド混入」の攻撃パターンを3つ書く📝

---

## 9) チェック✅（できたら勝ち！🏆）

* [ ] 「create」と「update」で見るべきキー集合が違う、と説明できる🙂
* [ ] `role` / `isAdmin` を混ぜた更新が、必ず弾かれる🛡️
* [ ] “隠したいフィールド”は別ドキュメントに分ける発想がある🙈
* [ ] AIで叩き台を作っても、最後はルールとテストを人がレビューする👀✅ ([Firebase][3])

---

次の第13章（Rules関数化）では、今作った「owner判定」「allowlist判定」を**読みやすく安全に再利用**できる形に整えていきます🧩✨

[1]: https://firebase.google.com/docs/firestore/security/rules-fields "Control access to specific fields  |  Firestore  |  Firebase"
[2]: https://firebase.blog/posts/2025/11/firebase-mcp-and-antigravity/ "Antigravity and Firebase MCP accelerate app development"
[3]: https://firebase.google.com/docs/ai-assistance/prompt-catalog/write-security-rules "AI Prompt: Write Firebase Security Rules  |  Develop with AI assistance"
