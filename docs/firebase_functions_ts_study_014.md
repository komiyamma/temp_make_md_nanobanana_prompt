# 第14章：スケジュール関数（Cronで定期実行）⏰

この章は「裏側に目覚まし時計をセットする回」だよ〜！⏰😆
毎日・毎時・毎週みたいな“定期処理”を、勝手に動くようにしていきます🤖✨

---

## まず結論：スケジュール関数って何？🧠

![Scheduled Function Concept](./picture/firebase_functions_ts_study_014_01_alarm_clock.png)

`onSchedule` を使うと、決めた時刻や間隔で関数が自動実行されます⏰
中では **Google Cloud の Cloud Scheduler が呼び出し役**になって、指定タイミングで関数を起動します。([Firebase][1])

---

## いつ使うの？（超実務あるある）📌

* 毎朝：前日の集計を作って Firestore に保存📊
* 毎時：古いデータ掃除🧹
* 毎週：ランキング再計算🏆
* 毎日：未読通知のまとめを作る📨
* 毎晩：AIで要約を作って翌朝表示🤖🌅

---

## 仕組みのイメージ（ここ大事）🧩

![Scheduler Architecture](./picture/firebase_functions_ts_study_014_02_scheduler_arch.png)

デプロイすると自動で👇が作られます：

* Cloud Scheduler の **ジョブ**
* 実行される **HTTP関数（裏で呼ばれるやつ）**

そして、ジョブが HTTP関数を起動する流れです。([Firebase][1])
さらに、**ジョブや関数をコンソールで手動で消したり弄ったりしないでね**（壊れる可能性あり）という注意も公式で強めに書かれてます。([Firebase][1])

---

## お金の感覚（ビビりポイントを先に潰す）💸🧯

![Cost Model Visualization](./picture/firebase_functions_ts_study_014_03_cost_model.png)

スケジュール関数は「Cloud Schedulerのジョブ課金」が基本です。

* **ジョブは $0.10 / 1ジョブ / 月**（実行回数課金じゃない）💡
* **請求アカウントごとに月3ジョブは無料枠**あり🎁
  （プロジェクトごとじゃなく“アカウント単位”）([Google Cloud][2])

✅ 節約ワザ：
「毎朝7時にAもBもCもやる」なら、**ジョブを増やさず1本にまとめて中で分岐**するのが強いです💪😎

---

## Cron（スケジュール文字列）の書き方🕰️

Cloud Scheduler は

* **Unix Crontab**
* **App Engine 形式**

どっちもOKです。([Firebase][1])

よく使う例👇

* `"every day 07:00"`：毎日7:00（わかりやすい）([Firebase][1])
* `"0 7 * * *"`：毎日7:00（Cron）([Firebase][1])
* `"*/10 * * * *"`：10分ごと（Cron）

---

## タイムゾーン（日本はここをミスりがち）🌏🇯🇵

![Timezone Setting](./picture/firebase_functions_ts_study_014_04_timezone_map.png)

スケジュールは **タイムゾーン指定**できます。
`ScheduleOptions.timeZone` を使うと、そのタイムゾーン基準で実行されます。([Firebase][3])

例：`"Asia/Tokyo"` にすれば **JST基準で毎朝7時**に動く🎌✨

---

## ハンズオン：毎朝レポートを Firestore に書く📝🔥

![Idempotent Report Logic](./picture/firebase_functions_ts_study_014_05_idempotent_report.png)

ここでは「毎朝7:00に、`dailyReports/YYYY-MM-DD` を作る」をやります☀️
さらに **二重実行でも壊れない**ように“ガード”も入れます🛡️

> ⚠️ 公式でも「前の実行が終わらないうちに次が走る可能性あるよ」と注意されています。([Firebase][1])
> なので「複数回動いてもOK（冪等）」が超重要です💡

---

## 1) `functions/src/scheduled/dailyReport.ts` を作る📄

```ts
import { onSchedule } from "firebase-functions/v2/scheduler";
import { logger } from "firebase-functions";
import { initializeApp } from "firebase-admin/app";
import { getFirestore, FieldValue } from "firebase-admin/firestore";

initializeApp();
const db = getFirestore();

const TZ = "Asia/Tokyo";

/** JSTで YYYY-MM-DD を作る（DateはだいたいUTCなので、表示だけJSTにする） */
function todayYmdInTimeZone(timeZone: string): string {
  const dtf = new Intl.DateTimeFormat("en-CA", {
    timeZone,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
  return dtf.format(new Date()); // 例: 2026-02-18
}

export const writeDailyReport = onSchedule(
  {
    // Cronでも "every day 07:00" でもOK
    schedule: "0 7 * * *",
    timeZone: TZ,

    // 失敗時のリトライ（必要なときだけでOK）
    retryCount: 3,
    minBackoffSeconds: 10,
    maxBackoffSeconds: 300,
    maxDoublings: 3,
  },
  async (event) => {
    const ymd = todayYmdInTimeZone(TZ);
    const docId = ymd; // ここを固定にしておくと「二重実行」でも同じ場所に書ける

    logger.info("writeDailyReport start", {
      scheduleTime: event.scheduleTime, // 実行トリガー時刻（参考）
      docId,
    });

    const ref = db.doc(`dailyReports/${docId}`);

    try {
      // create() は「既にあったら失敗」なので、二重実行ガードに使える👍
      await ref.create({
        createdAt: FieldValue.serverTimestamp(),
        ymd,
        message: "おはよう☀️ 今日もやっていこう💪",
        scheduleTime: event.scheduleTime ?? null,
      });

      logger.info("writeDailyReport created", { docId });
    } catch (e: any) {
      // すでに作成済みならスキップ（＝多重起動に強い）
      const msg = String(e?.message ?? "");
      if (msg.includes("ALREADY_EXISTS")) {
        logger.warn("writeDailyReport already exists, skip", { docId });
        return;
      }

      logger.error("writeDailyReport failed", e);
      throw e; // throwすると Cloud Scheduler 側のリトライ対象になり得る
    }
  }
);
```

* `schedule` は **Unix Crontab / AppEngine** どっちでもOK。([Firebase][1])
* `timeZone` で JST基準にできる。([Firebase][3])
* `retryCount` などでリトライ設定も可能。([Firebase][3])

---

## 2) `functions/src/index.ts` から export する📦

```ts
export { writeDailyReport } from "./scheduled/dailyReport";
```

---

## 3) デプロイする🚀

```bash
firebase deploy --only functions
```

デプロイすると、スケジューラージョブ＆HTTP関数が自動生成されます。([Firebase][1])

---

## 4) 手動で一回だけ実行してテストする▶️

Cloud Scheduler の画面から「今すぐ実行」できます（公式にも案内あり）。([Firebase][1])
→ 実行したら Firestore に `dailyReports/YYYY-MM-DD` が増えるか確認👀✨

---

## つまずきポイント集（初心者がハマる所だけ）🧯

## ✅ 1) 「7時のつもりがズレる」😇

* `timeZone: "Asia/Tokyo"` を付ける！([Firebase][3])
* そして「日付文字列」は `Intl.DateTimeFormat` で **表示だけJST**にするのが安全🎌

## ✅ 2) 「たまに2回動いてる気がする」😱

![Execution Overlap](./picture/firebase_functions_ts_study_014_06_overlap_execution.png)

それ、仕様として起き得ます（次が前の実行中に走る可能性）。([Firebase][1])
➡️ 対策は **冪等（同じ処理が複数回動いてもOK）**
今回みたいに `docId` 固定＋ `create()` でガードはかなり強い🛡️✨

## ✅ 3) 「コンソールでジョブを消したら壊れた」💥

公式が「手動で削除/変更しないで」って言ってます。([Firebase][1])
➡️ 基本は **コード直して deploy** で管理しよう👍

---

## AIを絡めて“朝レポ”を気持ちよくする🤖🌅

![AI Morning Routine](./picture/firebase_functions_ts_study_014_07_ai_morning.png)

ここ、2026っぽく行こう✨

## パターンA：スケジュール関数が「素材」を作り、フロントでAI整形🧠✨

* スケジュール関数：集計結果を Firestore に保存📊
* フロント（React）：そのデータを読み、**Firebase AI Logic** で「読みやすい日本語」に整形して表示📱✨([Firebase][4])
* App Check と相性も良い（AI Logic はモバイル/WEB向けの設計）🧷([Firebase][4])

⚠️ なお、モデルの入れ替わりは起きます。
例として、**Gemini 2.0 Flash / Flash-Lite が 2026-03-31 にリタイア予定**と明記されています（新モデルへ移行推奨）。([Firebase][4])

## パターンB：スケジュール関数の中でAI要約（サーバ側AI）🧠➡️🤖

「関数の中でAI処理」までやりたいなら、サーバ側AIは **Genkit** が王道ルートです（Firebase側でも案内あり）。([Firebase][4])
（この教材だとAI本格編は後ろの章でガッツリやるイメージだね🔥）

---

## Antigravity / Gemini CLI を“下ごしらえ職人”にする🛸🧰

* **Gemini CLI の Firebase拡張**は、Firebase MCP server を自動セットアップして、ドキュメント参照や作業補助を強化してくれます。([Firebase][5])
* MCP server は **Antigravity や Gemini CLI** など多くのクライアントで動くよ、と明記されています。([Firebase][6])

たとえばAIに👇みたいに頼むと便利です😆

* 「毎日7時JSTのCron式を提案して」⏰
* 「冪等な dailyReports 書き込みの雛形コード作って」🛡️
* 「失敗時リトライの設計を初心者向けに説明して」📚

※ただし最後は **必ず人間がレビュー**ね！😎✍️（特に権限・コスト系）

---

## ミニ課題（提出用）🎒✨

1. 毎朝7:00に `dailyReports/YYYY-MM-DD` を作る☀️
2. 二重実行でも壊れないように `create()` ガードを入れる🛡️
3. 週1回（日曜3:00とか）で「30日より古い dailyReports を削除」する関数も追加🧹
4. ジョブ数が増えすぎないよう、できるだけまとめる💸

---

## この章のチェック（できたら勝ち）✅🏁

* `onSchedule` が **Cloud Scheduler で動く**イメージを説明できる([Firebase][1])
* Cron と “every day 07:00” の違いがわかる([Firebase][1])
* `timeZone` を付けてJST基準にできる([Firebase][3])
* 「次が前の実行中に走る」可能性があるので、冪等にする理由を言える([Firebase][1])
* Cloud Scheduler の料金が「ジョブ課金」で、無料枠が3ジョブあることを知ってる([Google Cloud][2])

---

次の第15章は「ログ・エラー・アラート」🧯👀で、**“落ちても直せる人”**に進化する回だよ〜！😆

[1]: https://firebase.google.com/docs/functions/schedule-functions "Schedule functions  |  Cloud Functions for Firebase"
[2]: https://cloud.google.com/scheduler/pricing "Pricing  |  Cloud Scheduler  |  Google Cloud"
[3]: https://firebase.google.com/docs/reference/functions/2nd-gen/node/firebase-functions.scheduler.scheduleoptions "scheduler.ScheduleOptions interface  |  Cloud Functions for Firebase"
[4]: https://firebase.google.com/docs/ai-logic "Gemini API using Firebase AI Logic  |  Firebase AI Logic"
[5]: https://firebase.google.com/docs/ai-assistance/gcli-extension "Firebase extension for the Gemini CLI  |  Develop with AI assistance"
[6]: https://firebase.google.com/docs/ai-assistance/mcp-server "Firebase MCP server  |  Develop with AI assistance"
