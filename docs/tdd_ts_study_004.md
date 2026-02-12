# 第04章：TDDが向く場所・向かない場所🎯

![ロジックを狙い撃つ](./picture/tdd_ts_study_004_target.png)

（＝「どこをTDDで固めると一番ラクになる？」を決める章だよ〜💡🧪）

---

## 🎯 目的

TDDを「全部にやる」んじゃなくて、**効果がデカい場所に集中**できるようになること💪😊
テストがしんどくならず、むしろ「安心して進められる〜💕」って状態を作るよ！

---

## 📚 学ぶこと（この章のキモ3つ）

![ sweet spot target](./picture/tdd_ts_study_004_sweet_spot_target.png)

1. **TDDが超得意な場所（◎）**：入力→出力がはっきりしてる“純粋ロジック”
2. **TDDが苦手な場所（△/×）**：UIや外部I/Oなど“揺れる世界”
3. **境界で分ける考え方**：外の世界は薄く、中心ロジックを厚く守る🛡️

※テストを「粒度ごとに配分しよう」って考え方（テストピラミッド）は超有名だよ📐✨ ([martinfowler.com][1])

---

## ✅ まず結論：TDDは「変わりやすいのに壊れたら困るロジック」に全力🔥

![ core logic vs io](./picture/tdd_ts_study_004_core_logic_vs_io.png)

TDDって、**仕様をテストで固定して、安心してリファクタできる**のが最強ポイント🧪✨
だから狙い目はココ👇

### ◎ TDDが向く場所（気持ちよく回る😍）

* **純粋関数（同じ入力→同じ出力）**：計算、判定、変換、整形、ルール（割引・税・ポイント等）
* **ドメインルール**：ビジネスの“約束”そのもの（ここが壊れると事故るやつ😱）
* **境界の手前の判断**：API叩く前の「入力チェック」「分岐」「整合性」など

### △ ちょい工夫が必要（分ければ勝てる🙂）

* **日時・乱数・外部サービス**が絡むロジック（依存を外から渡すとテストしやすくなる👍）

### × TDDが苦手（やるなら最小限でOK🥺）

* **UIの見た目**（ボタンの色とかレイアウト）
* **外部I/Oど真ん中**（ネット・DB・ファイル・OS）
* **ライブラリ自身の挙動**（それは作者がテストしてる前提で使う🙆‍♀️）

> Node.jsのリリースラインには寿命（EOL）があって、EOL以降は更新されない＝外部要因が変わりやすい世界ってことも意識ね🧯 ([Node.js][2])

---

## 🗺️ 仕分けの地図（超かんたん4分類）

![画像を挿入予定](./picture/tdd_ts_study_004_quadrant_map.png)

テスト戦略を、ざっくりこの4つに分けると迷子になりにくいよ😊✨
（テストピラミッドの発想：**ユニット多め、E2E少なめ**） ([martinfowler.com][1])

1. **中心ロジック（ユニットテスト多め）**🧠🧪
2. **境界の手前（ユニット〜小さめ統合）**🚪
3. **境界アダプタ（統合テストは少数精鋭）**🌐📁
4. **UI/E2E（重要導線だけ、超少数）**🖥️🚶‍♀️

---

## 🔍 迷ったらコレ！「5つの質問」チェック✅

![ suitability flowchart](./picture/tdd_ts_study_004_suitability_flowchart.png)

次の機能（またはコード）に対して、上からYES/NOで答えてみてね👇

1. **同じ入力なら、毎回同じ結果になる？**（時間・乱数・通信なし？）

* YES → TDD向き◎
* NO → 2へ

2. **外部（HTTP/DB/FS/日時/乱数）を“外から渡す”形にできる？**

* YES → 分ければTDD向き◎
* NO → 3へ

3. **壊れたら大事故の“ルール”部分？**（金額、権限、状態遷移など）

* YES → ルールだけ切り出してTDD◎
* NO → 4へ

4. **UIの見た目を保証したい？それとも“導線”だけ？**

* 見た目 → だいたい×（コスト高💸）
* 導線 → E2E少数 or コンポーネント最小で△

5. **テストが遅くなる？不安定になる？**（フレークしそう？）

* YES → そのテストは減らして、中心ロジックを厚く🛡️

---

## 🧪 手を動かす：あなたの作りたい機能を“テストしやすさ”で仕分けよう✍️💕

![ sorting logic machine](./picture/tdd_ts_study_004_sorting_logic_machine.png)

### ① まず題材（例）

たとえば「推し活グッズ管理🎀」なら、こんな分解ができるよ👇

* **中心ロジック（◎）**：在庫数計算、合計金額、重複チェック、並び順ルール
* **境界の手前（◎〜△）**：入力のバリデーション、DTO→内部モデル変換
* **境界（△）**：localStorage保存、ファイル入出力、API通信
* **UI（×〜△）**：クリック→表示更新（重要導線だけ）

### ② 仕分けシート（コピペして埋めてね📝✨）

* 機能：＿＿＿＿＿＿＿＿＿＿
* 分解した部品（最低5個）：

  * A：＿＿＿＿（◎/△/×）理由：＿＿＿＿
  * B：＿＿＿＿（◎/△/×）理由：＿＿＿＿
  * C：＿＿＿＿（◎/△/×）理由：＿＿＿＿
  * D：＿＿＿＿（◎/△/×）理由：＿＿＿＿
  * E：＿＿＿＿（◎/△/×）理由：＿＿＿＿
* **“まずTDDする1個”**：＿＿＿＿（←ここが今日の勝ち筋🏆）

---

## 👩‍💻 ミニ例：TDDが向く（◎）純粋ロジックはこうなる

（ここは雰囲気が掴めればOK！まだ全部暗記しなくて大丈夫だよ☺️）

### ✅ 例：割引後の金額を計算（入力→出力が固定＝TDD向き）

```ts
// src/price.ts
export function applyDiscount(price: number, rate: number): number {
  if (price < 0) throw new Error("price must be >= 0");
  if (rate < 0 || rate > 1) throw new Error("rate must be between 0 and 1");
  return Math.floor(price * (1 - rate));
}
```

```ts
// tests/price.test.ts
import { describe, it, expect } from "vitest";
import { applyDiscount } from "../src/price";

describe("applyDiscount", () => {
  it("1000円を10%引きすると900円になる", () => {
    expect(applyDiscount(1000, 0.1)).toBe(900);
  });

  it("端数は切り捨てる（仕様）", () => {
    expect(applyDiscount(999, 0.1)).toBe(899);
  });

  it("負の価格はエラー（異常系も仕様）", () => {
    expect(() => applyDiscount(-1, 0.1)).toThrow();
  });
});
```

> こういうのがTDD向きの代表！テストが速い・安定・気持ちいい😍🧪

---

## 🌪️ 逆に：TDDが向かない（×）の典型パターン

* **UIの細かい見た目**：ちょっとした変更でテストが壊れて泣く😭
* **外部サービス直叩き**：ネットワーク次第で不安定＆遅い🐢
* **「実装の中身」を確認するテスト**：リファクタのたびにテストも壊れる⚡️

ここは割り切って、
✅ **中心ロジックはユニットで厚く**
✅ **UI/E2Eは重要導線だけ少数**
にすると、開発が楽になるよ〜🛟✨ ([martinfowler.com][1])

---

## 🤖 AI（Copilot/Codex等）の使い方：この章のテンプレ💬✨

![ ai classification helper](./picture/tdd_ts_study_004_ai_classification_helper.png)

AIはめちゃ便利だけど、**「どこをテストすべきか」まで丸投げ**すると迷子になりやすいの🥺
だから“仕分け”に使うのが最高に相性いいよ！

### ✅ プロンプト例（コピペOK）

1. **仕分け用**
   「この機能を“中心ロジック / 境界手前 / 境界(I/O) / UI”に分解して、TDD優先順位もつけて」

2. **依存の洗い出し**
   「このコード/機能に含まれる外部依存（時間・乱数・HTTP・FS・DB等）を列挙して、テストしやすい分離案を3つ」

3. **テスト観点だけ出させる**（コード生成より安全🙂）
   「この仕様で“正常/境界/異常”のテストケース案を箇条書きで。まだコードは書かないで」

---

## ✅ チェック（できたら合格🎉）

* [ ] 自分の機能を **◎/△/×で仕分け**できた
* [ ] 「まずTDDする1個」を決めた（中心ロジックから🎯）
* [ ] UIやI/Oを **無理にTDDしない**判断ができた
* [ ] “境界で分ける”って言葉の意味がふわっと分かった😊

---

## 🌟 おまけ：今どきの周辺事情（最新ベース）

* Node.jsはリリースラインごとにステータスが変わるよ（Current / Active LTS / Maintenance LTS など）([Node.js][3])
* TypeScriptは npm 上で最新版が更新され続けるので、教材やプロジェクトでは「安定版の範囲で追う」意識が大事だよ🧷([npmjs.com][4])
* Vitestは開発時に watch が基本で、編集したところに関連するテストを賢く回してくれるのが強み✨([Vitest][5])

---

次は、あなたが作りたいアプリの題材（例：推し活/家計簿/学食注文🍙）を1つだけ教えてくれたら、**この章の仕分けシートを一緒に埋めて**「まずTDDする1個」まで決めちゃおうね😊🎯💕

[1]: https://martinfowler.com/articles/practical-test-pyramid.html?utm_source=chatgpt.com "The Practical Test Pyramid"
[2]: https://nodejs.org/en/about/eol?utm_source=chatgpt.com "End-of-Life (EOL)"
[3]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[4]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "TypeScript"
[5]: https://vitest.dev/guide/features?utm_source=chatgpt.com "Features | Guide"

