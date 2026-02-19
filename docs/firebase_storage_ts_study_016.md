### 第16章：Rulesで「画像だけ＆サイズ上限」を強制する🧯🛡️

この章は「**アップロード前チェック（第7章）**」だけに頼らず、**最後の門番＝Storage Rules**で「画像以外＆デカすぎ」をガチで弾く回だよ〜📷🚫
（2026-02-03更新の公式ドキュメント内容で確認して組み立ててるよ✅） ([Firebase][1])

---

![Final Gatekeeper](./picture/firebase_storage_ts_study_016_01_final_gatekeeper.png)

## 1) まず“腹落ち”させたいこと🍞🧠

![Metadata Scanner](./picture/firebase_storage_ts_study_016_02_metadata_scanner.png)

### ✅ Rulesができること（この章の主役）

Storage Rulesは、ファイルの**メタデータ**を見てチェックできるよ👇

* `request.resource.size`：アップロードされるファイルのサイズ（バイト）📏
* `request.resource.contentType`：MIMEタイプ（例：`image/jpeg`）🏷️
  そして `matches()` を使って「`image/.*` だけ」みたいな制限が書ける✨ ([Firebase][1])

![Resource vs Request](./picture/firebase_storage_ts_study_016_03_resource_vs_request.png)

### ✅ “request.resource” と “resource” の違い🔍

超重要！ここで事故が減るよ🔥

* `resource`：**すでに存在してる**ファイルのメタデータ（既存）📦
* `request.resource`：**これから書き込まれる**メタデータ（新規/更新）🆕📦
  「書き込み時は両方使える」って公式でも説明されてるよ。 ([Firebase][2])

![Granular Write](./picture/firebase_storage_ts_study_016_04_granular_write.png)

### ⚠️ つまずきポイント（先に潰す）💥

* 「`allow write` に size / contentType を入れたら、削除が通らなくなった😇」
  → `write` は “create/update/delete” をまとめた操作。**操作ごとに分ける**と安全だよ（次でやる）🧯 ([Firebase][3])
* 「`image/*` ならOKでしょ？」
  → `image/svg+xml` みたいに扱いが難しいものもあるから、**PNG/JPEG/WebPだけ許可**みたいに狭めるのが安心なことが多いよ🧷

---

## 2) 手を動かす✋💻（Rulesを“運用っぽく”書く）

ここでは「プロフィール画像」想定で👇

* パス：`users/{uid}/profile/{fileId}` 📁
* 上限：例として **2MB**（好きに変えてOK）🧃
* 許可：**JPEG / PNG / WebP**のみ✅

---

![Operation Logic Flow](./picture/firebase_storage_ts_study_016_05_operation_flow.png)

### 手順A：まず“運用版”のRulesを用意する🧩

ポイントはこれ👇

* `write` でまとめず、**create / update / delete に分ける**🧯 ([Firebase][3])
* **create** で「サイズ」「contentType」をチェック
* **update** では「contentTypeを変えられない」も入れる（地味に効く）🧷 ([Firebase][2])

```txt
rules_version = '2';

service firebase.storage {
  match /b/{bucket}/o {

    // プロフィール画像置き場
    match /users/{uid}/profile/{fileId} {

      // 共通：ログインしてて本人
      function isOwner() {
        return request.auth != null && request.auth.uid == uid;
      }

      // 共通：許可する画像形式（SVGはあえて除外）
      function isAllowedImageType() {
        return request.resource.contentType.matches('image/(jpeg|png|webp)');
      }

      // 共通：サイズ上限（例: 2MB）
      function isUnderLimit() {
        return request.resource.size < 2 * 1024 * 1024;
      }

      // 読み取り：本人だけ（公開にしたいならここを調整）
      allow read: if isOwner();

      // ✅ 新規アップロード：画像形式 + サイズ制限
      allow create: if isOwner()
                    && isUnderLimit()
                    && isAllowedImageType();

      // ✅ メタデータ更新：本人 + contentType変更禁止（すり替え防止）
      // ※ update は「既存ファイルのメタデータ更新」に対して効くよ
      allow update: if isOwner()
                    && resource != null
                    && request.resource.contentType == resource.contentType;

      // 🗑️ 削除：本人だけ（“使用中は削除不可”は第13章の設計と合体でやる）
      allow delete: if isOwner();
    }
  }
}
```

> 公式でも `size` と `contentType` で「5MB未満の画像だけ」みたいな検証ができる例が載ってるよ（考え方は同じ）📚 ([Firebase][1])
> さらに `request.resource` と `resource` を使い分けて、形式すり替えを防ぐ例もあるよ🛡️ ([Firebase][2])

---

### 手順B：反映（コンソールでもCLIでもOK）🚀

#### ① コンソールで反映（サクッと）🧑‍💻

Firebase console → Storage → **Rules** → さっきのRules貼る → 公開（Publish）✅
（ミスっても戻せるから怖がらなくてOK🙂）

#### ② CLIで反映（おすすめ：Git管理できる）🧰

PowerShellでこんな感じ👇

```bash
# Firebase CLI（入ってなければ）
npm i -g firebase-tools

firebase login
firebase init storage
firebase deploy --only storage
```

---

### 手順C：テスト（わざと失敗させるのがコツ）🧪💥

✅ 成功ケース

* `me.jpg`（500KB）をアップロード → 通る🙆‍♀️

❌ 失敗ケース（期待通り弾けたら勝ち）

* 3MBの画像 → **サイズ超過で拒否**🙅‍♂️
* `.txt` をアップロード（contentTypeが `text/plain` になりがち）→ **形式で拒否**🙅‍♀️
* 他人の `users/{uid}` に突っ込む → **本人一致で拒否**🙅

---

![AI Rule Architect](./picture/firebase_storage_ts_study_016_06_ai_rule_architect.png)

## 3) AIを絡めて“強いRules”を最速で作る🤖⚡

### ✅ Gemini in Firebase：相談・原因究明に強い🧯

Rulesのエラー原因や考え方を聞くのに便利！
ただし **コンソールのGeminiはコードベースを見れないので、Rulesを生成する用途はGemini CLIなどが推奨**って公式にも明記されてるよ。 ([Firebase][4])

### ✅ Gemini CLI / Antigravity：Rulesの“生成・改修・レビュー”に強い🛠️

Firebaseの **MCP server** は、**Antigravity / Gemini CLI / Firebase Studio** などから使えるって公式に書かれてる！めっちゃ相性いいやつ🚀 ([Firebase][5])

#### そのまま使えるプロンプト例✍️✨

（Gemini CLI / Antigravity のチャットに投げる用）

```txt
目的：プロフィール画像アップロードのStorage Rulesを安全にしたい。
要件：
- パスは users/{uid}/profile/{fileId}
- 読み取りは本人のみ
- 書き込みは本人のみ
- create は JPEG/PNG/WebP のみ許可
- サイズは 2MB 未満
- update で contentType のすり替えを防ぎたい
- delete は本人のみ
上の要件を満たす rules_version=2 のルールを提案して。
さらに「ありがちな穴」「テストケース（成功/失敗）」も10個出して。
```

#### さらに一歩：Gemini CLIのFirebase拡張で“雛形生成”🧩

公式のプロンプトカタログでは、**Gemini CLI拡張は1回実行でRulesを生成する（自動追従はしない）**って注意もあるよ。つまり、作った後の更新は自分でやる方式📝 ([Firebase][6])

---

## 4) ミニ課題🎯📌

### ミニ課題A：許可する画像形式を増やす🧪

今は `jpeg|png|webp`。
ここに「`gif` を追加」してみてね（ただしプロフィールでGIFを許すかは好み！）😄

### ミニ課題B：上限を“プロダクトっぽく”決める💡

* アイコンだけなら 512KB〜1MB でも十分なこと多い
* 高画質を許すなら 2MB〜5MB
  「なぜその数値か」を一言で言えるようにしよ🗣️✨

---

![Concept Checklist](./picture/firebase_storage_ts_study_016_07_checklist_summary.png)

## 5) チェック✅✅✅

* `request.resource.size` と `request.resource.contentType` で弾ける理由を説明できる📏🏷️ ([Firebase][7])
* `request.resource` と `resource` の違いが言える🧠 ([Firebase][2])
* `write` を `create/update/delete` に分ける意味がわかる🧯 ([Firebase][3])
* 失敗テスト（サイズ超過/形式違い/他人パス）が全部ちゃんと拒否される🙅‍♂️💥
* AI（Gemini in Firebase / Gemini CLI / Antigravity）で「レビュー→修正→再テスト」が回せる🤖🔁 ([Firebase][5])

---

次の章（第17章）は **App Checkで“正規アプリ以外”を通しにくくする** から、ここで作ったRulesがさらに頼もしくなるよ🧿✨

[1]: https://firebase.google.com/docs/storage/security "Understand Firebase Security Rules for Cloud Storage  |  Cloud Storage for Firebase"
[2]: https://firebase.google.com/docs/storage/security/secure-filesBAK?hl=ja "ファイルを保護する方法を学ぶ  |  Cloud Storage for Firebase"
[3]: https://firebase.google.com/docs/storage/security/core-syntax "Learn the core syntax of the Firebase Security Rules for Cloud Storage language  |  Cloud Storage for Firebase"
[4]: https://firebase.google.com/docs/ai-assistance/gemini-in-firebase?utm_source=chatgpt.com "Gemini in Firebase - Google"
[5]: https://firebase.google.com/docs/ai-assistance/mcp-server?utm_source=chatgpt.com "Firebase MCP server | Develop with AI assistance - Google"
[6]: https://firebase.google.com/docs/ai-assistance/prompt-catalog/write-security-rules?utm_source=chatgpt.com "AI Prompt: Write Firebase Security Rules"
[7]: https://firebase.google.com/docs/storage/security/rules-conditions "Use conditions in Firebase Cloud Storage Security Rules  |  Cloud Storage for Firebase"
