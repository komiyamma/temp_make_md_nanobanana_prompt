# 第09章：AI（Copilot/Codex）をテスト学習に使うコツ 🤖💡🧪

この章は「AIを“テストの家庭教師”として使って、最短でテストに慣れる」ための回だよ〜！🥳
ポイントは **“AIに書かせる”より、まず“AIに考えさせる”** こと！🧠✨

---

## 9-0. この章のゴール 🎯✨

この章を読み終わると、こんな状態になれます👇💖

* テストケースを自分で思いつけるように、AIに引き出してもらえる📝🤝
* Arrange / Act / Assert（AAA）の骨組みをAIに作らせて、学習スピードUP⚡
* AIの出力をチェックして「これは危ないやつ！」が見分けられる👀⚠️
  -（おまけ）Visual Studio の **Copilot testing for .NET** みたいな“テスト生成＆実行”機能を、学習に上手く使える🚀
  ※ @test コマンドで、生成→ビルド→実行まで一気に回せる仕組みがあるよ。([Microsoft Learn][1])

---

## 9-1. AIは「テストの相棒」だけど、得意分野がある🐣➡️🤖


![testable_cs_study_009_ai_partner.png](./picture/testable_cs_study_009_ai_partner.png)

AIが得意なのはこのへん👇✨

* ✅ **テストケース案の大量出し**（抜け漏れ防止）📝
* ✅ **AAAの雛形作り**（書き方を覚えるのに最強）🧱
* ✅ **境界条件の洗い出し**（0、null、上限、期限切れ…）🎯
* ✅ **命名の提案**（テスト名が読みやすくなる）🪪
* ✅ **「このコード、テストしづらい理由」を言語化**（学習向き）🔍

AIが苦手・危険なのはここ👇⚠️

* ❌ 仕様を勝手に作る（「たぶんこう」って決めつける）😇
* ❌ 実装にベッタリなテストを作る（リファクタで壊れる）🧨
* ❌ I/Oが混ざってるのに気づかずテストを書き始める（遅い/不安定）🐢🌪️
* ❌ “それっぽいassert”で誤魔化す（重要な検証が抜ける）🕳️

だから、**AIに任せる順番**が大事！👇

> ① まず「テストケース案」を出させる
> ② 次に「AAAの骨組み」を作らせる
> ③ 最後に「コード化」させる（＆必ず自分でレビュー）👀✨

---

## 9-2. AI活用の黄金手順（これだけでOK）🥇🧪

## ステップ①：まず“テスト観点”だけ出してもらう📝

いきなりコードを書かせないで、まずはこれ！

**プロンプト例（観点出し）**👇

```text
このメソッドの単体テスト観点を「Given/When/Then」で10個出して。
境界値・異常系・代表値を混ぜて。コードはまだ書かないで。
```

👉 これで「何をテストするのが大事か」が先に身につくよ！💡

---

## ステップ②：AAAの“骨組みだけ”作らせる🧱

次に、観点のうち2〜3個だけ選んで、AAAの雛形を作る！

**プロンプト例（AAA雛形）**👇

```text
上の観点のうち「上位3つ」だけ、xUnitでAAAの骨組みを作って。
assertは“何を確認すべきか”が分かるようにコメントも添えて。
```

---

## ステップ③：実行して、落ちたら“直させ方”を覚える🔁

テストが落ちたら、ここが学習チャンス！🎉
落ちた理由を自分で考えつつ、AIにも説明させるのがコツ。

**プロンプト例（失敗解析）**👇

```text
このテストが失敗した理由を3つ候補で説明して。
「仕様の誤解」「実装のバグ」「テストの書き方ミス」に分類して。
```

---

## 9-3. 例題：ピュアなロジックにAIでテスト入門🧁🧪

例として、I/Oなしの“ピュア”なロジックを用意するよ（テスト学習に最高）✨

```csharp
public static class ShippingFee
{
    public static int Calc(int totalPrice, bool isRemoteArea)
    {
        if (totalPrice < 0) throw new ArgumentOutOfRangeException(nameof(totalPrice));

        if (totalPrice >= 5000) return 0;

        var fee = 500;
        if (isRemoteArea) fee += 300;
        return fee;
    }
}
```

## AIへの頼み方（最強の順番）💪🤖

**① 観点出し**

```text
ShippingFee.Calc の単体テスト観点を Given/When/Then で10個。
境界値（4999/5000）と異常系（負数）を必ず含めて。
```

**② AAA雛形（上位3つだけ）**

```text
上の観点から重要度が高い順に3つ選んで、xUnitでAAAの骨組みを書いて。
テスト名は「期待が読める英語」にして。
```

**③ 仕上げ（assertの質を上げる）**

```text
assertが弱い気がする。期待値の根拠をコメントで説明しつつ、より良いassertに改善して。
```

🎀 こうすると、**“テストの発想→形→質”** が順番に身につくよ！

---

## 9-4. Visual Studioの「@test」で、生成→実行まで体験する🚀🧪

最近の Visual Studio では、Copilot Chat から **@test** で対象を指定して
**テスト生成→ビルド→実行（Test Explorer）** までまとめて回せる仕組みがあるよ！([Microsoft Learn][1])

* `@test #target` みたいに指定（solution / project / file / class / member）([Microsoft Learn][1])
* 生成されたテストは **別のテストプロジェクト** に作られる([Microsoft Learn][1])
* フレームワークは **MSTest / NUnit / xUnit** 対応([Microsoft Learn][1])
* 生成後にビルドして、失敗があれば修正を試みて再実行…みたいな流れもある([Microsoft Learn][1])

## ⚠️ ここ超大事：安全面の注意

この系の機能は「AIが作ったものをローカルで実行する」場面があるので、
最初に同意を求められたり、コマンド実行の権限に注意してね…！([Microsoft Learn][2])
学習用プロジェクトで触るのが安心だよ🧸🔒

---

## 9-5. Codexを使うなら「どこで動くか」を先に把握しよ🐧🪟

Codex はIDE拡張があって、VS Code系で使う形が中心だよ。([OpenAI Developers][3])
ただ、**Windowsは“実験的サポート”** で、より良い体験は **WSLワークスペース推奨** と書かれているので、そこは知っておくとハマりにくい！([OpenAI Developers][3])

（学習目的なら、まずは Copilot 側で十分戦えるよ〜！😊🧪）

---

## 9-6. “鵜呑み禁止ポイント”チェックリスト ✅⚠️

AIが出したテスト、提出前にここだけ見て〜！👀✨

## ✅ テストの目的が「仕様の確認」になってる？

* ❌ 実装の内部（privateの動き）をなぞってない？🕵️‍♀️
* ✅ 「入力→出力」「例外」「境界」が見えてる？🎯

## ✅ I/Oが混ざってない？

* ❌ DateTime.Now / Random / ファイル / ネット / DB が直で出てこない？🌪️
* ✅ そういうのが出たら「境界に逃がす」話（次章以降）を思い出してね🚧✨

## ✅ assertが弱くない？

* ❌ “NotNull”だけ、みたいなフワッとした検証になってない？☁️
* ✅ 期待値が具体的で、理由が説明できる？🧠

## ✅ テスト名が読める？

* ✅ 「何が起きるべきか」がタイトルで分かる？📛✨

---

## 9-7. すぐ使える！AIプロンプトテンプレ集 📌🤖💖

## テンプレ①：観点出し（最重要）📝

```text
このメソッドの単体テスト観点をGiven/When/Thenで15個。
正常系:異常系:境界値 = 6:5:4 くらいで。
```

## テンプレ②：AAA雛形🧱

```text
観点の上位3つだけ、xUnitでAAAの骨組み。
Arrangeに“前提”、Assertに“何を守りたいか”が分かるコメント付きで。
```

## テンプレ③：不足ケースの指摘🔍

```text
このテスト群で抜けている重要ケースを5つ指摘して。
「境界値」「例外」「仕様の取り違えやすい点」に分けて。
```

## テンプレ④：テストが壊れやすいか判定🧨

```text
このテストがリファクタで壊れやすい理由を3つ挙げて、より壊れにくい書き方に直して。
```

---

## 9-8. ミニ課題（今日やると伸びるやつ）📚✨

## 課題A（超やさしい）🍓

ピュア関数1個を選んで
✅ 観点10個 → ✅ 上位3つだけAAA → ✅ 実装 → ✅ 実行

## 課題B（ふつう）🍰

例外系（負数、null、範囲外）を必ず入れて
「AIのassertが弱い問題」を自力で直す💪

## 課題C（ちょい上級）🍫

AIに“わざと雑なテスト”を作らせて、
チェックリストで **ダメ出し→改善** してみる😈✨

---

## 9-9. まとめ 🎀✨

![testable_cs_study_009_ai_tdd_flow.png](./picture/testable_cs_study_009_ai_tdd_flow.png)

* AIは「テストを書く手」より先に、「テスト観点を育てる先生」として使うのが強い🤝🧠
* **観点 → AAA → 実行 → 修正** のループで、テストが一気に身につく🔁⚡
* Visual Studio の **@test** みたいな機能で「生成→実行」を体験すると理解が早いよ([Microsoft Learn][1])
* でも最後は必ず自分の目でチェック👀💖（I/O混入・assert弱い・仕様ねつ造に注意！）

---

次の第10章は「`new`の怖さ（差し替え不能になる）」の話に入るよ〜！😳🔗✨
第9章で“AIがI/O混ぜちゃった時に、なぜ困るか”が分かってると、ここめちゃ繋がる👍💕

[1]: https://learn.microsoft.com/en-us/visualstudio/test/unit-testing-with-github-copilot-test-dotnet?view=visualstudio "Generate and run unit tests using GitHub Copilot testing - Visual Studio (Windows) | Microsoft Learn"
[2]: https://learn.microsoft.com/en-us/visualstudio/test/github-copilot-test-dotnet-overview?view=visualstudio "Overview of GitHub Copilot testing for .NET - Visual Studio (Windows) | Microsoft Learn"
[3]: https://developers.openai.com/codex/ide/ "Codex IDE extension"
