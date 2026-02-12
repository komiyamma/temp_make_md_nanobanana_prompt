# 第15章：乱数（Random）を境界にする 🎲🚧✨

## この章でできるようになること ✅😊

* 乱数が入った途端にテストが不安定になる理由がわかる🌪️
* 乱数を **I/O（外の世界）として境界に追い出す**やり方がわかる🚪
* `IRandom` を作って、**本番は本物・テストは偽物**に差し替えできるようになる🎭🧪
* “抽選/シャッフル/ゲーム”系のロジックを、安心して変更できるようになる🛡️✨

---

## 最新メモ（2026-01-16 時点）📝✨

* .NET 10 は **LTS**で、2025-11-11 リリース、2026-01-13 時点の最新パッチは 10.0.2 として案内されています。 ([Microsoft][1])
* C# は **C# 14 が最新**で、.NET 10 上でサポートされています。 ([Microsoft Learn][2])
* `Random.Shared` は **スレッドセーフに並行利用できる Random**として公式ドキュメントに明記されています。 ([Microsoft Learn][3])

（ここは「今の前提が最新だよ」っていう確認だけ💡 本編はガッツリ設計の話にいくよ〜😊）

---

## 1) 乱数があると、テストが“揺れる”理由 🌪️😵‍💫

たとえば「くじ引きで当たりが出たらOK」みたいな処理を考えるね🎯
ロジックの中で `Random` を直接使うと…

* テストの期待値が固定できない（当たりが出たり出なかったり）🎲
* “たまたま落ちた”が起きる（フレイキーテスト）💥
* 失敗を再現しづらい（デバッグ地獄）🔥

つまり、乱数は **外の世界のゆらぎ**。
だから **I/O と同じ扱いで境界にする**のがコツだよ〜🚧✨

---

## 2) 結論：乱数は I/O として外に出す！🚪🎲


![testable_cs_study_015_controlled_dice.png](./picture/testable_cs_study_015_controlled_dice.png)

第14章の「時間（IClock）」と同じノリでいけるよ😊
やることはシンプル！

* ✅ 乱数を引く役を **`IRandom`** みたいなインターフェースにする🧩
* ✅ 本番は `System.Random`（や `Random.Shared`）で実装する🎲
* ✅ テストは **決め打ちで値を返す偽物**を使う🎭🧪

---

## 3) 最小の境界：`IRandom` を作ろう 🧩🎲

ポイントは「機能を盛りすぎない」こと！
まずは **必要なメソッドだけ**に絞るのが勝ち✨

```csharp
public interface IRandom
{
    // 0以上 max未満
    int NextInt(int maxExclusive);

    // min以上 max未満
    int NextInt(int minInclusive, int maxExclusive);

    // 0.0以上 1.0未満
    double NextDouble();
}
```

---

## 4) 本番実装：`Random.Shared` をラップする 🎁✨

`Random.Shared` は並行利用OKの “共有Random” として用意されてるよ（公式にも明記）。 ([Microsoft Learn][3])
なので、まずはこれを素直に包むのがラク😊

```csharp
public sealed class DotNetRandom : IRandom
{
    public int NextInt(int maxExclusive)
        => Random.Shared.Next(maxExclusive);

    public int NextInt(int minInclusive, int maxExclusive)
        => Random.Shared.Next(minInclusive, maxExclusive);

    public double NextDouble()
        => Random.Shared.NextDouble();
}
```

> ここでの狙いは「`System.Random` を隠す」こと！
> ロジック側が `Random` を知らなければ、テストでいくらでも差し替えできる🎭✨

---

## 5) テスト用の偽物：決め打ちで返す `SequenceRandom` 🎭🧪

テストでは「次はこれ、次はこれ」って返せると最強だよ💪😊
“乱数っぽい顔をしてるけど中身は台本” って感じ📜✨

```csharp
using System.Collections.Generic;

public sealed class SequenceRandom : IRandom
{
    private readonly Queue<int> _ints;
    private readonly Queue<double> _doubles;

    public SequenceRandom(IEnumerable<int>? ints = null, IEnumerable<double>? doubles = null)
    {
        _ints = new Queue<int>(ints ?? new[] { 0 });
        _doubles = new Queue<double>(doubles ?? new[] { 0.0 });
    }

    public int NextInt(int maxExclusive)
    {
        var v = DequeueOrRepeat(_ints);
        // テストで雑に使っても壊れないように範囲へ丸める（超やさし設計😊）
        if (maxExclusive <= 0) return 0;
        var m = v % maxExclusive;
        return m < 0 ? m + maxExclusive : m;
    }

    public int NextInt(int minInclusive, int maxExclusive)
    {
        var width = maxExclusive - minInclusive;
        return minInclusive + NextInt(width);
    }

    public double NextDouble()
    {
        var v = DequeueOrRepeat(_doubles);
        // 0.0〜1.0未満に丸める
        if (v >= 1.0) v = 0.999999999999;
        if (v < 0.0) v = 0.0;
        return v;
    }

    private static T DequeueOrRepeat<T>(Queue<T> q)
    {
        var v = q.Dequeue();
        q.Enqueue(v); // なくならないように循環♻️
        return v;
    }
}
```

---

## 6) 例題：ガチャ（レア度抽選）をテスタブルにする 🎮🎁✨

## やりたい仕様（かわいいやつ）😊

* 乱数でレア度が決まる
* SSR / SR / R のどれかが返る
* でもテストでは **必ずSSRが出る状況**を作りたい🎯

## まず、ロジックは `IRandom` にだけ依存する📦

```csharp
public enum Rarity { R, SR, SSR }

public sealed class GachaService
{
    private readonly IRandom _random;

    public GachaService(IRandom random)
    {
        _random = random;
    }

    public Rarity Draw()
    {
        // 0〜99
        var roll = _random.NextInt(100);

        // 例：SSR 3% / SR 17% / R 80%
        if (roll < 3) return Rarity.SSR;
        if (roll < 20) return Rarity.SR;
        return Rarity.R;
    }
}
```

---

## 7) テスト：乱数を“台本”にして期待値を固定する 🧪🎭✨

```csharp
using Xunit;

public class GachaServiceTests
{
    [Fact]
    public void Draw_roll_0_returns_SSR()
    {
        // roll=0 にしたい → 0 が返る乱数を用意🎭
        var random = new SequenceRandom(ints: new[] { 0 });
        var sut = new GachaService(random);

        var result = sut.Draw();

        Assert.Equal(Rarity.SSR, result);
    }

    [Fact]
    public void Draw_roll_10_returns_SR()
    {
        var random = new SequenceRandom(ints: new[] { 10 });
        var sut = new GachaService(random);

        var result = sut.Draw();

        Assert.Equal(Rarity.SR, result);
    }

    [Fact]
    public void Draw_roll_99_returns_R()
    {
        var random = new SequenceRandom(ints: new[] { 99 });
        var sut = new GachaService(random);

        var result = sut.Draw();

        Assert.Equal(Rarity.R, result);
    }
}
```

はい、これでテストは **一切揺れない**🎉✨
当たり前だけど超大事〜😊💖

---

## 8) よくある落とし穴（ここ超重要）⚠️😵‍💫

## ❌ ロジックの中で `new Random()` しちゃう

* 差し替え不能になる → テストが不安定に🧊
* さらに、短時間に複数生成すると「同じような列」になって困る系の話も有名💦（だからこそ共有の `Random.Shared` が用意されてる流れ） ([Microsoft Learn][3])

## ❌ テストで「seed固定のRandom」を使えばいいや、に頼りすぎる

`Random(int seed)` は「同じ seed なら同じ列が出る」例が公式にもあるけど ([Microsoft Learn][4])
“実装が将来変わったら列が変わる” みたいな不安が残りがち😵‍💫
なので教材としては、**SequenceRandom みたいに自前で台本化**がいちばん安心だよ🎭✨

## ❌ セキュリティ用途に `Random` を使う（ダメ、ゼッタイ）🔐💥

パスワード、トークン、認証コードみたいな “安全が必要な乱数” は `RandomNumberGenerator` を使うのが公式に案内されてるよ🛡️ ([Microsoft Learn][5])

---

## 9) 乱数ロジックで「テストしやすい形」にするコツ 🎯✨

## コツA：乱数を引く回数を“見える化”する 👀

* ロジックが複雑になるほど「何回乱数を引くのか」がバグ源になるよ〜😵‍💫
* `IRandom` に逃がしておくと、テストで「この順番で呼ばれる」を組みやすい🎭

## コツB：乱数を引いた後は“ピュア”に寄せる 🌿

* 乱数で得た `roll` を元に、判定は純粋にする
* そうすると、境界がスッキリして「変更が怖くない」💖

---

## 10) AI（Copilot/Codex）に手伝ってもらうプロンプト例 🤖💡✨

そのままコピペで使える系を置いとくね😊📝

* 「`IRandom` を使ってガチャ抽選ロジックを書いて。ロジック内で `new Random()` は禁止。xUnitのテストも3ケース書いて」
* 「テスト用の `SequenceRandom`（int列を順に返す）を実装して。範囲外の値は丸めて良い」
* 「このメソッド、乱数と判定が混ざってるから、乱数取得を境界に出して責務分割して」

⚠️ ただしAIがありがちなのはこれ👇

* インターフェースを増やしすぎる（抽象化しすぎ病）😇
* “便利だから”ってロジック側で `Random.Shared` を直呼びしがち💥
  → 合言葉は **「ロジックは IRandom だけ見てろ」** だよ😊✨

---

## 11) 練習問題（手を動かすと最速で身につく）✍️🎉

## 問1：シャッフルをテスタブルにする 🃏🎲

* `Shuffle<T>(IList<T> list, IRandom random)` を作ってみよう
* テストでは `SequenceRandom` を使って、並びが固定になるのを確認✅

## 問2：重み付き抽選 🎯

* 例：A=80%, B=15%, C=5%
* `roll` の境界値（79/80/94/95…）をテストで固めると強い💪✨

## 問3：当たり演出の“確率”を仕様化する 🎬✨

* 「10回に1回はキラキラ」みたいなのを、台本乱数で確実に検証してみよう🎭

---

## まとめ 🎀😊

* 乱数はテストを揺らす元凶になりやすい🎲🌪️
* **`IRandom` を境界にして外へ追い出す**と、ロジックが安定してテストも安定する🎉✨
* 本番は `Random.Shared` を包むのがシンプルで実用的（公式でスレッドセーフ明記） ([Microsoft Learn][3])
* セキュリティ用途は `RandomNumberGenerator`（公式推奨）🔐 ([Microsoft Learn][5])

---

## 次章予告（第16章）🗂️🚧✨

次は **ファイルI/O**！
`File.ReadAllText()` みたいな直呼びを境界に出して、メモリ上Fakeで爆速テストするよ〜🎉😊

[1]: https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core?utm_source=chatgpt.com "NET and .NET Core official support policy"
[2]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "What's new in C# 14"
[3]: https://learn.microsoft.com/en-us/dotnet/api/system.random.shared?view=net-10.0&utm_source=chatgpt.com "Random.Shared Property (System)"
[4]: https://learn.microsoft.com/en-us/dotnet/api/system.random.-ctor?view=net-10.0&utm_source=chatgpt.com "Random Constructor (System)"
[5]: https://learn.microsoft.com/en-us/dotnet/fundamentals/runtime-libraries/system-random?utm_source=chatgpt.com "System.Random class - .NET"
