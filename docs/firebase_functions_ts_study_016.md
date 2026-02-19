# 第16章：ローカル検証（最小だけEmulator）🧪

この章は「本番を汚さずに試すクセ」を最短で身につける回だよ〜🙂✨
Functions と Firestore をローカルで動かして、**イベント → 関数実行 → ログ確認**までを一気に通します⚡

---

## 1) まずは全体像：Emulatorって何がうれしいの？🧠🧯

![Local Emulator vs Production](./picture/firebase_functions_ts_study_016_01_emulator_vs_prod.png)

ローカルの **Firebase Local Emulator Suite** を使うと、手元で **Firestore** や **Functions** の“ニセ本番”を動かせます💻🧪
これがあると…

* 本番DBにテストデータを混ぜない✅
* デプロイ前に「動くか」を確認できる✅
* 失敗してもローカルだから怖くない✅

しかも Emulator Suite UI で、Firestoreへのリクエストやルール評価の流れを見れるのが強いです👀✨ ([Firebase][1])

---

## 2) 最小構成の考え方（今日は “Functions + Firestore + UI” だけ）🧩

![Three Essential Emulators](./picture/firebase_functions_ts_study_016_02_three_essentials.png)

最低限はこの3つでOK👇

* Firestore emulator 🗃️
* Functions emulator ⚙️
* Emulator UI 🖥️

Functions emulator は HTTP / Callable / Firestoreトリガーなど色々エミュレートできます（やれる範囲が広い！） ([Firebase][2])

---

## 3) `firebase.json`：最小の emulators 設定を書く🧱

`firebase.json` に emulators を書くと、起動が安定します👍
（ポートは例。被ったら変えてOK）

```json
{
  "emulators": {
    "ui": { "enabled": true, "port": 4000 },
    "firestore": { "port": 8080 },
    "functions": { "port": 5001 }
  }
}
```

> UI はブラウザで開ける管理画面。ここで Firestore の中身やリクエストが見えます🖥️✨

---

## 4) 起動コマンド：まずは “必要なものだけ” 起動する🚀

![Import/Export Cycle](./picture/firebase_functions_ts_study_016_03_import_export.png)

PowerShell ならこんな感じでOK👇

```powershell
firebase emulators:start --only firestore,functions
```

「毎回データが消えるのイヤだな…」ってなったら、**import/export** が便利！📦✨
チームで共通の“テスト初期データ”を使うのにも向いてます。 ([Firebase][3])

```powershell
## 例：前回の状態を読み込みつつ、終了時に保存
firebase emulators:start --only firestore,functions --import=./emulator-data --export-on-exit
```

* `--import=...`：起動時にデータ復元🔁
* `--export-on-exit`：終了時にデータ保存💾

---

## 5) アプリ（React）を emulator に接続する🔌🧪

![Connection Switch](./picture/firebase_functions_ts_study_016_04_connection_switch.png)

ローカルで動かすときは、**SDKに「エミュレータ使ってね」**って教えます🙂
Firestore と Functions はそれぞれ接続します。

```ts
// firebaseClient.ts (例)
import { initializeApp } from "firebase/app";
import { getFirestore, connectFirestoreEmulator } from "firebase/firestore";
import { getFunctions, connectFunctionsEmulator } from "firebase/functions";

const app = initializeApp({
  // いつもの firebaseConfig（中身は省略でOK）
});

export const db = getFirestore(app);
export const fn = getFunctions(app);

// ローカル開発時だけ接続（雑にやるならこう）
if (location.hostname === "localhost") {
  connectFirestoreEmulator(db, "localhost", 8080);
  connectFunctionsEmulator(fn, "localhost", 5001);
}
```

接続の基本は公式ガイドの通りです📚 ([Firebase][4])

---

## 6) “イベント → 関数実行” をローカルで確認する⚡➡️⚙️➡️🧾

![Event Trigger Loop](./picture/firebase_functions_ts_study_016_05_event_loop.png)

ここが本日のメインイベント！🎉

### 6-1) 例：`messages/{id}` が作成されたら加工して保存する

（「作られた瞬間」のトリガーを使うと分かりやすいです🙂）

```ts
// functions/src/index.ts (例)
import { onDocumentCreated } from "firebase-functions/v2/firestore";
import { initializeApp } from "firebase-admin/app";
import { getFirestore } from "firebase-admin/firestore";
import { logger } from "firebase-functions";

initializeApp();
const adminDb = getFirestore();

export const onMessageCreated = onDocumentCreated("messages/{id}", async (event) => {
  const snap = event.data;
  if (!snap) return;

  const data = snap.data() as { text?: string };
  const text = (data.text ?? "").trim();

  logger.info("onMessageCreated fired", { id: snap.id, textLength: text.length });

  // 例：加工した結果を同じドキュメントに追記（無限ループにならないよう注意）
  await adminDb.doc(`messages/${snap.id}`).set(
    { normalizedText: text.toLowerCase() },
    { merge: true }
  );

  logger.info("normalizedText saved", { id: snap.id });
});
```

Firestore トリガーの基本はこの公式ページが核です📚 ([Firebase][4])

### 6-2) 動作確認の手順（超シンプル）✅

![Verification Feedback](./picture/firebase_functions_ts_study_016_06_feedback_loop.png)

1. `firebase emulators:start --only firestore,functions` で起動🚀
2. Emulator UI（だいたい `localhost:4000`）を開く🖥️
3. Firestore の画面で `messages` コレクションにドキュメント追加📝
4. ターミナルのログに `onMessageCreated fired` が出たら成功🎯
5. `normalizedText` が追記されてるのも UI で確認👀✨

さらに Firestore の **Requests Monitor** で、リクエストがどう評価されたか追えるのが強いです🔍 ([Firebase][4])

---

## 7) ローカルでも「秘密」を雑に扱わない🗝️🧯

![Secrets Management](./picture/firebase_functions_ts_study_016_07_secrets_management.png)

ローカル検証でありがちな事故👇
「Webhook URL とか APIキーを、とりあえずコードに直書き」

これ、後で絶対やらかします😇（Gitに残る…）

Functions は `.env` 形式の環境変数をサポートしていて、ローカル用に `.env.local` を使えます。さらに secrets もローカルで上書き可能です。 ([Firebase][5])

* `functions/.env`：共通の値（コミットは方針次第）
* `functions/.env.local`：ローカル専用（基本は **git ignore**）
* `.secret.local`：ローカルで secret を上書き（扱い注意） ([Firebase][5])

---

## 8) つまずきポイント集（初心者がハマりやすい😵‍💫➡️🙂）

### 🔥 A) 関数が発火しない

* Firestore 側が emulator に繋がってない（本番に繋がってる）
  → `connectFirestoreEmulator` が実行されてるか確認🔌
* `firebase emulators:start --only firestore,functions` で Functions を起動してない
  → 起動ログを見て確認👀

### 🔥 B) データがUIに見えない

* 別プロジェクトIDを見てる／別ポートを見てる
  → UI の接続先を確認🖥️
* リクエストは飛んでるのに保存されない
  → Requests Monitor で評価の流れを見る（ルールやパス違いが見える）🔍 ([Firebase][4])

### 🔥 C) もっと手早く試したい（UI操作すら面倒）

Functions shell で「手で関数を呼ぶ」もできます（ただし Firestore emulator との統合テスト目的なら、基本は emulators:start が楽）🧪 ([Firebase][6])

---

## 9) AI活用：エミュレータ運用を“雑務ごと”短縮する🤖🧰

ここ、地味だけど効きます🔥

* **Gemini CLI + Firebase拡張**に

  * `firebase.json` の雛形案
  * “この構成でどの emulators:start が最適？”
  * “ログの読み方”
    を作らせて、あなたはレビューする👀✅ ([Firebase][7])

* **Firebase MCP server** を使うと、AIツールがプロジェクトや設定を扱いやすくなる（“探す/整える”系の支援が強い）🛠️ ([Firebase][8])

> コツ：AIに「コマンド生成」→「あなたが実行」→「ログ貼って原因分析」このループが最強です🔁✨

---

## ミニ課題（15〜25分）🧩🔥

## お題：`messages/{id}` 作成で `normalizedText` を自動生成する⚡

1. emulator を起動
2. UI で `messages` に `{ text: "Hello Firebase!!" }` を追加
3. Functions のログを確認
4. Firestore に `normalizedText: "hello firebase!!"` が付いたらクリア🎉

## チェック✅

* 「本番DBを汚さずに」動作確認できた
* “イベント→関数→ログ→結果確認” の流れが言葉で説明できる
* 秘密情報をコードに直書きしない方向性が分かった 🗝️

---

次の章（第17章）で、ここに **AI（Genkit等）** を合体させて「裏側でAI処理」へ進めると、めちゃくちゃ“現代アプリ感”出ます🤖🔥

[1]: https://firebase.google.com/codelabs/firebase-emulator?utm_source=chatgpt.com "Local Development with the Firebase Emulator Suite - Google"
[2]: https://firebase.google.com/docs/functions/local-emulator?utm_source=chatgpt.com "Run functions locally | Cloud Functions for Firebase - Google"
[3]: https://firebase.google.com/docs/emulator-suite/install_and_configure?utm_source=chatgpt.com "Install, configure and integrate Local Emulator Suite - Firebase"
[4]: https://firebase.google.com/docs/emulator-suite/connect_firestore?utm_source=chatgpt.com "Connect your app to the Cloud Firestore Emulator - Firebase"
[5]: https://firebase.google.com/docs/functions/config-env?utm_source=chatgpt.com "Configure your environment | Cloud Functions for Firebase"
[6]: https://firebase.google.com/docs/functions/local-shell?utm_source=chatgpt.com "Test functions interactively | Cloud Functions for Firebase"
[7]: https://firebase.google.com/docs/ai-assistance/gcli-extension?utm_source=chatgpt.com "Firebase extension for the Gemini CLI"
[8]: https://firebase.google.com/docs/ai-assistance/mcp-server?utm_source=chatgpt.com "Firebase MCP server | Develop with AI assistance - Google"
