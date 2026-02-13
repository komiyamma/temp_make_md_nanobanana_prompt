# 第24章：AIにレビューさせる（設計チェックリスト）🤖✅

（テーマ：**I/O境界の分離が崩れてないか**を、AIと一緒にサクッと見抜く✨）

---

## 24.1 この章でできるようになること 🎯💖

この章が終わると、こんなことができるようになります😊✨

* 「このコード、I/Oが中に混ざってない？」を**チェックリストで即判定**できる🔍
* Copilot/Codexに「**境界の提案**」を出させて、設計の改善案を高速に集められる⚡
* AIの提案を**鵜呑みにせず**、ちゃんと採用/却下できる判断軸を持てる🧠✨

---

## 24.2 2026年1月時点の“今どきAIレビュー”事情（超ざっくり）🗞️✨

* Visual Studio 2026 は **18.2.0 が 2026/1/13 にリリース**されていて、更新も速いです📈 ([Microsoft Learn][1])
* Visual Studio では Copilot Chat が使えて、IDE内から起動して会話できます💬 ([Microsoft Learn][2])
* GitHub Copilot には **IDE内のコードレビュー**や、PRに対するレビューなど「レビュー系」機能が整理されてます🧾 ([GitHub Docs][3])
* OpenAI Codex は「リポジトリ上で作業してPR提案」みたいなエージェント方向にも進んでます🧑‍💻🤖 ([OpenAI][4])

> つまり：**AIに“設計レビュー係”をやらせやすい時代**になってます😆✨

---

## 24.3 まず手で見る！設計チェックリスト（I/O境界）🧾✅

![testable_cs_study_024_checklist_clipboard.png](./picture/testable_cs_study_024_checklist_clipboard.png)

![testable_cs_study_024_design_checklist.png](./picture/testable_cs_study_024_design_checklist.png)

AIに頼む前に、まず自分でサッと確認できると強いです💪✨
（AIレビューは「二重チェック」にすると事故が減ります🛡️）

### ✅チェック1：I/Oが “内側（ルール）” に混ざってない？🔌🚧

次のどれかが、**重要ロジックの中**に直書きされてたら黄色信号です⚠️

* `DateTime.Now` / 時刻取得 🕰️
* `Random` / 乱数 🎲
* `File.*` / ファイル 🗂️
* DBアクセス（ORM直叩き）🗄️
* `HttpClient` 直叩き 🌐
* UI要素直参照（Console.ReadLine/WriteLine含む）🖥️

👉 **方針**：それらは “境界インターフェース” の向こう側へ🚪✨

---

### ✅チェック2：依存が “見える形” になってる？👓

* 重要ロジックのクラスが、内部で勝手に `new` して依存を作ってない？😵
* コンストラクタ引数で受け取れてる？✉️
* 依存が多すぎて読めなくなってない？（多すぎも危険）🌀

👉 **理想**：依存が「見える＝説明できる」状態がスッキリ💖

---

### ✅チェック3：単体テストが “爆速” で回る？⚡

* テストが遅い原因が I/O になってない？🐘
* テストが「環境に左右」されてない？（PC/ネット/時刻/DB）🌪️
* 1回のテスト実行がストレスになってない？😇

👉 **目標**：単体テストは、気軽に連打できる速さが正義✨

---

## 24.4 AIにレビューさせるときの“基本姿勢”🤖🧠

![testable_cs_study_024_ai_strength_weakness.png](./picture/testable_cs_study_024_ai_strength_weakness.png)

AIは便利だけど、得意不得意があります😉

### AIが得意 💡

* 「I/O混ざりポイント」を**機械的に列挙**する🔍
* 「境界インターフェース案」を**大量に出す**🧩
* 「テストケース案」を**AAAで整形**する🧪
* 「リファクタ案」を**複数パターン**出す🔁

### AIが苦手（事故りやすい）⚠️

* **抽象化しすぎ**（インターフェース増殖祭り🎉→地獄👻）
* プロジェクト文脈無視で “正しそうな理想” に寄せる
* 命名・責務分割がズレる（それっぽいけど違う）

なので、**チェックリストで人間が最終判定**が鉄板です✅💖

---

## 24.5 Copilot/Codexに投げる「設計レビュー依頼」テンプレ集 📌💬

Copilotは「具体的な依頼」が強いです（細かく、分割して頼むのがコツ）📝✨ ([GitHub Docs][5])

### テンプレA：I/O混入チェック🔍

* 「このコードの **I/O箇所** を全部列挙して。
  それぞれ **境界インターフェース化** するとしたら、名前案も出して」

### テンプレB：内側/外側の線引き🧱

* 「この処理を **純粋ロジック** と **I/O** に分けたい。
  どこを“内側”に残し、どこを“外側”に出すべき？理由付きで」

### テンプレC：DI（コンストラクタ注入）案✉️

* 「このクラスが依存してるものを整理して、
  **コンストラクタ注入** に直す案を出して。テストのFake例も」

### テンプレD：テスト設計（AAA）🧪

* 「このユースケースの単体テストを
  **Arrange/Act/Assert** で3〜5ケース提案して。
  I/OはFake/Stubでやりたい」

### テンプレE：過剰抽象化のブレーキ🛑

* 「提案する抽象（interface）ごとに、
  **“なぜ必要？”** を1行で説明して。不要なら削って」

---

## 24.6 ミニ実演：AIレビューで“境界”を炙り出す🔥➡️🧊

例として、Consoleアプリでありがちな「I/O混ざり」を見ます😵‍💫

### ❌ダメ寄り例：ルールの中にI/Oが直撃してる💥

![testable_cs_study_024_bad_coupling.png](./picture/testable_cs_study_024_bad_coupling.png)

```csharp
public class CouponService
{
    public decimal ApplyCoupon(decimal price)
    {
        // I/O①：時刻
        var now = DateTime.Now;

        // I/O②：乱数（例：キャンペーン抽選）
        var rnd = new Random();
        var win = rnd.Next(0, 10) == 0;

        if (now.DayOfWeek == DayOfWeek.Sunday || win)
            return price * 0.8m;

        return price;
    }
}
```

### 🤖AIにこう聞く（テンプレA+B）💬

* 「このコードのI/O箇所を列挙して。内側/外側に分ける設計案も。
  テストしやすい形にしたい」

### ✅改善例：I/Oを境界へ、ルールはピュアへ🌿✨

![testable_cs_study_024_good_separation.png](./picture/testable_cs_study_024_good_separation.png)

```csharp
public interface IClock
{
    DateTime Now { get; }
}

public interface IRandom
{
    int Next(int minValue, int maxValue);
}

public class CouponRule
{
    public decimal Apply(decimal price, DateTime now, bool isWinner)
    {
        if (now.DayOfWeek == DayOfWeek.Sunday || isWinner)
            return price * 0.8m;

        return price;
    }
}

public class CouponService
{
    private readonly IClock _clock;
    private readonly IRandom _random;
    private readonly CouponRule _rule = new();

    public CouponService(IClock clock, IRandom random)
    {
        _clock = clock;
        _random = random;
    }

    public decimal ApplyCoupon(decimal price)
    {
        var now = _clock.Now;
        var win = _random.Next(0, 10) == 0;
        return _rule.Apply(price, now, win);
    }
}
```

ポイント🎉

* ルール（`CouponRule`）は **入力だけで決まる** → テスト爆速⚡
* I/O（時刻・乱数）は **境界**（`IClock`/`IRandom`）に隔離🚧
* Serviceは “組み立てて呼ぶ係” に寄せられる🧩

---

## 24.7 AIの提案を採用するかの判断ルール（超重要）🚦🧠

![testable_cs_study_024_judgment_traffic_light.png](./picture/testable_cs_study_024_judgment_traffic_light.png)

AIが「interfaceいっぱい作ろう！」って言い出したら、一旦これで止めます✋😆

### ✅採用してOKな提案

* テストが不安定になるI/Oを外に出してる🧊
* ルール（判断）がピュアになってる🌿
* 依存が読みやすく、増えすぎてない👀

### ❌採用しない寄りの提案

* 「将来のために」と言って抽象が増えすぎる（YAGNI警報）🚨
* 名前がフワフワして責務が不明（`IHelper`とか）😇
* 重要ロジックが“薄くなりすぎて”追跡不能🕵️‍♀️

👉 コツ：AIに **テンプレE** を追加で投げて「必要性を言語化」させると良いです🗣️✨

---

## 24.8 章末課題（やってみよう）📝🎮

第23章で作った小さなアプリ（ConsoleでOK）を題材にします😊

### ステップ1：セルフレビュー（チェックリスト）✅

* I/Oが内側に混ざってない？
* `new` が重要ロジックに埋まってない？
* 単体テストが速い構造？

### ステップ2：AIレビュー（テンプレA〜D）🤖

* 「I/O箇所列挙」
* 「境界インターフェース案」
* 「AAAテストケース案」

### ステップ3：採用/却下を“理由つき”で決める🧠✨

* 採用した改善：理由は？
* 却下した改善：なぜ不要？（YAGNI？過剰抽象？）

🎁おまけ：最後にAIへ

* 「この設計はテスト容易性の観点で何点？減点理由は？」
  って聞くと、振り返りがめちゃ捗ります📈✨

---

## 24.9 まとめ 🎀😊

* **チェックリスト（人間）**＋**AIレビュー（第二の目）** が最強コンボ🤝✨
* AIには「I/O列挙」「境界提案」「テスト案」をやらせると超速い⚡
* でも最後は、**抽象化しすぎてない？責務は明確？** を人間が決める🧠✅

次はいよいよ最終章🎓✨
「最小まとめ＆次の一歩」へ進もう〜！🚀💖

[1]: https://learn.microsoft.com/en-us/visualstudio/releases/2026/release-history?utm_source=chatgpt.com "Visual Studio Release History"
[2]: https://learn.microsoft.com/en-us/visualstudio/ide/visual-studio-github-copilot-get-started?view=visualstudio&utm_source=chatgpt.com "Get Started with GitHub Copilot - Visual Studio (Windows)"
[3]: https://docs.github.com/ja/copilot/how-tos/use-copilot-agents/request-a-code-review/use-code-review?utm_source=chatgpt.com "GitHub Copilot コード レビューの使用"
[4]: https://openai.com/index/introducing-codex/?utm_source=chatgpt.com "Introducing Codex"
[5]: https://docs.github.com/en/copilot/get-started/best-practices?utm_source=chatgpt.com "Best practices for using GitHub Copilot"
