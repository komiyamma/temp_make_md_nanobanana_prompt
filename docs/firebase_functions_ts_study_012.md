# 第12章：イベント処理の設計（冪等・重複・再試行）🧠

今回は「Firestoreイベントで動くFunctions」が、**たまに2回動いても壊れない**ようにする回だよ〜🙂✨
これができると、通知・集計・AI処理が一気に“実務の強さ”になる💪🔥

---

## この章でできるようになること🎯

* 「えっ、同じ通知が2回飛んだ…😱」を**設計で防げる**
* 失敗したときの**再試行（retry）**を理解して、安全に使える
* AI（要約/整形）みたいな**お金がかかる処理**も、重複で爆死しないようにできる💸🧯
* “壊れない3点セット”を言葉で説明できる

  * **冪等（idempotent）**
  * **重複排除（dedupe）**
  * **再試行（retry）**

---

## 1) まず大前提：「イベント駆動」は “1回だけ” を期待しちゃダメ🙅‍♂️💥

Cloud Functions（イベント駆動）は、仕組みとして **at-least-once（最低1回は動く）** を提供するよ。つまり、**同じイベントが複数回処理される可能性がある**ってこと。([Firebase][1])

さらに2nd genは **Cloud Run + Eventarc** の上に乗ってるので、イベント配信・再試行の世界観もそっち寄りになるよ〜📦🚀([Firebase][2])

---

## 2) 超重要ワード：冪等（idempotent）ってなに？🧩

**冪等**＝「同じ処理を2回やっても、結果が変わらない」こと🙂✨

Firebase公式のベストプラクティスでも「冪等に書こう」ってはっきり言ってるよ。([Firebase][3])

たとえば👇

* ✅ 冪等：`summary` フィールドが既にあれば **AI要約をもう作らない**
* ❌ 非冪等：`likes += 1` を毎回やる（2回動いたら+2になる😇）

---

## 3) retry（再試行）を正しく怖がる😈➡️😌

## retryの意味🔁

イベント駆動関数は、エラーで終わると **イベントが捨てられる（drop）**ことがある。
そこで retry を有効にすると、**成功するか、リトライ期間が切れるまで再実行**されるよ。([Firebase][1])

* 2nd gen：リトライ期間は **24時間** ([Firebase][1])
* 1st gen：**7日** ([Firebase][1])

## ただし注意⚠️（無限リトライ地獄）

retry は「バグ」みたいな**永久に治らない失敗**だと、延々と回って事故る😱
公式も「圧力テストしてから」「一時的な障害向け」と警告してるよ。([Firebase][1])

---

## 4) 壊れないイベント処理の “3本柱” 🏗️✨

## ① 入口ガード（早期return）🚪

「このイベントは処理対象？」を最初に判定して、違ったら即return🙂

* **古すぎるイベントは捨てる**（retryで遅れて来たやつ対策）
* **必要な変更が無いなら捨てる**（自分の書き込みで再発火…の対策）

retryのベストプラクティスでも「終了条件（end condition）を入れろ」って書かれてるよ。([Firebase][1])

---

## ② “処理済み” をどこかに刻む🪵（重複排除）

重複排除の考え方は大きく3つあるよ👇

* **A. 元ドキュメントにフラグを書く**（わかりやすい）
* **B. event.id をキーに “ロック用ドキュメント” を作る**（強い）
* **C. outbox（ジョブキュー用コレクション）を作る**（いちばん実務っぽい）

この章では **B** を中心にやるよ💪

---

## ③ 副作用（Slack通知/外部API/AI呼び出し）を安全にする🧯

副作用は **「1回だけ」** が必要なことが多い。
だから副作用の前に **dedupeが必須**だよ🙂

あと、Nodeのイベント関数は「終わった後に裏で通信」みたいなのをすると壊れるので、`await` でちゃんと待って終わらせるの大事⚠️([Firebase][3])

---

## 5) ハンズオン：event.id で二重通知を防ぐ（2nd gen）🛠️🔐

ここから「Slack通知」「AI要約」みたいな **高コスト/高副作用**にも効く鉄板パターン！

## ✅ ポイント：event.id は “このイベント固有のID” として使える🆔

Firebase Functions（2nd gen）のイベントは CloudEvent 形式で、`event.id` と `event.time` が取れるよ。([Firebase][4])

> ※API参照に “preview” 表記があるので、プロダクションでは念のため「取れない/形式が違う」を想定したフォールバックも用意すると安心🙂([Firebase][5])

---

## 手順①：retry を有効にできる形を知る🔁

2nd gen では、Firestoreトリガー定義のオプションに `retry: true` を付けられる。([Firebase][1])

---

## 手順②：ロック（dedupe用）コレクションを1個決める🗂️

例：`eventLocks/{eventId}`

* ここに「このイベントは処理したよ」を刻む
* `create()`（存在したら失敗）を使うと強い💪

---

## 手順③：コード例（超重要）🧪

```ts
import { onDocumentWritten } from "firebase-functions/v2/firestore";
import { initializeApp } from "firebase-admin/app";
import { getFirestore, FieldValue, Timestamp } from "firebase-admin/firestore";

initializeApp();
const db = getFirestore();

/**
 * messages/{id} の更新で動く例
 * - 重複排除：event.id をロックに使う
 * - 終了条件：古いイベントは捨てる（retry遅延対策）
 */
export const onMessageWritten = onDocumentWritten(
  {
    retry: true, // 失敗時に再試行（2nd gen）🔁
  },
  "messages/{id}",
  async (event) => {
    const eventId = event.id ?? null;      // CloudEventのid 🆔
    const eventTime = event.time ?? null;  // CloudEventのtime ⏱️

    // 0) 入口ガード：eventIdが無いなら安全側でやめる（必要ならフォールバック設計）
    if (!eventId) return;

    // 1) 入口ガード：古すぎるイベントは捨てる（例：10分より前）
    if (eventTime) {
      const t = new Date(eventTime).getTime();
      const now = Date.now();
      if (now - t > 10 * 60 * 1000) return;
    }

    const lockRef = db.collection("eventLocks").doc(eventId);

    // 2) “ロック作成” で重複排除（存在したら二重処理しない）
    try {
      await lockRef.create({
        createdAt: FieldValue.serverTimestamp(),
        state: "processing",
      });
    } catch (e: any) {
      // 既にロックがある＝過去に処理開始済み（重複イベント）✅
      return;
    }

    try {
      // 3) ここから本処理（例：AI要約を作って保存、Slack通知など）
      //    ※AIや外部APIは “重複するとコスト爆増” なので、ここに来るまでにdedupe必須💸🧯

      // ... 例：Firestore更新、AI生成、Slack送信（awaitで必ず待つ）

      // 4) 成功したらロックをdoneへ
      await lockRef.update({
        state: "done",
        doneAt: FieldValue.serverTimestamp(),
      });
    } catch (err) {
      // 5) 失敗したら state=error にして原因を刻む（観測しやすい）
      await lockRef.update({
        state: "error",
        errorAt: FieldValue.serverTimestamp(),
      });

      // retry を効かせたいなら “throw” で失敗扱いにする
      throw err;
    }
  }
);
```

## このコードの狙い🎯

* **同じイベントが2回届いても**、2回目は `create()` が失敗して即return → 二重通知を防ぐ✅
* 失敗時に `throw` すると retry の対象になる（設定している場合）([Firebase][1])
* retry は最大24時間なので「古いイベントは捨てる」終了条件が効く([Firebase][1])

---

## でも！落とし穴もある😱（ここ超大事）

上の実装だと👇こうなる可能性がある：

* ロック作成 ✅
* Slack送信で失敗 ❌
* retryで再実行 🔁
* でもロックがあるから return 😇（＝Slackが結局送れない）

だから実務では、ロックに **状態** を持たせて「done以外なら再試行OK」にすることが多いよ🙂✨
（例：`state: processing` が一定時間以上続いてたら “やり直しOK” にする、など）

---

## 6) AIを絡めるときの“重複対策”は最優先🧠💸🤖

AIをイベント処理に入れると、重複実行で **費用も遅延も倍増**しがち😇
だから「AIを呼ぶ前にdedupe」or「AI結果を保存して再利用」が必須！

## 例：AI要約を一度だけ作って保存📌

* 先に `summary` があるか確認
* 無ければ生成して保存
* 生成後の保存も「同じ結果に収束する」ようにする（冪等）

Firebaseの生成AI系は大きく2系統で考えると整理しやすいよ👇

* アプリ側（クライアント）から呼ぶ：**Firebase AI Logic**（旧 Vertex AI in Firebase）([Firebase][6])
* サーバ側（Functions）でAIワークフロー：**Genkit** + `onCallGenkit` など([Firebase][7])

---

## 7) 開発を速くする：Antigravity / Gemini CLI / MCP 🛸🧰🤖

この章の“設計テンプレ”は、AIにレビューさせると強いよ🙂
たとえば👇

* 「この関数、二重実行で壊れない？」チェックリスト生成
* “失敗→retry→再実行” のテスト観点を列挙
* ロック設計（state遷移）案を複数出す

Gemini CLIにはFirebase拡張があって、Firebase文脈に強い動きをさせやすいよ。([Firebase][8])
さらに MCP server を入れると、AI支援ツールがFirebaseプロジェクトやコードベースを扱いやすくなる。([Firebase][9])

---

## 8) ミニ課題（この章のゴール）🏁✨

## お題：二重通知を防ぐ作戦を完成させる📨🧠

1. `eventLocks/{eventId}` を作る
2. `create()` で重複排除
3. 失敗したら `throw` で retry（必要なら）
4. **done / error / processing** の状態を入れて、再試行で詰まらないようにする

✅ できたら「二重通知を防ぐ作戦」を自分の言葉で説明してみてね🙂✨

---

## 9) チェック（言えたら勝ち）✅🧩

* 冪等って何？（一言で）
* retry をオンにすると何が起こる？（良い点/怖い点）([Firebase][1])
* event.id を使って二重処理を防ぐ理由は？([Firebase][4])
* AIを入れるとき、重複対策が特に大事なのはなぜ？([Firebase][6])

---

## おまけ：別言語でも考え方は同じだよ🧩🐍💠

Firebase Functionsの中心はNode/TSだけど、イベント駆動の世界観（at-least-once / retry / 冪等）は、Pythonでも .NETでも同じ発想で戦えるよ。
Cloud Run functions側のランタイム情報は公式の runtime support を見るのが確実🙂([Google Cloud Documentation][10])

---

次の第13章は、ここで作った“壊れない設計”を使って **通知・集計** の王道パターンに突入するよ📣📊🔥

[1]: https://firebase.google.com/docs/functions/retries "Retry asynchronous functions  |  Cloud Functions for Firebase"
[2]: https://firebase.google.com/docs/firestore/extend-with-functions-2nd-gen "Extend Cloud Firestore with Cloud Functions (2nd gen)  |  Firebase"
[3]: https://firebase.google.com/docs/functions/tips "Tips & tricks  |  Cloud Functions for Firebase"
[4]: https://firebase.google.com/docs/reference/functions/2nd-gen/node/firebase-functions.firestore.firestoreevent "firestore.FirestoreEvent interface  |  Cloud Functions for Firebase"
[5]: https://firebase.google.com/docs/reference/functions/2nd-gen/node/firebase-functions.cloudevent.md "CloudEvent interface  |  Cloud Functions for Firebase"
[6]: https://firebase.google.com/docs/ai-logic?utm_source=chatgpt.com "Gemini API using Firebase AI Logic - Google"
[7]: https://firebase.google.com/docs/functions/oncallgenkit?utm_source=chatgpt.com "Invoke Genkit flows from your App | Cloud Functions for Firebase"
[8]: https://firebase.google.com/docs/ai-assistance/gcli-extension?utm_source=chatgpt.com "Firebase extension for the Gemini CLI"
[9]: https://firebase.google.com/docs/ai-assistance/mcp-server?utm_source=chatgpt.com "Firebase MCP server | Develop with AI assistance - Google"
[10]: https://docs.cloud.google.com/functions/docs/runtime-support?utm_source=chatgpt.com "Runtime support | Cloud Run functions"
