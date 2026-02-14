# 第03章：例外の基礎復習（C#）🧯

この章は「例外って何者？」「どこから来たの？」「どう追うの？」を、まず“最低限だけ”スッキリ掴む回だよ😊💕

---

## 1) この章のゴール🎯✨

終わるころに、これができるようになるよ〜！

* 例外（Exception）が起きた時に **慌てずに状況を説明できる** 😌📝
* **try / catch / finally** の動きを “自分の言葉” で言える 🔁🧠
* **スタックトレース（Stack Trace）** を見て「犯人の場所」を探せる 🔍📌
* デバッガで **例外の発生地点に一瞬で飛べる** 🪄🐞

（ちなみに今の最新版だと、C# 14 は .NET 10 で動くよ〜という前提で進むよ）([Microsoft Learn][1])

---

## 2) 例外（Exception）ってなに？💥😳

例外はひとことで言うと、

* 「処理が続けられない“緊急事態”が起きたから、今の流れを中断して上に知らせるよ〜！」📣🚨

っていう仕組みだよ。

ここで大事なのは、例外が出た瞬間に **今の処理の流れが“中断”される** こと。
そして「どこで起きたか」「そこに来るまで何を辿ったか」が **スタックトレース** に残るの！🧵🔎

---

## 3) try / catch / finally の動き方🔁🧯

![try catch finally flow](./picture/err_model_cs_study_003_try_catch_finally.png)

### ✅ try

「ここ、失敗するかも」って場所を囲う箱📦

### ✅ catch

例外が起きた時に「受け止める」場所👐
（※受け止めたら“処理を続ける”か“上に投げ直す”かを選ぶ）

### ✅ finally

成功でも失敗でも **だいたい最後に必ず動く** お片付けコーナー🧹✨
（リソース解放・後始末に使うのが定番）

例外処理の基本の書き方はここにまとまってるよ。([Microsoft Learn][2])

---

## 4) まずは1回、わざと例外を起こしてみよ😈💥（超重要）

「例外は怖い」→「例外は読める」に変える最短コース！

```csharp
using System;

static void Main()
{
    Console.WriteLine("スタート😊");

    try
    {
        A();
        Console.WriteLine("ここは表示されないはず😳");
    }
    catch (Exception ex)
    {
        Console.WriteLine("catch に来たよ🧯");
        Console.WriteLine("Message: " + ex.Message);
        Console.WriteLine("Type: " + ex.GetType().FullName);
        Console.WriteLine("StackTrace:\n" + ex.StackTrace);
    }
    finally
    {
        Console.WriteLine("finally は動くよ🧹✨");
    }

    Console.WriteLine("おわり🎉");
}

static void A() => B();
static void B() => C();

static void C()
{
    throw new InvalidOperationException("わざと落としたよ💥");
}
```

👀 見てほしいポイントはこれ！

* **例外が起きたら try の続きはスキップ** される🚫
* **catch で捕まえると、そこで情報を見れる** 🔍
* **finally は（基本）実行される** 🧹✨

---

## 5) スタックトレースの読み方🔎🧵（ここが勝ち筋！）

スタックトレースは「呼び出し履歴」だよ📞➡️📞➡️📞
だいたいこう読むと早い！

* **一番上**：いちばん “近い” 呼び出し（最後に呼ばれた）
* **どこで投げられたか**：例外が発生した地点（ファイル名・行番号が出ることが多い）
* **A→B→C** みたいに「どの順で辿ったか」が見える🧭

例外の StackTrace はこういう意味だよ、という公式説明もあるよ。([Microsoft Learn][3])

---

## 6) throw と「投げ直し」💨🎯（スタックトレースを守る技）

![throw vs throw ex](./picture/err_model_cs_study_003_throw_vs_throw_ex.png)

ここ、**超・事故りやすい** から先に覚えちゃお！

* ✅ **throw;** → 元のスタックトレースを保つ（おすすめ）
* ⚠️ **throw ex;** → スタックトレースが更新されがち（犯人が見えにくくなる）😢

これは公式にもハッキリ書いてあるよ。([Microsoft Learn][2])

ミニ比較コード👇

```csharp
try
{
    C();
}
catch (Exception ex)
{
    Console.WriteLine("ログは残すよ📝");
    // throw ex;  // ← こっちはスタックトレースが変わりやすい⚠️
    throw;       // ← こっちが基本おすすめ✅
}
```

---

## 7) InnerException（例外の“連鎖”）⛓️😵‍💫

![Inner Exception Chain](./picture/err_model_cs_study_003_inner_exception_chain.png)

現場でよくあるのがこれ！

* 表面の例外は「失敗しました！」って言ってるだけ
* 本当の原因は **InnerException** に入ってる💣

例：HTTPやDBの失敗が、別の例外に包まれて上がってくる…みたいなやつね。

チェックのコツ👇

* ex.Message だけで決めない
* ex.InnerException があったら **掘る** ⛏️👀
* さらに InnerException の中に InnerException… もある😇

---

## 8) async/await の例外（超入門）⏳⚡

「非同期って何か難しそう…」ってなるけど、ここだけ覚えればOK😊

* await している場所で例外が “表に出る”
* つまり **await した行で落ちる** ように見えることが多い

```csharp
static async Task Main()
{
    try
    {
        await BoomAsync();
    }
    catch (Exception ex)
    {
        Console.WriteLine("await で捕まえたよ🧯 " + ex.Message);
    }
}

static async Task BoomAsync()
{
    await Task.Delay(100);
    throw new Exception("async でも落ちるよ💥");
}
```

---

## 9) デバッガで追う（Visual Studio）🐞🪄

### 9-1) 「投げられた瞬間」に止める🛑✨（最強）

Visual Studio には **例外設定（Exception Settings）** があって、ここを使うと「投げられたその瞬間」に止められるよ！
メニュー例：**デバッグ → ウィンドウ → 例外設定**（ショートカットがある場合も）([Microsoft Learn][4])

ポイント💡

* “処理される例外” でも止められる（First chance exception）
* 「どこで投げられたか」が一発で分かる🔍⚡ ([Microsoft Learn][5])

### 9-2) Call Stack（呼び出し履歴）を見る🧵👀

止まったら、次は **呼び出し履歴（Call Stack）** を開く！
そこで「どの順で呼ばれたか」が見えるよ。([Microsoft Learn][6])

### 9-3) 例外ヘルパ＆Copilot（2026のデバッグ強化）🤖🔧

Visual Studio 2026 のリリースノートでは、デバッグ時に出力ウィンドウの情報も使って、例外解析をより賢くする流れが紹介されてるよ。([Microsoft Learn][7])
（「どうしてこれ起きた？」の初動が速くなるやつ！🚀）

---

## 10) VS Code でやる場合🧑‍💻🟦

VS Code でもデバッグビューで **Call Stack / 変数 / ブレークポイント** が扱えるよ。([Visual Studio Code][8])
まずは「ブレークで止める→Call Stackを見る」だけできればOK🙆‍♀️✨

---

## 11) ミニ演習（3本立て）🧪🎀

### 演習3-1：スタックトレースで犯人の行を特定🔍📌

1. さっきの A→B→C のコードを実行
2. StackTrace の中から **C() の行番号** を探す
3. 「どこで投げたか」を口で説明してみて😊🗣️

### 演習3-2：throw; と throw ex; を比べる⚖️😱

1. catch の中を throw; にする
2. 次に throw ex; にする
3. StackTrace がどう変わるか観察👀
   （違いが見えたら勝ち🎉）([Microsoft Learn][2])

### 演習3-3：Exception Settings で “投げた瞬間” に止める🛑🐞

1. 例外設定ウィンドウを開く([Microsoft Learn][4])
2. InvalidOperationException を “投げられたら中断” にする
3. 実行して、throw の行で止まるのを体験✨

---

## 12) AI活用：例外調査の「質問テンプレ」3つ🤖🧠✨

コピペで使えるやつ置いとくね😊💕

### テンプレ①：原因候補＆切り分け

* 「この例外メッセージとスタックトレースから、原因候補を3つ。各候補ごとに確認手順も出して🙏」

### テンプレ②：スタックトレース読解

* 「このスタックトレースを上から順に“何が起きたか”日本語で要約して。犯人っぽい行を1つに絞って理由も！」

### テンプレ③：直し方＋再発防止

* 「最小の修正案（安全側）と、再発防止のテストケース案を5個出して🧪」

---

## まとめ🌸✨

この章で押さえたのはこれだけ！💡

* 例外は “流れを中断して上に知らせる” 仕組み📣🚨
* try/catch/finally の役割が分かれば怖くない🧯🧹
* 勝ち筋は **スタックトレース** と **デバッガ（例外設定＋Call Stack）** 🔎🧵🐞
* 投げ直しは基本 **throw;**（スタックトレース守る）🛡️✨ ([Microsoft Learn][2])

次章（第4章）は、いよいよ「やっちゃダメ例外集」🙅‍♀️💥で事故を潰していくよ〜！😊🎀

[1]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "What's new in C# 14"
[2]: https://learn.microsoft.com/ja-jp/dotnet/csharp/language-reference/statements/exception-handling-statements?utm_source=chatgpt.com "例外処理ステートメント - throw、try、catch、finally - C# ..."
[3]: https://learn.microsoft.com/en-us/dotnet/api/system.exception.stacktrace?view=net-10.0&utm_source=chatgpt.com "Exception.StackTrace Property (System)"
[4]: https://learn.microsoft.com/ja-jp/visualstudio/debugger/managing-exceptions-with-the-debugger?view=visualstudio&utm_source=chatgpt.com "Visual Studio でデバッガーで例外を管理する"
[5]: https://learn.microsoft.com/en-us/visualstudio/debugger/managing-exceptions-with-the-debugger?view=visualstudio&utm_source=chatgpt.com "Manage exceptions with the debugger in Visual Studio"
[6]: https://learn.microsoft.com/ja-jp/visualstudio/debugger/how-to-use-the-call-stack-window?view=visualstudio&utm_source=chatgpt.com "デバッガーで呼び出し履歴を表示する - Visual Studio (Windows)"
[7]: https://learn.microsoft.com/en-us/visualstudio/releases/2026/release-notes?utm_source=chatgpt.com "Visual Studio 2026 Release Notes"
[8]: https://code.visualstudio.com/docs/debugtest/debugging?utm_source=chatgpt.com "Debug code with Visual Studio Code"
