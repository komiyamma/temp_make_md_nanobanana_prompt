# 第23章：境界でデータ変換（DTO ↔ Domain）🔁✨

![testable_ts_study_023_dto_converter.png](./picture/testable_ts_study_023_dto_converter.png)

## この章でできるようになること🎯💖* 「外から来たデータ（DTO）

」を、**中心（ドメイン）が扱いやすい形（Domain）**に変換できるようになる✨


* **命名・単位・null・欠損**みたいな「外の都合」を、**境界で吸収**できるようになる🧽🌟
* 変換ロジックを **I/Oなしの純粋処理**にして、**サクッとユニットテスト**で守れるようになる🧪⚡

---

## 2026年1月時点の“最新メモ”🗞️

✨* TypeScript の安定版は **npm の “Latest” が 5.9.3**（最終公開は 2025-09-30 表示）だよ📦✨ ([npm][1])


* 公式ブログでは、TypeScript 6.0 を「橋渡し（bridge）リリース」とし、TypeScript 7（ネイティブ移植）へ向けた方針が説明されてるよ🌉🚀 ([Microsoft for Developers][2])
* TypeScript 5.9 の “import defer” など、新しい仕様サポートも入ってきてるよ（公式リリースノート）🧠✨ ([TypeScript][3])

> ここから先は、どのバージョンでも役に立つ「設計の型」なので、安心して身につけてOKだよ☺️🍀

---

## DTOとDomainって、結局なに？🤔🧩### DTO（Data Transfer Object）

📦* API・DB・外部サービスなど、**外の世界の形のまま**運ばれてくるデータ


* 例：snake_case、文字列の数字、null多め、単位がバラバラ…などなど😇💦

### Domain（ドメインモデル）

💎* アプリの中心（ロジック）が「これが欲しい！」って思う、**意味のある形**


* 例：金額は Money、IDは UserId、日付は “Dateっぽい何か” など、**型で安全にしたい**やつ✨🛡️

---

## なぜ「境界で変換」しないとつらいの？😵‍💫💥外の形をそのまま中心に持ち込むと…



* 中心のあちこちで「snake_caseをcamelCaseに…」みたいな処理が散らばる🌀
* nullチェック地獄が始まる🕳️
* 単位（円/ドル/税込/税抜/秒/ミリ秒）が混ざって事故る💣
* API仕様変更が来た瞬間に、中心がバキバキに割れる🥶

だからルールはこれだけ👇✨

✅ **外から来たら境界で “整形＆変換”**
✅ **中心には “きれいなDomain” だけ通す**

---

## 変換で吸収したい「外の都合」あるある図鑑📚😂境界でよく直すのはこのへん👇

1. **命名**：snake_case ↔ camelCase 🐍➡️🐫
2. **単位**：cents（整数）↔ yen（整数）↔ dollars（小数）💰
3. **型**：数字が "123"（文字列）で来る🔢➡️🧵
4. **null**：null を許してくる（でも中心は嫌）🙅‍♀️
5. **欠損**：オプショナルが混ざる（仕様の揺れ）🫥
6. **列挙**：APIの文字列 enum が微妙に違う😇

---

## 置き場所の正解：DTOは「外側」、Domainは「中心」🏠➡️

🌍イメージはこれだよ👇✨



* 外側：HTTP/DBなど（ここにDTOがいる）
* 境界：DTO→Domain（or Domain→DTO）に変換する場所
* 中心：純粋ロジック（Domainだけで動く）

**ポイント**💡
変換関数は **I/Oしない**（つまり純粋）にすると、テストが爆速＆楽勝になる🧪⚡

---

## ハンズオン：カフェ注文APIでDTO→Domain変換してみよ☕🛒✨### 1) 外から来るデータ（DTO）

例📦APIが返すJSON（イメージ）👇



* 金額が "980"（文字列）
* 明細の名前が item_name（snake_case）
* クーポンが null のことがある

```ts
type OrderDto = {
  order_id: string;
  total_yen: string; // ←数字だけど文字列！
  coupon_code: string | null;
  lines: Array<{
    item_name: string;
    unit_price_yen: number;
    qty: number;
  }>;
};
```

---

### 2) 中心で扱いたいDomain（きれいな型）

💎「中心はこういうのが好き！」を作るよ✨
（※ここでは分かりやすさ優先で、Value Objectは最小の形にしてるよ☺️）

```ts
// ちょい安全な“ブランド型”の雰囲気（実運用ではもう少し整えることも多いよ）
type Brand<T, B extends string> = T & { readonly __brand: B };

type OrderId = Brand<string, "OrderId">;

type MoneyYen = Brand<number, "MoneyYen">; // 常に“円の整数”と約束✨

type OrderLine = {
  itemName: string;
  unitPriceYen: MoneyYen;
  qty: number;
};

type Order = {
  id: OrderId;
  totalYen: MoneyYen;
  couponCode?: string; // nullじゃなくて「無いなら undefined」に寄せる💖
  lines: OrderLine[];
};
```

---

### 3) 変換の出口を「Result」にして、失敗もテストできるようにする🧪🧯例外でもいいけど、初心者のうちは Result だと見通しがよくておすすめ☺️

✨



```ts
type Ok<T> = { ok: true; value: T };
type Err = { ok: false; message: string };
type Result<T> = Ok<T> | Err;

const ok = <T>(value: T): Ok<T> => ({ ok: true, value });
const err = (message: string): Err => ({ ok: false, message });
```

---

### 4) 小さい変換部品（パーサ）

を用意する🧩✨「数字文字列→円」「IDの形」みたいな**よくある整形**を、部品化しよう💪🌟



```ts
const toOrderId = (raw: string): Result<OrderId> => {
  if (raw.trim().length === 0) return err("order_id is empty");
  return ok(raw as OrderId);
};

const toMoneyYenFromString = (raw: string): Result<MoneyYen> => {
  if (!/^\d+$/.test(raw)) return err("total_yen is not a number string");
  const n = Number(raw);
  if (!Number.isSafeInteger(n) || n < 0) return err("total_yen is invalid");
  return ok(n as MoneyYen);
};

const toMoneyYenFromNumber = (n: number): Result<MoneyYen> => {
  if (!Number.isSafeInteger(n) || n < 0) return err("money is invalid");
  return ok(n as MoneyYen);
};
```

---

### 5) DTO → Domain の本体（境界の主役）

🔁✨「外の形」をここでぜんぶ吸収して、中心には “Order” だけ渡すよ💖



```ts
export const dtoToOrder = (dto: OrderDto): Result<Order> => {
  const idR = toOrderId(dto.order_id);
  if (!idR.ok) return idR;

  const totalR = toMoneyYenFromString(dto.total_yen);
  if (!totalR.ok) return totalR;

  const lines: OrderLine[] = [];
  for (const l of dto.lines) {
    const unitR = toMoneyYenFromNumber(l.unit_price_yen);
    if (!unitR.ok) return unitR;

    if (!Number.isInteger(l.qty) || l.qty <= 0) return err("qty is invalid");

    lines.push({
      itemName: l.item_name, // snake_case → camelCase✨
      unitPriceYen: unitR.value,
      qty: l.qty,
    });
  }

  const couponCode = dto.coupon_code ?? undefined; // null吸収✨

  return ok({
    id: idR.value,
    totalYen: totalR.value,
    couponCode,
    lines,
  });
};
```

---

## ここが大事：TypeScriptの「型」だけでは守れない話🧠⚠️

外から来る JSON は基本 **unknown**（信用しない）だよね。
TypeScriptの型はコンパイル時の助けで、実行時に勝手に検証してくれるわけじゃないの🥺

だから現場では、DTOの手前で **スキーマ検証**を入れることが多いよ✨

* Zod は「スキーマを定義して parse すると型安全に扱える」系の代表だよ🧸✨ ([Zod][4])
* Valibot も「型は実行されないけど、スキーマは実行できる」って説明が分かりやすいよ📘✨ ([Valibot][5])

（※この章は“変換の考え方”が主役なので、導入は次の章の入力検証とつなげると超キレイだよ☺️🔗）

---

## テスト：変換は“純粋”だからユニットで一瞬🧪⚡

```ts
import { describe, it, expect } from "vitest";
import { dtoToOrder } from "./dtoToOrder";

describe("dtoToOrder", () => {
  it("DTOをDomainに変換できる", () => {
    const dto = {
      order_id: "o-001",
      total_yen: "980",
      coupon_code: null,
      lines: [{ item_name: "Latte", unit_price_yen: 490, qty: 2 }],
    };

    const r = dtoToOrder(dto);
    expect(r.ok).toBe(true);
    if (!r.ok) return;

    expect(r.value.lines[0].itemName).toBe("Latte");
    expect(r.value.couponCode).toBeUndefined();
  });

  it("total_yenが数値文字列じゃないと失敗する", () => {
    const dto = {
      order_id: "o-001",
      total_yen: "9xx",
      coupon_code: null,
      lines: [{ item_name: "Latte", unit_price_yen: 490, qty: 2 }],
    };

    const r = dtoToOrder(dto);
    expect(r.ok).toBe(false);
    if (r.ok) return;

    expect(r.message).toContain("total_yen");
  });
});
```

---

## よくある落とし穴👀💥（ここ避けるだけで強い！

）* ❌ 中心（Domain）の中で DTO を参照しはじめる（依存の向きが逆転）


* ❌ 変換関数の中に “仕様（ビジネスルール）” を混ぜる

  * 変換＝整形/正規化
  * 仕様＝割引計算/在庫判定…（これは中心）
* ❌ null を中心に持ち込む（中心が急にしんどくなる）

---

## AI拡張をうまく使うコツ🤖🎀AIにはこう頼むと強いよ👇✨



* ✅ 「このDTO→Domain変換で想定すべき異常系を列挙して」
* ✅ 「Result型で失敗理由を返す実装案を出して」
* ✅ 「テストケースをAAAで増やして（境界値・null・欠損）」

逆にこれは丸投げしないでね👇🙅‍♀️

* 境界の線引き（どこまでが変換？どこからが仕様？）
* Domainの型の意味付け（Moneyは円？税込？）

---

## 章末ミニ課題🎓🌈### 課題A：単位変換💰

🔁* DTO：price_cents（整数）


* Domain：priceYen（円整数）
* 1ドル=150円…みたいな“レート”は **設定**なので、この章では境界で受け取って引数にしてOK（でも計算ルールは中心に寄せるのもアリ）🙂

### 課題B：列挙の吸収🎭* DTO：status が "paid" | "unpaid" | "canceled"


* Domain：Status を union で作って、未知の値は Err にする🧯

### 課題C：nullを消す🧽* DTO：nickname: string | null


* Domain：nickname?: string（undefined寄せ）にして、中心から null を追放する😆✨

---

## まとめ🌟* DTOは“外の形”、Domainは“中心の形”💎


* **境界で変換**して、中心を外部都合から守る🛡️
* 変換は **純粋関数**にしてテストでガッチリ固定🧪⚡
* 実行時の安全性は、次章の「入力検証（スキーマ）」につながるよ🔗✨

必要なら、この章の題材をそのまま使って「DTO→Domain→中心ロジック→Domain→DTO（返却）」まで一気通貫のミニ例も作るよ☕🛠️💖

[1]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "TypeScript"
[2]: https://devblogs.microsoft.com/typescript/progress-on-typescript-7-december-2025/?utm_source=chatgpt.com "Progress on TypeScript 7 - December 2025"
[3]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html?utm_source=chatgpt.com "Documentation - TypeScript 5.9"
[4]: https://zod.dev/?utm_source=chatgpt.com "Zod: Intro"
[5]: https://valibot.dev/?utm_source=chatgpt.com "Valibot: The modular and type safe schema library"
