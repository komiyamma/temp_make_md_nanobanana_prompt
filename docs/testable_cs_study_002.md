# 第02章：テストがつらいコードあるある 😵‍💫💥

この章は「うわぁ…これ、テスト無理じゃん…😭」ってなる“原因”を、あるある満載で先に体験しちゃう回だよ〜🫶✨
（次章以降で「じゃあどう分けるの？」をちゃんとやるから安心してね😊）

---

## 2-1. あるある①：DB直アクセス 🗄️💥（重い・遅い・壊れやすい）

![testable_cs_study_002_db_weight.png](./picture/testable_cs_study_002_db_weight.png)

たとえばロジックのど真ん中で、いきなりDBに繋ぎに行くやつ👇

```csharp
public class UserService
{
    public bool IsVipUser(int userId)
    {
        // いきなりDB接続して判定しにいく（あるある）
        using var conn = new SqlConnection("...本番っぽい接続文字列...");
        conn.Open();

        using var cmd = conn.CreateCommand();
        cmd.CommandText = "SELECT IsVip FROM Users WHERE Id = @id";
        cmd.Parameters.AddWithValue("@id", userId);

        return (bool)cmd.ExecuteScalar();
    }
}
```

### これが何を起こすか…😇

* テストのたびに **DBが必要**（PCにない、落ちてる、接続できない…😵）
* テストが **遅い**（1件でも秒単位になりがち🐢）
* テストデータの準備が地獄（初期化、掃除、順序依存…🧹💥）
* CI（自動テスト環境）でコケる（環境差で死ぬ🌪️）

結果：「テスト＝めんどい」になって、誰も書かなくなるやつ🥲🌀

---

## 2-2. あるある②：`DateTime.Now` 直読み 🕰️💥（“今”は揺れる）

![testable_cs_study_002_time_balance.png](./picture/testable_cs_study_002_time_balance.png)

「今日ならOK」「期限内ならOK」みたいな判定、ついこう書きがち👇

```csharp
public bool CanUseCoupon(DateTime expiresAt)
{
    return DateTime.Now <= expiresAt;
}
```

### 何がつらいの？😵‍💫

* テストが **時間に依存**して揺れる（朝は通るのに夜は落ちる🌙）
* 月末・年末・うるう年・サマータイム（地域）で事故る🧨
* 「0時またぎ」でたまに落ちる＝**フレークテスト**爆誕💥

ちなみに最近の .NET だと、時間をテストしやすくするための `TimeProvider` みたいな仕組みも公式に用意されてるよ（“時間を抽象化してテスタブルに”って方向性）⏳✨ ([Microsoft Learn][1])

---

## 2-3. あるある③：`HttpClient` 直叩き 🌐💥（外部は落ちる・遅い・変わる）

![testable_cs_study_002_http_bridge.png](./picture/testable_cs_study_002_http_bridge.png)

```csharp
public async Task<decimal> GetUsdRateAsync()
{
    using var http = new HttpClient();
    var json = await http.GetStringAsync("https://example.com/rate");
    return decimal.Parse(json);
}
```

### これが起こす悲劇😭

* ネットが不安定でテストが落ちる📉
* APIが遅いとテストが遅い🐢
* API仕様が変わると昨日までのテストが死ぬ🪦
* 回数制限でBANされることも…😱

外部は「自分がコントロールできない世界」だから、テストと直結させると一気に壊れやすくなるの🥺

---

## 2-4. テストが「環境依存」になると何が起きる？🌪️

![testable_cs_study_002_environment_puzzle.png](./picture/testable_cs_study_002_environment_puzzle.png)

環境依存っていうのは、ざっくり言うと👇
**“コード”じゃなくて“環境”の状態で結果が変わる**ってこと😵‍💫

たとえば…

* DBが起動してるかどうか
* ネットが速いかどうか
* 時刻（今が何時か）
* OS設定（タイムゾーン、カルチャ、パスの違い）
* その日の外部APIの機嫌

### するとどうなる？😇

* 自分のPCでは通るのに、CIで落ちる 🤝💥
* さっき通ったのに、今落ちる（再現しない）🌀
* 「原因調査」がテストじゃなくて環境調査になる🔍😵

---

## 2-5. “再現できないバグ”の地獄🔥（これ、ほんとに消耗する…）


![testable_cs_study_002_fragile_code.png](./picture/testable_cs_study_002_fragile_code.png)

いちばんつらいやつがコレ😭

* ユーザー「たまに落ちます」
* あなた「再現しません」
* ログ「情報不足」
* 修正「当てずっぽう」
* 結果「直ってない」😇

これが起きる典型パターンは👇

* `DateTime.Now` / `Random` / 外部API / ファイル / DB がロジックに混ざってる
* つまり **“毎回同じ入力でも結果が変わる”** 状態になってる😵‍💫

テストって本来「同じ入力→同じ結果」を確認して安心するものなのに、揺れる材料が混ざると安心できなくなるの…🥲

---

## 2-6. ミニ体験：0時またぎでテストが落ちる例 🌙⏱️💥

![testable_cs_study_002_midnight_bug.png](./picture/testable_cs_study_002_midnight_bug.png)

```csharp
public class GreetingService
{
    public string GetGreeting()
    {
        return DateTime.Now.Hour < 12 ? "おはよう" : "こんにちは";
    }
}
```

テストで「午前ならおはよう」ってやりたいのに…

* テスト実行が **11:59** なら通る😊
* **12:00** になった瞬間に落ちる💥

「え、私なにも変えてないのに…」ってなるやつ😇
（これが“フレーク”の入り口だよ〜🌀）

---

## 2-7. “つらいコード”を見分けるチェックリスト ✅😵‍💫

![testable_cs_study_002_bad_practice_checklist.png](./picture/testable_cs_study_002_bad_practice_checklist.png)

当てはまるほどテストがつらくなる率UP⬆️

* ロジックの途中で `DateTime.Now` / `UtcNow` を読んでる🕰️
* `new HttpClient()` して外部に飛んでる🌐
* `File.ReadAllText` みたいなファイル直読みがある🗂️
* DBに直接つなぎに行く🗄️
* `Random` や `Guid.NewGuid()` をその場で呼んでる🎲
* `Environment.GetEnvironmentVariable` を直で読んでる🌪️
* 例外がいろんな場所で投げられて、どこで握るか不明🚨
* 1つのメソッドが長くて、I/Oと判断（if）が混ざってる🧩💥

この章のゴールは「分け方」じゃなくて、まず **“これ混ざってるとつらいんだ！”** を体に入れることだよ〜💪✨

---

## 2-8. AI（Copilot/Codex）に助けてもらう小ワザ 🤖📝✨

![testable_cs_study_002_ai_audit.png](./picture/testable_cs_study_002_ai_audit.png)

コードを貼って、こんなお願いをするとめちゃ捗るよ🫶

* 「このメソッドの **外部依存（I/O）** を箇条書きにして」🔍
* 「このクラスが **テストしにくい理由** を指摘して」💥
* 「テストが揺れないようにするには、どこを分離すべき？」🧠✨

ただし！AIが提案した“分離”が、やたら抽象化しすぎてたら要注意⚠️
（やりすぎると逆に読みにくくなるので、最小でOKだよ😊）

---

## まとめ 🎀✨

この章で覚えてほしいのはこれだけ👇💡

* **DB・時間・ネット・ファイル**がロジックに混ざると、テストがつらくなる😵‍💫
* 環境依存になると、**再現できないバグ地獄🔥**が始まる
* だから次の章から、合言葉どおり **「I/Oを外に出す！」🚪✨** をやっていくよ〜😊💖

次は「I/Oって結局どこからどこまで？」をスッキリ整理するよ🔌📦✨

[1]: https://learn.microsoft.com/en-us/dotnet/standard/datetime/timeprovider-overview?utm_source=chatgpt.com "What is the TimeProvider class - .NET"
