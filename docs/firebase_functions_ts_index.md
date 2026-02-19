# Functions：HTTP/イベント/スケジューラーで裏側を作る⚙️⏰：教材アウトライン（20章）

## 到達イメージ（この20章でできるようになること）🎯

* HTTPで **自分のAPI** を作って公開できる🌐
* Firestoreの更新をトリガーにして **自動処理** ができる⚡

![Cloud Functions Role Overview](./picture/firebase_functions_ts_index_overview.png)

* スケジュールで **定期実行（Cron）** ができる⏰([Firebase][2])
* そして最後に **Firestore更新→Slack通知** を完成させる📨✨([Slack開発者ドキュメント][3])
* 開発はAI（Antigravity / Gemini CLI）で加速する🤖🧰([Firebase][4])

---

## 1章：Functionsって何？「裏側」を置く場所の全体像🗺️

* 🎯 狙い：フロントとFunctionsの役割分担がわかる🙂
* 📚 キーワード：HTTP / イベント / スケジュール / “サーバレス”
* 🛠️ 手を動かす：例を見て「どの処理をFunctionsに置くべきか」仕分けする✍️
* ✅ チェック：「秘密情報」「集計」「通知」「重い処理」がフロントNGな理由を説明できる

## 2章：2nd genを選ぶ理由（ざっくりでOK）🚀

* 🎯 狙い：なぜ2nd gen推しなのか腹落ちする
* 📚 キーワード：Cloud Runベース / 同時処理（concurrency）/ 冷スタート
* 🛠️ 手を動かす：1st gen/2nd genの違いを“言葉で”まとめる📝
* ✅ チェック：新規は2nd gen中心で迷わなくなる([Firebase][1])

## 3章：ランタイムと言語の選び方（Node / Python / それ以外）🧩

* 🎯 狙い：何で書けるかを整理して迷子にならない
* 📚 キーワード：Node.js / Python / ランタイム指定
* 🛠️ 手を動かす：

  * Node：Node.js **20 or 22** が現役、18は非推奨…みたいな位置づけを把握👀([Firebase][5])
  * Python：**3.10〜3.13（デフォルト3.13）** を把握👀([Firebase][6])
* ✅ チェック：「今回はTS中心で、必要ならPythonも使える」状態になる

## 4章：最小セットアップ（CLI初期化→1個デプロイ）🌱

* 🎯 狙い：「動いた！」を最速で作る😆
* 📚 キーワード：firebase init / deploy / codebase
* 🛠️ 手を動かす：Functionsを初期化して、HelloなHTTP関数をデプロイ
* ✅ チェック：デプロイが成功し、URLにアクセスしてレスポンスが返る
* 🤖 AI活用：Gemini CLIのFirebase拡張に“初期化/テンプレ生成”を手伝わせる([Firebase][4])

## 5章：TypeScriptの基本構成（読みやすさ命）🧱

* 🎯 狙い：初心者でも破綻しないフォルダ設計にする
* 📚 キーワード：src/ 分割 / services / utils / types
* 🛠️ 手を動かす：HTTP・Firestore・共通処理を分離する

![Functions Folder Structure](./picture/firebase_functions_ts_index_folder_structure.png)

* ✅ チェック：「どこに何を書くか」迷いが減る

---

## 6章：HTTPトリガー入門（Web APIの入口）🌐

* 🎯 狙い：onRequestでAPIを作れる
* 📚 キーワード：onRequest / Request / Response
* 🛠️ 手を動かす：`GET /health` を作る（監視にも使える）
* ✅ チェック：ブラウザで叩いてJSONが返る

## 7章：HTTPでJSONを正しく扱う（入力と出力）📦

* 🎯 狙い：APIっぽい形になる
* 📚 キーワード：JSON / status code / エラーレスポンス
* 🛠️ 手を動かす：`POST /echo`（入力を検証して返す）
* ✅ チェック：400/200を使い分けできる

## 8章：CORSとセキュリティの最初の壁🧱🔒

* 🎯 狙い：フロントから呼ぶ時の“つまずき”を潰す
* 📚 キーワード：CORS / origin / preflight
* 🛠️ 手を動かす：許可originを限定して呼び出し確認
* ✅ チェック：「なんでCORSが要るの？」を一言で言える

## 9章：Callable（onCall）で“認証つきAPI”を楽にする🔐✨

* 🎯 狙い：フロントから安全に呼ぶ王道を掴む
* 📚 キーワード：onCall / Auth連携 / App Check連携
* 🛠️ 手を動かす：ログインユーザーだけ実行できるCallableを作る
* ✅ チェック：未ログインだと弾かれる
* 📌 根拠：Callableの仕組み（プロトコル）

---

## 10章：設定と秘密情報（APIキーをコードに書かない）🗝️🧯

* 🎯 狙い：事故りがちな「秘密の管理」を最初に覚える
* 📚 キーワード：Secret Manager / defineSecret / 環境差分
* 🛠️ 手を動かす：Slack Webhook URLをSecretとして扱う準備
* ✅ チェック：「リポジトリに秘密を置かない」が習慣になる

## 11章：Firestoreイベント入門（自動処理の気持ちよさ）⚡

* 🎯 狙い：Firestore更新でFunctionsが動く
* 📚 キーワード：onDocumentCreated / onDocumentWritten
* 🛠️ 手を動かす：`messages/{id}` 作成→加工して別フィールドに保存

![Firestore Trigger Event](./picture/firebase_functions_ts_index_db_trigger.png)

* ✅ チェック：更新ループ（無限発火）を避ける考え方がわかる([Firebase][7])

## 12章：イベント処理の設計（冪等・重複・再試行）🧠

* 🎯 狙い：「たまに2回動いた」でも壊れない設計へ
* 📚 キーワード：idempotent / retry / 重複排除
* 🛠️ 手を動かす：処理済みフラグ or イベントIDでガードする
* ✅ チェック：二重通知を防ぐ作戦を言える

## 13章：通知・集計の基本形（実務っぽい）📣📊

* 🎯 狙い：「通知」「カウンタ更新」みたいな王道パターンを覚える
* 📚 キーワード：集計ドキュメント / トランザクション的発想
* 🛠️ 手を動かす：コメント数カウンタを更新する
* ✅ チェック：「どこに集計を置くか」説明できる

---

## 14章：スケジュール関数（Cronで定期実行）⏰

* 🎯 狙い：毎日/毎時の自動処理ができる
* 📚 キーワード：onSchedule / cron / timezone
* 🛠️ 手を動かす：毎朝レポートを作る（Firestoreに書く）

![Scheduled Functions (Cron)](./picture/firebase_functions_ts_index_cron_schedule.png)

* ✅ チェック：スケジュールがCloud Schedulerで動くイメージがある([Firebase][2])

## 15章：運用の基本（ログ、エラー、アラートの入口）🧯👀

* 🎯 狙い：落ちても直せる人になる
* 📚 キーワード：Logging / structured log / エラー追跡
* 🛠️ 手を動かす：重要ログ（開始/成功/失敗）を整える
* ✅ チェック：どこを見れば原因に辿れるか分かる

## 16章：ローカル検証（最小だけEmulator）🧪

* 🎯 狙い：本番を汚さず試すクセをつける
* 📚 キーワード：Functions emulator / Firestore emulator
* 🛠️ 手を動かす：ローカルでイベント→関数実行を確認
* ✅ チェック：本番に触らず確認できる流れがある

---

## 17章：AIを“裏側”に組み込む（Genkit連携の入口）🤖🔥

* 🎯 狙い：FunctionsでAIワークフローを回す入口を作る
* 📚 キーワード：Genkit / onCallGenkit / ストリーミング
* 🛠️ 手を動かす：短文を「整形/要約」して返すCallableを作る

![AI Integration in Functions](./picture/firebase_functions_ts_index_ai_integration.png)

* ✅ チェック：「AIの出力は常に正しいわけじゃない」前提のガードが入る([Firebase][8])

## 18章：AIで開発を速くする（Antigravity / Gemini CLI）🛸💻

* 🎯 狙い：実装・修正・テストの“下ごしらえ”をAIにやらせる
* 📚 キーワード：Firebase MCP server / Gemini CLI拡張 / slash commands
* 🛠️ 手を動かす：

  * Gemini CLIのFirebase拡張を使って、構成チェックや手順書生成をさせる
  * MCP経由で「設定・参照」系の作業を補助させる
* ✅ チェック：AIに丸投げせず「レビュー前提」で回せる([Firebase][4])

  * 参考：MCP serverはAntigravityやGemini CLIなどから利用できる([Firebase][9])

---

## ここからミニ課題：Firestore更新 → Slack通知 📩✨（3章で完成）

## 19章：Slack通知の準備（Webhook + Secret）🔔🗝️

* 🎯 狙い：Slackに安全に投げる準備が整う
* 📚 キーワード：Incoming Webhooks / Secret / メッセージ整形
* 🛠️ 手を動かす：Webhookを作ってSecretに登録→テスト送信

![Slack Notification Flow](./picture/firebase_functions_ts_index_slack_webhook.png)

* ✅ チェック：Webhook URLがコードやGitに出てこない([Zenn][10])

## 20章：Firestore更新→Slack通知を完成（実務の形に）🏁🔥

* 🎯 狙い：実際のアプリ運用で使える自動通知が完成
* 📚 キーワード：onDocumentWritten / 重複防止 / 失敗時リトライ設計
* 🛠️ 手を動かす：

  * `reports/{id}` や `posts/{id}` 更新でSlackへ通知
  * 連投防止（処理済みフラグ、イベントID、時間窓など）を入れる
* ✅ チェック：

  * 「更新→通知」が安定して動く
  * 失敗ログから原因が追える
  * “本番で怖いポイント”が言語化できる([Firebase][7])

---

## 補足：.NETや“別言語”はどう扱う？🧩

![Multi-Language Runtime Map](./picture/firebase_functions_ts_index_runtime_map.png)

* Firebase Functions自体は **Node/TS** が主軸で、**Pythonも利用可能（3.10〜3.13）** です([Firebase][6])
* もし **.NET** を“関数ランタイムとして”使うなら、Firebaseの外側で **Cloud Run functions**（.NET 8 など）に置いて、HTTPで連携するのが現実的です（サポート状況は公式のランタイム表で確認できる）([Google Cloud Documentation][11])

  * ここでのC#は、主にAdmin SDKでの運用ツール/バッチ側（別枠）として育てるのが相性良いです🙂

---


[1]: https://firebase.google.com/docs/functions/version-comparison?utm_source=chatgpt.com "Cloud Functions version comparison - Firebase - Google"
[2]: https://firebase.google.com/docs/functions/schedule-functions?utm_source=chatgpt.com "Schedule functions | Cloud Functions for Firebase - Google"
[3]: https://docs.slack.dev/tools/java-slack-sdk/guides/incoming-webhooks?utm_source=chatgpt.com "Incoming webhooks | Slack Developer Docs"
[4]: https://firebase.google.com/docs/ai-assistance/gcli-extension?utm_source=chatgpt.com "Firebase extension for the Gemini CLI"
[5]: https://firebase.google.com/docs/functions/manage-functions?utm_source=chatgpt.com "Manage functions | Cloud Functions for Firebase - Google"
[6]: https://firebase.google.com/docs/functions/get-started?utm_source=chatgpt.com "Get started: write, test, and deploy your first functions - Firebase"
[7]: https://firebase.google.com/docs/functions/firestore-events?utm_source=chatgpt.com "Cloud Firestore triggers | Cloud Functions for Firebase - Google"
[8]: https://firebase.google.com/docs/functions/oncallgenkit?utm_source=chatgpt.com "Invoke Genkit flows from your App | Cloud Functions for Firebase"
[9]: https://firebase.google.com/docs/ai-assistance/mcp-server?utm_source=chatgpt.com "Firebase MCP server | Develop with AI assistance - Google"
[10]: https://zenn.dev/tsubamejapan/articles/499998afd9660b?utm_source=chatgpt.com "Slack API 基本的な整理①：chat.postMessage APIテスター ..."
[11]: https://docs.cloud.google.com/functions/docs/runtime-support "Runtime support  |  Cloud Run functions  |  Google Cloud Documentation"
