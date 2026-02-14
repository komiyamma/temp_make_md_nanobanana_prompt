# 第13章：エラーカタログを作ろう（一覧で管理）📚🏷️

## 今日のゴール（この章の成果物）🎯✨

この章を終えると、あなたのアプリの「失敗」を **1枚の台帳（カタログ）** にまとめて、

* ✅ エラーが“散らからない”
* ✅ 表示文言がブレない（UXが安定）
* ✅ API/ログ/テストと **1対1でつながる**
* ✅ 新規追加・変更のレビューが超ラク

…って状態にできます😊📋

---

## 1) エラーカタログって何？なんで必要？🤔📚

![Error Catalog Book](./picture/err_model_cs_study_013_catalog_book.png)

エラーカタログは、ざっくり言うと **「エラーの辞書」** です📖✨
コードのあちこちに `throw new ...("メッセージ")` が散っていくと、

* 同じ意味なのにメッセージが違う😵
* エラーコードが重複する😱
* どれがユーザーに見えていい文言か分からなくなる🌀

…になりがち。
だから **「一覧で決めて、そこから使う」** にすると、設計が一気に安定します💪🌸

---

![err_model_cs_study_013_format_choice.png](./picture/err_model_cs_study_013_format_choice.png)

## 2) どの形式で作る？（おすすめ2択）🗂️✨

どっちでもOK。大事なのは **“一箇所に集約”** です😊

### A. Markdown（おすすめ！Gitで差分が見やすい）📝✨

* `docs/error-catalog.md` みたいに置く
* PRで差分レビューが楽👏

### B. Excel（チームで眺めやすい）📊✨

* フィルタ・並び替えが強い💡
* ただし差分レビューはMarkdownより弱め

---

![err_model_cs_study_013_catalog_fields.png](./picture/err_model_cs_study_013_catalog_fields.png)

## 3) カタログに入れる項目（これだけで強い）📋✨

「最低限これが揃ってると運用で困りにくい」セットです😊

### 必須カラム（まずはここから）✅

* **Code**：エラーコード（例：`ORDER_STOCK_SHORTAGE`）
* **Category**：分類（Domain / Infra / Bug）
* **Title**：短い要約（人間が一覧で見て分かる）
* **UserMessage**：画面に出す文言（やさしい日本語）🫶
* **DevDetail**：開発者向け説明（ログに載せたい内容）🔧
* **Action**：推奨アクション（例：再試行/問い合わせ/入力修正）
* **Retryable**：再試行して良い？（true/false）🔁
* **LogLevel**：Info/Warn/Error など（運用で効く）🔎

### APIをやるなら追加（あとで第21〜22章につながる）🌐✨

* **HttpStatus**：400/404/409/500…など
* **ProblemType**：`type` に入れるURI（または識別子）
* **ProblemTitle**：`title` に入れる短い題名

Problem Details は RFC 9457 で標準化されていて、`type/title/status/detail/instance` などの形で返せます🧾✨（Content-Type は `application/problem+json` が登録されています） ([RFCエディタ][1])

---

![err_model_cs_study_013_naming_rules.png](./picture/err_model_cs_study_013_naming_rules.png)

## 4) エラーコードの命名ルール（ここが9割）🏷️✨

エラーコードは **“変えにくい識別子”** なので、最初にルールを決めるのが超大事😊

### おすすめルール（迷ったらこれ）✅

* **英大文字 + アンダースコア**：`PAYMENT_CARD_DECLINED`
* **意味が分かる名詞＋状態**：`ORDER_NOT_FOUND`
* **HTTPステータスを埋め込まない**（後で変えたくなるから）🙅‍♀️
* **文言を埋め込まない**（翻訳や表現変更で死ぬ）🙅‍♀️

### “チームで事故りやすい”例（避けたい）😵

* `ERROR_001`（意味が分からない）
* `BAD_REQUEST_...`（ステータス変更で破綻）
* `INVALID` だけ（何が？ってなる）

---

![err_model_cs_study_013_user_vs_dev_message.png](./picture/err_model_cs_study_013_user_vs_dev_message.png)

## 5) UserMessage と DevDetail を分けるコツ🫶🔧

ここ、初心者が一番やりがちポイント！

### UserMessage（画面に出す）🪞

* ✅ やさしい
* ✅ 次に何をすればいいかが分かる
* ❌ 例外名やSQLやURLなど内部情報は出さない

### DevDetail（ログに出す）🧰

* ✅ 原因特定に必要な情報（例外、外部API名、キー、相関IDなど）
* ✅ 後で検索できるキーワードを入れる
* ❌ 個人情報や秘密情報は入れすぎない（必要最小限）🔒

---

![err_model_cs_study_013_catalog_example.png](./picture/err_model_cs_study_013_catalog_example.png)

## 6) 例：推し活グッズ購入管理🛍️💖（カタログ10件サンプル）

「在庫・予算・購入」あたりで作る例だよ😊
（この章は“台帳づくり”が主役なので、コードより先に台帳！）

| Code                     | Category | Title     | UserMessage                      | Action    | Retryable | LogLevel | HttpStatus |
| ------------------------ | -------- | --------- | -------------------------------- | --------- | --------- | -------- | ---------- |
| ORDER_STOCK_SHORTAGE     | Domain   | 在庫不足      | 在庫が足りません。数量を減らすか、入荷をお待ちください🥲    | 数量を変更     | false     | Info     | 409        |
| ORDER_BUDGET_EXCEEDED    | Domain   | 予算超過      | 予算を超えています。金額を確認してください💸          | 金額を見直す    | false     | Info     | 409        |
| ORDER_ITEM_NOT_FOUND     | Domain   | 商品が見つからない | 商品が見つかりませんでした🔎                  | 商品を選び直す   | false     | Info     | 404        |
| ORDER_ALREADY_PURCHASED  | Domain   | 重複購入      | すでに購入済みです🧾                      | 履歴を確認     | false     | Info     | 409        |
| USER_INPUT_INVALID       | Domain   | 入力不正      | 入力内容に不備があります。赤い項目を確認してください✍️     | 入力を修正     | false     | Info     | 400        |
| DB_TIMEOUT               | Infra    | DBタイムアウト  | ただいま混み合っています。少し待って再試行してください⏳     | 再試行       | true      | Warn     | 503        |
| EXTERNAL_API_UNAVAILABLE | Infra    | 外部API停止   | 通信に失敗しました。時間をおいて再試行してください📡      | 再試行       | true      | Warn     | 503        |
| NETWORK_DNS_FAILURE      | Infra    | 名前解決失敗    | 通信に失敗しました。ネットワークを確認してください🌐      | 環境を確認     | true      | Warn     | 503        |
| UNEXPECTED_EXCEPTION     | Bug      | 想定外例外     | 予期しない問題が発生しました。時間をおいて再度お試しください🙏 | 再試行/問い合わせ | false     | Error    | 500        |
| INVARIANT_VIOLATION      | Bug      | 不変条件違反    | 予期しない問題が発生しました🙏                 | 問い合わせ     | false     | Error    | 500        |

HTTPエラーの返し方（ステータスやエラー情報の持ち方）は、Microsoft系APIでも “コードとメッセージをセットで返す” 形式がよく使われています ([Microsoft Learn][2])

---

![err_model_cs_study_013_operational_rules.png](./picture/err_model_cs_study_013_operational_rules.png)

## 7) “運用で強くなる”エラーカタログ運用ルール（超おすすめ）🧠🔁

### ルール①：新しいエラーを作るときは「先に台帳」📋✨

* コードを書く前に、1行追加してから実装する
* これだけで散らかりが激減😊

### ルール②：PRのチェックリストにする✅

* [ ] Codeは一意？
* [ ] Categoryは合ってる？
* [ ] UserMessageは内部情報を漏らしてない？
* [ ] Retryableの判断は妥当？
* [ ] HttpStatusは妥当？

### ルール③：削除しない、非推奨にする（必要なら）🧓

クライアントやログ分析が死ぬので、消すより「Deprecated」列を足して運用が安全👍

---

## 8) ミニ演習（30〜60分）🧪✨

### 演習A：あなたのアプリ用に “最低15件” 作る📋

1. Domain を 8件（入力ミス、在庫、期限、権限など）💗
2. Infra を 5件（DB/HTTP/Timeout）🌩️
3. Bug を 2件（想定外、Invariant）⚡

### 演習B：3件だけ “UserMessage改善” をやる🫶

* 「何をすればいいか」が含まれてる？
* 「不安を煽らない」トーンになってる？😊

---

## 9) AI活用（この章のベストな使い方）🤖✅

AIは **“案出し・漏れチェック・言い換え”** が超得意！

### そのまま使えるプロンプト例🧠✨

* 「推し活グッズ購入管理のドメインエラーを20個、Code/Title/UserMessage/Action 付きで提案して」
* 「次のエラーカタログを見て、重複・曖昧・分類ミスを指摘して」
* 「UserMessage を“やさしい短文”に直して。内部情報は絶対に入れないで」

最後の判断（分類やRetry可否）はあなたがやるのが安全だよ🤝✨

---

## 10) まとめ（第13章のコア）🌸

* エラーカタログは **“エラーを散らさないための地図”** 🗺️
* まずは **Code / Category / UserMessage / Action / Retryable** を揃える📋
* APIまで見据えるなら **RFC 9457 の Problem Details** にもつながる🧾✨ ([RFCエディタ][1])

---

次、やるなら（第14章につながるやつ）😊👉
このカタログの1行を、`record`（エラー型）として表現して、`switch` で分岐できるようにしていこうね🧷✨

[1]: https://www.rfc-editor.org/rfc/rfc9457.html?utm_source=chatgpt.com "RFC 9457: Problem Details for HTTP APIs"
[2]: https://learn.microsoft.com/en-us/rest/api/storageservices/status-and-error-codes2?utm_source=chatgpt.com "Status and error codes (REST API) - Azure Storage"
