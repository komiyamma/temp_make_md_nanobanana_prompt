# 第19章：テストが本体！EmulatorでRules単体テスト🧪🧯

この章はズバリ、**「Rulesを書いたら、必ず“通る✅/弾く❌”を自動テストで固定する」**回です🙂✨
Security Rules は“門番🚪”なので、ここが揺れると全てが危なくなります…！💥

（公式も **Emulator + `@firebase/rules-unit-testing`** での単体テストを強く推しています。認証状態（auth）を疑似的に作れるのが超重要ポイントです🤖🧠）([Firebase][1])

---

## この章でできるようになること✅

* Emulator 上で Rules を動かして、**ローカルで安全に**検証できる🧪
* **未ログイン / 一般ユーザー / admin** の3パターンをテストで固める👤👮‍♂️👑
* `get` と `list` の違いを、テストで“事故らない形”に固定する📄📚
* AI（Gemini CLI / Antigravity）に叩き台を作らせても、**最後は人間レビュー＆テストで勝つ**💪🤖✅ ([Firebase][2])

---

## 1) 今日の流れ（最短ルート）🗺️

1. Emulator を「テスト実行のたびに起動→テスト→終了」できる形にする🚀
2. `@firebase/rules-unit-testing` で **auth を偽装**してテストを書く🧪
3. **通るべき✅ / 弾くべき❌** をセットで増やす（TDDっぽく）🧠
4. AIに作らせるなら、**テストが先に赤→緑**になるよう誘導する🤖🟩

Emulator は `emulators:exec` を使うと、**起動→実行→終了**が一発でできます（CIにも相性◎）。([Firebase][3])

---

## 2) 手を動かす：Rulesテスト用の“最小セット”を作る🧰✨

## 2-1. `firebase.json` に Rules ファイルを必ず紐づける⚠️

ここ、事故ポイントです😇
**`firebase.json` に Rules のファイルパスが無いと、エミュレータが“開放ルール扱い”になりうる**ので、テストが意味を失います💥([Firebase][3])

例（雰囲気でOK。既にあるなら確認だけでOK）👇

```json
{
  "firestore": {
    "rules": "firestore.rules"
  },
  "emulators": {
    "firestore": {
      "port": 8080
    }
  }
}
```

※ポート 8080 はデフォルト想定です。変えてるならテスト側も合わせます🙂([Firebase][3])

---

## 2-2. Rulesテスト専用の小さなNodeプロジェクトを作る📦

React本体と分けると気持ちがラクです😌（例：`tools/rules-tests/`）

PowerShell で👇

```powershell
mkdir tools\rules-tests
cd tools\rules-tests
npm init -y
npm i -D vitest typescript @firebase/rules-unit-testing
npm i firebase
```

---

## 2-3. `package.json` にテストコマンドを足す▶️

```json
{
  "type": "module",
  "scripts": {
    "test:rules": "vitest run"
  }
}
```

---

## 2-4. TS最低設定（1枚だけ）🧩

`tools/rules-tests/tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ES2022",
    "moduleResolution": "Bundler",
    "strict": true,
    "types": ["vitest/globals"]
  }
}
```

---

## 3) サンプルRules（ロール制御 + owner）🛡️

今回はテストが主役なので、Rules は“題材”としてシンプルにします🙂
（`posts` コレクション：公開/非公開、owner、admin）

`firestore.rules`（プロジェクト側にあるものを想定。無ければこれでOK👇）

```
// firestore.rules
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    function signedIn() { return request.auth != null; }
    function isAdmin() { return signedIn() && request.auth.token.admin == true; }
    function isOwner() { return signedIn() && request.auth.uid == resource.data.ownerUid; }

    function isCreatingOwnPost() {
      return signedIn()
        && request.resource.data.ownerUid == request.auth.uid;
    }

    function validTitle() {
      return request.resource.data.title is string
        && request.resource.data.title.size() >= 1
        && request.resource.data.title.size() <= 50;
    }

    match /posts/{postId} {
      // 1件取得は「公開 or 本人 or admin」
      allow get: if resource.data.isPublic == true || isOwner() || isAdmin();

      // 一覧は「adminのみ」（list事故をテストで防ぐ！）
      allow list: if isAdmin();

      // 作成は「本人のownerUid + title検証」
      allow create: if isCreatingOwnPost() && validTitle();

      // 更新/削除は「本人 or admin」
      allow update, delete: if isOwner() || isAdmin();
    }
  }
}
```

---

## 4) テストを書く（通る✅/弾く❌ をペアで）🧪✨

`tools/rules-tests/tests/posts.rules.test.ts`

```ts
import { readFileSync } from "node:fs";
import { beforeAll, afterAll, beforeEach, describe, it, expect } from "vitest";

import {
  initializeTestEnvironment,
  assertFails,
  assertSucceeds,
} from "@firebase/rules-unit-testing";

import {
  doc,
  setDoc,
  getDoc,
  getDocs,
  collection,
  query,
} from "firebase/firestore";

const PROJECT_ID = "rules-demo"; // 何でもOK（本番と違う名前がおすすめ）

let testEnv: Awaited<ReturnType<typeof initializeTestEnvironment>>;

beforeAll(async () => {
  testEnv = await initializeTestEnvironment({
    projectId: PROJECT_ID,
    firestore: {
      host: "127.0.0.1",
      port: 8080,
      rules: readFileSync("../../firestore.rules", "utf8"), // ←パスは自分の構成に合わせてね
    },
  });
});

afterAll(async () => {
  await testEnv.cleanup();
});

beforeEach(async () => {
  // 毎回まっさらにして、テストが影響し合わないようにする🧼
  await testEnv.clearFirestore();

  // ルール無視で初期データ投入（Arrange）
  await testEnv.withSecurityRulesDisabled(async (context) => {
    const db = context.firestore();

    await setDoc(doc(db, "posts/public1"), {
      ownerUid: "alice",
      title: "Hello",
      isPublic: true,
    });

    await setDoc(doc(db, "posts/private1"), {
      ownerUid: "alice",
      title: "Secret",
      isPublic: false,
    });
  });
});

describe("posts rules", () => {
  it("未ログインは公開だけ読める✅", async () => {
    const ctx = testEnv.unauthenticatedContext();
    const db = ctx.firestore();

    await assertSucceeds(getDoc(doc(db, "posts/public1")));
  });

  it("未ログインは非公開は読めない❌", async () => {
    const ctx = testEnv.unauthenticatedContext();
    const db = ctx.firestore();

    await assertFails(getDoc(doc(db, "posts/private1")));
  });

  it("本人(alice)は自分の非公開を読める✅", async () => {
    const ctx = testEnv.authenticatedContext("alice");
    const db = ctx.firestore();

    await assertSucceeds(getDoc(doc(db, "posts/private1")));
  });

  it("他人(bob)はaliceの非公開を読めない❌", async () => {
    const ctx = testEnv.authenticatedContext("bob");
    const db = ctx.firestore();

    await assertFails(getDoc(doc(db, "posts/private1")));
  });

  it("一覧(list)はadminだけ✅ / 一般は❌", async () => {
    const adminCtx = testEnv.authenticatedContext("root", { admin: true });
    const userCtx = testEnv.authenticatedContext("alice");

    const adminDb = adminCtx.firestore();
    const userDb = userCtx.firestore();

    await assertSucceeds(getDocs(query(collection(adminDb, "posts"))));
    await assertFails(getDocs(query(collection(userDb, "posts"))));
  });

  it("作成(create)：本人ownerUid + title OKなら✅", async () => {
    const ctx = testEnv.authenticatedContext("alice");
    const db = ctx.firestore();

    await assertSucceeds(
      setDoc(doc(db, "posts/new1"), {
        ownerUid: "alice",
        title: "New Post",
        isPublic: false,
      })
    );
  });

  it("作成(create)：ownerUidが本人と違うなら❌", async () => {
    const ctx = testEnv.authenticatedContext("alice");
    const db = ctx.firestore();

    await assertFails(
      setDoc(doc(db, "posts/bad1"), {
        ownerUid: "bob",
        title: "Hacked",
        isPublic: false,
      })
    );
  });

  it("作成(create)：title長すぎは❌", async () => {
    const ctx = testEnv.authenticatedContext("alice");
    const db = ctx.firestore();

    await assertFails(
      setDoc(doc(db, "posts/bad2"), {
        ownerUid: "alice",
        title: "x".repeat(51),
        isPublic: false,
      })
    );
  });
});
```

ポイントまとめ👇😊

* **`assertSucceeds` と `assertFails` は必ずセット**にする（片方だけだと穴が空く🕳️）
* データ投入は **`withSecurityRulesDisabled`** でやる（テスト準備のための“神の手”👐）
* `get` と `list` は別世界なので、**必ず両方テスト**する📄📚

（`@firebase/rules-unit-testing` が auth モックやデータ消去をサポートするのがキモです。）([Firebase][1])

---

## 5) 実行する🏃‍♂️💨（毎回安全に：`emulators:exec` 推奨）

エミュレータを起動しっぱなしにしなくてOK！✨

プロジェクトルート（`firebase.json` がある場所）で👇

```powershell
firebase emulators:exec --only firestore "npm --prefix tools/rules-tests run test:rules"
```

これで👇

* Firestore Emulator 起動🚀
* テスト実行🧪
* 終わったら自動で終了🛑

という流れになります。公式もこの使い方を案内しています。([Firebase][3])

---

## 6) よくある落とし穴（ここだけ見ればだいたい直る😇）🧯

## 落とし穴A：テストが全部通るのに、なんか怖い…

→ `firebase.json` の `firestore.rules` が抜けてる/パス違いの可能性大です⚠️
エミュレータが Rules を読めてないと“開放扱い”になりうるので、まずここ確認！([Firebase][3])

## 落とし穴B：Admin SDK で試したら Rules が効かない！

→ それ正常です🙂
**サーバー用ライブラリ（Admin/Server）は Rules をバイパス**するので、サーバー側は IAM など別の守りが必要です。([Firebase][3])

---

## 7) AIで加速する（ただし“テストが王様”👑）🤖✅

## 7-1. Gemini CLI：Rulesとテストを“自動で叩き台生成”🧠⚡

Firebase の AI プロンプトは **Gemini CLI 拡張**から使えて、
**Rules とテストの雛形を生成 → テスト実行結果を見て修正 → デプロイ**までの導線が用意されています。([Firebase][2])

公式手順の要点だけ抜くと👇

* 拡張を入れる
* Gemini CLI を起動
* `/firestore:generate_security_rules` を実行
* `firestore.rules` と、テスト用の `security_rules_test_firestore` ディレクトリが生成される

…という流れです。([Firebase][2])

💡注意：コンソール内の “Gemini in Firebase” は Rules 生成に対応してない、という制限も明記されています。([Firebase][2])

---

## 7-2. Antigravity：MCPで「プロジェクトを見ながら」整備🧰✨

Antigravity 側に **Firebase MCP server** を追加して、エージェントに
「Rulesのテストを増やして」「この失敗の理由を説明して」みたいに頼む使い方が紹介されています。([The Firebase Blog][4])

おすすめの頼み方（例）🙂

* 「posts の `list` は admin のみ。一般ユーザーの list を弾くテストを追加して」
* 「title検証（1〜50文字）の境界値テスト（0,1,50,51）を作って」
* 「この失敗ログから、Rules側の原因候補を3つ出して」

---

## 8) ミニ課題🎯（10〜20分）

次の3つを“テスト追加だけで”完成させてください🙂✨

1. **境界値テスト**を追加（title：0/1/50/51）🔤
2. **adminは非公開を誰のでもgetできる✅** を追加👑
3. **updateは owner/admin だけ✅** を追加（bob が alice の post を update しようとして ❌）🛡️

---

## 9) チェック✅（できたら勝ち！🎉）

* [ ] `emulators:exec` で **毎回まっさらから**テストが走る
* [ ] 未ログイン / user / admin の3者テストがある
* [ ] `get` と `list` が両方テストされてる
* [ ] “通る✅”と“弾く❌”がペアで増やせる
* [ ] AIでRulesを直したら、テストも同時に増やす癖がついた🤖✅

---

## おまけ：サーバー側（Admin SDK）を絡める時のバージョン感🧾

（この章の主役は Rules テストだけど、ロール付与などで Admin SDK を触るなら目安として）

* Functions の Node は **20 / 22 がフルサポート**、18は非推奨扱いの流れです。([Firebase][5])
* Admin SDK（.NET）は **.NET 8 以上推奨**（6/7 非推奨）。([Firebase][6])
* Admin SDK（Python）は **Python 3.10 以上推奨**（3.9 非推奨）。([Firebase][7])

---

次の第20章は「AIでRules作成を加速（でも必ず人間レビュー）」なので、今日作ったテスト一式が、そのまま“安全ブレーキ🧯”として超活躍します🙂✨

[1]: https://firebase.google.com/docs/rules/unit-tests "Build unit tests  |  Firebase Security Rules"
[2]: https://firebase.google.com/docs/ai-assistance/prompt-catalog/write-security-rules "AI Prompt: Write Firebase Security Rules  |  Develop with AI assistance"
[3]: https://firebase.google.com/docs/firestore/security/test-rules-emulator "Test your Cloud Firestore Security Rules  |  Firebase"
[4]: https://firebase.blog/posts/2025/11/firebase-mcp-and-antigravity "Antigravity and Firebase MCP accelerate app development"
[5]: https://firebase.google.com/docs/functions/get-started?utm_source=chatgpt.com "Get started: write, test, and deploy your first functions - Firebase"
[6]: https://firebase.google.com/support/release-notes/admin/dotnet?utm_source=chatgpt.com "Firebase Admin .NET SDK Release Notes"
[7]: https://firebase.google.com/support/release-notes/admin/python?utm_source=chatgpt.com "Firebase Admin Python SDK Release Notes - Google"
