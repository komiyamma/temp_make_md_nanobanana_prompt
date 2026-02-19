# 第19章：サーバー処理の選択肢（Functions/Cloud Run）🧠⚙️

この章は「Hosting / App Hosting だけじゃ足りない “サーバー側の仕事” を、どこに置く？」をスパッと決められるようになる回です😎✨
（API、Webhook、バッチ、AI呼び出し、画像処理…などなど！）

---

## この章でできるようになること🎯

* 「これ、サーバー必要？」を判断できる🤔➡️✅
* **Cloud Functions for Firebase** と **Cloud Run** を使い分けできる🧩
* Hosting の URL（`/api/**` みたいな）を **Functions に繋げる**ことができる🔁🌐
* AI（AI Logic / Genkit / Gemini / MCP / Gemini CLI）で、設計〜実装の詰まりを潰せる🤖🧯

---

## 1) そもそも「サーバー処理」って何？🤔💡

![Backend Tasks](./picture/firebase_hosting_ts_study_019_01_server_tasks.png)

Hosting は基本「静的ファイル配信（HTML/JS/CSS）」が得意です⚡
でも、こういうのはサーバーが必要になりがち👇

* フォーム送信 → メール送る📩
* DBを安全に更新（権限チェック込み）🔐
* 外部サービスからのWebhook受け取り（決済/通知など）🔔
* 重い処理（画像変換、PDF生成、AIの前処理）🧱
* 定期実行（毎朝集計、期限切れ掃除）⏰

ここで登場するのが **Functions / Cloud Run** です🚀

---

## 2) 結論：どう選ぶ？（3秒で決める）⚡🧩

![Functions vs Cloud Run Decision](./picture/firebase_hosting_ts_study_019_02_decision_tree.png)

## A. Cloud Functions for Firebase を選ぶ👍

こんなとき強いです👇

* Firebase（Auth/Firestore/Storage など）と **密接に連携**したい🧲
* “イベントで動く” 処理が欲しい（Firestore更新で動く等）📌
* まず最短で作りたい（学習コスト低め）🏃‍♂️💨

言語/ランタイムの目安（2026-02時点）👇

* Node.js は **20 / 22 を完全サポート**、18 は **2025年初頭に非推奨**扱い🟩 ([Firebase][1])
* Python は **3.10〜3.13** をサポート、**3.13 がデフォルト**🐍 ([Firebase][1])
* Node の選択は `package.json` の `"engines"` か `firebase.json` の `functions.runtime` で指定できます🧾 ([Firebase][2])

---

## B. Cloud Run（または Cloud Run functions）を選ぶ💪

こんなとき強いです👇

* **.NET** や、より自由な構成（依存ライブラリ/OSツール）を使いたい🧰
* 重い処理・長めの処理・メモリ多めが必要🏋️
* “普通の Web サーバー” っぽく作りたい（コンテナ/HTTP）🌐

Cloud Run functions のランタイム例（ページ更新: **2026-02-12**）👇

* **Python 3.13**（`python313`）あり🐍
* **.NET 8**（`dotnet8`）あり🟦
* Node.js 20 は **2026-04-30 に deprecation**（先々の寿命も見ながら選べる）⏳ ([Google Cloud Documentation][3])

---

## C. App Hosting だけで完結できるケースもある😌

* SSR/フルスタック（Next.jsなど）を **App Hosting で運用**して、画面側は完結🧩
* ただし「定期実行」「Webhook」「バッチ」などは、結局 Functions/Run が便利になりがちです⚙️

---

## 3) Hosting から “同じドメインで” Functions に繋げる（超重要）🔁🌐

![Hosting Rewrites](./picture/firebase_hosting_ts_study_019_03_rewrite_arch.png)

これができると何が嬉しい？😆

* フロントから `/api/...` を叩ける（別ドメインじゃない）
* **CORS 地獄を回避**しやすい🔥
* デプロイの流れがスッキリする✨

Firebase Hosting の `rewrites` は、リクエストを **Functions** や **Cloud Run** に振れます📌

* Functions に向ける rewrite の書き方が用意されてます🧾 ([Firebase][4])
* Cloud Run コンテナに向ける rewrite もできます🧾 ([Firebase][4])

---

## 4) 手を動かす：`/api/**` を Cloud Functions（TypeScript）に繋ぐ🛠️🟩

ここは「最短で動く」を優先します🏁✨
（すでに Hosting をデプロイできている前提でOK）

---

## 4-1. Functions を追加する（初期化）🧱

![Functions Initialization](./picture/firebase_hosting_ts_study_019_04_functions_init.png)

プロジェクトのルートで👇

```bash
firebase init functions
```

* TypeScript を選ぶ✨
* 依存インストールも基本は OK（迷ったら Yes）👍

---

## 4-2. Node のバージョンを決める（おすすめ: 22）🟩

`functions/package.json` に👇（例）

```json
{
  "engines": { "node": "22" }
}
```

Node 20/22 がサポート対象で、18 は非推奨扱いなので「新規なら 22」が無難です👍 ([Firebase][1])

---

## 4-3. HTTP API を 1本作る（`apiHello`）👋🌐

`functions/src/index.ts`

```ts
import { onRequest } from "firebase-functions/v2/https";
import { logger } from "firebase-functions";

export const apiHello = onRequest((req, res) => {
  logger.info("apiHello called", { path: req.path, query: req.query });
  res.json({
    ok: true,
    message: "Hello from Cloud Functions! 🎉",
    now: new Date().toISOString(),
  });
});
```

---

## 4-4. Hosting の `/api/**` を Functions に rewrite する🔁

![Rewrite JSON Config](./picture/firebase_hosting_ts_study_019_05_rewrite_config.png)

`firebase.json` の `hosting.rewrites` に追加します👇
（**rewrite は上から順に効く**ので、`** -> index.html` より上に！）

```json
{
  "hosting": {
    "rewrites": [
      {
        "source": "/api/**",
        "function": {
          "functionId": "apiHello",
          "region": "asia-northeast1",
          "pinTag": true
        }
      },
      { "source": "**", "destination": "/index.html" }
    ]
  }
}
```

* `functionId` は関数名（ここでは `apiHello`）📛
* `pinTag: true` は「Hosting 側が特定の関数バージョンに固定」できて、プレビュー環境でも事故りにくくて良いです🧷（例が公式にあります）([Firebase][4])

---

## 4-5. ローカルで動作確認（エミュレータ）🧪

```bash
firebase emulators:start --only hosting,functions
```

ブラウザで👇

* `http://localhost:5000/api/hello`（または表示される URL）👀✨

---

## 4-6. デプロイ🚀

```bash
firebase deploy --only functions,hosting
```

公開サイトの `https://あなたのドメイン/api/hello` が JSON を返せたら成功🎉🎉🎉

---

## 5) じゃあ Cloud Run はいつ使う？（わかりやすい例）🟦🔥

![Cloud Run Flexibility](./picture/firebase_hosting_ts_study_019_06_cloud_run_runtimes.png)

## 「Functions だと辛い」代表例💦

* **.NET（C#）で書きたい**（既存資産がある）🟦
* 画像/動画処理でネイティブ依存が多い（ffmpeg 等）🎞️
* “普通のWebサーバー” を立てたい（ルーティング多い/ミドルウェア多い）🧩

Cloud Run functions なら、**.NET 8** や **Python 3.13** がランタイムとして載っています（2026-02-12 更新）🧾 ([Google Cloud Documentation][3])

そして Hosting 側から Cloud Run に rewrite もできます👇（公式例あり）([Firebase][4])

---

## 6) AI を絡めると “サーバー置き場” が一気に決まる🤖🧠

![AI Tools Ecosystem](./picture/firebase_hosting_ts_study_019_07_ai_tools_map.png)

## 6-1. 「AIをクライアントから直接呼ぶ」なら AI Logic が強い📱🌐🤖

Firebase AI Logic は、モバイル/Web アプリから **Gemini/Imagen を直接呼ぶ**ケース向けのクライアントSDKで、**不正クライアント対策や Firebase 連携**が用意されています🛡️ ([Firebase][5])

> ただし「ログ保存」「課金ガード」「長い前処理」みたいな“サーバー都合”があるなら、Functions/Run 併用が現実的です👍

---

## 6-2. Genkit を Functions から呼ぶ（AI処理を “フロー” にする）🧰✨

Cloud Functions for Firebase には **`onCallGenkit`** があって、Genkit の Flow を callable で包んで呼べます📞🤖 ([Firebase][6])
（認証情報が自動で付く呼び出しルートを作りやすいのが嬉しい！）

---

## 6-3. Gemini in Firebase / Gemini CLI / MCP で “詰まり” を消す🧯

* Firebase コンソール内の AI アシスタント（Gemini in Firebase）で、設定やデバッグを相談できます🧯 ([Firebase][7])
* さらに **Firebase MCP server** を使うと、AIツールが Firebase プロジェクトを理解して操作しやすくなります🧩 ([Firebase][8])
* Firebase MCP Server は GA になって、**Gemini CLI 向けの公式拡張**も出ています（2025-10-08）🚀 ([The Firebase Blog][9])
* Firebase の AI 支援ドキュメント側にも **「MCP / Gemini CLI / エージェント」**の導線が整理されています（日本語ページあり）🗺️ ([Firebase][10])

## Gemini CLI に投げると強いプロンプト例💬🧠

* 「このプロジェクトで `/api/**` を Functions に繋ぐ `firebase.json` の rewrites を提案して」
* 「Node 22 と Node 20 のどっちを選ぶべき？サポート期限も踏まえて」([Google Cloud Documentation][3])
* 「この API は Functions と Cloud Run、どっちが事故りにくい？理由も」

---

## 7) ミニ課題🎒✨（20〜30分）

次のうち **2つ**を選んで、どこに置くか決めてください✍️（Functions or Cloud Run）

1. お問い合わせフォーム送信📩
2. 外部サービスWebhook受信🔔
3. 画像をサムネ化🖼️
4. 毎朝9時に集計してFirestoreに保存⏰
5. AIで「リリース前チェックリスト」を自動生成🤖🧾

**提出物（自分用メモでOK）**

* 選んだ2つ
* 置き場（Functions / Cloud Run）
* 理由（1行でOK）

---

## 8) チェック✅✅✅

* [ ] Hosting から `/api/**` を rewrite して、同一ドメインで API を動かせる🌐
* [ ] Functions は Node 20/22 が主力で、18 は非推奨扱いだと説明できる🟩 ([Firebase][1])
* [ ] Cloud Run なら .NET 8 / Python 3.13 なども選べる（用途が違う）🟦🐍 ([Google Cloud Documentation][3])
* [ ] AI Logic / Genkit / MCP / Gemini CLI を「設計の補助輪」として使える🤖 ([Firebase][5])

---

次の章（第20章）は、この「サーバー置き場」の上に **AI合体（手順書・自動チェック・最終完成）** を乗せて、いよいよ“実務っぽいリリース”に仕上げますよ🏁🔥😆

[1]: https://firebase.google.com/docs/functions/get-started "Get started: write, test, and deploy your first functions  |  Cloud Functions for Firebase"
[2]: https://firebase.google.com/docs/functions/manage-functions "Manage functions  |  Cloud Functions for Firebase"
[3]: https://docs.cloud.google.com/functions/docs/runtime-support "Runtime support  |  Cloud Run functions  |  Google Cloud Documentation"
[4]: https://firebase.google.com/docs/hosting/full-config "Configure Hosting behavior  |  Firebase Hosting"
[5]: https://firebase.google.com/docs/ai-logic?utm_source=chatgpt.com "Gemini API using Firebase AI Logic - Google"
[6]: https://firebase.google.com/docs/functions/oncallgenkit?utm_source=chatgpt.com "Invoke Genkit flows from your App | Cloud Functions for Firebase"
[7]: https://firebase.google.com/docs/ai-assistance/gemini-in-firebase?utm_source=chatgpt.com "Gemini in Firebase - Google"
[8]: https://firebase.google.com/docs/ai-assistance/mcp-server?utm_source=chatgpt.com "Firebase MCP server | Develop with AI assistance - Google"
[9]: https://firebase.blog/posts/2025/10/firebase-mcp-server-ga/ "It’s graduation day for the Firebase MCP Server"
[10]: https://firebase.google.com/docs/ai-assistance/prompt-catalog?hl=ja "Firebase の AI プロンプト カタログ  |  Develop with AI assistance"
