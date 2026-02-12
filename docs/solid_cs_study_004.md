# 第04章：設計の超基本ことば（責務・依存・境界）🧠📌

この章は「SOLIDを読むための日本語をそろえる回」だよ〜😊💖
ここがふわっとしたままだと、後の章で「言ってることは分かるけど、どこを直せばいいの…？」って迷子になりがち🥺🌀
逆にここが分かると、設計の話が一気にスッと入ってくるよ🌸

---

## この章のゴール🎯✨

読み終わったら、次ができるようになるのが目標だよ💪😊

* 「責務＝変更理由」って言葉で説明できる📌✨
* 「依存＝影響の向き」って矢印で描ける➡️✨
* 「境界＝混ぜない線」って判断できる🧱✨
* “ぐちゃぐちゃコード”を見て、**責務・依存・境界のどれが破れてるか**見分けられる👀💡

---

## 0) 最新環境メモ（安心材料）🧰✨

この教材の前提に出てきた「最新環境」は、ちゃんと公式に揃ってるよ👍😊

* .NET 10 は 2025/11/11 リリースの LTS（長期サポート）だよ🛡️✨（2028年までサポート） ([Microsoft][1])
* C# 14 も 2025年11月に公開されてるよ🧩✨ ([Microsoft Learn][2])
* Visual Studio 2026 は .NET 10 と C# 14 を“追加設定なしで”サポートするよ✅ ([Microsoft Learn][3])

（※ここから先は、概念を覚えるのが主役だから、言語機能の細かい話は後回しでOKだよ〜😊💕）

---

## 1) 「責務」ってなに？📌😊（＝変更理由）

### ✅ 結論：責務は「やること」じゃなくて「変わる理由」だよ

![solid_cs_study_004_responsibility_sign.png](./picture/solid_cs_study_004_responsibility_sign.png)

よくある勘違い👇😵‍💫

* ❌「責務＝メソッド1個！」
* ❌「責務＝小さければいい！」

本質はこれ👇✨

* ✅ **責務＝そのコードが“変わる理由”**

つまり…

> 「このクラス、なんで変更することになる？」
> この答えが複数あるなら、責務が混ざってる可能性大だよ🚨😇

---

### 責務を見つける“3つの質問”💡💬

コードを見ながら、これを自分に聞いてみてね😊

1. **仕様変更が来るとしたら何が変わる？** 📝
2. **誰（どのチーム）がこの変更を要求しそう？** 👩‍💼👨‍💼
3. **このクラスの中に“違う種類の知識”が混ざってない？** 🧠🌀

   * 例：業務ルール、UI、DB、通信、ファイル、メール…ごちゃ混ぜ😵‍💫

---

### 例：ミニECだと「変更理由」はこう分かれる🛒✨

![solid_cs_study_004_change_reason_list.png](./picture/solid_cs_study_004_change_reason_list.png)

たとえば「注文」まわりって、変更が来そうな理由がいっぱいあるよね😳

* 値引きルールが変わる（セール、クーポン）🎫
* 支払い方法が増える（カード、Pay系）💳
* 送料計算が変わる（地域、サイズ）📦
* メール文面が変わる（キャンペーン文言）💌
* 保存先が変わる（DB種類、API化）🗄️

これ、全部1クラスで背負うと……
**変更のたびに全部が揺れる“地震ハウス”**になるよ🏚️💥😇

---

## 2) 「依存」ってなに？➡️😌（＝影響の向き）
![Bad Dependency Chain](./picture/solid_cs_study_004_bad_dependency_chain.png)


### ✅ 結論：依存は「AがBを使ってる」以上に、“変更が伝染する”こと

超ざっくり言うと👇

* **AがBに依存している**
  ＝ **Bが変わると、Aも直す羽目になりやすい** 😵‍💫

ここが大事なのは、SOLIDが全部「影響範囲を小さくするゲーム」だからだよ🎮✨

---

### 依存が生まれやすい“分かりやすいサイン”🚩

* `new` して具体クラスを作ってる🎁
* `static` を直呼びしてる📌
* 直接 `HttpClient` / DB / File / SMTP 触ってる🌐🗄️📁💌
* でっかいクラスをあちこちから呼び出してる📣

もちろん「依存＝悪」じゃないよ🙆‍♀️✨
**問題は、依存のせいで変更が広がること**だよ🔥

---

### 依存の矢印を描くコツ✏️➡️

![solid_cs_study_004_dependency_arrow_direction.png](./picture/solid_cs_study_004_dependency_arrow_direction.png)

矢印はこう考えるとミスりにくいよ😊

* **「呼ぶ側」→「呼ばれる側」**
* **「使う側」→「使われる側」**
* **「知ってる側」→「知られてる側」**

たとえば👇

* `OrderService` が `SqlConnection` を直接使う
  → `OrderService` ➡️ `SqlConnection`（DBの都合がOrderServiceに刺さる😇）

---

## 3) 「境界」ってなに？🧱✨（＝混ぜない線）

### ✅ 結論：境界は「ここから先は別の世界だよ」って線引き🌍✨

設計でよくある事故はこれ👇💥

* 業務ロジックの中に、DBや通信やUIの都合が混ざる😵‍💫

だから境界はこういう役目を持つよ👇

* **業務のルール（内側）** を守る🛡️
* 外の都合（DB/HTTP/ファイル/メール）を **境界で止める** 🚧
* 変更が来ても、**外側だけ差し替え**しやすくする🔁✨

イメージは「校舎（内側）と校門の外（外側）」🏫🚪
校門の外の事情（交通、天気、工事）を、校舎の授業に持ち込まない感じ😊☔🚧

---

### 境界があると何が嬉しいの？😍✨

![solid_cs_study_004_boundary_gate.png](./picture/solid_cs_study_004_boundary_gate.png)

* テストがラクになる🧪✨（外部なしで業務だけ検証しやすい）
* 仕様変更が局所化する🎯✨
* “壊れ方”が限定される🧯✨（被害が広がりにくい）

---

## 4) ハンズオン：ぐちゃぐちゃコードで「3つの言葉」を当てる🔍😈✨

ここでは“わざと最悪”の例を使うよ😇
（第3章の地獄を、**言葉で切れるように**する練習✂️✨）

```csharp
public class OrderService
{
    public void PlaceOrder(OrderDto dto)
    {
        // バリデーション
        if (dto.Items.Count == 0) throw new Exception("No items");

        // 合計計算
        decimal total = dto.Items.Sum(i => i.Price * i.Quantity);

        // 割引
        if (dto.CouponCode == "WELCOME10") total *= 0.9m;

        // 支払い（外部HTTP）
        using var http = new HttpClient();
        var res = http.PostAsJsonAsync("https://pay.example/charge", new { total }).Result;
        if (!res.IsSuccessStatusCode) throw new Exception("Pay failed");

        // DB保存
        using var conn = new SqlConnection("...");
        conn.Open();
        // ...INSERT...

        // 発送ファイル出力（なぜここに…）
        File.AppendAllText("shipping.csv", $"{dto.Email},{total}\n");

        // メール送信
        using var smtp = new SmtpClient("smtp.example");
        smtp.Send("noreply@example.com", dto.Email, "Thanks", "Your order is placed!");
    }
}
```

---

### Step 1：責務（変更理由）を付箋みたいに列挙しよ📝✨

この `OrderService` が変わる理由、何個ある？って考えるよ😊

* 注文の入力チェックの仕様が変わる✅
* 合計計算の仕様が変わる🧮
* 割引ルールが変わる🎫
* 決済APIの仕様が変わる💳🌐
* DBの種類/テーブルが変わる🗄️
* 発送CSVの形式が変わる📦📄
* メール文面/送信方式が変わる💌

👉 もうこの時点で「責務いっぱい盛り合わせ定食」だね🍱😇

---

### Step 2：依存（影響の向き）を見つけよ➡️👀

このクラスが直接触ってる“外の世界”はどれ？🌍

* `HttpClient`（決済）🌐
* `SqlConnection`（DB）🗄️
* `File`（ファイル）📁
* `SmtpClient`（メール）💌

👉 これらが変わると、`OrderService` も高確率で直すよね😵‍💫
つまり **依存の矢印が全部OrderServiceに刺さってる** 状態🎯💥

---

### Step 3：境界（混ぜない線）が壊れてる場所を言語化🧱💬

境界の観点で見ると…

* 本来「業務ルール」：合計、割引、注文の成立条件🧠
* 本来「外部I/O」：決済、DB、ファイル、メール🌐🗄️📁💌

なのに、ぜんぶ同じメソッドに混ざってる😇🌀
👉 **境界がない＝全部が同じ世界** になってるよ🌍💥

---

## 5) ここまでの“超まとめ”🌈✨（3行で覚える）

![責務・依存・境界の3つのキーワード](./picture/solid_cs_study_004_three_keywords.png)

* **責務＝変更理由** 📌
* **依存＝影響の向き** ➡️
* **境界＝混ぜない線** 🧱

この3つが口に出せると、SOLIDが急に「実務の道具」になるよ🛠️😊✨

---

## 6) 🤖AI（Copilot/Codex）に頼むときの“良い聞き方”テンプレ💬✨

そのまま貼って使ってOKだよ〜😊💕

### 責務を洗い出すプロンプト📌

```text
このクラス（OrderService）の「変更理由（責務）」を、想定される仕様変更の例つきで10個挙げて。
それを「業務ルール」「外部I/O」「表示/入出力」「横断関心（ログ等）」に分類して。
```

### 依存の矢印を出すプロンプト➡️

```text
このコードの依存関係を「呼ぶ側 -> 呼ばれる側」の矢印で列挙して。
特に外部I/O（HTTP/DB/ファイル/メール）への依存を強調して、変更が伝播するリスクも説明して。
```

### 境界の候補を提案させるプロンプト🧱

```text
このコードで「境界（業務ロジックと外部I/Oの分離）」を作るなら、
どこに線を引くべき？境界の内側/外側に分けて、候補クラス名も提案して。
```

---

## 7) 今日のミニ課題🎓💖（15分でOK）

やることはこれだけ😊✨

1. さっきの `OrderService` を見て、責務を5〜8個に絞って書く📝
2. 依存（外部I/O）を4つ挙げる➡️
3. 「境界はここ！」って1行で宣言する🧱

   * 例：「注文の業務ルールは内側、HTTP/DB/メール/ファイルは外側」✨

できたら最高〜〜🙌💕

---

## 次章予告🎀🪄（第5章：リファクタリング最初の武器セット）

![solid_cs_study_004_refactoring_checklist.png](./picture/solid_cs_study_004_refactoring_checklist.png)

次はこの“言葉”を使って、実際に手を動かすよ🧹✨

* メソッド抽出✂️
* クラス分割📦
* 移動🚚
* 名前付け🎯

「どう切れば安全？」って手順もセットでやるから、怖くないよ😊💕

---

必要なら、この第4章の内容に合わせて「第3章の“最悪コード”をミニEC題材で完全版に拡張」して、責務・依存・境界をもっとハッキリ見える教材用コードも作るよ😈🧱✨

[1]: https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core?utm_source=chatgpt.com "NET and .NET Core official support policy"
[2]: https://learn.microsoft.com/ja-jp/dotnet/csharp/whats-new/csharp-version-history?utm_source=chatgpt.com "C# の歴史"
[3]: https://learn.microsoft.com/ja-jp/visualstudio/releases/2026/release-notes?utm_source=chatgpt.com "Visual Studio 2026 リリース ノート"
