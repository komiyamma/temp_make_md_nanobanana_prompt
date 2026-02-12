# 第14章：“1章の粒度”ルール（ブレ防止）📏

![定規で測る粒度](./picture/tdd_ts_study_014_ruler.png)

TDDって、**小さく回すほど気持ちいい**んだけど…
教材でも実務でも「1回の作業がデカくなる」と、急にしんどくなるのね🥲💦

だからこの章は、**“ブレない粒度”の決め方**をガチ固定します💪✨
（＝迷いが減って、テストが回り続けるよ🌀🩷）

---

## 🎯 目的（この章でできるようになること）🎀

* 「1章＝どこまで？」を**毎回同じ基準**で決められる📏✨
* 1章を **1〜3コミット**に収める設計ができる🧩
* コミットメッセージを**読み物**にして、あとから自分が助かる📚💕

---

## 📚 学ぶこと（超重要3点）💡

### 1) **1章＝1ゴール（1つの“約束”）**🤝

1章で増やすのは、基本 **「新しい仕様（テスト）」は1テーマだけ**にするのがコツ🎯
テーマが2つあると、だいたい途中でグチャる🥺

---

### 2) **小さく刻む＝小さく統合できる**🧷

小さく刻むと何が嬉しいの？っていうと…

* 小さな変更はレビューしやすい👀✨（大きい塊は読むのが地獄）
* 小さな変更はマージや統合がラク🧩
* 小さな変更はロールバックもしやすい🔙

こういう “小ささの勝ち” は、CI/継続的デリバリー系のガイドでも強く推されてる考え方だよ📌✨ ([about.gitlab.com][1])

---

### 3) **コミットは“履歴の文章”**📝✨

おすすめは **Conventional Commits** みたいな形式👇
`<type>(scope): <description>` の形で揃えると、履歴が読みやすくなるよ📚✨ ([conventionalcommits.org][2])

---

## 🧪 手を動かす（この章のメイン課題）🛠️🎀

### ✅ ステップ0：この章の“粒度ルール”を固定する📏

![画像を挿入予定](./picture/tdd_ts_study_014_granularity_balance.png)

まず、あなたのプロジェクトに「粒度ルール」を置いちゃおう！

* `docs/chapter-rule.md`（ファイル名は何でもOK）を作って、これを書く👇

**章の定義（おすすめの固定文）**✨

* 1章＝**1つのゴール**
* 1章＝**1〜3コミット**
* 章の終わり＝**全テストが緑＋リファクタ済み＋読み物としてOK**📗✅

---

### ✅ ステップ1：「1章＝1〜3コミット」テンプレを作る🧱

この教材では、基本テンプレはこれでいこう💕

* **Commit A（test:）**：仕様をテストで追加する🧪🔴
* **Commit B（feat:）**：最小実装で通す🟢✨
* **Commit C（refactor:）**：読みやすく整える🧹💎

> 💡ポイント：**“Redのままコミット”は基本しない**（あとで履歴が混乱しがち）
> まず「テスト追加 → 最小実装で緑」までを1セットでコミットにするのが初心者向けで安全だよ🛡️

---

### ✅ ステップ2：コミット種別（type）を決める🏷️

最小セットはこれで十分かわいい＆強い🩷

* `test:` テスト追加・修正
* `feat:` 機能追加
* `fix:` バグ修正
* `refactor:` 振る舞いを変えない整理
* `docs:` ドキュメント
* `chore:` 雑務（設定、依存更新など）

この “typeで揃える” 発想自体が Conventional Commits のど真ん中だよ📌 ([conventionalcommits.org][2])

---

### ✅ ステップ3：コミット文テンプレをコピペできる形にする📋✨

このまま使ってOKだよ〜！🥰

```text
test: add spec for <対象> (case: <ケース名>)
feat: implement <対象> minimally to satisfy spec
refactor: rename/extract to improve readability of <対象>
```

例もつけちゃう👇

```text
test: add spec for price rounding (case: 0.5 rounds up)
feat: implement rounding rule for subtotal
refactor: extract rounding function and rename variables
```

---

## 🤖 AIの使いどころ（この章はここが本命）🧠✨

### 1) 「この章、デカすぎ？」をAIに判定させる🔍

AIにこれを投げてね👇（コピペ用💕）

```text
今から実装したい内容を貼るので、
「1章＝1ゴール、1〜3コミット」に収めるために
(1) ゴール定義
(2) 分割案（章を2つ以上にしてOK）
(3) 1章あたりのコミット案（test/feat/refactor）
を箇条書きで出して。
```

---

### 2) コミットメッセージをAIに“候補3つ”出させる📝

```text
この差分の意図を説明するコミットメッセージを
Conventional Commits形式で3案ください。
typeは test/feat/fix/refactor/docs/chore から選んで。
短く、何が変わったかわかる文章にして。
```

Conventional Commits形式は、こういう自動整形・自動チェックとも相性いいよ✨ ([conventionalcommits.org][2])

---

## ✅ チェック（合格ライン）💮✨

### ✅ 章の終わりチェック（絶対）🧪

* テストは全部グリーン？🟢
* テスト名だけ読んで仕様が想像できる？📘
* “つらい重複” を放置してない？👃🚨
* 1章のゴールを一言で言える？🎯
* コミットが 1〜3 に収まった？📏✨

---

## 🧯 ありがち事故と直し方（ここ超あるある）🥺

### 😵「コミットが5個以上になる…」

👉 それ、だいたい **章が2章分**！
**“仕様のテーマ”**で割るのが一番キレイ✂️✨
（例：税計算 と 端数処理 は別章にする、みたいな）

---

### 😵「refactorの時間がなくて放置…」

👉 それ、次回の自分が泣くやつ😭💦
Refactorは “見た目” じゃなくて **次の変更をラクにする保険**だよ🛡️✨

---

### 😵「コミットメッセージ適当になりがち」

👉 typeだけでも揃えると世界が変わる🌈
Conventional Commitsは “履歴が読める” ための最低限ルールだよ📚✨ ([conventionalcommits.org][2])

---

## 🎁 この章の提出物（できたら優勝）🏆💕

* ✅ 粒度ルールを書いた `docs/chapter-rule.md`
* ✅ コミット種別と例を書いた `docs/commit-convention.md`
* ✅ この章のテンプレに沿ったコミットが **1〜3個**入ってること🎀

---

次の章（第15章）は、いよいよ **AAA（Arrange/Act/Assert）でテストの型を固定**して、毎回迷わない書き方に入るよ🧱🧪✨

[1]: https://about.gitlab.com/topics/version-control/version-control-best-practices/?utm_source=chatgpt.com "What are Git version control best practices?"
[2]: https://www.conventionalcommits.org/ja/v1.0.0/?utm_source=chatgpt.com "Conventional Commits"
