# 第95章：非同期の考え方（なぜ必要？）⏳🌍

![非同期の考え方：なぜ必要？](./picture/ddd_ts_study_095_async_timeline.png)

## この章のゴール🎯💕

この章を読み終わったら、こんな状態になれます👇✨

* 「同期でやるべき処理」と「非同期に逃がすべき処理」の見分けがつく👀✅
* 非同期にすると **何がラクになって、何が難しくなるか** が言葉で説明できる🗣️🌼
* 次章（冪等性🔁🛡️）に向けて「重複・順序・再試行」の地雷を先に知っておける💣➡️🧯

---

## 1) まず同期のおさらい🔔☕

第94章はこんな感じでしたよね👇
「ドメインイベントが起きた → その場で購読者が処理する」方式✨

イメージ（同期）📌

* 例：支払い完了イベント → その場でレシート作成 → その場で通知
* つまり「**今この瞬間に全部やる**」💪🔥

### 同期の強み💎

* **結果がすぐ揃う**（画面に即反映しやすい）✨
* 失敗したらその場で止められる（分かりやすい）🧯

### 同期の弱み😵‍💫

* 1つ重い処理があると **全体が遅くなる** 🐢💦
* 外部APIが不調だと **全体が巻き添えで落ちる** 🌩️
* 一時的に注文が殺到すると **詰まって崩れやすい** 🚧💥

---

## 2) 非同期が必要になる“よくある瞬間”⏳🌍

DDDのイベント連携で非同期が欲しくなるのは、だいたいこの3つ👇💡

### ① 重い処理を混ぜたくない🏋️‍♀️💦

![Heavy Task Separation](./picture/ddd_ts_study_095_heavy_task_separation.png)

* PDFレシート生成📄
* 画像変換🖼️
* 集計・分析📊
* まとめてメール送信✉️
  → これ、支払い処理の中でやると遅いです😇

### ② 外部連携は“失敗する前提”🌩️🔌

決済・通知・配送・CRM…
外は落ちるし遅いしタイムアウトします（現実）🥲
だから **「外がコケても注文の核心は守る」** 方向に寄せたい✨

### ③ “混雑”を吸収したい🚶‍♀️🚶‍♀️🚶‍♀️➡️🧺

![Queue Overflow](./picture/ddd_ts_study_095_queue_overflow.png)

注文が一気に増える日（セール、TVで紹介、昼休み）🍔🔥
同期だとサーバが「一気に全部やって」パンクしがち💥
非同期だと「いったんキューに積んで、順番にさばく」ができる🧺✅

---

## 3) 非同期にすると“世界がどう変わるか”🌈

![Sync vs Async Compare](./picture/ddd_ts_study_095_sync_vs_async_compare.png)

非同期にすると、こういう感じになります👇

### 同期（その場で全部）⚡

* 画面で「支払い完了」→ すぐレシートも通知も全部終わってる✨

### 非同期（あとでやる）⏳

* 画面で「支払い完了」→ **支払いだけ確定** ✅
* レシート作成や通知は **あとで勝手に進む** 🚶‍♀️💨
* だから一瞬だけ「反映待ち」みたいなズレが起きることがある🌫️
  これが **最終的整合性（eventual consistency）** の入口です🌍✨

![Eventual Consistency](./picture/ddd_ts_study_095_eventual_consistency.png)
  （“いつか揃うけど、今この瞬間は揃ってないことがある”）([ウィキペディア][1])

---

## 4) 非同期の基本セット🧰✨（超ざっくり版）

![キューとワーカーの構成](./picture/ddd_ts_study_095_queue_worker.png)

非同期の設計って、道具は増えるけど、考え方は単純です💕

### 📮 キュー（Queue）

「あとでやる仕事の箱」🧺
入れる人＝Producer（発行側）
取り出す人＝Consumer（処理側）

### 👷 ワーカー（Worker）

キューから仕事を取り出して実行する子✨

* 失敗したらリトライするかも🔁
* めちゃ失敗するなら隔離（DLQ）するかも🪦

### 🔁 配送保証（超重要）

現実のメッセージングはだいたい **“少なくとも1回”**（重複あり得る）です😇
例：Amazon SQSのStandard Queueは at-least-once で、重複を想定して冪等にせよ、が基本方針になってます([AWS ドキュメント][2])
（Azure Service Busも「at-least-once」やDLQなどの信頼性機能を前提に語られます）([Microsoft Learn][3])

👉 つまり：**同じイベントが2回届いても壊れない設計**が必要
→ 次章（第96章：冪等性🔁🛡️）へ繋がる✨

---

## 5) まずは“疑似キュー”で体験しよう🎮☕

いきなり本物のMQ（Kafkaとか）に行くと怖いので、まずは **アプリ内の簡易キュー**で感覚を掴みます🧺✨
（本番では耐久性や再起動耐性が必要になるけど、ここでは理解優先！）

### 5.1 ドメインイベント（最小）📣

```ts
export type DomainEvent = Readonly<{
  type: string;
  occurredAt: Date;
  payload: unknown;
}>;

export const PaymentCompleted = (args: {
  orderId: string;
  amountYen: number;
}): DomainEvent => ({
  type: "payment.completed",
  occurredAt: new Date(),
  payload: { ...args },
});
```

### 5.2 同期購読（第94章っぽい）🔔

「publishした瞬間にhandlerを呼ぶ」⚡

```ts
type Handler = (event: DomainEvent) => void | Promise<void>;

export class SyncEventBus {
  private handlers = new Map<string, Handler[]>();

  on(type: string, handler: Handler) {
    const list = this.handlers.get(type) ?? [];
    list.push(handler);
    this.handlers.set(type, list);
  }

  async publish(event: DomainEvent) {
    const list = this.handlers.get(event.type) ?? [];
    for (const h of list) {
      await h(event); // ここで重い処理があると詰まる😵‍💫
    }
  }
}
```

### 5.3 非同期：publishは“積むだけ”🧺✨

「publishは軽く終える」→ 仕事は後でワーカーが処理👷

```ts
type Handler = (event: DomainEvent) => void | Promise<void>;

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

export class InProcessAsyncEventBus {
  private handlers = new Map<string, Handler[]>();
  private queue: DomainEvent[] = [];
  private running = false;

  on(type: string, handler: Handler) {
    const list = this.handlers.get(type) ?? [];
    list.push(handler);
    this.handlers.set(type, list);
  }

  // ✅ publishは“積むだけ”なので速い
  publish(event: DomainEvent) {
    this.queue.push(event);
  }

  // 👷 ワーカー起動（アプリ起動時に1回呼ぶイメージ）
  startWorker() {
    if (this.running) return;
    this.running = true;

    (async () => {
      while (this.running) {
        const event = this.queue.shift();
        if (!event) {
          await sleep(10);
          continue;
        }

        const list = this.handlers.get(event.type) ?? [];
        for (const h of list) {
          try {
            await h(event);
          } catch (e) {
            // ここでは雑にログだけ（本番はリトライやDLQが欲しい）🧯
            console.error("async handler failed", event.type, e);
          }
        }
      }
    })();
  }

  stopWorker() {
    this.running = false;
  }
}
```

### 5.4 体験：支払いは即完了、レシートは後で☕📄

```ts
const bus = new InProcessAsyncEventBus();
bus.startWorker();

bus.on("payment.completed", async (e) => {
  // 重い処理のつもり😇
  await new Promise((r) => setTimeout(r, 500));
  console.log("✅ receipt created:", e.payload);
});

// 支払い完了の瞬間に全部終わらせない✨
bus.publish(PaymentCompleted({ orderId: "O-001", amountYen: 1200 }));

console.log("✅ payment finished (fast!)");
```

**ポイント**💡

* 「支払い完了」のログはすぐ出る✅
* 「レシート作成」は0.5秒後に出る📄⏳
  → “あとでやる”が体感できる🎉

---

## 6) 非同期で増える“困りごと”トップ3🥲⚠️

![Async Risks](./picture/ddd_ts_study_095_async_risks.png)

非同期は万能じゃなくて、代わりにこの3つが増えます👇

### ① 重複（同じイベントが2回来る）🔁😇

多くの仕組みは **at-least-once** なので、重複しうるのが前提です([AWS ドキュメント][2])
→ だから次章の「冪等性」が必須になる🛡️✨

### ② 順序（1→2→3の順で来ないかも）🔀

* 「支払い完了」より先に「レシート発行」処理が走ったら事故💥
* なので “同じ注文IDは順番を守る” 工夫が必要

例：

* Azure Service Bus なら **Sessions** で順序処理を作れる話があります([Microsoft Learn][4])
* Google Cloud Pub/Sub も ordering key などで順序を扱いつつ、再配送で後続も巻き戻る注意が書かれています([Google Cloud][5])

### ③ 失敗の扱い（リトライ・隔離・見える化）🧯👀

![Retry and DLQ](./picture/ddd_ts_study_095_retry_dlq.png)

非同期は「失敗しても後で取り返せる」が強み✨
でも設計しないと「失敗が闇に消える」😱
だから

* リトライ回数🔁
* 失敗の隔離（DLQ）🪦
* 監視（ログ・メトリクス）📈
  がセットになる（Azure Service BusもDLQなど信頼性機能に触れます）([Microsoft Learn][3])

---

## 7) どこまで非同期にする？判断のコツ🧠✨

![Decision Balance](./picture/ddd_ts_study_095_decision_balance.png)

迷ったらこの基準でOKです👇🌼

### 同期が向いてる✅

* その場で「成功/失敗」を返さないとUXが崩れる（支払い確定など）💳
* 強い整合性が必須（在庫の確保を同時に確定したい、など）🔒

### 非同期が向いてる✅

* **重い・遅い・外部**（通知、レシート生成、分析、検索インデックス更新）📩📄📊
* 一時的な混雑を吸収したい（注文殺到）🧺
* 失敗しても「後からやり直せばOK」な仕事🔁✨

---

## 8) AIに手伝ってもらうと速いところ🤖💞

### 🧠 設計の壁打ちプロンプト例

* 「同期購読でやってる“レシート作成”を非同期に分けたい。副作用を分離して、必要なインターフェース案と責務を箇条書きにして」
* 「“重複配送”が起きたときに壊れない設計チェックリストを作って」
* 「注文ID単位で順序を守る案を3つ。実装コストと運用コストも比較して」

### 🧪 テスト観点を増やすプロンプト例

* 「非同期化した後の失敗パターン（タイムアウト、二重実行、順序逆転）をGiven/When/Thenで10個出して」

---

## 9) ミニ演習（やってみよ〜！）🧁✍️

### 演習1：レシート作成を“非同期”に移す📄➡️🧺

1. `PaymentCompleted` を publish する
2. レシート作成は handler に寄せる
3. publish 側（支払いユースケース）は“速く終わる”状態にする

✅ ゴール：支払い処理が軽くなることをログで確認🎉

### 演習2：失敗をわざと起こす🌩️

* handler 内でランダムに例外を投げる🎲
* ログに「失敗したイベント」を出す🧯
  ✅ ゴール：「失敗が見える」状態を作る👀

（次章で、ここに“冪等キー”や“重複防止”を足して強くするよ🔁🛡️）

---

## 10) ふりかえりクイズ🎓💗

1. 非同期にすると「速くなる」代わりに増える問題を3つ言える？（ヒント：重複・順序・失敗）🔁🔀🧯
2. 「今すぐ揃ってないかも」を何て呼ぶ？🌍
3. at-least-once ってどういう意味？（そして何が必要になる？）🛡️

---

## おまけ：2026年2月時点の“周辺の最新”メモ🗓️✨

* TypeScript 5.9 は公式発表があり（2025/08/01）、GitHubのリリース上でも 5.9.x が最新として見えます([Microsoft for Developers][6])
* TypeScript のネイティブ移植プレビュー（npm＋VS Code向け）も公式に案内されています([Microsoft for Developers][7])
* 進捗アップデート（TypeScript 7関連）も公式ブログで継続的に出ています([Microsoft for Developers][8])
* Node.js は 2026/02/03 に v25.6.0（Current）がリリースされています([nodejs.org][9])

---

次の第96章は、この章で出てきた最大の地雷💣
**「同じイベントが2回来ても安全（冪等）」** をガッツリやります🔁🛡️✨

[1]: https://en.wikipedia.org/wiki/Eventual_consistency?utm_source=chatgpt.com "Eventual consistency"
[2]: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-queue-types.html?utm_source=chatgpt.com "Amazon SQS queue types - Amazon Simple Queue Service"
[3]: https://learn.microsoft.com/en-us/azure/reliability/reliability-service-bus?utm_source=chatgpt.com "Reliability in Azure Service Bus"
[4]: https://learn.microsoft.com/en-us/azure/service-bus-messaging/advanced-features-overview?utm_source=chatgpt.com "Azure Service Bus messaging - advanced features"
[5]: https://cloud.google.com/pubsub/docs/ordering?utm_source=chatgpt.com "Order messages | Pub/Sub"
[6]: https://devblogs.microsoft.com/typescript/announcing-typescript-5-9/?utm_source=chatgpt.com "Announcing TypeScript 5.9"
[7]: https://devblogs.microsoft.com/typescript/announcing-typescript-native-previews/?utm_source=chatgpt.com "Announcing TypeScript Native Previews"
[8]: https://devblogs.microsoft.com/typescript/progress-on-typescript-7-december-2025/?utm_source=chatgpt.com "Progress on TypeScript 7 - December 2025"
[9]: https://nodejs.org/en/blog/release/v25.6.0?utm_source=chatgpt.com "Node.js 25.6.0 (Current)"
