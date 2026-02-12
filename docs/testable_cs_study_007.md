# 第07章：テストの種類をゆるく知る 🔍😊

この章は「テスタブル設計（I/O境界の分離）」ロードマップの中で、**“どのテストを、どれくらい、どこに打つ？”**の感覚をつかむ回だよ〜！🧠✨
（次章で、実際にテストプロジェクトを作って動かすよ🛠️）

---

## 0. この章のゴール 🎯💖

読み終わったら、こんな状態になればOK！

* ✅ **単体テスト / 結合テスト / E2E** の違いをざっくり説明できる
* ✅ 「このケースはどの種類のテストが合う？」を判断できる
* ✅ **I/O境界の分離**が、どのテストをラクにしてくれるかイメージできる 🚪✨

---

## 1. まず結論：テストは “3階建て” で考えるのがラク 🏠✨


![testable_cs_study_007_test_pyramid.png](./picture/testable_cs_study_007_test_pyramid.png)

よくある考え方が **テストピラミッド**だよ〜！🔺
**下ほど数が多くて速い / 上ほど数が少なくて重い**、ってイメージ。 ([martinfowler.com][1])

* 🧩 **単体テスト（Unit）**：速い・安定・たくさん
* 🤝 **結合テスト（Integration）**：ちょい重い・ほどほど
* 🚀 **E2E**：重い・不安定になりがち・必要最小限

> つまり…
> **“土台（単体）を厚くして、上（E2E）を薄くする”** のが基本戦略だよ〜！💪😊 ([martinfowler.com][1])

---

## 2. 単体テスト（ユニット）ってなに？🧩✨

### ✅ ひとことで

**「小さく切ったロジックだけを、外の世界なしでテストする」**やつ！🌿

### 🟢 単体テストが得意なもの

* 条件分岐（if）の正しさ ✅
* 計算・変換・判定ロジック 🧮🔁
* 入力に対して出力が決まる “ピュアな処理” 🎯

### 🟣 単体テストの強み

* ⚡爆速（たくさん回せる）
* 🧊安定（ネットやDBに左右されにくい）
* 🧭バグの場所がすぐ分かる

Microsoftのベストプラクティスでも、**読みやすくて壊れにくい（brittleじゃない）単体テスト**が大事って話がまとまってるよ〜！📚✨ ([Microsoft Learn][2])

---

## 3. 結合テスト（Integration）ってなに？🤝✨

### ✅ ひとことで

**「複数の部品が、ちゃんとつながって動くか」**を見るテスト！

ここで注意ポイント⚠️
「結合テスト」って言葉、けっこう人によって範囲がブレがち…！
なので **“何と何を結合してるのか”** を言えるのが大事だよ🗣️✨（このへんは定義が揺れるって話もよく出る） ([jayfreestone.com][3])

### 🟢 たとえばこんな結合

* 🧩 アプリのロジック × 🗄️ DBアクセス層（Repository）
* 🧩 アプリ × 🌐 外部APIクライアント
* 🧩 ASP.NET Core のパイプライン全体（ルーティング〜DI〜コントローラ〜など）

ASP.NET Coreの統合テストの公式説明も、
**単体より広い範囲で、複数コンポーネントが協調して結果を出すかを見る**って説明になってるよ📚 ([Microsoft Learn][4])

### 🟠 結合テストの特徴

* 🐢 単体より遅い（DB/ファイル/起動が絡むことが多い）
* 🧪 でも「つなぎ目の事故」を拾うのがうまい！
* ⚠️ 環境差でコケやすい（だから数は絞りたい）

---

## 4. E2E（End-to-End）ってなに？🚀✨

### ✅ ひとことで

**「ユーザー目線で、最初から最後まで通るか」**を見るテスト！

例：

* 🖥️ 画面でログイン → 🛒 購入 → 📩 メール通知 → ✅ 完了画面
  みたいな “一連の流れ” をまるっと確認する感じ！

### 🟡 E2Eの強み

* 「ユーザー体験として成立してる？」を確認できる 💖
* 大きな回帰（致命的な壊れ）を防ぐ最後の砦 🛡️

### 🔴 でも弱点もある

* 🐘 重い（準備も実行も）
* 🌪️ 壊れやすい（通信・環境・タイミング）
* 🔍 失敗したとき、原因特定が難しい

なので基本は **“必要なところにだけ少数”**が王道だよ〜！ ([martinfowler.com][1])

---

## 5. I/O境界の分離と、テスト種類の相性が最高にいい話 🚪✨

ここがこのロードマップの本題につながるところ！💡😊

### 🎯 理想の割り振り（めちゃおすすめ）

* 📦 **内側（ルール・判断・計算）**：🧩単体テストで厚く！
* 🚧 **境界（I/Oを包んだインターフェース）**：🤝結合テストで“つなぎ目”確認
* 🌍 **外側（本物のDB/ネット/UI）**：🚀E2Eは最小限

つまり…
**I/Oを外に追い出せば追い出すほど、単体テストで守れる範囲が増える**🎉
→ 変更が怖くなくなる！🛡️✨

---

## 6. 「これはどのテスト？」分類ゲーム 🎮✨

想像してみてね👇

### ケースA：クーポン割引の計算（条件いっぱい）🎟️🧮

* ✅ **単体テスト**向き
  理由：I/Oなし、分岐と計算の正しさが命

### ケースB：期限チェック（“今日”を使う）🕰️

* ✅ **単体テスト**にしたい
  コツ：`今`は揺れるから、後の章で `IClock` に逃がすと勝ち✨

### ケースC：DBからユーザーランク取得して送料を決める 🗄️🚚

* 🧩ロジック自体は単体で守りつつ
* 🤝 DBとの接続・SQL・マッピングが絡むなら **結合テスト**も少し置く
  （“つなぎ目”が壊れやすいからね😵‍💫）

### ケースD：購入フロー全体（画面→API→DB→メール）🛒📩

* 🚀 **E2E**（ただし少数！）
  「購入できない」は致命的だから、ここは保険として価値が高い💎

---

## 7. 初心者がハマりやすい罠トップ5 😵‍💫💥

### ① E2Eだけで全部守ろうとする 🚀🚀🚀

→ すぐ遅くなる＆壊れやすくなる＆原因追跡地獄👻
**土台（単体）を先に固める**のが最短ルートだよ〜！ ([martinfowler.com][1])

### ② “結合テスト”の言葉がふわふわ問題 🤝🌫️

→ 何を結合してるか言おう！
「DB込み？HTTP込み？UI込み？」みたいに範囲をはっきり✨ ([jayfreestone.com][3])

### ③ モックしすぎて、現実から離れる 🎭🌀

→ 最初は **Fake/Stub中心**でOK（呼び出し回数の検証地獄に入らない）😊

### ④ テストが遅い＆不安定（フレイキー）🐢🌪️

→ それ、I/Oが内側に混ざってるサインかも🚨
境界に逃がすと改善しやすい✨

### ⑤ 1テストで確認しすぎて、失敗すると原因不明 🔍❓

→ 1テスト1理由！
単体は特に「何が壊れたか」が分かるのが強みだよ🧠✨ ([Microsoft Learn][2])

---

## 8. ミニコラム：2026年1月時点の “.NETテスト界隈” 超ざっくり 📰✨

> 次章（環境構築）への予習にもなるよ〜😊

* .NET は **.NET 10 がLTS**（2025-11-11リリース、2026-01-13時点の最新パッチは 10.0.2） ([Microsoft][5])
* C# は **C# 14** が “最新のVisual Studio 2026 または .NET 10 SDK” で試せる、という位置づけで案内されてるよ📚 ([Microsoft Learn][6])
* MSTest は **v4 が stable**（v3と互換じゃない点があるよ、という移行ガイドが出てる） ([Microsoft Learn][7])
* xUnit は **v3 が正式リリース済み**（v3のリリースノートも継続して更新されてる） ([xunit.net][8])
* Visual Studio 2022 は 2026-01-13 に 17.14 系の更新が出てる（リリース履歴に載ってる） ([Microsoft Learn][9])
* さらに “Visual Studio 2026” 自体も配布ページ・リリースノートが公開されてるよ📦 ([Visual Studio][10])

---

## 9. 章末ミニ演習 ✍️😊（サクッとでOK！）

次のそれぞれ、どのテストが向きそう？理由も1行で✨

1. 年齢から料金区分（子ども/学生/一般）を決める 🎫
2. CSVを読み込んでインポートする（ファイルが絡む）🗂️
3. 外部APIから為替レートを取って換算する 🌐💱
4. 「ログイン→設定変更→保存→再ログインで反映」の一連 🔐
5. DBのマイグレーション後も、検索が動くか確認 🗄️🔍

（答え合わせしたくなったら、そのまま投げて〜！私が一緒に判定するよ🙌💕）

---

## まとめ 🎁✨

* 🧩 **単体テスト**：ロジック守る、速い、たくさん
* 🤝 **結合テスト**：つなぎ目守る、ほどほど
* 🚀 **E2E**：全体の保険、少数精鋭
* 🚪 **I/O境界の分離**をすると、単体で守れる範囲が増えて超ラクになる！

---

次の第8章では、いよいよ **テスト基盤を用意して、実行して、気持ちよく回す**ところに行くよ〜！🛠️✨

[1]: https://martinfowler.com/articles/practical-test-pyramid.html?utm_source=chatgpt.com "The Practical Test Pyramid"
[2]: https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-best-practices?utm_source=chatgpt.com "Best practices for writing unit tests - .NET"
[3]: https://www.jayfreestone.com/writing/integration-tests/?utm_source=chatgpt.com "Defining 'integration' tests"
[4]: https://learn.microsoft.com/en-us/aspnet/core/test/integration-tests?view=aspnetcore-10.0&utm_source=chatgpt.com "Integration tests in ASP.NET Core"
[5]: https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core?utm_source=chatgpt.com "NET and .NET Core official support policy"
[6]: https://learn.microsoft.com/ja-jp/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "C# 14 の新機能"
[7]: https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-mstest-migration-v3-v4?utm_source=chatgpt.com "MSTest migration from v3 to v4 - .NET"
[8]: https://xunit.net/releases/v3/1.0.0?utm_source=chatgpt.com "Core Framework v3 1.0.0 [2024 December 16]"
[9]: https://learn.microsoft.com/ja-jp/visualstudio/releases/2022/release-history?utm_source=chatgpt.com "Visual Studio 2022 リリース履歴"
[10]: https://visualstudio.microsoft.com/downloads/?utm_source=chatgpt.com "Visual Studio & VS Code Downloads for Windows, Mac, Linux"
