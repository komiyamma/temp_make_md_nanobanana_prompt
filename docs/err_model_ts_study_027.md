# 第27章：ログ設計① 何を残す？（安全に）🔎🧾🔒

ある日、障害が起きました⚡
「どこで失敗したの？」「誰の操作？」「何が原因？」って追いたいのに…ログが足りない😭
逆に、ログに**個人情報やトークン**が出てて大事故💥 …も最悪です🙈

この章では、「あとで原因に辿りつける」＋「危険なものは残さない」を両立するログ設計を身につけます💪✨
（ログは“デバッグのためのメモ”じゃなくて、“運用のための設計物”だよ〜📦）

---

## 1) ログって何のため？（目的が決まると、残すものも決まる）🎯🧭

![err_model_ts_study_027_logging_purpose_tripod.png](./picture/err_model_ts_study_027_logging_purpose_tripod.png)



ログの主な用途はこの3つ👇

* **障害対応**：いつ・どこで・何が起きた？を追う🚑
* **原因調査**：再現しにくい不具合を、あとから解剖する🧪
* **セキュリティ/監査**：不正っぽい動きを検知したい🕵️‍♀️

OWASPも「セキュリティ観点のログ設計」を強く推してます。闇雲に出すと危ないよ、って方向性が明確です🔒 ([OWASP Cheat Sheet Series][1])

---

## 2) 大原則：ログは「最小限」＋「追跡できる」＋「漏らさない」🧡🔍🙈

![err_model_ts_study_027_log_filter_principle.png](./picture/err_model_ts_study_027_log_filter_principle.png)



### ✅ 最小限（Data Minimization）

必要以上に“生データ”を残さない。
**“見たい情報”** と **“残していい情報”** は別です⚖️

### ✅ 追跡できる（Reproducible）

あとから「一本道」で追えるように、**毎回同じ形（構造化）**で残す📦

### ✅ 漏らさない（Secrets/PII）

ログは人が読むもの…だからこそ、漏れると最悪😱
Sentryみたいな監視ツールでも「送る前にセンシティブ情報をスクラブ（除去）できる」仕組みが前提になってます🧽 ([Sentry Docs][2])

![安全なログ金庫：秘密情報を守りつつ記録する[(./picture/err_model_ts_study_027_safe_log_vault.png)

---

## 3) まず決めよう：ログの「1行フォーマット（設計図）」📐🧾

![err_model_ts_study_027_structured_vs_unstructured.png](./picture/err_model_ts_study_027_structured_vs_unstructured.png)



おすすめは **“構造化ログ（JSON）”**。
OpenTelemetryもログを「ただの文字列」じゃなく、**イベント（LogRecord）**として扱えるデータモデルを定義してます📦✨ ([OpenTelemetry][3])



![err_model_ts_study_027_log_fields_backpack.png](./picture/err_model_ts_study_027_log_fields_backpack.png)

### 🧩 最低限入れたい項目（Must）✅

* `timestamp`：いつ🕒
* `level`：重要度（debug/info/warn/error）🚦
* `event`：何が起きた？（短いイベント名）🏷️
* `message`：人間向け説明（短く）💬
* `component`：どの機能/層？（例: auth, payments）🧱
* `result`：成功/失敗（ok/err）🎲
* `errorCode`：失敗なら“機械で扱えるコード”🏷️

### 🧁 あると強い（Should）✨

* `userId`：ただし **生のメール等は避ける**（後述）🙂
* `operation`：ユースケース名（例: “Checkout”）🛒
* `latencyMs`：遅い原因に刺さる⏱️
* `retryable`：リトライ可能？🔁

> 次の第28章で `requestId` を入れて“一本道”にするよ🧵（ここでは先に伏線だけ☺️）

---

## 4) 絶対に残しちゃダメ（またはマスク必須）🙅‍♀️🚫

![err_model_ts_study_027_dangerous_log_items.png](./picture/err_model_ts_study_027_dangerous_log_items.png)



OWASPのログ指針でも「センシティブ情報をログに入れない」ことが強調されます🔒 ([OWASP Cheat Sheet Series][1])
具体的にNG例いくよ〜💥

### 🚨 Secrets（秘密情報）

* パスワード、ワンタイムコード
* APIキー、Bearerトークン、OAuthアクセストークン
* セッションID、Cookie丸ごと
* 署名（HMAC）材料、秘密鍵

→ トークンがログに出ると「なりすまし」一直線😱（実例系の説明も多い） ([Guidewire Documentation][4])

### 🚨 PII（個人情報）※扱い注意

* 氏名、住所、電話、メール
* クレカ番号、口座、身分証番号
* 生年月日など

### 🚨 “まるごと”系（地雷）💣

* HTTPリクエスト/レスポンスbody全量
* フォーム入力値全量
* ヘッダ全量（Authorization混ざる…！）

---

## 5) 安全に残すテクニック（実務で効くやつ）🛡️✨

![err_model_ts_study_027_redaction_technique.png](./picture/err_model_ts_study_027_redaction_technique.png)



### 5-1) ブラックリストより「ホワイトリスト」✅

**残していい項目だけを選ぶ**（allow-list）方が事故りにくいです👍
「とりあえず全部ログ」は、未来の自分を殴るやつ🥲

### 5-2) どうしても必要なら “マスク/短縮/ハッシュ” 🥷

* メール → `a***@example.com` みたいに部分マスク✂️
* トークン → 先頭4文字だけ `abcd…`（ただし原則は残さない）
* userId → 内部の数値ID（PIIじゃない形）に寄せる

### 5-3) ログ出力時点で自動redact（超つよ）🧽

Nodeで人気の **Pino** は `redact` で特定パスを自動マスクできます。公式ドキュメントでも仕様がまとまってるよ📘 ([GitHub][5])

---

## 6) TypeScript実装例：安全なロガーを“最初に”作る🧰🧡

![err_model_ts_study_027_pino_redaction.png](./picture/err_model_ts_study_027_pino_redaction.png)



ポイントは👇

* ログは**構造化（オブジェクト）**
* センシティブは**redact**
* “何を残すか”を**型で縛る**（ログ用の型）✨

```ts
import pino from "pino";

type LogLevel = "debug" | "info" | "warn" | "error";

type SafeLogBase = {
  event: string;          // 例: "user.login.failed"
  message: string;        // 人間向け（短く）
  component: string;      // 例: "auth"
  result: "ok" | "err";
  userId?: string;        // 内部IDなど（メールは避ける）
  operation?: string;     // 例: "Login"
  latencyMs?: number;
  errorCode?: string;     // 例: "AUTH_INVALID_CREDENTIALS"
  retryable?: boolean;
};

export const logger = pino({
  level: "info",
  // ✅ “ログに混ざりがち”なものを強制マスク
  redact: {
    paths: [
      "*.password",
      "*.pass",
      "*.token",
      "*.accessToken",
      "*.refreshToken",
      "*.authorization",
      "*.cookie",
      "*.secret",
      "req.headers.authorization",
      "req.headers.cookie",
    ],
    censor: "[REDACTED]",
  },
});

export function log(level: LogLevel, base: SafeLogBase, extra?: Record<string, unknown>) {
  // ✅ extra を付けるときも、できるだけ “許可した情報”だけにする意識で！
  logger[level]({ ...base, ...extra });
}
```

Pinoの `redact` は「初期化時に設定して、ユーザー入力からパスを作るな」みたいな注意も含めてちゃんと説明されています🔒 ([GitHub][5])

---

## 7) エラーをログに残すときのコツ（“事故らない”）😇🧯

### ✅ 残すと強い

* `errorCode`（設計した分類コード）
* `error.name` / `message`（必要最小限）
* `stack`（サーバ側では重要。でも出しすぎ注意）

### ❌ やりがち事故

* `err` に **リクエストbody丸ごと**が混ざってる（SDKが入れることある😭）
* `stack` に **個人情報が混ざって**いる（入力値を例外メッセージに入れると起きる）

---

## 8) ミニ演習📝：ログ項目チェックリストを作ろう✅✨

### Step1：3つの箱を作る📦📦📦

* ✅ **必須（Must）**
* 🌟 **あると助かる（Should）**
* 🚫 **禁止（Never）**

### Step2：あなたのアプリ想定で10個ずつ書く✍️

### Step3：危ないログ例を3つ作って、改善する😆💥

例）

* 🚫「ログイン失敗: email=..., password=...」
* 🚫「API呼び出し: Authorization: Bearer ...」
* 🚫「注文失敗: requestBody=（全部）」

→ ✅「userId（内部ID）」「errorCode」「operation」「retryable」みたいに置き換える💡

---

## 9) AI活用🤖：ログ設計を“監査”させるプロンプト集👮‍♀️✨

### 🔎 危険ログ検出

* 「このコードのログ出力で、個人情報/秘密情報が漏れる可能性がある箇所を指摘して。修正案も出して」

### ✅ チェックリスト生成

* 「この機能（◯◯）の障害調査に必要なログ項目を、Must/Should/Neverで提案して」

### 🧽 redact設計

* 「このログ構造に対して、Pinoのredact paths案を作って。なぜその項目が危険かも説明して」

Sentryのような監視ツールでも「センシティブ情報を送らない／送る前にスクラブする」が前提だから、AIに“漏えい観点レビュー”をやらせるのは相性いいよ🧽✨ ([Sentry Docs][2])

---

## 10) まとめ🎀（この章でできるようになったこと）✅

* ログの目的から、残す項目を設計できる🎯
* 「構造化ログ（JSON）」で、毎回同じ形にできる📦
* PII/Secretsを避ける・マスクする方針が作れる🙈🔒
* redact（自動マスク）で“うっかり事故”を防げる🧽

OpenTelemetryのログデータモデルみたいに、ログを“イベント”として扱って相関（トレース等）も見据えられる設計が主流になってきてるよ📈✨ ([OpenTelemetry][3])

---

次の第28章は、いよいよ **requestId/correlationId** で「ログを一本道にする」やつだよ〜🧵🚶‍♀️✨

[1]: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html?utm_source=chatgpt.com "Logging - OWASP Cheat Sheet Series"
[2]: https://docs.sentry.io/security-legal-pii/scrubbing/advanced-datascrubbing/?utm_source=chatgpt.com "Advanced Data Scrubbing"
[3]: https://opentelemetry.io/docs/specs/otel/logs/data-model/?utm_source=chatgpt.com "Logs Data Model"
[4]: https://docs.guidewire.com/security/secure-coding-guidance/logging-sensitive-information-credentials?utm_source=chatgpt.com "Logging Sensitive Information - Credentials"
[5]: https://github.com/pinojs/pino/blob/main/docs/redaction.md?utm_source=chatgpt.com "pino/docs/redaction.md at main · pinojs/pino"
