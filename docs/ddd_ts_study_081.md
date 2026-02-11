# 第81章：ルールの分離：if地獄を見つける👀

この章はひとことで言うと…
**「ルール（条件）が増えたとき、コードが“爆発”する前兆＝if地獄を見抜く回」**だよ〜！💣✨
次の章（Specification）に進むために、まず **“何が複雑なのか”をちゃんと見える化**します📝🔎

ちなみに、**2026-02-07時点**で、npm上のTypeScriptの最新版表示は **5.9.3** になってるよ（安定版として扱いやすい）📌✨ ([NPM][1])
（「TypeScript 5.9」の公式Release Notesページもあるよ🧾） ([typescriptlang.org][2])

---

## 1) “if地獄”ってなに？どうして起きるの？😵‍💫🌪️

### ✅ if地獄の正体

**条件（if）が増えすぎて、変更が怖くなる状態**のことだよ🥺💦
たとえば割引やキャンペーンって、こうなるでしょ？

* 新キャンペーン追加🎉
* 既存キャンペーンの条件が微修正🪛
* 併用不可ルールが増える🚫
* 「例外」が増える（でも仕様書は増えない）📄😇

そして気づくと、コードがこうなる👇

* 条件が長い（&& と || がぐちゃぐちゃ）🫠
* 同じ条件がコピペで散らばる📎
* どれが“業務ルール”で、どれが“手順”か分からない🤯
* テストが書けない／壊れる💥

---

## 2) 例：カフェ注文に“割引地獄”を発生させてみる☕🏷️（わざとね！）

ここでは「割引ルール」が増える未来を想像して、あえて地獄を作るよ😂🧨

### 🎯 ありがちな割引ルール（例）

* 学割：学生なら10%OFF🎓
* 平日限定：平日だけ適用📅
* ハッピーアワー：15:00〜17:00なら15%OFF⏰
* 初回クーポン：合計1500円以上で500円引き🎫
* VIP：20%OFF（ただし他と併用不可👑🚫）
* 「一番お得な1つだけ適用」みたいなルールもありがち💰✨

### 😇 こういうコードが生まれやすい（例）

（※ “ダメ例”として見てね！）

```ts
type Order = {
  totalYen: number;
  isStudent: boolean;
  isVip: boolean;
  isFirstOrder: boolean;
  hasCoupon: boolean;
  dayOfWeek: "Mon" | "Tue" | "Wed" | "Thu" | "Fri" | "Sat" | "Sun";
  hour: number; // 0-23
};

export function calculateDiscountYen(order: Order): number {
  let discount = 0;

  // VIPは強い（併用不可）
  if (order.isVip) {
    discount = Math.floor(order.totalYen * 0.2);
  } else {
    // 学割（平日限定）
    if (order.isStudent) {
      if (
        order.dayOfWeek === "Mon" ||
        order.dayOfWeek === "Tue" ||
        order.dayOfWeek === "Wed" ||
        order.dayOfWeek === "Thu" ||
        order.dayOfWeek === "Fri"
      ) {
        discount = Math.floor(order.totalYen * 0.1);
      }
    }

    // ハッピーアワー（さらにお得？）
    if (order.hour >= 15 && order.hour < 17) {
      const happy = Math.floor(order.totalYen * 0.15);
      if (happy > discount) discount = happy;
    }

    // 初回クーポン
    if (order.isFirstOrder && order.hasCoupon) {
      if (order.totalYen >= 1500) {
        if (500 > discount) discount = 500;
      }
    }
  }

  // 念のため上限（よくある）
  if (discount > order.totalYen) discount = order.totalYen;

  return discount;
}
```

### 💥 これが“地獄の入口”な理由

この時点でもう、未来が見える…👀🧨

* 条件が増えるたびにこの関数が太る🐷
* 「平日判定」みたいな条件が他でも必要になってコピペされる📎
* “一番お得なやつだけ”の比較ロジックが散らばる⚖️
* ルール同士の優先順位が“ifの順番”に埋まってしまう🧩😱
* 「この割引、なぜ適用されないの？」が説明できない💬🫥

---

## 3) if地獄の“見分け方”チェックリスト✅👀

当てはまるほど、**「ルールを分離する道具（Specification/Policyなど）」が必要**だよ🧰✨

### 🧨 におい（コードの症状）

* ✅ ifのネストが深い（3段くらいで警戒）🕳️
* ✅ 条件式が長い（&& || が多い、カッコが多い）🧠💦
* ✅ 同じ判定があちこちにある（平日判定、会員判定など）📎
* ✅ “例外だけ特別扱い”が増える（VIPだけ別、初回だけ別…）👑🎫
* ✅ 変更のたびに「どこを直せば？」って探検が始まる🧭😵‍💫
* ✅ 仕様を説明するとき、コードを開かないと話せない📖💥

### 🧪 におい（テストの症状）

* ✅ テストが「全パターン網羅できない」感じになる🧪😇
* ✅ 1つのテストで準備が重い（データが大きい）🧱
* ✅ 失敗時に「どの条件が原因？」が分からない🔍💦

---

## 4) “見える化”のコツ：ルールを箇条書きに分解する📝✨

ここがこの章のメイン作業だよ〜！💪💖
やることはシンプル：

### 🎯 手順A：コードから「ルール文」を抜く

さっきの例なら、こんなふうに書き出す：

* ルール1：VIPなら20%引き（他と併用不可）👑🚫
* ルール2：学生かつ平日なら10%引き🎓📅
* ルール3：15〜17時なら15%引き⏰
* ルール4：初回かつクーポンありかつ1500円以上なら500円引き🎫
* ルール5：複数ある場合は「最大割引1つだけ」💰✨
* ルール6：割引は合計を超えない🧱

✅ **ポイント**：まず“自然言語”に戻すの！
コードのまま考えると、ifの順番に引っ張られて迷子になるよ🧭🥺

### 🎯 手順B：各ルールを「条件」と「結果」に分ける

* 条件（いつ？）→ 学生 && 平日
* 結果（どうする？）→ 10%引く

これを分けるだけで、次章のSpecification/Policyがすごく作りやすくなるよ🔎📄✨

---

## 5) “まずは軽く分離”してみる：名前をつけて外に出す🏷️➡️📦

いきなりSpecificationに行く前に、**最小の改善**をやってみよ〜！💡
コツは **「条件に名前をつける」** だけ！それだけで世界が変わる🌍✨

```ts
function isWeekday(day: Order["dayOfWeek"]): boolean {
  return day === "Mon" || day === "Tue" || day === "Wed" || day === "Thu" || day === "Fri";
}

function isHappyHour(hour: number): boolean {
  return hour >= 15 && hour < 17;
}

function canUseFirstCoupon(order: Order): boolean {
  return order.isFirstOrder && order.hasCoupon && order.totalYen >= 1500;
}

export function calculateDiscountYen(order: Order): number {
  if (order.isVip) {
    return Math.min(Math.floor(order.totalYen * 0.2), order.totalYen);
  }

  const candidates: number[] = [];

  if (order.isStudent && isWeekday(order.dayOfWeek)) {
    candidates.push(Math.floor(order.totalYen * 0.1));
  }

  if (isHappyHour(order.hour)) {
    candidates.push(Math.floor(order.totalYen * 0.15));
  }

  if (canUseFirstCoupon(order)) {
    candidates.push(500);
  }

  const best = candidates.length === 0 ? 0 : Math.max(...candidates);
  return Math.min(best, order.totalYen);
}
```

### ✅ この時点で得してること🎉

* 条件が「読める」📖✨（isWeekday / isHappyHour って意味がそのまま）
* ルールごとにテストが書ける🧪💪
* ルール追加が “関数を1個足す” に近づく🧩➡️🧩
* 次章の **Specificationの形（isSatisfiedBy）** に超近い😍

---

## 6) テストの勝ち筋：ルール単位で小さく検証する🧪💎

「割引計算の全部」をテストしようとするとしんどい😇
だから、**条件関数を先にテスト**するのが楽だよ〜！

```ts
import { describe, it, expect } from "vitest";

describe("isWeekday", () => {
  it("Monは平日", () => {
    expect(isWeekday("Mon")).toBe(true);
  });

  it("Satは平日じゃない", () => {
    expect(isWeekday("Sat")).toBe(false);
  });
});

describe("canUseFirstCoupon", () => {
  it("初回+クーポン+1500円以上ならOK", () => {
    const order = {
      totalYen: 1500,
      isStudent: false,
      isVip: false,
      isFirstOrder: true,
      hasCoupon: true,
      dayOfWeek: "Mon",
      hour: 12,
    } satisfies Order;

    expect(canUseFirstCoupon(order)).toBe(true);
  });
});
```

ここで使ってる **satisfies** は「型に合ってるかチェックしつつ、型を変えない」便利機能だよ🧡
テストデータ作る時、地味に事故が減る✨ ([typescriptlang.org][3])

---

## 7) AIの使いどころ（この章は“壁打ち”が最強🤖🫶）

この章は、AIがめちゃくちゃ相性いいよ〜！😍✨
おすすめの使い方だけ置いとくね（そのまま投げてOK）📮💕

### 🧠 プロンプト例①：ルール抽出（自然言語化）

* 「この関数の条件分岐を、業務ルールとして箇条書きにして。条件と結果を分けて。」

### 🧠 プロンプト例②：重複発見

* 「このコード内で重複している条件（同じ意味の判定）を見つけて、共通関数名を提案して。」

### 🧠 プロンプト例③：テスト観点生成

* 「この割引ルールの境界値と例外ケースをGiven/When/Thenで10個提案して。」

### 🧠 プロンプト例④：仕様の矛盾チェック

* 「ルール同士の矛盾（同時に成り立たない、優先順位が必要など）を指摘して。」

✅ ただし注意：**AIは“仕様の正しさ”は保証できない**から、最後は自分の言葉でOK/NG決めよ〜！🫶🧠

---

## 8) まとめ：この章でできるようになったこと🎒✨

* ✅ if地獄の“におい”を嗅ぎ分けられる👃🧨
* ✅ ルールを「条件」と「結果」に分解できる📝
* ✅ 条件に名前をつけて、まずは関数に逃がせる🏷️➡️📦
* ✅ ルール単位でテストを書ける🧪💎

そして次章（第82章）でついに…
**条件をオブジェクト化する（Specification）**に入るよ〜！🔎📄✨
この章の「名前をつけた条件関数」が、そのまま材料になる😍

---

## 9) ミニ宿題（15〜30分）🧁⏳

### 宿題A：if地獄センサーON👀

自分のコード（または例題）で、以下を探してみて👇

* ネスト深めのif
* 長い条件式
* 重複条件

### 宿題B：ルールを5個、自然言語に戻す📝

「条件」と「結果」に分けて箇条書き！✨

### 宿題C：条件を2個だけ関数にしてみる🏷️

例：isWeekday / isHappyHour みたいにね💕

---

必要なら、あなたの現行コード（割引やキャンペーン周り）を貼ってくれたら、**“どこがif地獄の芽か”**を一緒にマーキングして、**ルールの分解（条件/結果）**まで一気にやるよ👀🧡

[1]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "TypeScript"
[2]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html?utm_source=chatgpt.com "Documentation - TypeScript 5.9"
[3]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-9.html?utm_source=chatgpt.com "Documentation - TypeScript 4.9"
