# 第05章：TypeScriptの基本構成（読みやすさ命）🧱

この章は、**Functions の TypeScript を「増えても破綻しない形」**にする回です🙂
HTTP / Firestore / スケジュールが混ざっても、**迷子にならない地図**を作ります🗺️

---

## 0) 先に結論：迷子にならない “3ルール” 🧭

1. **`src/index.ts` は「公開口」だけ**（中身は別ファイルへ）🚪
2. **種類ごとにフォルダ分け**（http / firestore / schedule）🧩
3. **共通処理は `lib/` に隔離**（初期化・ログ・バリデーション）🧰

これだけで、初心者でも壊しにくい構成になります😄👍

---

## 1) まずは “標準に寄せる” のが一番ラク 🧠

Firebase の TypeScript Functions は基本的に、**TS → JS にビルドしてからデプロイ**します。
「ビルドし忘れて `lib/index.js が無い`」みたいな事故を減らすために、**`predeploy` で `npm run build` が走る形**に寄せるのが安定です🧯 ([Firebase][1])

---

## 2) まず作るべきフォルダ構成（最小で強い）🏗️

Functions の中（`functions/`）は、こんな感じがおすすめです👇

```text
functions/
  package.json
  tsconfig.json
  .eslintrc.cjs   (または eslint.config.js)
  src/
    index.ts                 ← ここは「公開する関数のexport」だけ
    http/
      health.ts              ← HTTP関数（onRequestなど）
    firestore/
      onMessageCreated.ts    ← Firestoreトリガー
    schedule/
      dailyReport.ts         ← スケジュール関数
    lib/
      firebaseAdmin.ts       ← Admin初期化（1か所だけ！）
      log.ts                 ← ログの整形（後で運用が楽）
      validate.ts            ← 入力チェック（Zodなど）
    types/
      message.ts             ← 型（DBの形をここに集約）
    ai/
      genkit.ts              ← AIまわりの入口（後の章で育てる🔥）
```

ポイントはこれ👇

* **関数の種類（http/firestore/schedule）で分ける**と脳が疲れません🧠💤
* **共通処理（初期化・ログ・検証）を `lib/` に隔離**すると、後から伸びます📈
* **AI は “専用フォルダ” を先に切っておく**と、後で混ぜて地獄にならないです🤖🔥

---

## 3) `src/index.ts` は “薄く” する（最重要）🚪✨

`index.ts` に全部書くと、すぐカオス化します😇
ここは **「どの関数を公開するか」だけ**にしましょう！

```ts
// functions/src/index.ts
export { health } from "./http/health";
export { onMessageCreated } from "./firestore/onMessageCreated";
export { dailyReport } from "./schedule/dailyReport";
```

**これだけ**で OK 👍
中身は各ファイルへ分散です🧩

---

## 4) “共通の初期化” を 1か所にまとめる（Admin SDK）🧰

Firestore を触るトリガーや HTTP API が増えると、初期化をあちこちでやりがちです🙃
**初期化は 1ファイルに固定**が安全です✅

```ts
// functions/src/lib/firebaseAdmin.ts
import { initializeApp, getApps } from "firebase-admin/app";
import { getFirestore } from "firebase-admin/firestore";

export function getDb() {
  // 二重初期化防止（ローカル/ホットリロード/複数import対策）
  if (getApps().length === 0) initializeApp();
  return getFirestore();
}
```

---

## 5) ログは “後で助かる形” に揃える 🧯👀

運用すると「どこで失敗した？」が命になります。
いまのうちに “ログの出し方” を統一しておくと未来の自分が喜びます🥹✨

```ts
// functions/src/lib/log.ts
export function logInfo(message: string, data?: Record<string, unknown>) {
  console.log(JSON.stringify({ severity: "INFO", message, ...data }));
}

export function logError(message: string, data?: Record<string, unknown>) {
  console.error(JSON.stringify({ severity: "ERROR", message, ...data }));
}
```

---

## 6) HTTP / Firestore / Schedule を “別ファイルで” 書く（例）🧪

### 6-1) HTTP：`/health` 的なやつ🌐

```ts
// functions/src/http/health.ts
import { onRequest } from "firebase-functions/v2/https";

export const health = onRequest((req, res) => {
  res.status(200).json({ ok: true, ts: Date.now() });
});
```

### 6-2) Firestore：ドキュメント作成トリガー⚡

```ts
// functions/src/firestore/onMessageCreated.ts
import { onDocumentCreated } from "firebase-functions/v2/firestore";
import { getDb } from "../lib/firebaseAdmin";
import { logInfo } from "../lib/log";

export const onMessageCreated = onDocumentCreated("messages/{id}", async (event) => {
  const data = event.data?.data();
  if (!data) return;

  logInfo("message created", { id: event.params.id });

  // 例：加工結果を書き戻す（このへんは第11章で本格的にやる🔥）
  const db = getDb();
  await db.doc(`messages/${event.params.id}`).update({ touchedAt: Date.now() });
});
```

Firestore トリガーの種類（created/updated/written など）は公式の一覧を見ながら選ぶと迷いません👀 ([Firebase][2])

### 6-3) Schedule：毎朝のレポート⏰

（第14章で深掘りしますが、構造だけ先に作る😄）

```ts
// functions/src/schedule/dailyReport.ts
import { onSchedule } from "firebase-functions/v2/scheduler";
import { getDb } from "../lib/firebaseAdmin";
import { logInfo } from "../lib/log";

export const dailyReport = onSchedule("every day 09:00", async () => {
  logInfo("daily report start");
  const db = getDb();
  await db.collection("reports").add({ createdAt: Date.now(), kind: "daily" });
  logInfo("daily report done");
});
```

---

## 7) `package.json` / `firebase.json` の “見るべき場所” 👀

### 7-1) Node ランタイム（超重要）⚙️

2nd gen の Node は **22 / 20** が選べて、**18 は非推奨**です。迷ったらまず **Node 22** で OK🙆‍♂️ ([Firebase][3])
（※ 1st gen だと Node 22 が使えないケースがあるので、2nd gen中心の方が安全です⚠️ ([Stack Overflow][4])）

また、Firebase CLI 側も Node 22 対応が入った版があるので、**CLI は新しめを使う**のが吉です🛠️ ([Firebase][5])

### 7-2) Python を使うなら（参考）🐍

Python は **3.10〜3.13 がサポート**で、**デフォルトは 3.13**です。 ([Firebase][6])
（この章は TS 中心だけど、後で混在させたくなった時に安心材料🙂）

---

## 8) AI（Genkit / Gemini CLI / MCP）を “混ぜても崩れない” 置き場所🤖🧩

### 8-1) AI用フォルダ `src/ai/` を最初に作っておく🔥

「とりあえず index.ts に AI を直書き」すると、後で絶対ぐちゃります😂
なのでこの章で **置き場所だけ確保**します（中身は第17章で育てる）🌱

### 8-2) Gemini CLI 拡張 + MCP を “設計レビュー係” にする🧑‍⚖️🤖

Firebase は **Gemini CLI 用の公式拡張**や **Firebase MCP サーバー**を用意していて、CLI から Firebase を扱う支援ができます🛠️ ([Firebase][7])
さらに CLI 側には MCP サーバーを動かすコマンド（実験機能）も入っています。 ([Firebase][8])

この章での使い方はシンプルに👇

* 「このフォルダ構成で良い？」「責務分けできてる？」を **AIにレビュー**させる
* `src/index.ts` が太ってきたら「分割案」を出させる
* `lib/` に置くべき共通処理を提案させる

AI は便利だけど、**“最終判断は人間”**でいきましょう😄👍

---

## 🛠️ 手を動かす（この章のミニ演習）✍️✨

1. いまの `functions/src/index.ts` を開いて、**exportだけにする**🚪
2. `http/ firestore/ schedule/ lib/ types/ ai/` を作る📁
3. `health.ts / onMessageCreated.ts / dailyReport.ts` を配置して export する🧩
4. `lib/firebaseAdmin.ts` を作って、初期化を1か所に寄せる🧰
5. `log.ts` を作って、ログの形を統一する🧯

---

## ✅ チェック（できたら勝ち）🏁😆

* `index.ts` を見た瞬間に「何が公開されてるか」わかる👀
* HTTP / Firestore / Schedule が **別フォルダ**で迷わない🧭
* Admin 初期化が **1か所**にまとまっている🧰
* “AI を入れても散らからない” 置き場所がある🤖✨

---

## 🔥 次章につながる一言

この構成ができると、第6章（HTTPトリガー）から先が一気に楽になります🌐✨
特に **CORS** や **認証つきAPI（Callable）** みたいな “増えがちな処理” が来ても、崩れません😄

次は **HTTPトリガー入門（Web APIの入口）🌐** に進もう！

[1]: https://firebase.google.com/docs/functions/typescript?utm_source=chatgpt.com "Use TypeScript for Cloud Functions - Firebase - Google"
[2]: https://firebase.google.com/docs/functions/firestore-events?utm_source=chatgpt.com "Cloud Firestore triggers | Cloud Functions for Firebase - Google"
[3]: https://firebase.google.com/docs/functions/manage-functions?utm_source=chatgpt.com "Manage functions | Cloud Functions for Firebase - Google"
[4]: https://stackoverflow.com/questions/79615069/firebase-function-failed-to-deploy-at-other-region?utm_source=chatgpt.com "Firebase function failed to deploy at other region"
[5]: https://firebase.google.com/support/releases?utm_source=chatgpt.com "Release Notes | Firebase"
[6]: https://firebase.google.com/docs/functions/get-started?utm_source=chatgpt.com "Get started: write, test, and deploy your first functions - Firebase"
[7]: https://firebase.google.com/docs/ai?utm_source=chatgpt.com "AI | Firebase Documentation"
[8]: https://firebase.google.com/support/release-notes/cli?utm_source=chatgpt.com "Firebase CLI Release Notes"
