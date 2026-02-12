# 第03章：I/Oってなに？どこからがI/O？🔌📦✨

## この章のゴール🎯

* 「これはI/Oだ！」「これは純粋ロジックだ！」を**見分けられる**ようになる👀✨
* あなたのコードから **“外の世界”ポイント**を発掘できるようになる🕵️‍♀️🔍
* 次の章以降でやる **「I/Oを外に出す」**準備ができる🚪💨

---

## まず結論：I/O＝外の世界とのやりとり🌍↔️📦

I/O（Input/Output）は、ざっくり言うと **「プログラムの外側とデータをやりとりする操作」**だよ〜！😊
Windowsの世界でも、I/Oは「デバイスなど外部とのデータの流れ」を扱うモデルとして整理されてる（＝外に触るやつはI/O）って考え方でOK✨ ([Microsoft Learn][1])

---

## I/Oの代表メンバーたち（C#あるある付き）🧑‍🤝‍🧑✨

### 1) ファイル🗂️

* 読む：**File.ReadAllText** / **FileStream**
* 書く：**File.WriteAllText**
* ありがち：設定ファイル、ログ、CSV、画像など📄🖼️

### 2) DB🗄️

* **SqlConnection** / **DbContext**（EF）
* ありがち：検索・登録・更新・削除💾

### 3) ネットワーク🌐

* **HttpClient**（外部API）
* **gRPC** / **WebSocket**
* ありがち：決済、天気、認証、社内APIなど📡

### 4) 時刻🕰️（めっちゃ重要！）

* **DateTime.Now** / **DateTimeOffset.UtcNow**
* **Stopwatch** / **Task.Delay** / **Thread.Sleep**
* ポイント：時間は「外の世界」なので、テストを揺らす主犯になりやすい😈💥

### 5) 乱数🎲（これもテストの敵！）

* **Random** / **RandomNumberGenerator**
* ポイント：毎回結果が変わる＝テストが不安定になりがち🌪️

### 6) UI/コンソール🖥️

* **Console.ReadLine** / **Console.WriteLine**
* ボタン押下・画面入力・表示など🧑‍💻✨

### 7) OSや環境🌎

* **Environment.GetEnvironmentVariable**
* **Registry**（レジストリ）
* **Process.Start**（別プロセス起動）
* **ネットワークの状態**、**PC設定**、**ファイル配置**…ぜんぶ外の都合💦

---

## 「I/Oかどうか迷ったら」判定ルール✅🧠

次のどれかに当てはまったら、だいたいI/Oだよ〜！🙆‍♀️✨

* **失敗する理由が自分のコード以外にある**（ネット落ちた、DB止まった、ファイル無い、権限ない…）😵
* **遅い/待つ可能性がある**（通信、ディスク、DB）🐢
* **結果が毎回変わり得る**（時刻、乱数、環境変数）🎲🕰️
* **何かを書き換える/残す**（ファイル保存、DB更新、ログ出力）📝💾

この章では、I/Oを **「外の世界の都合で揺れるやつ」**って覚えてOK！🌪️✨

---

## 純粋ロジック（ピュア）との違い🌱✨


![testable_cs_study_003_io_vs_pure.png](./picture/testable_cs_study_003_io_vs_pure.png)

### 純粋ロジックって？

* 入力が同じなら、出力も同じ🎯
* 外部に触らない（ファイル/DB/ネット/時刻/乱数/画面に触らない）🧼
* だからテストが超ラクになる⚡💖

---

## 実例：I/O混ぜ混ぜコードを見抜こう🕵️‍♀️🔍💥

### 例1：I/Oが混ざってるパターン😵‍💫

```csharp
public class ReportService
{
    public string CreateMonthlyReport()
    {
        var now = DateTime.Now;                 // 🕰️ I/O（時刻）
        var userJson = File.ReadAllText("user.json"); // 🗂️ I/O（ファイル）
        var users = ParseUsers(userJson);       // 🌱 ピュア寄り（変換）
        return $"[{now:yyyy-MM}] users={users.Count}";
    }

    private List<string> ParseUsers(string json)
    {
        // ここは例として超雑でもOK
        return json.Split('\n').ToList();
    }
}
```

✅この中でI/Oはどれ？

* **DateTime.Now**（時刻）🕰️
* **File.ReadAllText**（ファイル）🗂️

🌱ピュア寄りなのはどれ？

* **ParseUsers**（文字列→リストの変換）🍳✨

> ポイント：**I/Oとピュアが同居**すると、「テストで固定できない要素」が混ざって苦しくなる😣💦
> （でも今は“見つけられた”だけで大勝利🎉）

---

## もっと実戦的：「I/O発掘チェックリスト」🧾✅✨

コードレビューで、ここだけ目を皿にする👀🔥

* **System.IO** が見えたらI/O率高い🗂️
* **HttpClient** が見えたらI/O確定🌐
* **DbContext / SqlConnection** が見えたらI/O確定🗄️
* **DateTime.Now / UtcNow** が見えたらI/O確定🕰️
* **Random / Guid.NewGuid** が見えたら“揺れる要素”🎲🧬
* **Environment** が見えたらI/O（環境依存）🌎
* **Console** が見えたらI/O（入出力）🖥️

---

## ミニ演習：I/Oに赤丸をつけよう🔴📝

次のコードの「I/O行」を当ててみてね😊✨

```csharp
public int DrawLotteryAndSave(string path)
{
    var n = new Random().Next(1, 101);
    File.WriteAllText(path, n.ToString());
    return n;
}
```

### 解答✅

* **Random().Next** → 🎲 I/O扱い（結果が揺れる＝外の都合）
* **File.WriteAllText** → 🗂️ I/O（ファイル）
* **return n** → 🌱 これはただの値返し

---

## AI（Copilot/Codex）活用：I/O探しを手伝わせる🤖🔍✨

おすすめの頼み方（コピペでOK）💖

* 「このコードの **I/O（外部依存）箇所**を列挙して。理由もつけて」🧠
* 「I/Oと純粋ロジックを分けるなら、分割案を3つ出して」🧩
* 「このI/Oを後で差し替えたい。境界の名前案を出して」🏷️✨

⚠️注意：AIはたまに「ただのメモリ上の処理」をI/O扱いしたり、逆に時刻/乱数を見落としたりするよ〜！最後はあなたがチェック👀💪

---

## 2026年1月の“いま”のC#周辺ミニ情報🧊✨（さらっと）

この教材は **.NET 10 / C# 14** が最新ラインとして整理されてるよ〜（.NET 10はLTS）📌✨ ([Microsoft][2])
また、Visual Studio側も **2026系**が案内されていて、**.NET 10 SDK同梱**の流れになってるよ🛠️✨ ([Microsoft Learn][3])
（参考：Visual Studio 2022の最新更新も2026年1月に出てる）📅 ([Microsoft Learn][4])

---

## この章のまとめ🎁✨

* I/O＝**外の世界とのやりとり**🌍↔️📦
* 代表は **ファイル/DB/ネット/時刻/乱数/UI/環境** 🗂️🗄️🌐🕰️🎲🖥️🌎
* 迷ったら「外の都合で揺れる？遅い？失敗しうる？」で判定✅
* 次の章から、ピュア（純粋ロジック）をもっとはっきり掴んでいくよ〜！🌿✨

---

次は「第4章：純粋ロジック（ピュア）ってなに？🌿✨」に進もう〜！🚀💖

[1]: https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/overview-of-the-windows-i-o-model?utm_source=chatgpt.com "Overview of the Windows I/O Model - Windows drivers"
[2]: https://dotnet.microsoft.com/ja-jp/platform/support/policy?utm_source=chatgpt.com "公式の .NET サポート ポリシー | .NET"
[3]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "What's new in C# 14"
[4]: https://learn.microsoft.com/en-us/visualstudio/releases/2022/release-history?utm_source=chatgpt.com "Visual Studio 2022 Release History"
