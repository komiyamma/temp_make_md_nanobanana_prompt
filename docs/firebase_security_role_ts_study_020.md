# 第20章：AIでRules作成を加速（でも必ず人間レビュー）🤖✅

この章のゴールはこれ👇✨
**AIに「Rules＋テストの叩き台」を作らせつつ、最終的な安全性は“人間のチェック”と“自動テスト”で担保できる**ようになることです🛡️🧪

---

## 1) まず大事な前提：AIが得意なこと／苦手なこと 🤝😵‍💫

## AIが得意👏

* ルールの雛形づくり（関数化、構造整理）🧩
* ありがちな穴（list丸見え、role書き換え等）を洗い出す視点の提示🔍
* **Rulesとテストをセットで生成**する叩き台づくり🧪

FirebaseのAI支援は、Firestore/Storage向けのRules生成に特化したプロンプトが用意されていて、Gemini CLI の Firebase 拡張から **Rulesとテストを作る流れ**が案内されています。さらに、ソースコード解析でスキーマやアクセスパターンを推測し、反復的な“攻撃シミュレーション”的アプローチで弱点を探そうとします。([Firebase][1])

## AIが苦手😇（ここを人間が守る）

* 「あなたのアプリの本当の要件」までは知らない（どこまで公開していいか等）🌀
* ルールが“動く”＝“安全”じゃない（穴があっても動いちゃう）😱
* 例外ケース（BANユーザー、退会、管理者の委任など）を漏らしがち💣

---

## 2) AIに渡す“材料”を用意しよう 🧠📦（これが8割）

AIにいきなり「Rules書いて」だと、だいたい雑になります😂
先にこの4点をメモにして渡すと精度が跳ねます⬆️✨

## (A) コレクション一覧（何がどこにある？）🗂️

例：

* `users/{uid}`：プロフィール
* `adminOnlyLogs/{id}`：管理者だけ読む/書くログ
* `posts/{id}`：公開記事（下書きは別管理 など）

## (B) ロール定義（増やしすぎない）🎭

* user：基本
* admin：管理画面の操作ができる

## (C) 操作表（誰が何できる？）📝

* `users/{uid}`：本人は read/update、他人は不可、adminは read 可
* `adminOnlyLogs`：adminだけ read/write
* `posts`：公開は list/get OK、下書きは本人だけ…など

## (D) “危険フィールド”の宣言 ☠️

* `role`, `isAdmin`, `status`, `plan`, `billing` みたいな **権限や課金に関わる項目はクライアントから変更不可**🚫

---

## 3) Gemini CLI（Firebase拡張）で叩き台を作る 🧰🤖

Firebaseには **Gemini CLI 用の Firebase 拡張**があり、ターミナルでFirebase向けのAI支援を扱えます。([Firebase][2])
さらに、Rules生成用の“Write security rules”プロンプトが用意されていて、Firestore/Storage向けのRules＋テストを作る導線があります。([Firebase][1])

## 例：AIに投げる指示（コピペ用）📋✨

（※あなたの実データ名に置き換えてね）

```text
あなたはFirebase Security Rulesの専門家です。
以下の要件で Cloud Firestore の Security Rules を作ってください。

【コレクション】
- users/{uid}: プロフィール
- adminOnlyLogs/{id}: 管理者専用ログ
- posts/{id}: 公開記事

【ロール】
- admin: request.auth.token.admin == true
- user: 通常ユーザー

【要件】
1) users/{uid}
- read: 本人のみ（adminはread可）
- update: 本人のみ
- updateで書き換え可能なキーは displayName と updatedAt のみ
- displayName は 1〜20文字
- create/deleteは禁止

2) adminOnlyLogs/{id}
- read/write: adminのみ

3) posts/{id}
- public == true のものは誰でもget/list可
- public == false は作成者(uid)のみget可、list不可
- create/update/delete はログイン必須で、作成者のみ（adminは全操作可）

さらに、@firebase/rules-unit-testing（v9想定）で
「通るべき✅」「落ちるべき❌」の単体テストも同時に作ってください。
```

🔎 このプロンプトの“狙い”は、「get と list を分ける」「更新可能キーのホワイトリスト」「admin領域の隔離」をAIに強制することです🛡️✨

---

## 4) Antigravity + Firebase MCP で“会話しながら直す” 🧑‍💻🤖💬

Antigravity には Firebase MCP server を追加でき、エージェントがFirebase作業を手伝いやすくなります。導入手順として、AntigravityのAgent画面から **MCP servers → Firebase → install** の流れが案内されています。([The Firebase Blog][3])

ここで便利なのが👇

* 「いまのRulesを読んで、危ないところだけ直して」みたいな **レビュー＆修正の往復**が速い⚡
* “要件メモ”を会話で育てながら、ルールの責務を固められる🧠✨

さらに、Gemini CLI拡張（コミュニティ/関連実装）側で **Rulesを取得/検証するツール**が用意されている例もあり、`get_rules` や `validate_rules` のような操作が紹介されています。([GitHub][4])
（※環境により使える/使えないはあるので、「取得できたらラッキー」くらいでOK👌）

---

## 5) 人間レビューの“鉄板チェックリスト” ✅🧑‍⚖️

AIが出したRulesを、これで殴ってください（重要）🥊😂

## 🚨即アウト（見つけたら赤信号）

* `allow read, write: if true;`（公開爆発💥）
* `allow list: if request.auth != null;`（ログインしてるだけで一覧丸見え😱）
* role系フィールドをクライアント更新OKにしてる（権限昇格👑💣）
* `get` と `list` を区別してない（“1件OK”のつもりが“全件OK”になりやすい）📖⚠️

## ✅OKに近い（ただし要件と照合）

* 「管理領域（adminOnly〜）」が **完全に隔離**されてる🚪🔐
* updateで **書いていいキーだけ許可**（ホワイトリスト）📝
* `create / update / delete` が分離されてる✍️🧯
* `public==false` は **list不可**（検索でバレるのを防ぐ）🙈

---

## 6) “AIのRules”をテストで縛る 🧪🔒（ここが本番）

Firestore Rules は **エミュレータで単体テスト**できます。([Firebase][5])
そして「サーバー用ライブラリ（Server/Admin系）はRulesをバイパスする」ので、**クライアント経由の挙動をテストで固める**のが超大事です。([Firebase][6])

## 6-1) テストの実行コマンド（例）🏃‍♂️💨

（エミュレータ起動→テスト→終了をまとめてやるやつ）

```bash
firebase emulators:exec --only firestore "npm test"
```

## 6-2) テスト雛形（TypeScript / v9イメージ）🧪✨

（ざっくり雰囲気を掴む用。AIに「これをベースに増やして」って投げてもOK👌）

```ts
import { readFileSync } from "node:fs";
import { initializeTestEnvironment, assertFails, assertSucceeds } from "@firebase/rules-unit-testing";
import { doc, getDoc, setDoc, updateDoc } from "firebase/firestore";

let testEnv: any;

beforeAll(async () => {
  testEnv = await initializeTestEnvironment({
    projectId: "demo-rules-ch20",
    firestore: {
      rules: readFileSync("firestore.rules", "utf8"),
    },
  });

  // 初期データは「ルール無効化」で投入（テスト準備の定番）
  await testEnv.withSecurityRulesDisabled(async (ctx: any) => {
    const db = ctx.firestore();
    await setDoc(doc(db, "users/alice"), { displayName: "Alice", updatedAt: Date.now(), role: "user" });
    await setDoc(doc(db, "adminOnlyLogs/log1"), { message: "secret", createdAt: Date.now() });
  });
});

afterAll(async () => {
  await testEnv.cleanup();
});

test("未ログインは adminOnlyLogs を読めない❌", async () => {
  const db = testEnv.unauthenticatedContext().firestore();
  await assertFails(getDoc(doc(db, "adminOnlyLogs/log1")));
});

test("admin は adminOnlyLogs を読める✅", async () => {
  const db = testEnv.authenticatedContext("boss", { admin: true }).firestore();
  await assertSucceeds(getDoc(doc(db, "adminOnlyLogs/log1")));
});

test("本人は users/alice を更新できる（許可キーだけ）✅", async () => {
  const db = testEnv.authenticatedContext("alice", { admin: false }).firestore();
  await assertSucceeds(updateDoc(doc(db, "users/alice"), { displayName: "Alice2", updatedAt: Date.now() }));
});

test("本人でも role を書き換えようとしたら落ちる❌", async () => {
  const db = testEnv.authenticatedContext("alice", { admin: false }).firestore();
  await assertFails(updateDoc(doc(db, "users/alice"), { role: "admin" }));
});
```

💡コツはこれ👇

* **✅通るべき / ❌落ちるべき を必ずペアで書く**
* 「listが禁止されてるか」「updateで余計なキーが弾かれるか」を重点的に🧯
* AIがRulesを直すたびに、テストも一緒に更新（セット運用）🔁

---

## 7) Custom Claims（adminフラグ）をRulesで読むときの注意 🎫⚠️

admin判定は `request.auth.token` 経由でできます（公式にも案内あり）。([Firebase][7])
ただし実務でよくハマるのが👇😵

* admin付与後、クライアント側で **トークン更新が必要**（反映までラグ）
* だからテストでは、`authenticatedContext("boss", { admin: true })` のように **明示的にadminを付けた状態**で検証するのが安心🧪✨

---

## 8) ついでに：AIを使う開発の“安全運用”も決めよう 🔐🤖

Gemini CLIや拡張は強いけど、**ローカルでコマンドを動かす系**は安全策が大切です🧯
最近のガイドでも、セキュリティ観点での分析・レビュー用途が用意されています。([Google Codelabs][8])
また、過去にGemini CLIまわりで“危ない実行”につながり得る脆弱性が報告され、修正や明示的承認を強める対応が入った、という報道もあります。([IT Pro][9])

この章で決めるルールはシンプルでOK👇😊

* 🔑 **秘密情報（APIキー等）はAIに貼らない**
* 🧱 AIに「削除/公開/デプロイ」系を任せない（人が最後に実行）
* 👀 AIが出したRulesは、**必ずテストが通るまで信用しない**

---

## 9) バージョン目安メモ（この章で触れる範囲）🧾✨

* Functions（Node.jsランタイム）は **Node.js 20 / 22** がサポート、**18はdeprecated**。([Firebase][10])
* Admin SDK（ロール付与などの管理側）

  * .NET は **.NET 8以上推奨（6/7 deprecated）**。([Firebase][11])
  * Python は **Python 3.10以上推奨（3.9 deprecated）**。([Firebase][12])

---

## 10) ミニ課題（10〜20分）🎯🔥

## お題💡

**「adminOnlyLogs」を作って、AIにRules＋テストを作らせ、最後に人間レビューで仕上げる**🛡️🧪

## 手順（最短ルート）🏁

1. AIに要件を渡して `adminOnlyLogs` のRules＋テストの叩き台を作る🤖
2. 人間レビュー（チェックリスト）で穴を潰す🧑‍⚖️
3. `firebase emulators:exec --only firestore "npm test"` でテスト固定🧪
4. ✅/❌テストを1本ずつ追加して、ルール変更に強い状態にする💪

---

## 11) チェック（できた？）✅✨

* admin領域が一般ユーザーから **存在すら見えない**ようにできた？🙈
* `get` と `list` の扱い、ちゃんと意識できた？📖
* updateで **許可キー以外を弾く**テストがある？🧱
* ルールを変えたらテストが守ってくれる状態？🧪🛡️

---

次の章（第21章）は、この章で作った「AI＋レビュー＋テスト」の型をそのまま使って、**“管理画面専用コレクション”を完成品として仕上げる**流れになります👑✨

[1]: https://firebase.google.com/docs/ai-assistance/prompt-catalog/write-security-rules?utm_source=chatgpt.com "AI Prompt: Write Firebase Security Rules"
[2]: https://firebase.google.com/docs/ai-assistance/gcli-extension?utm_source=chatgpt.com "Firebase extension for the Gemini CLI"
[3]: https://firebase.blog/posts/2025/11/firebase-mcp-and-antigravity/?utm_source=chatgpt.com "Antigravity and Firebase MCP accelerate app development"
[4]: https://github.com/gemini-cli-extensions/firestore-native?utm_source=chatgpt.com "gemini-cli-extensions/firestore-native"
[5]: https://firebase.google.com/docs/rules/unit-tests?hl=ja&utm_source=chatgpt.com "単体テストを作成する | Firebase Security Rules - Google"
[6]: https://firebase.google.com/docs/firestore/security/test-rules-emulator?utm_source=chatgpt.com "Test your Cloud Firestore Security Rules - Firebase - Google"
[7]: https://firebase.google.com/docs/rules/basics?utm_source=chatgpt.com "Basic Security Rules - Firebase - Google"
[8]: https://codelabs.developers.google.com/gemini-cli-security-review?hl=en&utm_source=chatgpt.com "Use Gemini CLI Security Extension for GitHub PR reviews"
[9]: https://www.itpro.com/security/a-flaw-in-googles-new-gemini-cli-tool-couldve-allowed-hackers-to-exfiltrate-data?utm_source=chatgpt.com "A flaw in Google's new Gemini CLI tool could've allowed hackers to exfiltrate data"
[10]: https://firebase.google.com/docs/functions/manage-functions?utm_source=chatgpt.com "Manage functions | Cloud Functions for Firebase - Google"
[11]: https://firebase.google.com/support/release-notes/admin/dotnet?utm_source=chatgpt.com "Firebase Admin .NET SDK Release Notes"
[12]: https://firebase.google.com/support/release-notes/admin/python?utm_source=chatgpt.com "Firebase Admin Python SDK Release Notes - Google"
