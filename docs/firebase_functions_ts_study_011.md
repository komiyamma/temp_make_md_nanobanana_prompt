# 第11章：Firestoreイベント入門（自動処理の気持ちよさ）⚡

この章は「Firestoreにデータが入った瞬間に、裏側（Functions）が勝手に動く！」を体験する回です😆✨
**やることはシンプル**：`messages/{id}` にドキュメントが作られたら、Functionsが文を整えて別フィールドに保存します✍️➡️💾

---

## この章のゴール🎯

* Firestoreの**イベントトリガー**（作成/更新/削除/書き込み）をざっくり使える🙂
* **`onDocumentCreated` / `onDocumentWritten`** の違いが腹落ちする🧩
* そして最大の落とし穴… **更新ループ（無限発火）** を避ける考え方がわかる🌀🚫 ([Firebase][1])

---

## まずは用語を超かんたんに👶📚

Firestoreのイベントトリガーは「**ドキュメントが変わった瞬間に起動する関数**」です⚡
ポイントは3つだけ覚えればOK👇

1. **イベントは“ドキュメントの変更”でしか起きない**（同じ内容を書き直すだけ＝no-op write だと起きない）🫥 ([Firebase][1])
2. **特定フィールドだけに反応**…みたいな指定はできない（ドキュメント単位）🧱 ([Firebase][1])
3. **少なくとも1回以上（at-least-once）**で届く＝たまに“同じイベントが2回”があり得る😇
   なので「何回呼ばれても壊れない（冪等）」を意識する💪 ([Firebase][1])

---

## 今日の主役：Firestoreトリガー4兄弟👨‍👩‍👧‍👦⚡

Functions v2（2nd gen）では、Firestore向けにだいたいこの4つを使います👇 ([Firebase][1])

* `onDocumentCreated`：作成時だけ✨（更新で再発火しないのが超えらい）
* `onDocumentUpdated`：更新時だけ📝
* `onDocumentDeleted`：削除時だけ🗑️
* `onDocumentWritten`：作成/更新/削除ぜんぶ😈（便利だけどループ事故の温床）

---

## ハンズオン：`messages/{id}` 作成→自動で整形して保存✍️⚙️✨

## 1) つくるFirestoreの形（イメージ）🧾

`messages/{id}` に、こういう感じのドキュメントが入る想定👇

* `text`: ユーザーが書いた文章
* `normalizedText`: Functionsが整えた文章（後で追加される）
* `processedAt`: Functionsが処理した時刻（後で追加される）

---

## 2) Functions（TypeScript）を書く🛠️

ここでは **作成時だけ動く `onDocumentCreated`** を使います。
これにより「同じドキュメントへ書き戻す（update）しても、作成トリガーは再発火しない」ので、初心者に優しいです☺️🌱 ([Firebase][1])

```ts
// functions/src/index.ts
import { onDocumentCreated } from "firebase-functions/v2/firestore";
import { initializeApp } from "firebase-admin/app";
import { getFirestore, FieldValue } from "firebase-admin/firestore";

initializeApp();
const db = getFirestore();

export const onMessageCreated = onDocumentCreated("messages/{id}", async (event) => {
  const snap = event.data;
  if (!snap) return; // 念のため（基本は来る）

  const data = snap.data() as { text?: unknown; normalizedText?: unknown };

  // ① 入力を安全に文字列化
  const text = (data.text ?? "").toString();

  // ② 超かんたんな整形（あとでAI整形に進化させられる✨）
  const normalizedText = normalizeText(text);

  // ③ 念のためガード（同じドキュメントに normalizedText が既にあるなら何もしない）
  if (typeof data.normalizedText === "string" && data.normalizedText.length > 0) return;

  // ④ 同じドキュメントへ追記（merge）
  await snap.ref.set(
    {
      normalizedText,
      processedAt: FieldValue.serverTimestamp(),
    },
    { merge: true }
  );
});

function normalizeText(text: string): string {
  return text
    .trim()
    .replace(/\s+/g, " ")
    .replace(/[！!]+/g, "!")
    .replace(/[？?]+/g, "?");
}
```

> 🧠 補足：FunctionsのAdmin SDKでの読み書きは **Security Rulesの対象外**（全部アクセスできる）なので、権限設計は別でちゃんと考える必要があります🧯 ([Firebase][1])

---

## 3) デプロイする🚀

（すでに Functions 初期化は終わっている前提でOK👌）

```powershell
firebase deploy --only functions:onMessageCreated
```

---

## 4) 動作確認（いちばん早い）👀🔥

Firestoreコンソールで `messages` コレクションにドキュメントを追加してみてください🧪
`text` を入れて保存すると、数秒後に `normalizedText` と `processedAt` が増えていたら成功です🎉✨

---

## つまずきポイント：更新ループ（無限発火）って何？🌀😇

たとえば `onDocumentWritten` は「作成/更新/削除ぜんぶ」で動くので、こういう事故が起きがち👇

1. ドキュメント作成
2. 関数が動く
3. 関数が同じドキュメントを更新（`normalizedText` を書く）
4. **更新だからまた `onDocumentWritten` が動く**
5. 2へ戻る🌀🌀🌀

Firestoreトリガーはこういう落とし穴があるよ、というのが公式側でも重要ポイントとして出ています（イベントは少なくとも1回以上、順序保証なし、など）([Firebase][1])

---

## ループ回避の“鉄板3パターン”🛡️✨

初心者はまずこれだけでOKです🙂

## パターンA：作成だけなら `onDocumentCreated` を使う（今回）🥇

更新で再発火しないので、超安全です👍 ([Firebase][1])

## パターンB：`onDocumentWritten` を使うなら「処理済みフラグ」でガード✅

```ts
import { onDocumentWritten } from "firebase-functions/v2/firestore";
import { FieldValue } from "firebase-admin/firestore";

export const onMessageWritten = onDocumentWritten("messages/{id}", async (event) => {
  const change = event.data;
  if (!change) return;

  const after = change.after;
  if (!after.exists) return; // 削除イベントなど

  const data = after.data() as { processedAt?: unknown; text?: unknown };

  // すでに処理済みなら終了（＝ループ止め）
  if (data.processedAt) return;

  const text = (data.text ?? "").toString();
  const normalizedText = normalizeText(text);

  await after.ref.set(
    { normalizedText, processedAt: FieldValue.serverTimestamp() },
    { merge: true }
  );
});
```

## パターンC：書き戻し先を別ドキュメントにする📦

例：`messages/{id}` を受けて、加工結果を `messageDerived/{id}` に書く
→ 同じトリガー対象を触らないのでループしにくいです🙆‍♂️

---

## “二重に動くかも”対策：冪等（idempotent）ってこう考える🧠🔁

Firestoreイベントは **at-least-once** なので、「同じイベントが2回来てもOK」設計が安心です💪 ([Firebase][2])
今日の例なら、以下のどれかを入れるだけで強くなります👇

* `processedAt` があれば何もしない✅（いちばん簡単）
* `processedVersion: 1` みたいにバージョン管理する🧩
* “結果が同じ”になる処理だけにする（例：正規化は何回やっても同じ）🧼✨

さらに、バックグラウンド関数は失敗時にリトライさせる設計もあるので、冪等が効いてきます🔁([Firebase][3])

---

## AIで開発を加速する🤖🛸（Antigravity / Gemini CLI）

ここ、ちゃんと最新に追従しておきます💡
**Gemini CLI の Firebase拡張**は、Firebase MCP server を自動で入れてくれて、Firebase向けのプロンプトやツール連携が強化されます🔧✨ ([Firebase][4])

## 使いどころ（この章で効くやつ）🧠

* 「`onDocumentCreated` の雛形を作って」➡️ まず動く形を生成してもらう
* 「無限ループしないガードを入れて」➡️ 事故りポイントを先に潰す
* 「Firestoreのデータ構造をこの用途に最適化して」➡️ 設計レビュー役にする

> MCP server は Antigravity や Gemini CLI など“ツール側”から Firebase を触れるようにする仕組み、という位置づけです🧰 ([Firebase][5])

---

## ミニ課題（5〜15分）🧩🔥

1. `normalizeText()` を改造して、次を追加👇

   * 先頭と末尾の絵文字だけ削る（例：😀😀こんにちは😀→こんにちは）
   * 連続する「w」を最大3つまでにする（例：wwwwww→www）
2. できたら `normalizedText` を見てニヤッとする😏✨

---

## チェック（できたら勝ち）✅🏁

* `onDocumentCreated` と `onDocumentWritten` の違いを一言で言える🙂
* 「同じドキュメントに書き戻すとループすることがある」を説明できる🌀
* 「処理済みフラグで止める」発想がある✅
* “たまに2回動くかも”を前提にできる（冪等）🔁 ([Firebase][1])

---

## ついでに：ランタイムの最新メモ📝✨

（この章では深掘りしないけど、迷子防止にだけ置いときます）

* Node.js は **22 / 20 が主要、18は非推奨**という扱いになっています📌 ([Firebase][6])
* Firebase CLIのリリースノートでは **デフォルトランタイムが nodejs22、Python は 3.13 がデフォルト**になった旨も記載があります🐍🟢 ([Firebase][7])

---

次の第12章は、この章で触れた「たまに2回動く」「順序が前後するかも」を真正面から倒して、**壊れないイベント設計（冪等・重複・再試行）**に進みます🧠🔥

[1]: https://firebase.google.com/docs/functions/firestore-events "Cloud Firestore triggers  |  Cloud Functions for Firebase"
[2]: https://firebase.google.com/docs/functions/locations?utm_source=chatgpt.com "Cloud Functions locations - Firebase - Google"
[3]: https://firebase.google.com/docs/functions/retries?utm_source=chatgpt.com "Retry asynchronous functions | Cloud Functions for Firebase"
[4]: https://firebase.google.com/docs/ai-assistance/gcli-extension "Firebase extension for the Gemini CLI  |  Develop with AI assistance"
[5]: https://firebase.google.com/docs/ai-assistance/mcp-server "Firebase MCP server  |  Develop with AI assistance"
[6]: https://firebase.google.com/docs/functions/1st-gen/manage-functions-1st?hl=ja&utm_source=chatgpt.com "関数を管理する（第 1 世代） | Cloud Functions for Firebase"
[7]: https://firebase.google.com/support/release-notes/cli?utm_source=chatgpt.com "Firebase CLI Release Notes"
