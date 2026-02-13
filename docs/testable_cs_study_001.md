# 第01章：まずはゴールのイメージを作ろう 🧭😊✨

この章は「技術を詰め込む」より、**“これから何ができるようになるの？”** を頭にインストールする回だよ〜！🧠💖
ここでゴール像が見えると、次の章の「I/Oってなに？」「境界ってなに？」がスルスル入るようになるよ😆🌈

---

## 1. この講座のゴールはこれ！🎯✨

![testable_cs_study_001_logic_vs_io_world.png](./picture/testable_cs_study_001_logic_vs_io_world.png)

**テスタブル設計（I/O境界の分離）**で目指すのは、ひとことで言うと👇

**「大事なロジックが、外の世界に振り回されないコード」** 📦🧘‍♀️

* ロジック（ルール・計算・判断）＝📦 “内側”
* I/O（DB・ファイル・時間・ネット・UI…）＝🌍 “外側”

内側を **ピュアに保つ** と、テストが簡単になるし、変更も怖くなくなるよ🛡️✨

---

## 2. 「テストしやすいコード」って何がうれしいの？✨🥰

![testable_cs_study_001_testable_benefits.png](./picture/testable_cs_study_001_testable_benefits.png)

### ✅ うれしさ①：変更が怖くなくなる（これが最強）🛡️💖

機能追加やリファクタのときに、
**「壊れてないかな…😨」** って手が止まることあるよね？

テストが効くと👇

* 変更 → テスト実行 → すぐ安心😌✅
* “壊れたらすぐわかる” ＝ **怖くない変更** 💪✨

### ✅ うれしさ②：バグが「早く・小さく」見つかる🐛🔍

バグって、後で見つかるほど重くなるの…🥲💸
テストがあると、**ロジック単位**で早期発見できるよ⚡

### ✅ うれしさ③：テストが仕様書になる📘✨

テストコードって、
「この入力ならこうなるべき」っていう**実例の集合**なのね🧩
未来の自分（とチーム）を助けるメモになるよ〜📝💖

---

## 3. じゃあ「テスタブル設計」って何するの？🤔✨

今日の合言葉はこれっ👇

## **I/Oを外に出す！** 🚪🌍✨


![testable_cs_study_001_io_door.png](./picture/testable_cs_study_001_io_door.png)

ポイントは「テストしやすくする」ために、**“混ざると困るもの”** を分けること！

* **判断・計算・ルール**（内側）
  → できるだけ **入力→出力が安定**（ピュア）🌿
* **I/O**（外側）
  → 実際のDB、ファイル、時間、ネット、UIなど🔌

この分け方を「境界（Boundary）」って呼ぶよ🚧😊

---

## 4. なんで I/O が混ざるとテストがつらいの？😵‍💫💥

![testable_cs_study_001_environment_luck.png](./picture/testable_cs_study_001_environment_luck.png)

I/O が混ざると、テストがこうなる👇

* DBがないと動かない 🗄️❌
* ネットが遅いと落ちる 🌐🐢
* 時刻が変わると結果が変わる 🕰️🌪️
* 乱数で結果がブレる 🎲😵

つまり…
**テストが「あなたのPCの運・環境」に依存する** のが最悪ポイント😭💦

だから、ロジックからI/Oを追い出して、テストを “室内” で完結させるの🧪🏠✨

---

## 5. ゴールの完成形イメージ（ざっくり図）🗺️✨

![testable_cs_study_001_goal_architecture.png](./picture/testable_cs_study_001_goal_architecture.png)

こんな感じを目指すよ〜👇

* 内側（テストしやすい）📦

  * ルール
  * 計算
  * 判断（if）
  * ドメインの知識
* 外側（差し替え可能）🌍

  * DB
  * ファイル
  * Web API
  * 時刻
  * UI
  * メール送信 など

外側は **インターフェース** で包んで、
必要なときに「本物」と「偽物（テスト用）」を差し替えるよ🎭🔁

（ちなみに今どきのC#環境だと、C# 14 が .NET 10 上で使えるのが公式に明記されてるよ🧩✨） ([Microsoft Learn][1])

---

## 6. “未来のあなた”がニコニコになる瞬間 😊💖

![testable_cs_study_001_future_self.png](./picture/testable_cs_study_001_future_self.png)

たとえば機能追加で、ロジックを直したとするよね✍️

* テストがない世界：
  「画面ぽちぽち…全部確認…漏れ怖い…😱」
* テストがある世界：
  「テスト全部✅ じゃあ安心して出せる〜😆🎉」

この差、積み重なると **人生変わるやつ** だよ…！🫶✨

---

## 7. 超ミニ例：同じ処理でも“置き場所”が違うだけで天国😇/地獄👻

![testable_cs_study_001_price_service_bad_vs_good.png](./picture/testable_cs_study_001_price_service_bad_vs_good.png)

ここでは雰囲気だけつかもうね！🙆‍♀️✨
（細かい実装は後の章でじっくりやるよ🧁）

### 👻 つらい例：ロジックの中にI/Oが混ざってる

```csharp
public class PriceService
{
    public int CalcTotal(int price)
    {
        // I/Oが混ざってる：今の時間に依存🕰️
        var now = DateTime.Now;

        // ルール：夜は10%オフ（例）
        if (now.Hour >= 20) price = (int)(price * 0.9);

        // I/Oが混ざってる：画面出力に依存🖥️
        Console.WriteLine($"total = {price}");

        return price;
    }
}
```

これ、テストしようとすると「今の時間」に左右されるし、コンソールも邪魔〜😵‍💫💥

### 😇 うれしい例：I/Oを外に出す（ロジックをピュア寄りに）

```csharp
public interface IClock
{
    DateTime Now { get; }
}

public class PriceService
{
    private readonly IClock _clock;

    public PriceService(IClock clock) => _clock = clock;

    public int CalcTotal(int price)
    {
        var now = _clock.Now; // ← 外からもらう🧃

        if (now.Hour >= 20) price = (int)(price * 0.9);

        return price; // ロジックは返すだけ📦✨
    }
}
```

こうするとテストでは👇みたいに「偽物の時計」を渡せる🎭✨
（この“差し替え”は後で本格的にやるよ〜！）

---

## 8. いまのC#テスト周りの“空気感”だけ先に知っとこ🧪✨

最近はテスト実行の仕組みも進化してて、`.NET 10` では `dotnet test` が **VSTest** だけじゃなく **Microsoft Testing Platform (MTP)** でも動く流れが公式に整理されてるよ🔧✨ ([Microsoft Learn][2])
（このへんは第8章でちゃんと触れるから安心してね😌💖）

それから、C# 14 の解説ページには **Visual Studio 2026** の言及もあって、今はIDE側もAI含めてどんどん統合が進んでる感じだよ🤖✨ ([Microsoft Learn][1])

---

## 9. AI（Copilot/Codex）を最初から味方につけるコツ 🤖💡✨

![testable_cs_study_001_ai_collaboration.png](./picture/testable_cs_study_001_ai_collaboration.png)

AIは「コードそのもの」より、まず **分離の発想を引き出す** のに使うと強いよ〜！💪😆

### 💬 そのままコピペで使えるお願い例（プロンプト）

* 「このメソッドの **I/Oっぽい部分** と **純粋ロジック** を分けたい。境界の作り方を提案して！🧩」
* 「IClock / IFileSystem みたいな **インターフェース案** と命名案を出して！📝✨」
* 「テストが書きやすい形にするために、責務の分割案を3パターン出して！🎭🔁」

### ⚠️ 鵜呑み禁止チェック（超大事）

AIが出した案を見たら、ここだけ確認してね👇

* 「ロジックの中に DateTime.Now とか File とか Http とか残ってない？😳」
* 「インターフェースが“ただの飾り”になってない？🧸」
* 「差し替えが本当にできる形？🔁✨」

---

## 10. 章末まとめ（ここだけ覚えればOK）📌💖

* テストしやすい＝**変更が怖くない** 🛡️✨
* そのための合言葉＝ **I/Oを外に出す！** 🚪🌍
* まずは “内側（ルール）” をピュア寄りにして、外側（I/O）を差し替え可能にする🎭🔁

---

## 11. ミニ課題（3分）⏱️📝✨

あなたの最近のコードを思い出して、I/Oっぽいものを **5個** 書き出してみて〜！💖
例：🗄️DB / 🗂️ファイル / 🌐HTTP / 🕰️時間 / 🎲乱数 / 🖥️UI / 📩メール

書けたら次の章で、「それ、どこからがI/O？」って感覚が一気に育つよ🌱😆✨

[1]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "What's new in C# 14"
[2]: https://learn.microsoft.com/ja-jp/dotnet/core/testing/unit-testing-with-dotnet-test?utm_source=chatgpt.com "'dotnet test' を使用したテスト - .NET"
