# 第15章：運用の基本（ログ、エラー、アラートの入口）🧯👀

## この章のゴール🎯

* 「動かない…😇」となったとき、**どこを見ればいいか**分かる
* ログを **“あとから自分が助かる形”** に整えられる
* **エラーの自動通知（アラート）** の入口まで作れる📣

---

## 1) まず覚える「3つの観測窓」🪟🪟🪟

![Three Observation Windows](./picture/firebase_functions_ts_study_015_01_three_windows.png)

## ① ログ（何が起きた？）🧾

* **Cloud Logging** に集まる（Functionsはここが中心）([Firebase][1])

## ② エラー一覧（どのクラッシュが多い？）💥

* **Error Reporting** に、未処理例外などがまとまる([Firebase][2])

## ③ アラート（気づける仕組み）🔔

* **Cloud Monitoring** のアラートは、**メトリクス**も**ログ**も条件にできる([Google Cloud Documentation][3])
* 「ERRORログが出たら通知」みたいな **ログベースアラート** も作れる([Google Cloud Documentation][4])

---

## 2) ログは「console.log」でもいいけど、できれば“logger”🧰✨

![Structured Logging](./picture/firebase_functions_ts_study_015_02_structured_log.png)

Cloud Functions は **logger SDK（Node / Python）** が用意されてて、**構造化ログ（structured data）** を出せます。これが超強いです💪([Firebase][1])

## logger の基本（TypeScript）🧩

* “重要度”が付けられる（debug/info/warn/error）
* JSONっぽく **キー付き情報** を付けられる（後で検索が楽）([Firebase][1])

```ts
import { info, warn, error, debug } from "firebase-functions/logger";

export function sampleLog(uid: string) {
  info("START sampleLog", { uid, step: "begin" });

  debug("debug detail", { uid, hint: "only for dev" });

  warn("something looks odd", { uid, retry: true });

  try {
    // 何か処理…
    info("OK sampleLog", { uid, step: "done" });
  } catch (e) {
    // ここが超重要👇
    error("NG sampleLog", e as Error);
    throw e;
  }
}
```

> ✅ **error() は Error Reporting にも飛ばせる**（運用が一気に楽）([Firebase][2])

---

## 3) “良いログ”の型：START / OK / NG 🧯✨

![Log Pattern Flow](./picture/firebase_functions_ts_study_015_03_log_pattern.png)

初心者が最速で強くなるログ設計はこれです👇

* `START`: 入口（何を始めた？誰の処理？）
* `OK`: 成功（どれくらい？結果は？）
* `NG`: 失敗（どこで？例外は？）

## ログに入れると便利な項目（テンプレ）🧠

* `function`: 関数名（手で書いてもOK）
* `uid`: 誰の処理か（Auth連携してるなら）
* `docPath` / `id`: Firestoreなら対象ID
* `eventId`: イベント系なら「このイベント」識別子
* `latencyMs`: 何msかかったか
* `version`: デプロイ世代（手で入れてもOK）

> 🔥コツ：**秘密（APIキー/トークン）や個人情報をログに出さない**
> ログは“チーム共有されがち＆長く残りがち”なので、マジで注意です🧯

---

## 4) ログを見る：最短は Firebase CLI 🖥️⚡（Windows）

ログを見る手段は複数あります（CLI / Cloud Console）。まずは CLI が楽です🧰([Firebase][1])

```bash
## ぜんぶ見る
firebase functions:log

## 特定の関数だけ
firebase functions:log --only <FUNCTION_NAME>
```

---

## 5) Cloud Logging で“原因に突き刺す”探し方🔎💡

## まずは「ERRORだけ」絞る😇➡️🙂

* Logs Explorer で `severity>=ERROR` を基本に
* “関数名っぽい文字列”や “uid” を追加で絞る

> Cloud Logging には **クエリの例（Query library）** もあるので、真似から入るのが早いです📚([Google Cloud Documentation][5])

## 実行単位でまとめて追う（execution ID）🧵

1st gen などでは、ログの `labels.execution_id` を使って「同じ実行のログ」を追えます([Firebase][6])

> 2nd gen（Cloud Run functions 側）では **LOG_EXECUTION_ID** で実行IDをログに出せる仕組みが案内されています（運用の武器）([Google Cloud Documentation][7])
> ※ここは“ちょい上級”なので、必要になったら導入でOK👌

---

## 6) Error Reporting：エラーを「一覧」で見れるようにする💥📌

![Error Reporting Grouping](./picture/firebase_functions_ts_study_015_04_error_grouping.png)

## 自動で入るケース

* **未処理例外** などは自動で Error Reporting に出る([Firebase][2])

## 手動で“ちゃんと飛ばす”なら error() ✅

`error("message", err)` の形にしておくと、**ログ＋エラー一覧**が揃います([Firebase][2])

---

## 7) アラートの入口：2種類だけ覚えよう🔔✨

![Alert Types Comparison](./picture/firebase_functions_ts_study_015_05_alert_types.png)

## A) メトリクスでアラート（王道）📈

例：

* エラー率が一定以上
* レイテンシが急に悪化
* 呼び出し回数が急増（バグ/攻撃/無限ループ疑い）

Cloud Monitoring のアラートは、**条件→インシデント→通知**の流れで動きます([Google Cloud Documentation][3])

## B) ログでアラート（最短で効く）🧾➡️🔔

例：

* `severity>=ERROR` のログが出たら通知
  ログベースのアラートは Logs Explorer から作れます([Google Cloud Documentation][4])

---

## 8) 通知先：Slack に飛ばすのが便利📣💬

![Slack Alert Flow](./picture/firebase_functions_ts_study_015_06_slack_flow.png)

Cloud Monitoring は **Slack 通知チャンネル**を作れます（手順も公式にある）([Google Cloud Documentation][8])

> ✅「アラートが来た→Slackで気づく→すぐ直す」
> これが“運用できてる感”を一気に出します🔥

---

## 9) AIで運用を楽にする（Gemini CLI / Firebase拡張）🤖🧰

![AI Ops Assistant](./picture/firebase_functions_ts_study_015_07_ai_ops.png)

Firebase の **Gemini CLI 拡張**を入れると、Firebase向けの能力が増えます。

* Firebase MCP server を自動で入れてくれる
* Firebase作業を補助するツールや、ドキュメント参照がしやすくなる([Firebase][9])

インストール例（参考）🧩([Firebase][9])

```bash
gemini extensions install https://github.com/gemini-cli-extensions/firebase/
```

## この章での“AIの使いどころ”💡

* 「この関数のログ設計、START/OK/NGのテンプレ作って」
* 「Logs Explorer のクエリを、エラーだけ拾う形で提案して」
* 「アラートが鳴った時の“手順書（runbook）”を1枚にして」

> ⚠️AIに貼るログや設定には、**秘密情報を混ぜない**（ここ超大事）🧯

---

## 10) ミニ実習：5分で“運用の入口”を作る🧪⏱️

## 手順🪜

1. Functions に `START/OK/NG` ログを入れる🧾
2. わざとエラーを起こす（例：throw）💥
3. Logs Explorer で `severity>=ERROR` で検索🔎
4. Error Reporting でエラーがまとまって見えるか確認📌([Firebase][2])
5. 「ERRORログが出たら通知」のログベースアラートを作る🔔([Google Cloud Documentation][4])

（できれば）通知先を Slack にして完成💬([Google Cloud Documentation][8])

---

## ✅ チェック（理解できたら勝ち）💯

* ログを見る場所が「ログ」「エラー一覧」「アラート」の3つに分かれるのを説明できる🪟
* logger を使って **structured data 付きログ**を出せる🧾✨([Firebase][1])
* `error()` を使うと Error Reporting にも出せる理由が分かる💥([Firebase][2])
* 「ログベースアラート」と「メトリクスアラート」の違いを一言で言える🔔([Google Cloud Documentation][4])

---

## 次につながる一言🚀

ここまでできると、**第20章（Firestore更新→Slack通知）**で落ちたときも、ログ→原因→修正がちゃんと回ります📩✨
「運用できる人」への第一歩、ここです🧯🔥

[1]: https://firebase.google.com/docs/functions/writing-and-viewing-logs "Write and view logs  |  Cloud Functions for Firebase"
[2]: https://firebase.google.com/docs/functions/reporting-errors "Report errors  |  Cloud Functions for Firebase"
[3]: https://docs.cloud.google.com/monitoring/alerts "Alerting overview  |  Cloud Monitoring  |  Google Cloud Documentation"
[4]: https://docs.cloud.google.com/logging/docs/alerting/log-based-alerts "Configure log-based alerting policies  |  Cloud Logging  |  Google Cloud Documentation"
[5]: https://docs.cloud.google.com/logging/docs/view/query-library?hl=ja&utm_source=chatgpt.com "サンプルクエリ | Cloud Logging"
[6]: https://firebase.google.com/docs/functions/writing-and-viewing-logs?utm_source=chatgpt.com "Write and view logs | Cloud Functions for Firebase - Google"
[7]: https://docs.cloud.google.com/functions/docs/release-notes?utm_source=chatgpt.com "Cloud Run functions (formerly known as Cloud Functions ..."
[8]: https://docs.cloud.google.com/monitoring/support/notification-options?hl=ja "通知チャンネルを作成して管理する  |  Cloud Monitoring  |  Google Cloud Documentation"
[9]: https://firebase.google.com/docs/ai-assistance/gcli-extension "Firebase extension for the Gemini CLI  |  Develop with AI assistance"
