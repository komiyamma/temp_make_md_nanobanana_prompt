# 第10章：設定と秘密情報（APIキーをコードに書かない）🗝️🧯

この章は「**事故りやすい秘密情報の扱い**」を最初に固めて、次章以降の **Slack通知** や **AI連携（Genkit / Gemini API）** を安全に進める土台を作ります😊✨

---

## この章でできるようになること 🎯

* ✅ 「秘密情報」を**Gitに入れない**習慣がつく
* ✅ Functionsで **Secret Manager（シークレット）** を使える
* ✅ **Slack Webhook URL** を “秘密” として登録して、関数から参照できる
* ✅ ローカル検証（Emulator）でも秘密を扱える

---

## 1) まず「秘密情報」って何？🧨

秘密情報は、こういうの👇

* 🔑 APIキー（例：Gemini API / 外部SaaS）
* 🧾 Webhook URL（SlackのIncoming Webhooksなど）
* 🪪 トークン / パスワード / 署名用シークレット
* 🧪 “開発用だけど流出したら困る値”（例：社内Webhook、管理者用の隠しURL）

特に **Webhook URLは「URLそのものが秘密」** です。公開すると悪用されるので、絶対に貼らないのが鉄則です😱
（Slack側も「Webhook URLは秘密、漏れたら無効化されるよ」系の注意を強く出しています） ([Slack Developer Docs][1])

---

## 2) 2026の正解：Secrets + params を使う🧠✨

昔の `functions.config()` は **非推奨** で、**2027年3月に廃止予定**（その後は `functions.config` を含むデプロイが失敗）と明記されています。なので今からは「Secret Manager / params」寄せが安全です。 ([Firebase][2])

今どきの基本はこれ👇

* 🌱 “ただの設定値”（公開しても致命傷じゃない） → `.env` 系でOK
* 🔥 “秘密”（漏れたらアウト） → **Secret Manager**（Firebase CLIで登録）
* 🧷 秘密は **関数ごとに「使うよ」ってバインド**する（不要な関数に渡さない） ([Firebase][2])

---

## 3) ハンズオン：Slack Webhook URL を Secret にする 🔔🗝️

ここでは、次の名前で行きます👇

* Secret名：`SLACK_WEBHOOK_URL`

## 3-1) SlackでIncoming Webhookを作る（準備）🧩

Slack側で Incoming Webhooks を作って URL を取得します。
**そのURLは秘密**なので、メモ帳に貼ってもOKだけど、**Git管理のファイルに書かない**でね！ ([Slack Developer Docs][1])

---

## 3-2) Firebase CLIでSecret登録（Windows / PowerShell）🪟⚙️

プロジェクト直下で👇（値の入力を促されるので、Webhook URLを貼るだけ）

```powershell
firebase functions:secrets:set SLACK_WEBHOOK_URL
```

Secret管理コマンドの一覧も公式にまとまってます（set / access / destroy / prune など）。 ([Firebase][2])

> ⚠️大事：Secretの値を変えたら、**それを参照している関数は再デプロイが必要**です（反映の仕組みがそうなってる）。 ([Firebase][2])

---

## 3-3) 「Secretを使う関数」を1つ作る（TypeScript）🧪

ポイントは2つだけ👇

1. `defineSecret()` で Secret を定義
2. 関数定義のオプションで `secrets: [...]` を指定（これが “バインド”） ([Firebase][2])

例：HTTP関数（Slackへテスト投稿）

```ts
import { onRequest } from "firebase-functions/v2/https";
import { defineSecret } from "firebase-functions/params";

const slackWebhookUrl = defineSecret("SLACK_WEBHOOK_URL");

export const slackTest = onRequest(
  { secrets: [slackWebhookUrl] },
  async (req, res) => {
    // Secretの値を取り出す（これが “秘密”）
    const url = slackWebhookUrl.value();

    // Node 20+ なら fetch が使える前提でOK（小さく書ける✨）
    const r = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: "✅ Functionsからテスト投稿できたよ！" }),
    });

    const text = await r.text();
    res.status(200).send({ ok: true, slackResponse: text });
  }
);
```

### よくある事故ポイント 🚑

* ❌ `console.log(url)` しない（ログは漏えい経路になりがち）
* ❌ レスポンスに秘密を返さない（デバッグのつもりでやりがち）
* ✅ 使う関数だけに `secrets` を付ける（付けない関数だと `undefined` になる、が仕様） ([Firebase][2])

---

## 3-4) デプロイして動作確認 🧯➡️✅

```powershell
firebase deploy --only functions:slackTest
```

叩いてみて、Slackに投稿されれば成功🎉
（レスポンスには `slackResponse` が返ります）

---

## 4) ローカル（Emulator）で秘密を扱う🧪🛡️

Emulatorは、状況によっては本番のSecretを読みに行こうとします。で、権限がないとコケます😵
そこで **`.secret.local`** でローカルだけ上書きできる、と公式に書かれています。 ([Firebase][2])

* `.env.local`：環境変数の上書き ([Firebase][2])
* `.secret.local`：Secretの上書き ([Firebase][2])

（中身は `KEY=VALUE` の形で揃えると運用しやすいです👌）

---

## 5) AI連携の“鍵”も同じ考え方 🔥🤖

AI系って「APIキーをうっかり貼る事故」が起きやすいんですが、ここでやったのと同じでOKです。

公式ページにも、`defineSecret('GOOGLE_API_KEY')` を使って Gemini API クライアントを初期化する例が載っています。 ([Firebase][2])
つまり **AIほどSecrets必須**です🧠✨

---

## 6) Gemini CLI / MCPで「手順の抜け」を減らす🛸💻

ターミナルの **Gemini CLI** にFirebase拡張を入れると、Firebase向けのプロンプトやツール連携（MCP含む）を使えるようになります。インストール手順・`/firebase:init` や `/firebase:deploy` みたいな例も公式にあります。 ([Firebase][3])

さらにFirebase CLIのリリースノートには、AIアシスタント連携向けの **MCPサーバー起動コマンド追加**も書かれています。 ([Firebase][4])

この章でのおすすめ使い方はこれ👇

* 🤖「Secretsを使うときのチェックリスト作って」
* 🤖「このFunctionsコード、秘密がログやレスポンスに混ざってない？」
* 🤖「`secrets: [...]` を付け忘れてない？」（付け忘れはマジで多い😇）

---

## 7) 寄り道：Python / .NET だとどうなる？🐍🧩

## Python（Firebase Functions）

Pythonでも `secrets=[...]` を指定して、環境変数として読む形が公式にあります。 ([Firebase][2])
Pythonランタイムは **3.10〜3.13（デフォルト3.13）** がサポート、と明記されています。 ([Firebase][5])

## C#（.NET）はどうする？

FirebaseのFunctions本体はNode/TSが主役なので、C#を“関数ランタイム”でやるなら **Cloud Run** 側（Cloud Run functions）に置くのが現実的です。
Cloud RunでSecretを環境変数として参照する公式手順もあります。 ([Google Cloud Documentation][6])
（.NETランタイム選択の話も公式にまとまってます） ([Google Cloud Documentation][7])

---

## ✅ チェック（ここまでできた？）📝

* ✅ `SLACK_WEBHOOK_URL` を `firebase functions:secrets:set` で登録できた ([Firebase][2])
* ✅ `defineSecret()` + `secrets: [...]` を付けた関数が書けた ([Firebase][2])
* ✅ Slackへテスト投稿できた 🔔
* ✅ Secret更新は **再デプロイが必要**だと理解できた ([Firebase][2])
* ✅ Emulator用に `.secret.local` の存在を知った ([Firebase][2])
* ✅ `functions.config()` は将来詰むので避ける、と腹落ちした ([Firebase][2])

---

次章（Firestoreイベント）に進むと、**「データが作られた瞬間に自動で動く」**が始まって楽しくなります⚡
その前に、この章の「秘密を守る型」だけはガチで身につけちゃいましょ😊🛡️

[1]: https://docs.slack.dev/messaging/sending-messages-using-incoming-webhooks "Sending messages using incoming webhooks | Slack Developer Docs"
[2]: https://firebase.google.com/docs/functions/config-env "Configure your environment  |  Cloud Functions for Firebase"
[3]: https://firebase.google.com/docs/ai-assistance/gcli-extension "Firebase extension for the Gemini CLI  |  Develop with AI assistance"
[4]: https://firebase.google.com/support/release-notes/cli?utm_source=chatgpt.com "Firebase CLI Release Notes"
[5]: https://firebase.google.com/docs/functions/get-started?utm_source=chatgpt.com "Get started: write, test, and deploy your first functions - Firebase"
[6]: https://docs.cloud.google.com/run/docs/configuring/services/secrets?utm_source=chatgpt.com "Configure secrets for services | Cloud Run"
[7]: https://docs.cloud.google.com/run/docs/runtimes/dotnet?utm_source=chatgpt.com "The .NET runtime | Cloud Run"
