# 第3章：Rulesの管理とデプロイの基本（Console vs CLI）🧰🛡️

この章は「**ルール運用で事故らない型**」を作る回だよ🙂✨
Security Rulesって、内容そのものも大事だけど……**管理とデプロイ方法**がグダると一瞬で事故る😱💥（“昨日コンソールで直したのに、CLIで上書きされた！”とか）

---

## 読む📖：Console編集とCLI編集、どっちが正解？🤔

## 1) Console（Web画面）で編集するメリット / 罠 🖥️🧨

![Console vs CLI Conflict (Data Overwrite Risk)](./picture/firebase_security_role_ts_study_003_01_console_cli_conflict.png)

**メリット**

* ブラウザでサッと直せる🙆‍♀️
* その場で簡単な動作チェック（Playground）もしやすい🧪✨ ([Firebase][1])

**罠（超重要）**

* **CLIでデプロイすると、ローカルのrulesがConsoleの既存ルールを上書き**する⚠️
  → Consoleで直した内容が、次のCLIデプロイで消える事故が起きがち😇 ([Firebase][1])
* Consoleは（少なくとも現時点では）**FirestoreのデフォルトDBへのデプロイが中心**で、複数DB運用だとCLIが必要になるケースがあるよ🧩 ([Firebase][1])

## 2) CLI（ローカルファイル）で管理するメリット / 注意点 💻🧯

![CLI & Git as Source of Truth](./picture/firebase_security_role_ts_study_003_02_cli_source_of_truth.png)

**メリット（こっちが“守りの中心”）**

* `firestore.rules` をファイルとして管理できる📄✅
* Gitで履歴が残る（いつ・誰が・何を変えたか）📌
* 自動テストやCIにも繋げやすい🤖🧪

**注意点**

* `firebase init` をやり直すと、`firebase.json` の該当セクションが**初期設定に戻る（上書き）**ことがある⚠️ ([Firebase][2])
* デプロイ対象を間違えると大惨事なので、**部分デプロイ（--only）**を基本にするのが安全🚦 ([Firebase][1])

---

## 手を動かす🧑‍💻：Windowsで「安全なルール運用セット」を作る🧯✨

## 0) 今日のゴール🎯

* ルールを **ファイルで管理**できる
* **最小のコマンド**で **安全にデプロイ**できる
* 「上書き事故」を **仕組みで防ぐ**

---

## 1) まずはCLI準備（Windows）🧰

PowerShellでもOK👌

```bash
npm install -g firebase-tools
firebase login
```

（CLI自体は “プロジェクトの設定ファイルを見てデプロイする道具” ってイメージでOK🙂）([Firebase][3])

---

## 2) プロジェクトを初期化して、ルールをファイル管理にする📁✨

プロジェクトのルートで初期化（対話形式でFirestoreなどを選ぶ）：

```bash
firebase init
```

初期化が済むと、だいたいこのへんが増えるよ👇

![Firebase Init Generated Files](./picture/firebase_security_role_ts_study_003_03_firebase_init_files.png)

* `firebase.json`（何をデプロイするかの設計図🗺️）
* `firestore.rules`（ルール本体🛡️）
* `firestore.indexes.json`（インデックス設定📌：今回は脇役） ([Firebase][2])

---

## 3) `firebase.json` を理解する（ここが事故防止の心臓❤️）

![Firebase JSON Mapping to Rules](./picture/firebase_security_role_ts_study_003_04_firebase_json_mapping.png)

`firebase.json` は「デプロイ対象を決める」ファイル。Firestoreだと最低限こうなる👇 ([Firebase][2])

```json
{
  "firestore": {
    "rules": "firestore.rules",
    "indexes": "firestore.indexes.json"
  }
}
```

ポイントはこれ👇

* **CLIはこの設定を見て**「どのrulesファイルをデプロイするか」決める
* だから **Consoleで直したルールがここに反映されてない**と、次のデプロイで上書き事故💥 ([Firebase][1])

---

## 4) まず覚えるべき“安全デプロイ”コマンド3つ🧯

![Deployment Command Scope](./picture/firebase_security_role_ts_study_003_05_deploy_command_scope.png)

## A. Firestore Rulesだけデプロイ（基本これ）🛡️

```bash
firebase deploy --only firestore:rules
```

→ `firebase.json` に設定された **すべてのDB分のRules**をデプロイする動きだよ📦 ([Firebase][1])

## B. Firestore（Rules＋Indexes）まとめてデプロイ📦

```bash
firebase deploy --only firestore
```

→ Firestoreの **RulesとIndexes** をまとめて出す（設定された全DBぶん） ([Firebase][2])

## C. 特定のDBだけデプロイ（複数DBのとき便利）🎯

```bash
firebase deploy --only firestore:<databaseId>
```

→ `<databaseId>` は `firebase.json` 側の設定と対応するよ ([Firebase][1])

---

## 5) 複数DBを使うときの `firebase.json`（超ざっくり最重要形）🧩

![Multiple Database Configuration](./picture/firebase_security_role_ts_study_003_06_multi_db_config.png)

Firestoreが複数DBのときは、`firestore` を **配列**にしてDBごとにrules/indexesを紐づける👇 ([Firebase][2])

```json
{
  "firestore": [
    {
      "database": "(default)",
      "rules": "firestore.default.rules",
      "indexes": "firestore.default.indexes.json"
    },
    {
      "database": "ecommerce",
      "rules": "firestore.ecommerce.rules",
      "indexes": "firestore.ecommerce.indexes.json"
    }
  ]
}
```

ここまでやると、DBごとにルールを分けられて「運用が現実的」になる🙂👍 ([Firebase][2])

---

## 事故を防ぐ“運用ルール”✅（ここだけ守ればかなり堅い）

## ✅ ルール運用の鉄則3つ🛡️

![Safe Rules Workflow](./picture/firebase_security_role_ts_study_003_07_safe_workflow.png)

1. **ソース・オブ・トゥルースはローカル（Git）**に寄せる📌
2. Consoleで一時修正したら、**必ずローカルへ同期（コピペでもOK）**してから次のデプロイ
3. デプロイは原則、**`--only firestore:rules`**（慣れるまで全部デプロイしない） ([Firebase][1])

## ✅ よくある地雷💣

* 「Consoleで直した！」→ **CLIで上書き**😇 ([Firebase][1])
* `firebase init` をやり直して **`firebase.json` が初期化される**😱 ([Firebase][2])

---

## AI活用🤖✨：Rules作成〜テスト〜デプロイを速くする（でも最後は人間が決める🧑‍⚖️）

## 1) Gemini CLI（Firebase拡張）で「Rules＋テスト」の叩き台を作る🧪

公式の流れとして、Firebase拡張を入れて… ([Firebase][4])

```bash
gemini extensions install https://github.com/gemini-cli-extensions/firebase
gemini
```

起動後に、Firestore向け生成コマンドを実行👇

* `/firestore:generate_security_rules`

すると、`firestore.rules` と、テスト用のディレクトリ（Node.jsプロジェクト）が生成されるよ🛠️🧪 ([Firebase][4])

しかもこれ、**最小権限**の考え方で叩き台を作りつつ、弱点を探す試行も含めた設計になってる（便利だけど過信NG）🙅‍♀️ ([Firebase][4])

> 重要：新しい機能やパスを追加したら、AIプロンプトを再実行するか手でルール更新が必要。放置すると「穴」か「機能が動かない」になる😱 ([Firebase][4])

さらに重要：**Firebaseコンソール内の「Gemini in Firebase」は、この用途（Rules生成）には対応してない**ので、CLI側でやるのが前提だよ⚠️ ([Firebase][4])

## 2) Antigravity × Firebase MCP で「プロジェクトを見ながら相談」🧠

Antigravityでは、MCP Servers から Firebase を入れる導線が用意されてるよ🙂 ([Firebase][5])
これで「今のプロジェクト構成を前提に、どこにルールを書くべき？」みたいな相談がしやすくなる👍

---

## ミニ課題🎯（10分）

1. `firebase.json` に `firestore.rules` が紐づいてるのを確認✅
2. `firestore.rules` の先頭にコメントで「自分の運用メモ」を1行入れる📝

   * 例：「Consoleで直したら必ずここに反映！」
3. `firebase deploy --only firestore:rules` を **実行する前に**、自分に質問👇

   * 「今デプロイしたいのは本当にこのプロジェクト？」
   * 「上書きして困るConsole修正はない？」

（実デプロイまでやるなら、まずは開発用プロジェクトでね🧯）

---

## チェック✅（ここまでできた？）

* [ ] 「Console修正がCLIで消える」理由を説明できる🙂 ([Firebase][1])
* [ ] `firebase.json` が“デプロイ設計図”だと分かった🗺️ ([Firebase][2])
* [ ] `firebase deploy --only firestore:rules` の意味が言える🛡️ ([Firebase][1])
* [ ] 複数DBのとき `firebase.json` が配列になるのを理解した🧩 ([Firebase][2])
* [ ] Gemini CLI / Antigravity でルール作成を加速できるイメージが湧いた🤖✨ ([Firebase][4])

---

次の章（第4章）では、いよいよ **`match` と `allow` の読み書き**に入って「最小のルールを自分の手で書ける」状態にするよ✍️😊

[1]: https://firebase.google.com/docs/rules/manage-deploy "Manage and deploy Firebase Security Rules"
[2]: https://firebase.google.com/docs/cli "Firebase CLI reference  |  Firebase Documentation"
[3]: https://firebase.google.com/docs/functions/local-emulator?utm_source=chatgpt.com "Run functions locally | Cloud Functions for Firebase - Google"
[4]: https://firebase.google.com/docs/ai-assistance/prompt-catalog/write-security-rules "AI Prompt: Write Firebase Security Rules  |  Develop with AI assistance"
[5]: https://firebase.google.com/docs/ai-assistance/mcp-server "Firebase MCP server  |  Develop with AI assistance"
