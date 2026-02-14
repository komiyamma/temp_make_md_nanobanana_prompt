# 第21章：APIエラー設計① HTTPステータスの決め方🚦🌐

APIの失敗って、**「仕様」**として揃ってないとクライアント側がめちゃくちゃ困るの…😵‍💫
そこで今日は **HTTPステータスを“迷わず決めるルール”** を作って、エラーカタログに貼れる状態にするよ📌💕

---

## 1) 今日のゴール🎯✨

### できるようになること😊

* エラーを見て「何番のステータスにする？」を判断できる🚦
* **ドメイン / インフラ / バグ**の分類と、**4xx / 5xx**がブレなくなる🧭
* エラーカタログ（第13章）に **Status列**を足して運用できる📋✨

> ステータスは「骨格」🦴で、細かい情報は次章の **ProblemDetails（RFC 9457）** で返す感じだよ🧾✨ ([rfc-editor.org][1])

---

## 2) まず大原則：4xxと5xxの境界線🧠🚧

![Traffic Lights 200/400/500](./picture/err_model_cs_study_021_http_traffic_lights.png)

HTTPステータスは「誰が直すべき？」を伝える記号だよ📶

* **4xx（クライアントエラー）**：リクエストを直してね🙏（入力・権限・状態が合わない等）
* **5xx（サーバーエラー）**：サーバー側の問題だよ🥲（障害・依存先・想定外バグ）

この分類自体も、HTTPの標準的な扱いに沿ってるよ✨（ステータスはRFC 9110で整理されてる） ([MDNウェブドキュメント][2])

---

## 3) 3分類（ドメイン/インフラ/バグ）からの最短ルート🗺️✨

あなたのロードマップの「3分類」を、そのままステータスに落とすとこう👇

### ✅ 超ざっくり対応表（迷ったらココに戻る）🧩

* **ドメインエラー（業務ルール違反）** → だいたい **4xx**（主に 404 / 409 / 422 / 400）💗
* **インフラエラー（DB/ネット/外部API）** → だいたい **5xx**（主に 502 / 503 / 504）🌩️
* **バグ（不変条件違反）** → **500**（Fail Fastでログへ）⚡

![Status Decision Tree](./picture/err_model_cs_study_021_status_decision_tree.png)

---

## 4) ステータス決定の“判断フロー”🚦🔀（これを型にしよう！）

迷ったらこの順番でOK😊

1. **認証いる？** → 401 / 403 🔐
2. **そのリソース無い？** → 404 🔎
3. **入力が壊れてる？（形式）** → 400 ✍️
4. **入力は形式OKだけど、業務的に無理？** → 422（または409）💗
5. **状態の衝突？（二重登録/在庫競合/楽観ロック）** → 409（条件付きなら412/428も候補）⚔️
6. **レート制限？** → 429 ＋ Retry-After ⏳
7. **依存先がコケた？（外部API/ゲートウェイ）** → 502 🌐💥
8. **一時的に無理（DB落ち/メンテ/過負荷）** → 503 ＋ Retry-After 🛠️
9. **タイムアウト系** → 504（ゲートウェイ）/ 408（要求待ち）⌛
10. **それ以外の想定外** → 500 😇（=バグ/未知の事故）

Retry-After は **429/503** で「どれくらい待ってね」を伝えられるよ⏳✨ ([MDNウェブドキュメント][3])

---

## 5) よく使うステータス：実戦セット🍙✨

「推し活グッズ購入管理🛍️💖」っぽい例でいくね！

| ステータス                     | いつ使う？              | 例（推し活）                     | クライアントの行動              |
| ------------------------- | ------------------ | -------------------------- | ---------------------- |
| 400 Bad Request           | 形式がダメ（型/必須/JSON壊れ） | `quantity: "many"` みたいな型違い | 入力を直して再送✍️             |
| 401 Unauthorized          | 認証してない             | トークン無し                     | ログイン/再認証🔐             |
| 403 Forbidden             | 認証はあるが権限なし         | 他人の購入履歴にアクセス               | 権限不足を表示🙅‍♀️           |
| 404 Not Found             | リソースが無い            | `GET /items/999`           | 存在しない表示🔎              |
| 409 Conflict              | 状態の衝突（重複/競合）       | 在庫が同時購入で足りなくなった / 二重登録     | 状態更新してやり直し🔁           |
| 422 Unprocessable Content | 形式OKだが業務的に無理       | 予算オーバー / 期限切れ              | 内容を変えて再送💗             |
| 429 Too Many Requests     | 叩きすぎ               | 短時間に購入API連打                | 待って再試行⏳                |
| 500 Internal Server Error | 想定外（バグ）            | 不変条件違反が漏れた                 | 再試行は基本NG・問い合わせ誘導😵     |
| 502 Bad Gateway           | 依存先が変な応答           | 決済APIが壊れた                  | 少し待って/別手段案内🌐          |
| 503 Service Unavailable   | 一時的に使えない           | DBメンテ/過負荷                  | 待って再試行（Retry-After）🛠️ |
| 504 Gateway Timeout       | 依存先がタイムアウト         | 外部在庫APIが遅すぎ                | 待って再試行⌛                |

ステータス一覧や定義は、MDNがRFC 9110ベースでまとまってて読みやすいよ📚 ([MDNウェブドキュメント][2])

---

## 6) 「409 vs 422」ここが一番迷うやつ😆💥

![409 vs 422](./picture/err_model_cs_study_021_409_vs_422.png)

### 409 Conflict を選びやすいケース⚔️

* **リソースの状態と衝突**して処理できない
  例：在庫がもう無い、同時更新で競合、二重作成が発生

### 422 Unprocessable Content を選びやすいケース💗

* 入力は正しいけど、**業務ルール的に成立しない**
  例：予算オーバー、購入期限切れ、年齢制限など

> 迷ったらこう覚える：
> **409 = 状態のケンカ**⚔️ / **422 = ルール違反**📏💗

---

## 7) エラーカタログに「Status列」を足す📋✨（今日の成果物）

第13章のエラーカタログがこういう列だったとして👇

* Code / Title / UserMessage / Detail / Retryable / Action …

ここに **Status** を足すよ✅
さらにおすすめで **Retry-After（秒）** も列で持つと運用が楽⏳✨（429/503で使える） ([MDNウェブドキュメント][3])

---

## 8) ミニ演習✍️🎓（Statusを割り当てよう！）

次のエラーに、ステータスを決めてみてね😊（理由も1行で！）

1. `ITEM_NOT_FOUND`（商品IDが存在しない）
2. `INVALID_JSON`（JSONが壊れてる）
3. `BUDGET_EXCEEDED`（予算オーバー）
4. `OUT_OF_STOCK`（在庫不足）
5. `DUPLICATE_PURCHASE`（同一購入の二重送信）
6. `UNAUTHENTICATED`（ログインしてない）
7. `FORBIDDEN_ACCESS`（他人の購入にアクセス）
8. `RATE_LIMITED`（短時間に連打）
9. `PAYMENT_PROVIDER_DOWN`（決済APIが落ちてる）
10. `UNEXPECTED_NULL`（想定外nullで落ちた）

### 例の答え（こっそり答え合わせ）👀✨

1=404、2=400、3=422、4=409（or 422）、5=409、6=401、7=403、8=429、9=503 or 502、10=500
（9は「依存先が落ちた/変な応答」なら 502、「一時的に利用不可」なら 503 が多いよ🌐🛠️）

---

## 9) 実装イメージ（Result → HTTP）🧰✨

ここでは「ステータスに変換する場所」を **API境界**に置くのがポイントだよ🚪
（ドメインやアプリ層は “HTTPを知らない” ままにして守る🛡️）

### 最小APIの例：ErrorCodeでステータスを決める🎯

```csharp
app.MapPost("/purchases", async (CreatePurchaseRequest req, PurchaseService service) =>
{
    var result = await service.CreatePurchaseAsync(req);

    return result.Match(
        onSuccess: value => Results.Ok(value),
        onFailure: err =>
        {
            var status = err.Code switch
            {
                "INVALID_JSON" => StatusCodes.Status400BadRequest,
                "UNAUTHENTICATED" => StatusCodes.Status401Unauthorized,
                "FORBIDDEN_ACCESS" => StatusCodes.Status403Forbidden,
                "ITEM_NOT_FOUND" => StatusCodes.Status404NotFound,
                "DUPLICATE_PURCHASE" => StatusCodes.Status409Conflict,
                "OUT_OF_STOCK" => StatusCodes.Status409Conflict,
                "BUDGET_EXCEEDED" => StatusCodes.Status422UnprocessableEntity,
                "RATE_LIMITED" => StatusCodes.Status429TooManyRequests,
                "PAYMENT_PROVIDER_DOWN" => StatusCodes.Status503ServiceUnavailable,
                _ => StatusCodes.Status500InternalServerError
            };

            // 今日は「ステータス決め」が主役なのでボディは仮。
            // 次章で ProblemDetails(RFC 9457) にするよ🧾✨
            return Results.StatusCode(status);
        }
    );
});
```

ASP.NET Core側でも「ステータスが400以上＝エラー結果」として扱い、ProblemDetails生成の仕組みが用意されてる（次章でガッツリ使うよ🧾） ([Microsoft Learn][4])

---

## 10) AI活用🤖💬（今日の“いい使い方”）

### ✅ 割り当てのブレを消す質問テンプレ🧠

* 「このエラーは *クライアントが直す？サーバーが直す？* どっち？」
* 「409と422で迷ってる。状態衝突？ルール違反？で判定して！」
* 「このエラーに対して、クライアントが取るべき行動を1文で書いて！」

### ✅ エラーカタログ整形✍️

* 「このStatus割り当ての理由を、API仕様書っぽい短文にして」
* 「同じ意味のエラーが重複してないかチェックして」

---

## まとめ🍵✨

* まず **4xx/5xxの境界** を固定する🚧
* 次に **404/409/422/429/503/502/500** あたりの“定番セット”を握る🤝
* そしてエラーカタログに **Status列** を足して運用できる形へ📋✨
* ボディの統一は次章の **ProblemDetails（RFC 9457）** で完成🧾💕

---

次の第22章では、今日決めたステータスを土台にして
**Result → ProblemDetails（RFC 9457）** の変換マップを作って「機械にも人にも優しい」エラー応答に仕上げるよ〜🧾✨💪

[1]: https://www.rfc-editor.org/rfc/rfc9457.html?utm_source=chatgpt.com "RFC 9457: Problem Details for HTTP APIs"
[2]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status?utm_source=chatgpt.com "HTTP response status codes - MDN Web Docs - Mozilla"
[3]: https://developer.mozilla.org/ja/docs/Web/HTTP/Reference/Headers/Retry-After?utm_source=chatgpt.com "Retry-After - HTTP - MDN Web Docs"
[4]: https://learn.microsoft.com/en-us/aspnet/core/fundamentals/error-handling-api?view=aspnetcore-10.0 "Handle errors in ASP.NET Core APIs | Microsoft Learn"
