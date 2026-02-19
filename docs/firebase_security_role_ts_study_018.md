# 第18章：よくある事故パターン集（教材で先に踏む😂💥）

この章は、「事故を教材内で先に踏んでおく」回です😇✨
本番で踏むと泣けるやつを、ここで笑いながら潰します🤣🛡️

---

## 0) まず“事故の共通原因”だけ押さえる🧠💡

![Read and Write Granularity Trap](./picture/firebase_security_role_ts_study_018_01_read_write_trap.png)

Firestore Rules の `allow read` / `allow write` は便利だけど、**広すぎる**のが罠です😱
`read` は **get と list** を含むし、`write` は **create / update / delete** を含みます。([Firebase][1])

つまり…

* 「1件だけ読ませたい」つもりで `allow read` 👉 **一覧まで読める**（=漏れる）😇
* 「更新だけOK」つもりで `allow write` 👉 **削除までOK**（=壊れる）😇

---

## 1) 事故パターン図鑑（見抜けるようになるやつ）📚👀

## 事故①：`allow read, write: if true;`（全開放）🚪💥

![Security Rule "if true"](./picture/firebase_security_role_ts_study_018_02_open_house.png)

**症状**：とりあえず動いた！→そのまま放置
**何がヤバい？**：世界中の誰でも読める/書ける😱
**直し方**：まず “全面deny” を置いて、必要な場所だけ開ける🔐

---

## 事故②：「list を許して丸見え」📜👁️

**症状**：「自分のデータだけ見せたい」つもり
**実際**：`list` が開いていて、条件が甘いと **他人のデータが出る**😱
**直し方（初心者に強い）**：**get と list を分ける**（list を閉じる or 公開専用コレクションを作る）([Firebase][1])

---

## 事故③：update で「所有者すり替え」🎭🪤

![Owner ID Swap Attack](./picture/firebase_security_role_ts_study_018_03_owner_swap.png)

**症状**：`request.resource.data.ownerId == request.auth.uid` で守ったつもり
**実際**：攻撃者が update 時に `ownerId` を自分に変えて通過する可能性💥
**直し方**：update では **resource（元データ）と request.resource（新データ）を比較**して“変更禁止”を入れる🔒

---

## 事故④：「危険フィールドを書ける」🧨📝

**症状**：`role` / `isAdmin` / `plan` / `price` みたいな大事項目をクライアントが自由に更新
**実際**：権限昇格・課金改ざん・管理者化👑😱
**直し方**：**書いていいキーだけ許可（allowlist）**＋危険キーは “絶対に変更不可”🛡️

---

## 事故⑤：「サーバーはRulesで守られてる」勘違い🧯🤯

![Admin SDK Bypass](./picture/firebase_security_role_ts_study_018_04_admin_bypass.png)

**症状**：「Admin SDK から叩く処理も Rules で制限されるっしょ」
**実際**：サーバー用ライブラリ（Admin/Server SDKなど）は **Rulesをバイパス**します。([Firebase][2])
**直し方**：サーバー側は **IAM** と “鍵の管理” が本体（Rulesとは別物）🔑

---

## 事故⑥：「Consoleで直したのに、CLIデプロイで戻る」🔁😵

![CLI Overwriting Console Edits](./picture/firebase_security_role_ts_study_018_05_cli_overwrite.png)

**症状**：Consoleで緊急修正→安心→次のデプロイで再発
**原因**：Firebase CLI でデプロイすると、**ローカルのルールがConsoleを上書き**します。([Firebase][3])
**直し方**：**ルールはリポジトリを正**にして、Consoleで直したら必ずファイルも反映＆コミット🧑‍⚖️✅

---

## 2) ハンズオン：事故ルールを“安全ルール”に直す🧑‍💻🛠️

ここでは、ありがちな3連コンボを直します😂💥
（例：`profiles` と `posts` がある想定でいきます📦）

## (A) 事故ルール例（わざと危ない）😈

```rules
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    match /{document=**} {
      // 💥とりあえず動かす用（絶対に本番に置かない）
      allow read, write: if true;
    }
  }
}
```

これが “事故①の王様” です👑💀
まずは **全面deny** に戻します👇

## (B) まず「全面deny」に戻す（事故を止血）🩹

```rules
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if false;
    }
  }
}
```

ここから「必要な場所だけ開ける」方式にします🔐✨

---

## 3) “安全な直し方テンプレ”を入れる（この章の核心）🧩🛡️

## 3-1) 署名系の関数（読みやすさUP）🙂

![Helper Functions in Rules](./picture/firebase_security_role_ts_study_018_06_function_stamp.png)

```rules
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    function signedIn() {
      return request.auth != null;
    }

    function isAdmin() {
      return signedIn() && request.auth.token.admin == true;
    }

    // 以降、必要なmatchだけ開ける
  }
}
```

ロール（admin）判定は `request.auth.token` を使うのが王道です👮‍♂️✨（前章の続き）

---

## 3-2) `profiles/{uid}`：get と list を分けて事故②を潰す📖🔒

```rules
match /profiles/{uid} {

  // ✅ 本人だけ 1件取得OK
  allow get: if signedIn() && request.auth.uid == uid;

  // ❌ 一覧は禁止（まずは事故を潰す）
  allow list: if false;

  // ✅ 作成/更新は本人だけ（＋入力検証は前章の内容を足す）
  allow create, update: if signedIn() && request.auth.uid == uid;

  // ❌ 削除は一旦禁止（必要になったら設計して開ける）
  allow delete: if false;
}
```

ポイント：**“read” を書かない**。get/list を分ける。これだけで漏れが激減します🧯✨([Firebase][1])

---

## 3-3) `posts/{postId}`：update の“所有者すり替え”事故③を潰す🎭🚫

```rules
match /posts/{postId} {

  // ✅ 公開投稿だけ読む（例）
  allow get: if resource.data.status == "public";

  // ❌ 一覧は一旦閉じる（安全第一）
  allow list: if false;

  // ✅ 作成：ownerId は本人固定
  allow create: if signedIn()
    && request.resource.data.ownerId == request.auth.uid;

  // ✅ 更新：元のownerIdと一致していること（すり替え防止）
  allow update: if signedIn()
    && resource.data.ownerId == request.auth.uid
    && request.resource.data.ownerId == resource.data.ownerId;

  // ✅ 削除：本人か管理者だけ（例）
  allow delete: if signedIn()
    && (resource.data.ownerId == request.auth.uid || isAdmin());
}
```

`resource`（元データ）と `request.resource`（新データ）を比べるのがコツです🧠✨

---

## 3-4) “危険フィールドを書ける”事故④を潰す（allowlist）🧨🔒

例えば posts に `isPinned`（管理者しか触れない）を入れたいとき…

```rules
function onlyAllowedKeys(data) {
  return data.keys().hasOnly([
    "ownerId", "title", "body", "status", "createdAt", "updatedAt"
  ]);
}

match /posts/{postId} {

  allow create: if signedIn()
    && onlyAllowedKeys(request.resource.data)
    && request.resource.data.ownerId == request.auth.uid;

  allow update: if signedIn()
    && onlyAllowedKeys(request.resource.data)
    && resource.data.ownerId == request.auth.uid
    && request.resource.data.ownerId == resource.data.ownerId;
}
```

これで、クライアント改造されても `isPinned` とか `role` とかを混ぜられなくなります🛡️✨

---

## 4) ルールは“テストが本体”🧪🧯（エミュレータで殴る）

Firestore Rules は、エミュレータで **通るべき✅ / 弾くべき❌**を自動テストできます。([Firebase][2])
テストは v9 のテストライブラリ推奨です（事故って本番触るのを避けやすい）。([Firebase][4])

## 実行の型（エミュレータ起動→テスト→自動終了）🏃‍♂️💨

```powershell
firebase emulators:exec --only firestore "npm test"
```

`emulators:exec` が便利です👍（起動しっぱなし事故を減らせる）([Firebase][2])

---

## 5) AIで“事故を見つける速度”を爆上げする🤖⚡（でも最後は人間チェック✅）

![AI Security Detective](./picture/firebase_security_role_ts_study_018_07_ai_detective.png)

## 5-1) Gemini CLI（Firebase拡張）の“Rules＋テスト下書き”を使う🧠📄

FirebaseのAI支援には、Rules作成向けのプロンプトが用意されていて、**Gemini CLI の Firebase拡張で Rules とテストを起こす**用途が想定されています。([Firebase][5])
※Realtime Database の Rules は対象外、など制限もあります。([Firebase][5])

## 5-2) Antigravity（Firebase MCP）で“いまのプロジェクト前提”でレビューさせる🧑‍⚖️🤖

Antigravity は Firebase MCP を入れると、エージェントが Firebase まわりの作業支援をしやすくなります。([Firebase][6])

---

## 5-3) 今日いちばん使えるAI指示文（コピペOK）📋✨

**① 事故検出（攻撃者ロール）😈**

* 「次の Firestore Rules を“攻撃者目線”でレビューして、データ漏えい・権限昇格・改ざんの可能性を箇条書きで出して。各項目に“修正案（Rulesコード）”もつけて。」

**② テスト設計（通る/弾く）🧪**

* 「このルールに対して、未ログイン/一般ユーザー/管理者の3種類で、通るべき✅と弾くべき❌のテストケースを10個作って。`@firebase/rules-unit-testing` の形式で。」

**③ 事故再発防止（運用）🔁**

* 「Console直し→CLIデプロイで戻る事故を防ぐ、チーム運用ルール（PRのチェック項目）を作って。」

AIは間違えるので、**最後に人が読むのが絶対**です🙏（Firebase側も注意喚起しています）([Firebase][7])

---

## 6) ミニ課題🎯（事故を1個選んで“再発防止メモ”を書く📝）

次のうち1つ選んで、**再発防止メモ（5行）**を書いてください🙂✨

* A：`allow read` を雑に書いて list が漏れた
* B：update で ownerId をすり替えられた
* C：Consoleで直したのにCLIで戻った
* D：サーバーがRulesで守られてると勘違いした（Admin SDK）

テンプレ👇

* 何が起きた？😱
* 原因は？🧩
* 直し方は？🛠️
* 予防策は？🔐
* 次回チェック項目は？✅

---

## 7) チェック✅（この章を終えた判定）

* `read/write` が広すぎることを説明できる？（get/list/create/update/delete）([Firebase][1])
* “list を開くのは慎重に”が腹落ちした？📜⚠️
* update のときに `resource` と `request.resource` を比べる理由を言える？🧠
* 「サーバーはRulesをバイパスしうる」を理解した？([Firebase][2])
* `emulators:exec` でテストを回す習慣、作れそう？([Firebase][2])

---

次の章（第19章）は、ここで作った “事故を潰すルール” を **テストでガチガチに固める回**です🧪🧱✨

[1]: https://firebase.google.com/docs/rules/rules-behavior?utm_source=chatgpt.com "How Security Rules work - Firebase - Google"
[2]: https://firebase.google.com/docs/firestore/security/test-rules-emulator "Test your Cloud Firestore Security Rules  |  Firebase"
[3]: https://firebase.google.com/docs/rules/manage-deploy?utm_source=chatgpt.com "Manage and deploy Firebase Security Rules - Google"
[4]: https://firebase.google.com/docs/rules/unit-tests?hl=ja "単体テストを作成する  |  Firebase Security Rules"
[5]: https://firebase.google.com/docs/ai-assistance/prompt-catalog/write-security-rules?utm_source=chatgpt.com "AI Prompt: Write Firebase Security Rules"
[6]: https://firebase.google.com/docs/ai-assistance/mcp-server?utm_source=chatgpt.com "Firebase MCP server | Develop with AI assistance - Google"
[7]: https://firebase.google.com/docs/ai-assistance/prompt-catalog?hl=ja&utm_source=chatgpt.com "Firebase の AI プロンプト カタログ | Develop with AI assistance"
