# 第19章：UI（入力/表示）もI/Oだよ 🖥️🚧✨

この章のゴールはね👇
**「画面は“入出力装置”」って割り切って、UIを薄〜くする**ことだよ😊💖
そうすると、**単体テストがラク**になって、UI変更にも強くなる〜！💪✨

---

## 19-1. UIは「外の世界」＝I/Oだよ！🌍🔌

![testable_cs_study_019_ui_is_io.png](./picture/testable_cs_study_019_ui_is_io.png)

UIって、やってることを分解すると超シンプル👇

* ユーザー入力を受け取る（クリック・文字・選択）🖱️⌨️
* 画面に表示する（ラベル・メッセージ・一覧更新）🖥️
* たまにナビ（画面遷移）🚪

つまり UI は、**ファイル/DB/HTTP/時刻**と同じく「外部I/O」仲間だよ〜📦↔️🌍✨

---

## 19-2. UIにロジック置くと何が起きる？👻💥

![testable_cs_study_019_fat_ui_nightmare.png](./picture/testable_cs_study_019_fat_ui_nightmare.png)

UIコード（WinFormsのイベント、WPFのCode-behind、BlazorのUI側）に、判断が増えると…😵‍💫

* テストがしづらい（ボタン押さないと動かない）😇🔫
* 仕様変更が怖い（画面とルールが絡まる）🕸️
* バグが「画面操作の順番依存」になりがち🌀
* ちょっとした修正が“全体の地雷原”になる💣

なので合言葉はこれ👇
**「UIは薄く、判断は中へ」**📦✨

---

## 19-3. “薄いUI”の正体：UIは変換・表示だけ🪄🖥️

![testable_cs_study_019_thin_ui_filter.png](./picture/testable_cs_study_019_thin_ui_filter.png)

UIに残してOKなもの（おすすめ）👇😊

* 入力の受け取り（文字列）✍️
* 画面表示（文字に整形、色、並び、ラベル）🎨
* クリック→処理を呼ぶ（橋渡し）🌉
* 画面遷移（次の画面へ）🚪

UIから追い出したいもの（ここからが“判断”）👇🚫

* 料金計算、割引、会員ランク判定、在庫判定…💰📦
* ifだらけのビジネスルール分岐🌳
* DB/HTTP直呼び🗄️🌐
* MessageBoxをルール層で出す（←UIが混ざる）📛

---

## 19-4. いちばん小さい形：Humble Object（UIをアホにする）🧸✨


![testable_cs_study_019_humble_object.png](./picture/testable_cs_study_019_humble_object.png)

考え方はこれが最強にわかりやすいよ👇

* **UI（View）**：入力/表示だけ🖥️
* **Presenter / ViewModel（UIアダプタ）**：UIの都合と中身を橋渡し🌉
* **UseCase（中身）**：ルール・判断・手続き📦✨（テストしやすい！）

ざっくり図👇

* 外側：UI（I/O）🖥️
* 中：Presenter/ViewModel（変換役）🧩
* さらに中：UseCase（判断/ルール）🧠💖

---

## 19-5. ミニ題材：ポイント計算アプリ（UI→中→表示）🎁🧮✨

## 仕様（かわいいけど実務っぽいやつ）😊

* 購入金額 amount（円）を入力💴
* 会員ランク rank（Normal / Gold）を選択👑
* ポイント =

  * Normal：1%
  * Gold：2%
* ただし amount は 0以上、上限も適当にチェック（例：10,000,000まで）🚧

ここで大事なのは👇
**UIは文字列を受け取って表示するだけ**。
ポイント計算ルールは中へ📦✨

---

## 19-6. “中身（ルール）”をピュアに作る🧼✨

![testable_cs_study_019_pure_logic_isolation.png](./picture/testable_cs_study_019_pure_logic_isolation.png)

```csharp
public enum MemberRank
{
    Normal,
    Gold
}

public static class PointsRule
{
    public static int CalculatePoints(int amountYen, MemberRank rank)
    {
        if (amountYen < 0) throw new ArgumentOutOfRangeException(nameof(amountYen));

        var rate = rank switch
        {
            MemberRank.Normal => 0.01m,
            MemberRank.Gold   => 0.02m,
            _ => throw new ArgumentOutOfRangeException(nameof(rank))
        };

        // 端数は切り捨て（例）
        return (int)Math.Floor(amountYen * rate);
    }
}
```

✅ これ、**UIなしで単体テストできる**やつ〜！🧪⚡
（入力が同じなら結果も同じ＝ピュア）🌿✨

---

## 19-7. UIアダプタ（Presenter）で「文字→型」変換する🌉🔁

![testable_cs_study_019_presenter_translation.png](./picture/testable_cs_study_019_presenter_translation.png)

UIから来るのはだいたい **string** だからね😅
それを中で使える形にして、UseCase/Ruleを呼ぶよ✨

## View（UI）が満たすインターフェース

```csharp
public interface IPointsView
{
    string AmountText { get; }
    string RankText { get; }

    void ShowResult(string message);
    void ShowError(string message);
}
```

## Presenter（橋渡し）

```csharp
public sealed class PointsPresenter
{
    private readonly IPointsView _view;

    public PointsPresenter(IPointsView view)
    {
        _view = view;
    }

    public void OnCalculateClicked()
    {
        // 1) UI入力を読む（I/O）🖥️
        var amountText = _view.AmountText;
        var rankText = _view.RankText;

        // 2) 変換・検証（UI寄り）🧩
        if (!int.TryParse(amountText, out var amount))
        {
            _view.ShowError("金額は数字で入れてね💦");
            return;
        }

        if (amount < 0 || amount > 10_000_000)
        {
            _view.ShowError("金額の範囲が変だよ〜😵‍💫");
            return;
        }

        if (!Enum.TryParse<MemberRank>(rankText, out var rank))
        {
            _view.ShowError("ランクが選ばれてないかも👀");
            return;
        }

        // 3) ルール（中身）を呼ぶ📦✨
        var points = PointsRule.CalculatePoints(amount, rank);

        // 4) 表示（I/O）🖥️✨
        _view.ShowResult($"ポイントは {points} pt だよ〜🎉");
    }
}
```

ここがポイント👇💡

* PresenterはUIのI/Oを扱うけど、**判断の中心はRule/UseCaseに寄せる**
* UIは `ShowResult` / `ShowError` だけやってればOK🖥️✨

---

## 19-8. WinForms側（超うすUIの例）🪟🖱️

（フォームが `IPointsView` を実装するイメージだよ）

```csharp
public partial class PointsForm : Form, IPointsView
{
    private readonly PointsPresenter _presenter;

    public PointsForm()
    {
        InitializeComponent();
        _presenter = new PointsPresenter(this);

        // ここはUIイベント → presenterへ橋渡しだけ🖱️➡️🌉
        btnCalc.Click += (_, _) => _presenter.OnCalculateClicked();
    }

    public string AmountText => txtAmount.Text;
    public string RankText => cmbRank.SelectedItem?.ToString() ?? "";

    public void ShowResult(string message) => lblResult.Text = message;

    public void ShowError(string message) => MessageBox.Show(message, "入力エラー", MessageBoxButtons.OK, MessageBoxIcon.Warning);
}
```

✅ フォームの中に「計算式」ないよね？😊
**これが勝ち筋**だよ〜🏆✨

---

## 19-9. 単体テスト：UI無しでPresenterもテストできる🎭🧪

![testable_cs_study_019_fake_view_testing.png](./picture/testable_cs_study_019_fake_view_testing.png)

フォームを起動しなくてOK！最高！⚡

```csharp
using Xunit;

public sealed class FakePointsView : IPointsView
{
    public string AmountText { get; set; } = "";
    public string RankText { get; set; } = "";

    public string? Result { get; private set; }
    public string? Error { get; private set; }

    public void ShowResult(string message) => Result = message;
    public void ShowError(string message) => Error = message;
}

public class PointsPresenterTests
{
    [Fact]
    public void 金額が数字じゃないとエラー()
    {
        var view = new FakePointsView { AmountText = "abc", RankText = "Gold" };
        var presenter = new PointsPresenter(view);

        presenter.OnCalculateClicked();

        Assert.NotNull(view.Error);
        Assert.Null(view.Result);
    }

    [Fact]
    public void 正常なら結果が出る()
    {
        var view = new FakePointsView { AmountText = "10000", RankText = "Gold" };
        var presenter = new PointsPresenter(view);

        presenter.OnCalculateClicked();

        Assert.Null(view.Error);
        Assert.Contains("ポイントは", view.Result);
    }
}
```

これで、UIの見た目を変えても🖥️🎨
**中のテストは壊れにくい**よ〜！🥳✨

---

## 19-10. WPF / MVVM だとどうなる？🧩✨

MVVMでも考え方は同じだよ😊

* View（XAML）＝入出力🖥️
* ViewModel＝UIアダプタ🌉
* UseCase/Rule＝中身📦

ViewModelは `INotifyPropertyChanged` とかでUIと繋ぐけど、
**ビジネスルールはUseCaseへ**、がコツだよ〜💖

---

## 19-11. UIテスト（E2E）は“少なめ”が正解💡🚦

![testable_cs_study_019_test_balance.png](./picture/testable_cs_study_019_test_balance.png)

UI自動化テストって、できるけど重い＆壊れやすい😵‍💫
だからおすすめはこのバランス👇

* ルール/UseCase：単体テスト多め（速い⚡）
* Presenter/ViewModel：単体テストそこそこ🧪
* UI自動化：**スモークだけ**（起動→主要導線1本）🚬

## Web UIなら：Playwright が強いよ🌐🎭

Playwrightは .NET でも使えるし、クロスブラウザ対応でE2E向き！ ([playwright.dev][1])

## Desktop UIなら：候補はいくつか🪟🤖

WinAppDriver系や、UI Automation ライブラリ（例：FlaUI）もあるよ。FlaUIは .NET 向けUI自動化ライブラリとして継続的にリリースされてる。 ([GitHub][2])
（ただしUI自動化は環境差・実行の不安定さが出やすいから、まずは単体テスト優先が安心💖）

---

## 19-12. AI（Copilot/Codex）で爆速リファクタ🧠⚡🤖

UIからロジックを剥がす作業、AIがめっちゃ得意だよ〜✨

## おすすめプロンプト例📝

* 「このWinFormsのクリックイベントから、Presenterクラスを抽出して。Viewインターフェースも作って」🤖
* 「PointsRuleの単体テスト（境界値含む）をxUnitで生成して」🧪
* 「UIに残すべきもの/追い出すべきものを指摘して、差分パッチ案を出して」🔍

⚠️ ただし、AIがやりがちなミス👇

* ルールの中に `MessageBox` を入れちゃう📛
* Presenterが巨大化して“第2の地獄”になる👻
* 例外/戻り値の境界がぐちゃる（第20章で整えるよ）🚨

---

## 19-13. “UIが薄い”かセルフチェック✅👀

* 画面クラス（Form/ページ/コンポーネント）に計算式ある？🧮
* 画面クラスでDB/HTTP呼んでる？🗄️🌐
* ifが増えて読みにくい？🌳
* ルールをUI無しでテストできる？🧪⚡

1つでも「うっ…」ってなったら、UIが太り始めてる合図だよ〜😆🍔

---

## 19-14. 実践課題🎓✨（手を動かすと身につく！）

## 課題A：UI地獄の救出🆘

1. 既存のボタンイベントにある「判断(if)」を数えてみて👀
2. ルールを `Rule` / `UseCase` に移動📦
3. Presenter（またはViewModel）を作る🌉
4. 単体テストを3本以上🧪✨（正常・異常・境界値）

## 課題B：表示だけUIに残す🎨

* 「ポイントは 1,234 pt」みたいに、表示整形をUI側へ寄せる
* ルールは「数」を返すだけにする（ピュア強化）🌿✨

---

## 19章のまとめ🎉💖

* UIは **I/O（外の世界）** 🖥️🚧
* UIにロジック置くとテストがつらい👻
* **UIは薄く、判断は中へ** 📦✨
* Presenter / ViewModel は「橋渡し」🌉
* 単体テスト中心＋UI自動化はスモーク程度が安定🚦
* .NET 10 + C# 14 は Visual Studio 2026 や .NET 10 SDK で触れるよ（最新の言語機能もこの流れでOK） ([Microsoft Learn][3])
* Windowsの“モダンUI”なら WinUI 3（Windows App SDK）も選択肢として継続アップデート中だよ ([Microsoft Learn][4])

---

次の第20章はね、ここで出てきた
「エラーってどこで握るの？」「例外はどこまで投げるの？」🚨🤔
をスッキリ整理して、さらにテストしやすくするよ〜✨

[1]: https://playwright.dev/?utm_source=chatgpt.com "Playwright: Fast and reliable end-to-end testing for modern ..."
[2]: https://github.com/FlaUI/FlaUI?utm_source=chatgpt.com "FlaUI/FlaUI: UI automation library for .Net"
[3]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "What's new in C# 14"
[4]: https://learn.microsoft.com/en-us/windows/apps/windows-app-sdk/?utm_source=chatgpt.com "Build desktop Windows apps with the Windows App SDK"
