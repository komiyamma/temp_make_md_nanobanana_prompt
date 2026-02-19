# 第19章：Slack通知の準備（Webhook + Secret）🔔🗝️

この章は「Slackに投稿できる！」「しかもURL（秘密）をコードに書いてない！」までを一気に完成させます💪😆
次の第20章で **Firestore更新→Slack通知** を完成させるための“下ごしらえ”だよ〜🍳✨

---

## この章のゴール 🎯

* Slackの **Incoming Webhook URL** を作れる🔗
* そのURLを **Secret（Secret Manager）** に安全に入れられる🗝️
* Functions（2nd gen）から Secret を読み出して、Slackに **テスト投稿** できる📩✨
* **Gitに秘密が混ざらない** 習慣がつく🧯✅

---

## 1) まず理解：Incoming Webhooksって何？🤔

![Incoming Webhook Mechanism](./picture/firebase_functions_ts_study_019_01_webhook_concept.png)

Slackの **Incoming Webhooks** は、「専用URLにJSONをPOSTすると、そのまま指定チャンネルへ投稿できる仕組み」だよ📮
メッセージ本文だけじゃなく、レイアウト（Blocks）も使えるので、通知を見やすくできる✨ ([Slack開発者ドキュメント][1])

⚠️ ただし！このWebhook URLは **“投稿できる権利そのもの”** なので、漏れたらアウトです😱
だから **Secretに入れて守る** のがこの章の主役🗝️🔥

---

## 2) Slack側：Webhook URL を作る手順 🧩

![Slack Setup Steps](./picture/firebase_functions_ts_study_019_02_slack_setup.png)

やることはシンプル👇（Slack管理画面でポチポチ）

1. Slackで **アプリ（Slack App）** を作る
2. **Incoming Webhooks** を有効化（ON）
3. **Add New Webhook to Workspace**
4. 投稿先チャンネルを選んで許可 ✅
5. できあがった **Webhook URL** をコピー（この時点では“誰にも見せない”）🔒

公式の説明はここが基準だよ📚 ([Slack開発者ドキュメント][1])

💡 あるある

* 「ワークスペースでアプリ作成が禁止」→ 管理者に許可が必要なことがあるよ🙏
* 投稿チャンネルは最初は `#dev-notify` みたいに専用を作るのが安全でラク👍

---

## 3) Firebase側：Secret を作って、Webhook URL を入れる 🗝️

ここが最重要ポイント！
**Webhook URL をコードにも .env にも入れない**。Secretに入れる🙂‍↕️

## 3-1. Secret を作成（Firebase CLI）🧰

![Secret Set Command](./picture/firebase_functions_ts_study_019_03_secret_command.png)

プロジェクトのルートで👇（Secret名は例：`SLACK_WEBHOOK_URL`）

```bash
firebase functions:secrets:set SLACK_WEBHOOK_URL
```

入力を促されるので、SlackのWebhook URLを貼り付けてEnter🔐
このやり方が公式の基本手順だよ。 ([Firebase][2])

### Secret運用の大事な注意⚠️

* Secretの値を更新したら、**そのSecretを使う関数は再デプロイが必要**（反映されないことがある）🔁 ([Firebase][2])
* 使ってるSecretを消すと、関数が静かに失敗することがある（地味に怖い）😇 ([Firebase][2])

### 料金メモ（軽く知っておく）💸

Secret Managerは無料枠があるけど、アクセス回数などで課金が発生しうるよ〜という話が公式にある👌 ([Firebase][2])
（とはいえ、この教材レベルの通知でいきなり高額になるケースは稀！でも“意識”は大事🧠）

---

## 4) Functions側：Secretを「関数に紐づけて」使う 🔗

## 4-1. TypeScript：defineSecret + secrets オプション（2nd gen）🧱

![Accessing Secret in Code](./picture/firebase_functions_ts_study_019_04_define_secret.png)

2nd genの基本形はこれ👇
Secretを `defineSecret()` で宣言して、関数のオプション `secrets: [...]` で **その関数にだけ渡す** イメージだよ。 ([Firebase][3])

例：HTTPでテスト送信する関数 `slackTest` を作る（最小でOK）✨

```ts
import { onRequest } from "firebase-functions/v2/https";
import { defineSecret } from "firebase-functions/params";

const SLACK_WEBHOOK_URL = defineSecret("SLACK_WEBHOOK_URL");

// ✅ テスト送信用（まずはここで動作確認）
export const slackTest = onRequest(
  { secrets: [SLACK_WEBHOOK_URL] },
  async (req, res) => {
    try {
      const url = SLACK_WEBHOOK_URL.value(); // 👈 Secretの実体

      // Node 20/22 なら fetch が標準で使えることが多いよ👍
      const payload = {
        text: "✅ Slack通知テスト：Functions から送信できたよ！🎉",
      };

      const r = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json; charset=utf-8" },
        body: JSON.stringify(payload),
      });

      if (!r.ok) {
        const body = await r.text();
        res.status(500).send(`Slack error: ${r.status} ${body}`);
        return;
      }

      res.status(200).send("ok");
    } catch (e: any) {
      res.status(500).send(e?.message ?? String(e));
    }
  }
);
```

✅ ここでのポイント

* `SLACK_WEBHOOK_URL.value()` は **絶対にログに出さない**（漏れたら終わり）😱
* `secrets: [SLACK_WEBHOOK_URL]` を付け忘れると、関数がSecretにアクセスできず詰むことがある🧱 ([Firebase][3])

---

## 5) デプロイして、Slackに投稿テストする 🚀📩

![Test Flight](./picture/firebase_functions_ts_study_019_05_test_flight.png)

## 5-1. デプロイ

```bash
firebase deploy --only functions:slackTest
```

デプロイ後、表示されたURLにアクセスすると、Slackにメッセージが飛ぶはず！🎯

## 5-2. Slack側で確認

指定チャンネルに👇みたいなのが出れば勝ち🏆

* ✅ Slack通知テスト：Functions から送信できたよ！🎉

---

## 6) ローカル検証（Emulator）で詰まったら 🧪😵‍💫

![Local Secret Override](./picture/firebase_functions_ts_study_019_06_local_override.png)

エミュレータは、既定だとSecretを取りに行こうとする（権限がなくて失敗することもある）という挙動が公式にあるよ。 ([Firebase][2])
その場合は `functions/.secret.local` で **ローカル用にSecretを上書き**できる👌 ([Firebase][2])

（この章では“まずクラウドでテスト送信成功”を優先でOK！ローカル最適化は第16章でガッツリやると気持ちいい🧠✨）

---

## 7) よくある事故と対策 🧯

![Secret Leak Accident](./picture/firebase_functions_ts_study_019_07_leak_accident.png)

## 事故A：Slackに何も出ない😇

* Webhook URLが間違ってる／古い
* Slack側でチャンネル許可を変えた
* `fetch()` のレスポンスが `ok` じゃない（このコードはエラー本文も返すので、そこを見る👀）

👉 Incoming Webhooksは「URLにJSONを送る」仕組みが前提。公式の送信仕様（payloadなど）も確認できるよ。 ([Slack開発者ドキュメント][1])

## 事故B：Secret更新したのに反映されない😇

👉 **Secret更新後は、そのSecretを使う関数を再デプロイ**が基本！ ([Firebase][2])

## 事故C：Gitに秘密が混ざった😱

* `.env` に入れてコミットした
* READMEに貼った
* スクショにURLが映った

👉 “Webhook URLはパスワード”と思って扱うのが正解🔒

---

## 8) AI活用：Gemini CLI / Antigravityで爆速にする 🤖🛸

![Gemini CLI Helper](./picture/firebase_functions_ts_study_019_08_gemini_cli.png)


ここ、ちゃんと“効く”やつだけ紹介するね👍

## 8-1. Gemini CLI の Firebase拡張：何が嬉しい？🧰

Firebase公式の **Gemini CLI 拡張**は、Firebase MCP server を自動セットアップして、

* Firebase開発向けの **定型プロンプト（slash commands）**
* Firebaseプロジェクトに対して **ツール実行**（作成・デプロイ等の補助）
* Firebaseドキュメント参照をLLM向けに扱いやすくする
  みたいな機能を提供する、という説明が公式にあるよ。 ([Firebase][4])

## 8-2. MCP server は Antigravity など色んな“エージェント環境”から使える🧩

Firebase MCP server は **Antigravity や Gemini CLI、Firebase Studio など**、MCPクライアントになれるツールから使えると明言されてる👌 ([Firebase][5])

### 使い方のコツ（この章向け）💡

Geminiにこう頼むと強い👇

* 「2nd genのonRequestで、defineSecretを使ってSlack Incoming WebhooksにPOSTする最小コードを書いて」
* 「Secretを更新したら再デプロイが必要？どこに書いてある？」
* 「Slackのpayloadの最低限は？textだけでいい？」

AIに作らせて、**公式ドキュメントと突き合わせてレビュー**すると最速で安全🧠✨

---

## 9) ミニ課題（この章のゴール確認）📝🏁

![Assignment Goal](./picture/firebase_functions_ts_study_019_09_assignment.png)


## 必須 ✅

* `slackTest` をデプロイして、Slackに **1通** 送る📩✨

## 余裕があれば 🌟

* payloadをちょい改造して、通知に「環境名」「時刻」を入れる⌛
* 「成功/失敗」を分けて、失敗時は `res.status(500)` の本文を読みやすくする🧯

---

## 10) チェックリスト ✅✅✅

![Final Checklist](./picture/firebase_functions_ts_study_019_10_checklist.png)


* [ ] Webhook URL を作れた（Slack側）🔗
* [ ] `firebase functions:secrets:set SLACK_WEBHOOK_URL` でSecretに入れた🗝️ ([Firebase][2])
* [ ] `defineSecret()` + `secrets: [...]` で関数に紐づけた🔗 ([Firebase][3])
* [ ] Slackにテスト投稿できた📩
* [ ] URLをログやコードに出してない🔒

---

## ちょい寄り道：.NET / Python でやるなら？🧩

この教材はTS中心だけど、「別言語で関数を書く」話が出たときは **Cloud Run functions（v2系）** のランタイム表が基準になるよ。 ([Google Cloud Documentation][6])
たとえば **.NET 8** を使う選択肢も“公式にサポート枠として存在”するので、C#でWebhook送信のHTTP関数を書くこと自体は現実的👍（ただしこの章はTSで統一して進めるのが学習効率◎） ([Google Cloud Documentation][7])

---

次の第20章は、いよいよ **Firestore更新 → Slack通知** を“実務っぽく壊れにくく”仕上げるよ🔥
（重複通知ガード、失敗時のリトライ、ログ設計あたりが主役になるはず🧠📣）

[1]: https://docs.slack.dev/messaging/sending-messages-using-incoming-webhooks "Sending messages using incoming webhooks | Slack Developer Docs"
[2]: https://firebase.google.com/docs/functions/config-env "Configure your environment  |  Cloud Functions for Firebase"
[3]: https://firebase.google.com/docs/functions/2nd-gen-upgrade?hl=ja "第 1 世代の Node.js 関数を第 2 世代にアップグレードする  |  Cloud Functions for Firebase"
[4]: https://firebase.google.com/docs/ai-assistance/gcli-extension "Firebase extension for the Gemini CLI  |  Develop with AI assistance"
[5]: https://firebase.google.com/docs/ai-assistance/mcp-server?utm_source=chatgpt.com "Firebase MCP server | Develop with AI assistance - Google"
[6]: https://docs.cloud.google.com/functions/docs/runtime-support?utm_source=chatgpt.com "Runtime support | Cloud Run functions"
[7]: https://docs.cloud.google.com/functions/docs/release-notes?utm_source=chatgpt.com "Cloud Run functions (formerly known as Cloud Functions ..."
