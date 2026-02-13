# 第03章：テストしやすいってどういう状態？🧪✨

![testable_ts_study_003_stability_scale.png](./picture/testable_ts_study_003_stability_scale.png)

この章は「テストしやすさ」を“感覚”じゃなくて“条件”で言えるようになる回だよ〜！😊💡
（あとで境界線（I/O）を引くときに、迷子になりにくくなるよ🗺️✨）

---

## 1. 今日のゴール🎯💖**「テストしやすい状態」を3つの条件で説明できる**ようになること！

✨
そして、コードを見たときに「ここがテストしづらさの原因だ！」って指差せるようになるよ👉👀

---

## 2. まず結論：テストしやすい状態＝この3つ🧪✨

### ✅ 条件A：入力→出力が安定してる（同じ入力なら同じ結果）

![testable_ts_study_003_io_list.png](./picture/testable_ts_study_003_io_list.png)

🔁🍀テストって「同じことしたら同じ結果になってほしい」よね？😊
でもコードの中にこんなのが混ざると、**勝手に結果が変わる**…😵‍💫

* 今の時刻（`Date`）⏰
* 乱数（`Math.random()`）🎲
* ネットワーク（`fetch`）🌐
* ファイル（読み書き）📁
* 環境変数（`process.env`）⚙️
* DBアクセス🗄️
* `console.log` みたいな出力📝（※出力も“外の世界”）

➡️ これらは「外の世界（I/O）」に触れてるので、テストの世界では不安定の原因になりがち💥

---

### ✅ 条件B：外部依存を“差し替え”できる🧩

![testable_ts_study_003_swappable_dep.png](./picture/testable_ts_study_003_swappable_dep.png)

🔌「本番では本物、テストではニセモノ」を入れ替えできると超強い💪✨

例）

* 本番：本物のHTTP
* テスト：固定データを返す“スタブ”🐣

この“差し替え”ができる状態を作るのが、あとでやる **I/O境界の分離**のド本命だよ〜！🚪✨

---

### ✅ 条件C：実行が速い⚡😆

![testable_ts_study_003_speed_comparison.png](./picture/testable_ts_study_003_speed_comparison.png)

テストが遅いと…



* だんだん回さなくなる😪
* 直すたびに待ち時間が苦痛😫
* CIが遅くてテンション下がる🫠

だから「中心（ロジック）」のテストは **爆速**が理想！🚀
I/Oが混ざると遅くなりやすい（ネット・DB・ファイルは特に）⚠️

---

## 3. “テスタブル度”セルフチェック✅🧠（10点満点）

![testable_ts_study_003_scoreboard.png](./picture/testable_ts_study_003_scoreboard.png)

次の質問に **YESなら+1点**で数えてみて〜！📋✨

1. 関数の引数を見るだけで必要な情報が揃ってる？🧾
2. 関数の中で `Date` や `Math.random()` を直接呼んでない？⏰🎲
3. 関数の中で `fetch` / DB / ファイルを直接触ってない？🌐🗄️📁
4. 関数が `console.log` とか“出力”を勝手にしてない？📝
5. 同じ入力を渡すといつも同じ出力になる？🔁
6. テストを書くとき“準備”が少ない？（依存を用意しなくていい）🧸
7. テストが1秒以内で終わりそう？⚡
8. 仕様変更が入ったとき、テスト直す場所が少なそう？✂️
9. 境界（I/O）が薄くて、ロジックが中心に集まってそう？🏠
10. 「ここがロジック」「ここがI/O」って説明できる？🗣️✨

**7点以上**ならかなり良い感じ〜！🎉
**4点以下**なら「I/Oが中心に混ざってる」疑い強め😵‍💫（次章以降でめっちゃ改善できるよ✨）

---

## 4. 例題：テストしにくいコード → テストしやすいコード🔁🛠

️### ❌ まずは“つらい版”😱（ロジックとI/Oがごちゃまぜ）

「会員ランクで割引して、APIでクーポンもらって、ログ出して…」みたいな処理を想像してね🍩🛒



```ts
// 悪い例：I/O + ロジック + 時刻が全部まざってる
export async function calcCheckoutTotal(userId: string, basePrice: number) {
  console.log("start checkout"); // 出力(I/O)

  const now = new Date(); // 時刻(I/O寄り)
  const res = await fetch(`https://example.com/coupon?user=${userId}`); // HTTP(I/O)
  const coupon = await res.json() as { discountRate: number };

  const isNight = now.getHours() >= 20;
  const nightBonus = isNight ? 0.1 : 0;

  const total = Math.floor(basePrice * (1 - coupon.discountRate - nightBonus));

  console.log("done"); // 出力(I/O)
  return total;
}
```

このコード、テストしようとすると…

* 時刻で結果が変わる⏰
* ネットワークが必要🌐
* ログ出力が混ざってうるさい📝
* テストが遅くなる⚡💦

➡️ **テスト以前に、準備がつらい**やつ😵‍💫

---

### ✅ “テストしやすい版”のコツ：中心を「入力→出力」に寄せる🏠✨

![testable_ts_study_003_core_separation.png](./picture/testable_ts_study_003_core_separation.png)

ポイントはこれだけ👇

1. **中心（ロジック）**は「必要な情報を引数で受け取る」
2. **外側（I/O）**が「時刻取得・HTTP・ログ」を担当
3. 外側が集めた材料を中心に渡す🎁

---

#### ✅ 中心：純粋ロジック（入力→出力だけ）

🍰✨

```ts
export type Coupon = { discountRate: number };

export function calcTotalCore(basePrice: number, coupon: Coupon, hour: number): number {
  const isNight = hour >= 20;
  const nightBonus = isNight ? 0.1 : 0;
  return Math.floor(basePrice * (1 - coupon.discountRate - nightBonus));
}
```

* `Date` なし⏰🙅‍♀️
* `fetch` なし🌐🙅‍♀️
* `console.log` なし📝🙅‍♀️
* 引数が“材料”だから分かりやすい🧾✨

これならテストが超ラク！😆

---

#### ✅ 外側：I/Oで材料を集めて中心に渡す🌍➡️

🏠

```ts
export async function calcCheckoutTotal(userId: string, basePrice: number) {
  console.log("start checkout");

  const now = new Date();
  const hour = now.getHours();

  const res = await fetch(`https://example.com/coupon?user=${userId}`);
  const coupon = await res.json() as { discountRate: number };

  const total = calcTotalCore(basePrice, coupon, hour);

  console.log("done");
  return total;
}
```

外側はI/OがあってOK！🙆‍♀️
でも「ロジックの核」は中心に隔離できたよね？🏠✨

---

## 5. “テストしやすさ”の最小イメージ（まだテスト環境なくてもOK）

🧪🌱中心がこうなってると👇



* 20時なら夜割が乗る
* クーポン10%ならこうなる
* どのケースも**一瞬で確認できる**⚡

たとえば（雰囲気だけ！）👇

```ts
// 例：中心ロジックのテストは「材料を渡して結果を見る」だけ
calcTotalCore(1000, { discountRate: 0.1 }, 10) // 10時 → 900
calcTotalCore(1000, { discountRate: 0.1 }, 21) // 21時 → 800
```

---

## 6. ハンズオン：同じ処理を「テストしやすい版」に言い換える🔁✨### 🥨 お題：あなたのコード（または下のミニ例）

を分解してみよう！まずはこの短いやつでもOK👇



```ts
export function greeting() {
  const hour = new Date().getHours();
  if (hour < 12) return "おはよう";
  if (hour < 18) return "こんにちは";
  return "こんばんは";
}
```

### ✅ ステップ1：隠れ入力を見つける👀🕵️

![testable_ts_study_003_hidden_input.png](./picture/testable_ts_study_003_hidden_input.png)

‍♀️* この関数の“材料”は何？
  → **hour（時刻）**だよね⏰

### ✅ ステップ2：材料を引数に出す🎁

```ts
export function greetingCore(hour: number) {
  if (hour < 12) return "おはよう";
  if (hour < 18) return "こんにちは";
  return "こんばんは";
}
```

### ✅ ステップ3：外側で時刻を取る🌍

```ts
export function greeting() {
  return greetingCore(new Date().getHours());
}
```

これだけで「中心のテスト」は秒で書ける状態になるよ⚡🧪

---

## 7. AI活用コーナー🤖🎀（“境界”を自分で握るのがコツ！

）AIに頼むと便利なやつ👇✨

**プロンプト例①：I/O洗い出し**

* 「次の関数から、テストを不安定にするI/O（時刻・乱数・HTTP・ファイル・環境変数・ログ）を列挙して、隠れ入力/隠れ出力として分類して」

**プロンプト例②：中心関数の提案**

* 「この関数を“中心（純粋関数）”と“外側（I/O）”に分けて。中心は引数で材料を受け取って返すだけにして」

**プロンプト例③：テストケース列挙**

* 「中心関数に対して、境界値を含むテストケースを表形式で10個出して」

AIが出した案を見て、あなたがチェックするポイントはこれ👇👀

* 中心に `Date` / `fetch` / `console.log` が残ってない？🙅‍♀️
* 引数が“材料”として十分？🧾
* 外側が薄くなってる？🚪✨

---

## 8. 2026/1/16 時点の“最新メモ”📰✨

（安心材料）* **TypeScript のnpm最新は 5.9.3**（少なくとも npm 上はこれが最新として公開されてるよ）([npm][1])


* **Jest は 30.0 が安定版**として案内されてるよ([Jest][2])
* **Vitest は 4.0 がリリース済み**（Vitest公式が発表）([Vitest][3])
* **Node.js は v24 が Active LTS**として扱われてる（公式のリリース表）([Node.js][4])

（この講座の後半で、こういう最新スタック前提で“実際にテストを回す”ところまで行くよ〜！🧪🚀）

---

## 9. この章のまとめ🎀✨

この章の結論はシンプル👇😊



* **テストしやすい状態**とは

  1. **入力→出力が安定**してて🔁
  2. **外部依存を差し替え可能**で🧩
  3. **実行が速い**⚡
* やることはだいたい **「中心を“材料→結果”に寄せる」**だけ🏠✨
* I/Oは悪じゃないけど、**中心に混ぜるとテストがつらくなる**😵‍💫

---

## 次章へつながるよ〜！

➡️🌈次の第4章は、今日の話を“地図”にする回！🗺️✨
「中心（ロジック）」と「外側（I/O）」を頭の中で分けられるようにして、**境界線を引く準備**をするよ✂️😊

必要なら、この章の例題をもう1つ（HTTPじゃない版：ファイル/環境変数/乱数）でも作れるよ〜！📁⚙️🎲

[1]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "TypeScript"
[2]: https://jestjs.io/versions?utm_source=chatgpt.com "Jest Versions"
[3]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
[4]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
