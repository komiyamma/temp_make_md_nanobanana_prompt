# 第17章：Firestore内ロール管理パターン（やるなら注意点もセット）⚠️📦

この章はひとことで言うと👇
**「ロール（権限）を“Firestoreのドキュメント”として持つやり方」**を、事故らない形で理解して使えるようにする回です🛡️✨
（Custom Claimsの王道（第15〜16章）と比べて、**便利さの代わりに地雷が増える**ので、そこも含めてセットで行きます💣）

---

## 1) まず結論：Firestoreロール管理は“使いどころ”がある😼

Firestore内ロール管理が刺さるのは、だいたいこの2パターン👇

* **権限が頻繁に変わる**（今日だけモデレーター、明日解除…みたいな）🔁
* **「プロジェクト別」「グループ別」**のように、権限が“リソース単位”で違う🏷️

一方で、**「管理者 / 一般ユーザー」みたいな“全体ロール”**は、Custom Claimsの方が堅くて軽いことが多いです🎫🔐 ([Firebase][1])

---

## 2) Firestoreロール管理の代表3パターン 🧩

## パターンA：`roles/{uid}`（ユーザーごとのロール表）

例：`roles/abc123` に `{ admin: true, editor: false }` みたいに入れる。

* 👍 直感的で分かりやすい
* 👎 Rulesの中で `get()` / `exists()` 参照が増えがち（＝コスト＆制限に影響）([Firebase][2])

## パターンB：`projects/{projectId}/members/{uid}`（“所属”をドキュメントで表現）

例：メンバーであることを `exists(/projects/p1/members/abc123)` で判定。

* 👍 “プロジェクト単位”権限に強い
* 👍 ユーザー全体ロールより自然
* 👎 設計を雑にすると「membersを書き換えて昇格😱」が起きる

## パターンC：`groups/{groupId}` に `members: [uid...]`（配列で持つ）

* 👍 ルールは書きやすい
* 👎 人数が増えると地獄になりやすい（ドキュメントサイズ上限、更新競合、管理がつらい）
  なので初心者向けには「**Bが一番安全寄り**」でおすすめです🙂

---

## 3) ここが地雷：Firestoreロール管理の“事故ポイント集”💥

## 地雷①：ロール情報をクライアントに書かせる（即アウト）🙅‍♂️

ロールをFirestoreに置くなら、**ロールを更新する権限は超・限定**しないと詰みます😇
Rulesで「rolesは誰も書けない」または「管理者だけ」みたいに固定します。

## 地雷②：`get()` / `exists()` は“追加の読み取り課金”になる💸

Rules内で `get()` / `exists()` / `getAfter()` を使うと、**Rules評価のための追加Read**が発生します（拒否されても発生し得る）😱 ([Firebase][2])

## 地雷③：`get()` / `exists()` の呼び出し回数には上限がある🚧

1リクエストあたりの上限が決まってます👇

* 単一ドキュメント読み取り / クエリ：**10回**
* 複数ドキュメント読み取り / トランザクション / バッチ書き込み：**20回**（ただし各操作あたり10回の制限も意識） ([Firebase][3])

つまり「membersをシャーディングしていっぱい `exists()`」みたいなのは、割とすぐ限界に当たります😵

## 地雷④：サーバー側ライブラリはRulesをバイパスする🕳️

ロール更新をサーバーでやるのは正解なんだけど、**サーバー用ライブラリ（Admin/Server SDK）はRulesを通りません**。
なので「サーバー側の権限」はIAMなど別の守りが必要です🧯 ([Firebase][4])

---

## 4) ハンズオン：安全な “rolesドキュメント参照” を作る🧪🔥

今回は分かりやすい **パターンA（roles/{uid}）** で行きます。
（この作りを理解すると、Bにも応用できます🙂）

## 4-1) 目標 🎯

* `adminOnlyLogs/{logId}` は **adminだけ read/write OK** 👑
* `publicPosts/{postId}` は **ログインしてれば read OK**（書き込みは別条件でもOK）

---

## 5) ルール実装（テンプレ）🛡️

ポイントはこれ👇

* `roles/{uid}` 自体は **クライアントから読めなくてOK**（むしろ読ませない）🙈
* Rulesの中では `exists()` / `get()` で参照して判定する
* 失敗時に落ちないように `exists()` を先に置く

```rules
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    function signedIn() {
      return request.auth != null;
    }

    function roleDocPath(uid) {
      return /databases/$(database)/documents/roles/$(uid);
    }

    function isAdmin() {
      return signedIn()
        && exists(roleDocPath(request.auth.uid))
        && get(roleDocPath(request.auth.uid)).data.admin == true;
    }

    // 🔒 roles は “誰にも直接触らせない”
    match /roles/{uid} {
      allow read, write: if false;
    }

    // 👑 管理者だけ触れるログ
    match /adminOnlyLogs/{logId} {
      allow read, write: if isAdmin();
    }

    // 🙂 公開投稿：ログインしてれば読める（例）
    match /publicPosts/{postId} {
      allow read: if signedIn();
      allow write: if false; // ここはアプリ要件で調整してOK
    }
  }
}
```

`exists()` / `get()` は追加Readになり得る＆回数制限もあるので、**「isAdmin() を1回で済む形」に寄せる**のが大事です💡 ([Firebase][2])

---

## 6) テスト：Emulatorで“通る✅/弾く❌”を固定する🧪

Rulesは **テストが本体**です🙂
Firebase公式も、Emulatorでユニットテストを回す流れを強く推しています。([Firebase][5])

## 6-1) テスト用ライブラリ

`@firebase/rules-unit-testing` を使います（v9系のテストが推奨）([Firebase][6])
※最近の変更で **Nodeの最小バージョンが引き上げ**られているので、プロジェクトのNodeは新しめで👍 ([GitHub][7])

## 6-2) テストでやること（最小セット）

* ❌ 未ログイン：`adminOnlyLogs` は読めない
* ❌ 一般ユーザー：`adminOnlyLogs` は読めない
* ✅ admin：`adminOnlyLogs` を読める＆書ける

（※ admin判定のために `roles/{uid}` を **テスト側で事前に書いておく**）

---

## 7) AIで加速：Rules＆テストを“叩き台生成→人間が締める”🤖🧑‍⚖️

## 7-1) Gemini CLI / Antigravity で何ができる？⚡

* Firebase MCP server は、**Antigravity / Gemini CLI / Firebase Studio などのMCPクライアント**から使えます。([Firebase][8])
* Gemini CLIには **Firebase拡張**があり、Firebase向けの能力とプロンプト群が使えます。([Firebase][9])
* さらに「Write security rules」プロンプトは、**ソースコードやスキーマを解析してRulesとテストの叩き台を作り、攻撃シミュレーションで弱点を探す**方向の設計になっています（ただし制限もあるので過信はNG）([Firebase][10])

## 7-2) 使い方のコツ（事故らない線引き）🧠

AIにやらせるのは👇

* ルールの雛形（match構造、関数化、deny by default）
* テストケースの列挙（未ログイン/一般/admin、想定攻撃パターン）

人間が必ず握るのは👇

* **ロールの置き場所**（rolesなのかmembersなのか）
* **ロール更新の責任者**（誰が更新できるか）
* `get()` / `exists()` をどこまで許すか（コスト＆上限）([Firebase][3])

---

## 8) ミニ課題 🎯（10〜15分）

次の2択で、自分のアプリに寄せて考えてみてください🙂

1. **roles方式（A）**

* `roles/{uid}` に `{ admin: true }` を入れる設計にして、
  「rolesは誰もread/write不可」にした上で、`adminOnlyLogs` を守る🛡️

2. **members方式（B）**

* `projects/{projectId}/members/{uid}` を作る設計にして、
  「membersは本人が勝手に作れない」ようにする（ここが腕の見せ所🔥）

---

## 9) チェック✅（この章のゴール）

* `get()` / `exists()` が **追加課金＆回数制限**があるのを説明できる💸🚧 ([Firebase][2])
* 「rolesドキュメントをクライアントに書かせたら終わる」理由が言える😇
* Emulatorテストで、未ログイン/一般/admin の3者が **毎回同じ判定**になる🧪 ([Firebase][5])

---

## 10) おまけ：ロール更新をサーバーでやる時の“バージョン目安”🧾✨

ロール付与や更新はサーバー側でやるのが基本です（例：Admin SDKでCustom Claims付与、またはroles更新など）🎫

* Cloud Functions（Node）：Node.js **20 / 22** がサポート、18はdeprecated扱い ([Firebase][11])
* Admin SDK（Python）：Python **3.10+ 推奨（3.9はdeprecated）** ([Firebase][12])
* Admin SDK（.NET）：**.NET 8+ 推奨（6/7はdeprecated）** ([Firebase][12])

---

次の第18章は、この章で触れた地雷を「事故パターン集」としてまとめて、見た瞬間にツッコめる力を作っていきます😂💥

[1]: https://firebase.google.com/docs/auth/admin/custom-claims?utm_source=chatgpt.com "Control Access with Custom Claims and Security Rules"
[2]: https://firebase.google.com/docs/firestore/security/rules-conditions?utm_source=chatgpt.com "Writing conditions for Cloud Firestore Security Rules - Firebase"
[3]: https://firebase.google.com/docs/firestore/quotas?utm_source=chatgpt.com "Usage and limits | Firestore | Firebase - Google"
[4]: https://firebase.google.com/docs/firestore/security/test-rules-emulator?utm_source=chatgpt.com "Test your Cloud Firestore Security Rules - Firebase - Google"
[5]: https://firebase.google.com/docs/rules/unit-tests?utm_source=chatgpt.com "Build unit tests | Firebase Security Rules - Google"
[6]: https://firebase.google.com/docs/rules/unit-tests?hl=ja&utm_source=chatgpt.com "単体テストを作成する | Firebase Security Rules - Google"
[7]: https://github.com/firebase/firebase-js-sdk/blob/main/packages/rules-unit-testing/CHANGELOG.md?utm_source=chatgpt.com "firebase-js-sdk/packages/rules-unit-testing/CHANGELOG. ..."
[8]: https://firebase.google.com/docs/ai-assistance/mcp-server?utm_source=chatgpt.com "Firebase MCP server | Develop with AI assistance - Google"
[9]: https://firebase.google.com/docs/ai-assistance/gcli-extension?utm_source=chatgpt.com "Firebase extension for the Gemini CLI"
[10]: https://firebase.google.com/docs/ai-assistance/prompt-catalog/write-security-rules?utm_source=chatgpt.com "AI Prompt: Write Firebase Security Rules"
[11]: https://firebase.google.com/docs/functions/get-started?utm_source=chatgpt.com "Get started: write, test, and deploy your first functions - Firebase"
[12]: https://firebase.google.com/docs/admin/setup?utm_source=chatgpt.com "Add the Firebase Admin SDK to your server - Google"
