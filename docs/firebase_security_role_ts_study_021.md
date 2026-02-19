# 第21章：ミニ総合課題「管理画面だけ見えるコレクション」を完成させる！🧑‍💼🔐✨

この章は “総仕上げ” です🔥
**一般ユーザーには存在すら見えない🙈**、でも **管理者だけ読めて書ける👑** コレクションを作って、**Rules + Emulatorテスト + AI支援**まで一気に通します💪✨

---

## 1) 今日作る完成品（仕様）🎯

![Admin Only Collection](./picture/firebase_security_role_ts_study_021_01_black_box.png)

作るコレクション例👇

* コレクション名：`adminOnlyLogs`
* ドキュメント例：`adminOnlyLogs/{logId}`
* フィールド（この形だけ許可🧱）

  * `message`: string（1〜200文字）
  * `level`: `"info" | "warn" | "error"`
  * `createdAt`: timestamp

権限ルール（超重要🛡️）

* 未ログイン：**全部NG** ❌
* 一般ユーザー：**全部NG** ❌（存在も見えない）
* 管理者（adminクレーム持ち）：**read / create / update / delete 全部OK** ✅

この「管理者だけ」のログは、たとえば **AI生成の監査ログ**（生成結果のレビュー、危険判定、モデレーション結果、プロンプト改変の痕跡など）を入れる場所にピッタリです🤖📌

---

## 2) AIを先に味方につける（叩き台づくり）🤖⚡

![AI Drafting Rules](./picture/firebase_security_role_ts_study_021_02_ai_draft.png)

## Antigravity（Agent）でやるなら🏎️

**Firebase MCP server** は Antigravity と連携できて、開発を加速できます🚀（MCPサーバーの追加手順も紹介されています） ([The Firebase Blog][1])

> ただし！AIが作るRulesは「それっぽい事故」が混ざりがち😇
> **最終判断は人間レビュー✅** でいきましょう。

## Gemini CLIでやるなら🧰

Firebase公式の **「Security Rulesを書かせるプロンプト」**が用意されていて、**Gemini CLI の Firebase拡張**からRulesとテストの叩き台を作れます。 ([Firebase][2])
しかも “攻撃シミュレーションで脆弱性を探す” 方向も意識されています💥 ([Firebase][2])

ただし制約もあるよ👇

* Firestore / Storage向け（Realtime Databaseは対象外） ([Firebase][2])
* 1回実行で、**自動追従で更新されるわけじゃない**（機能追加したら手動更新が必要） ([Firebase][2])

## Gemini in Firebase（コンソール内AI）も便利😊

Rulesについて質問には答えられるけど、**コードベースにアクセスできないのでRules生成はできない**…という位置づけです。 ([Firebase][3])
→「理解」や「レビュー観点の相談」に使うと強いです🧠✨

---

## 3) 実装パート：Rulesを書こう！🛡️✍️

![Admin Gatekeeper](./picture/firebase_security_role_ts_study_021_03_admin_gate.png)

今回のキモはこれ👇
**request.auth.token.admin == true の人だけ通す**（＝RBACの最小形）👑

`firestore.rules` を作って、こう書きます👇（コピペOK）

```rules
rules_version = '2';

service cloud.firestore {
  match /databases/{database}/documents {

    function isSignedIn() {
      return request.auth != null;
    }

    function isAdmin() {
      // Custom Claims: { admin: true } を想定
      return isSignedIn() && request.auth.token.admin == true;
    }

    function isValidLogCreate() {
      return request.resource.data.keys().hasOnly(['message', 'level', 'createdAt'])
        && request.resource.data.message is string
        && request.resource.data.message.size() >= 1
        && request.resource.data.message.size() <= 200
        && request.resource.data.level in ['info', 'warn', 'error']
        && request.resource.data.createdAt is timestamp;
    }

    function isValidLogUpdate() {
      // createdAt は更新させない（改ざん防止🧯）
      return request.resource.data.keys().hasOnly(['message', 'level', 'createdAt'])
        && request.resource.data.createdAt == resource.data.createdAt
        && request.resource.data.message is string
        && request.resource.data.message.size() >= 1
        && request.resource.data.message.size() <= 200
        && request.resource.data.level in ['info', 'warn', 'error'];
    }

    match /adminOnlyLogs/{logId} {
      allow get, list: if isAdmin();
      allow create: if isAdmin() && isValidLogCreate();
      allow update: if isAdmin() && isValidLogUpdate();
      allow delete: if isAdmin();
    }
  }
}
```

---

## 4) Emulator準備：firebase.json（Rules読み込み設定）🧪⚙️

![Emulator Configuration](./picture/firebase_security_role_ts_study_021_04_emulator_config.png)

`firebase.json` に「どのRulesファイルを読むか」を書きます✍️
**エミュレータは firebase.json の rules 指定を最初に読みます**（これ大事！） ([Firebase][4])

```json
{
  "firestore": {
    "rules": "firestore.rules"
  },
  "emulators": {
    "firestore": { "port": 8080 },
    "ui": { "enabled": true, "port": 4000 }
  }
}
```

Firestore Emulator のデフォルトは **8080** です（覚えやすい！） ([Firebase][5])

---

## 5) テストが本体：Rules単体テストを書く🧪✅❌

![Role Testing](./picture/firebase_security_role_ts_study_021_05_role_masks.png)

公式は **@firebase/rules-unit-testing** を推してます（authの擬似再現ができるのが強い） ([Firebase][4])
最新版は npm 上で **5.0.0** が案内されています。 ([npm][6])

## 5-1) npmインストール（WindowsでOK）🪟📦

```bash
npm init -y
npm i -D vitest typescript @types/node
npm i -D firebase @firebase/rules-unit-testing
npm i -g firebase-tools
```

`package.json` の scripts（例）👇

```json
{
  "type": "module",
  "scripts": {
    "test": "vitest run",
    "test:emu": "firebase emulators:exec --only firestore \"npm test\""
  }
}
```

> PowerShell なら、ダブルクォートが面倒ならこうでもOK👇
> `firebase emulators:exec --only firestore 'npm test'`
> （公式も “起動→テスト→終了” を `emulators:exec` でやるのを推してます） ([Firebase][7])

## 5-2) テストコード（Vitest + rules-unit-testing）🧪

`tests/rules.test.ts` を作ります👇

```ts
import { beforeAll, afterAll, beforeEach, describe, it, expect } from "vitest";
import fs from "node:fs";

import {
  initializeTestEnvironment,
  assertFails,
  assertSucceeds,
} from "@firebase/rules-unit-testing";

import {
  doc,
  getDoc,
  setDoc,
  updateDoc,
  deleteDoc,
} from "firebase/firestore";

let testEnv: Awaited<ReturnType<typeof initializeTestEnvironment>>;

const PROJECT_ID = "demo-rbac-admin-only";

const goodLog = {
  message: "AI生成の監査ログ：安全✅",
  level: "info",
  createdAt: new Date(), // テストでは Date でOK（Firestore SDKがTimestampに変換）
};

beforeAll(async () => {
  testEnv = await initializeTestEnvironment({
    projectId: PROJECT_ID,
    firestore: {
      rules: fs.readFileSync("firestore.rules", "utf8"),
    },
  });
});

afterAll(async () => {
  await testEnv.cleanup();
});

beforeEach(async () => {
  // テスト間のデータ持ち越しを消す🧹
  await testEnv.clearFirestore();
});

function ctxAdmin() {
  return testEnv.authenticatedContext("adminUid", { admin: true });
}
function ctxUser() {
  return testEnv.authenticatedContext("userUid", { admin: false });
}
function ctxAnon() {
  return testEnv.unauthenticatedContext();
}

async function seedLog(id = "log1") {
  // ルール無視でデータ投入（公式推奨のやり方）🧯
  await testEnv.withSecurityRulesDisabled(async (ctx) => {
    await setDoc(doc(ctx.firestore(), "adminOnlyLogs", id), goodLog);
  });
}

describe("adminOnlyLogs (管理者だけアクセス可能)", () => {
  it("未ログインはgetできない🙈", async () => {
    await seedLog();
    const anonDb = ctxAnon().firestore();
    await assertFails(getDoc(doc(anonDb, "adminOnlyLogs", "log1")));
  });

  it("一般ユーザーはgetできない🙈", async () => {
    await seedLog();
    const userDb = ctxUser().firestore();
    await assertFails(getDoc(doc(userDb, "adminOnlyLogs", "log1")));
  });

  it("管理者はgetできる👑", async () => {
    await seedLog();
    const adminDb = ctxAdmin().firestore();
    await assertSucceeds(getDoc(doc(adminDb, "adminOnlyLogs", "log1")));
  });

  it("管理者はcreateできる✅", async () => {
    const adminDb = ctxAdmin().firestore();
    await assertSucceeds(setDoc(doc(adminDb, "adminOnlyLogs", "log2"), goodLog));
  });

  it("管理者でも余計なフィールドがあるとcreateできない🧨", async () => {
    const adminDb = ctxAdmin().firestore();
    await assertFails(
      setDoc(doc(adminDb, "adminOnlyLogs", "log3"), {
        ...goodLog,
        isAdmin: true, // ←こういう権限っぽいの混ぜられたら事故るので拒否
      })
    );
  });

  it("管理者はupdateできる（createdAtは変更NG）🧱", async () => {
    await seedLog("log4");

    const adminDb = ctxAdmin().firestore();
    const ref = doc(adminDb, "adminOnlyLogs", "log4");

    // createdAtを変えないupdateはOK
    await assertSucceeds(updateDoc(ref, { message: "更新OK！", level: "warn" }));

    // createdAtを変えるupdateはNG（改ざん防止）
    await assertFails(updateDoc(ref, { createdAt: new Date() }));
  });

  it("管理者はdeleteできる🗑️", async () => {
    await seedLog("log5");
    const adminDb = ctxAdmin().firestore();
    await assertSucceeds(deleteDoc(doc(adminDb, "adminOnlyLogs", "log5")));
  });
});
```

このテストの土台になってる API（`initializeTestEnvironment` / `authenticatedContext` / `withSecurityRulesDisabled` / `clearFirestore` など）は公式ドキュメントに載ってます。 ([Firebase][4])

---

## 6) 実行：エミュレータ起動→テスト→自動終了🧪🚀

![Test Execution](./picture/firebase_security_role_ts_study_021_06_test_run.png)

いちばんラクなのはこれ👇（推奨✨）

```bash
npm run test:emu
```

公式も「テストのためにエミュレータ起動→テスト→終了」を `emulators:exec` でやる流れを案内してます。 ([Firebase][7])

---

## 7) デプロイ（本番反映）🔥⚠️

![Deployment Overwrite Warning](./picture/firebase_security_role_ts_study_021_07_deploy_warning.png)

RulesをCLIでデプロイすると…
**コンソールで編集してた既存Rulesを上書き**します😱（運用事故ポイント！） ([Firebase][8])

デプロイ例👇

```bash
firebase deploy --only firestore:rules
```

---

## 8) ありがち事故チェック（この章の“落とし穴”）🕳️😇

* `allow read, write: if true;` を一瞬でも置く（公開事故の王👑💥）
* `list` を気軽に許して全件丸見え（検索機能が漏洩装置に😇）
* “サーバーはRulesで守られる” と誤解する
  → **サーバー用クライアントライブラリはRulesをバイパス**するので、別途IAMなどが必要です。 ([Firebase][7])
* AIが作ったRulesをノールックで採用
  → Gemini CLI拡張の例でも「AI生成は信用せず、人がレビューしてテスト実行してね」と明記されています。 ([GitHub][9])

---

## 9) ミニ課題（＋1で強くなる💪✨）🎯

できたらレベルアップ👇

1. `adminOnlyLogs` を **「作成だけOK / 更新と削除はNG」** にしてみる✍️
2. `message` に **禁止ワード**が入ったら拒否（例：URLっぽい文字列）🔍
3. `level == "error"` のときだけ `stack`（string）を追加で許可してみる🔥

---

## 10) 最終チェックリスト（合格ライン✅）🧾✨

* [ ] 未ログインが `adminOnlyLogs` を **get/list どっちも失敗**する🙈
* [ ] 一般ユーザーも同じく **get/list どっちも失敗**する🙈
* [ ] 管理者だけ **get/list/create/update/delete** が通る👑
* [ ] 余計なフィールド混入を **Rulesが拒否**する🧨
* [ ] `npm run test:emu` で毎回同じ結果になる🧪
* [ ] CLIデプロイが上書きになるのを理解して運用できる🧯 ([Firebase][8])

---

必要なら次は、この完成品に **「管理者の付与（Custom Claims）」を安全に回す手順**（運用フロー：付与→トークン更新→監査ログ）も、同じノリで“手を動かす回”として作れます👑🔐🤖

[1]: https://firebase.blog/posts/2025/11/firebase-mcp-and-antigravity/?utm_source=chatgpt.com "Antigravity and Firebase MCP accelerate app development"
[2]: https://firebase.google.com/docs/ai-assistance/prompt-catalog/write-security-rules?utm_source=chatgpt.com "AI Prompt: Write Firebase Security Rules"
[3]: https://firebase.google.com/docs/ai-assistance/gemini-in-firebase?utm_source=chatgpt.com "Gemini in Firebase - Google"
[4]: https://firebase.google.com/docs/rules/unit-tests?hl=ja "単体テストを作成する  |  Firebase Security Rules"
[5]: https://firebase.google.com/docs/emulator-suite/install_and_configure?utm_source=chatgpt.com "Install, configure and integrate Local Emulator Suite - Firebase"
[6]: https://www.npmjs.com/package/%40firebase/rules-unit-testing?utm_source=chatgpt.com "firebase/rules-unit-testing"
[7]: https://firebase.google.com/docs/firestore/security/test-rules-emulator?utm_source=chatgpt.com "Test your Cloud Firestore Security Rules - Firebase - Google"
[8]: https://firebase.google.com/docs/rules/manage-deploy?utm_source=chatgpt.com "Manage and deploy Firebase Security Rules - Google"
[9]: https://github.com/firebase/snippets-rules?utm_source=chatgpt.com "Snippets for security rules on firebase.google.com"
