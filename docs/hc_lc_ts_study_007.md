# 第07章：高凝集① “責務で切る”（関数・ファイルの基本）✂️🎯

## この章でできるようになること💪✨

* 「この関数、やってること多すぎない…？😵‍💫」を**責務（せきむ）で分解**できる
* 分けた後に、**読める順番（ストーリー）**で並べ直せる📖
* “同じ理由で変わるもの”を**近く（同じ関数/同じファイル）**に集められる🏠
* VS Code の **Extract Function / Rename** を使って安全に分割できる🛠️
* AI（Copilot/Codex等）に「分割案」を出させつつ、**最終判断は自分**でできる🤖✅

> ちなみに、本日時点のTypeScriptは **5.9系が現行の安定版**として扱われています（GitHub Releases上の “Stable” 表記） ([GitHub][1])
> （TypeScript 5.9 の公式リリースノートも公開・更新されています） ([TypeScript][2])

---

## 7-1. そもそも「責務」ってなに？🧠💡

![Responsibility Components](./picture/hc_lc_ts_study_007_responsibility_pie.png)

**責務 = “このコードが守るべき役割（担当）”** だよ🎀
たとえば同じ「注文する」でも、役割は別々に存在しがち👇

* 入力を整える（trimするとか）🧹
* 入力を検証する（空欄NGとか）🧪
* ルールで判断する（割引OK？など）⚖️
* 実行する（API呼ぶ）🌐
* 結果を整形する（表示用の形にする）🎁
* 失敗時の扱い（リトライ？メッセージ？）🧯

💥これが1つの関数に全部入ると、「どれかを変えたい」だけなのに全部に影響が出やすい…
だから **責務で切る = 高凝集の第一歩** になるよ✂️✨

---

## 7-2. “良い分け方”のコツは「読み順＝ストーリー」📖✨

![Story Ordering Template](./picture/hc_lc_ts_study_007_story_scroll.png)

分割って「細切れにすること」が目的じゃないよ🙅‍♀️
目的は **読みやすくすること**＆**変更しやすくすること**🎯

おすすめはこれ👇

### ✅ ストーリー並びテンプレ（超よく効く）💯

1. **準備**（入力を整える）🧹
2. **検証**（ダメなら早期return）🧪
3. **判断**（ルール・分岐）⚖️
4. **実行**（外部I/Oや計算の本体）🚀
5. **整形**（返す形にする）🎁

これにすると、上から読んで「何してるか」がスルスル入ってくるよ📖💕

---

## 7-3. 分割の手順（迷ったらこの順でOK）🗺️✨

![Extract Function](./picture/hc_lc_ts_study_007_extract_function.png)


### Step0：まず“責務ラベル”を貼る🏷️🎨

長い関数を見たら、コメントでいいからラベル付けしてみて👇
（あとで消す前提でOK！）

* `// 準備`
* `// 検証`
* `// 判断`
* `// 実行`
* `// 整形`

### Step1：境界線を引く✂️

ラベルごとに「ここからここまで同じ責務」って線を引くイメージ✍️

### Step2：Extract Function で切り出す🛠️

VS Code は TypeScript のリファクタをサポートしてて、**Extract Method / Extract Variable** みたいな操作ができるよ ([Visual Studio Code][3])

* Windowsだとだいたい `Ctrl + .` でリファクタ候補が出る✨
* まずは **“検証”** を切り出すのが安全（副作用少なめ）🧪

### Step3：関数名は“責務を1文で言う”📛

良い名前は「何をするか」が文章っぽくなるやつ💡

* ✅ `validateOrderInput()`
* ✅ `buildOrderRequest()`
* ✅ `mapOrderResponseToViewModel()`
* ❌ `doStuff()` 🙅‍♀️
* ❌ `process()` 🙅‍♀️（何を？ってなる）

### Step4：ファイル分割は“同じ理由で変わるもの同士”🏠

* 検証が増える → `validation` 側が変わる
* APIの形が変わる → `api` / `client` 側が変わる
* 表示用の形が変わる → `mapper` 側が変わる

この「変わり方」が違うなら、**同じファイルに閉じ込めない**ほうが吉🎯

---

## 7-4. ハンズオン🛠️：長い関数を「準備/判断/実行/整形」で分割しよう🧹✨

### お題：注文確定の処理（ごちゃ混ぜ版）😱

#### Before（わざと混ぜてる）

```ts
type OrderInput = {
  userId: string;
  items: Array<{ sku: string; qty: number }>;
  coupon?: string;
};

type OrderResult = { ok: true; orderId: string } | { ok: false; reason: string };

export async function submitOrder(input: OrderInput): Promise<OrderResult> {
  // 準備
  const userId = input.userId.trim();
  const items = input.items.map(x => ({ sku: x.sku.trim(), qty: x.qty }));

  // 検証
  if (!userId) return { ok: false, reason: "userId is empty" };
  if (items.length === 0) return { ok: false, reason: "items is empty" };
  if (items.some(x => !x.sku || x.qty <= 0)) return { ok: false, reason: "invalid items" };

  // 判断（ルール）
  const coupon = input.coupon?.trim();
  const hasCoupon = !!coupon;
  const payload = {
    userId,
    items,
    discount: hasCoupon ? 10 : 0,
    coupon: hasCoupon ? coupon : undefined,
  };

  // 実行（外部I/O想定）
  try {
    const res = await fakePost("/orders", payload);
    if (typeof res.orderId !== "string") return { ok: false, reason: "bad response" };

    // 整形
    return { ok: true, orderId: res.orderId };
  } catch (e) {
    return { ok: false, reason: "network error" };
  }
}

// ダミー
async function fakePost(_path: string, _body: unknown): Promise<any> {
  return { orderId: "ORD-123" };
}
```

---

### 目標🎯：「上から読むだけで理解できる」形にする📖💕

![Before vs After Story](./picture/hc_lc_ts_study_007_before_after_story.png)

ポイントはこれ👇

* **検証は早期return**（失敗の出口を上に寄せる）🧪🚪
* “判断” は **名前の付いた小さな関数**へ⚖️
* “実行” は **1か所**へ🌐

#### After（責務で切った例）

```ts
type OrderInput = {
  userId: string;
  items: Array<{ sku: string; qty: number }>;
  coupon?: string;
};

type NormalizedOrderInput = {
  userId: string;
  items: Array<{ sku: string; qty: number }>;
  coupon?: string;
};

type OrderPayload = {
  userId: string;
  items: Array<{ sku: string; qty: number }>;
  discount: number;
  coupon?: string;
};

type OrderResult = { ok: true; orderId: string } | { ok: false; reason: string };

export async function submitOrder(input: OrderInput): Promise<OrderResult> {
  const normalized = normalizeInput(input);

  const error = validateInput(normalized);
  if (error) return { ok: false, reason: error };

  const payload = buildPayload(normalized);

  const res = await postOrder(payload);
  return mapResponseToResult(res);
}

// 1) 準備🧹
function normalizeInput(input: OrderInput): NormalizedOrderInput {
  return {
    userId: input.userId.trim(),
    items: input.items.map(x => ({ sku: x.sku.trim(), qty: x.qty })),
    coupon: input.coupon?.trim(),
  };
}

// 2) 検証🧪（失敗理由は文字列で返すだけにしておくと扱いやすい）
function validateInput(input: NormalizedOrderInput): string | null {
  if (!input.userId) return "userId is empty";
  if (input.items.length === 0) return "items is empty";
  if (input.items.some(x => !x.sku || x.qty <= 0)) return "invalid items";
  return null;
}

// 3) 判断⚖️
function buildPayload(input: NormalizedOrderInput): OrderPayload {
  const hasCoupon = !!input.coupon;
  return {
    userId: input.userId,
    items: input.items,
    discount: hasCoupon ? 10 : 0,
    coupon: hasCoupon ? input.coupon : undefined,
  };
}

// 4) 実行🚀（外部I/Oは“ここ”って決めると見通しが良い）
async function postOrder(payload: OrderPayload): Promise<unknown> {
  try {
    return await fakePost("/orders", payload);
  } catch {
    return { error: "network error" };
  }
}

// 5) 整形🎁
function mapResponseToResult(res: any): OrderResult {
  if (res?.error === "network error") return { ok: false, reason: "network error" };
  if (typeof res?.orderId !== "string") return { ok: false, reason: "bad response" };
  return { ok: true, orderId: res.orderId };
}

// ダミー
async function fakePost(_path: string, _body: unknown): Promise<any> {
  return { orderId: "ORD-123" };
}
```

### いい感じポイント🌸

* `submitOrder()` が **“物語”** になった📖✨
* “何をしてるか” が関数名でわかる📛
* 変更が起きても、直す場所が絞れる🎯

---

## 7-5. ここまでできたら「ファイル分割」も一歩だけ👣📁

![File Split Steps](./picture/hc_lc_ts_study_007_file_split_step.png)

全部いきなり分割しなくてOKだよ〜☺️
まずは **塊ごと**に分けるだけで十分強い💪

例👇（イメージ）

* `submitOrder.ts`（ストーリーだけ置く）📖
* `orderNormalize.ts`（準備）🧹
* `orderValidation.ts`（検証）🧪
* `orderPayload.ts`（判断/組み立て）⚖️
* `orderApi.ts`（実行）🌐
* `orderMapper.ts`（整形）🎁

💡さらに「外から触っていい関数」だけ `export` して、内部は隠すと、あとで崩れにくいよ🔒✨

---

## 7-6. AI活用🤖✨：分割“案”はAI、決定はあなた✅

![Naming Convention](./picture/hc_lc_ts_study_007_naming_convention.png)


AIは分割案を量産するのが得意だよ💡
でも「その分け方、責務が混ざってない？依存増えない？」は人間チェックが強い🔥

GitHub Copilot には、チャットの指示で**複数ファイルをまとめて編集する** “Copilot Edits” もあるよ（VS Code等で利用） ([GitHub Docs][4])
→ ファイル分割に入るタイミングで相性よし🧩✨

### この章のAIプロンプト🤖（ロードマップ準拠）

1. 「この関数を責務で分割するとしたら、分割案を3つ出して（メリデメ付き）」

💡おすすめの追加指示（1行足すだけで精度UP）

* 「準備/検証/判断/実行/整形 の形で並べたい」
* 「関数名案も出して」
* 「最終的に submitOrder が上から読める形にして」

---

## 7-7. 仕上げチェックリスト✅✨（ここ超大事！）

分割後にこれだけ確認してね🧠💕

* [ ] `submitOrder()` を上から読むだけで流れがわかる？📖
* [ ] 1つの関数が **2つ以上の変更理由** を抱えてない？🧨
* [ ] “検証” が他の処理（I/Oや整形）と混ざってない？🧪
* [ ] 関数名が「何をするか」を言えてる？📛
* [ ] 分割したのに、呼び出し側が逆に読みにくくなってない？（細かすぎ注意）⚠️

---

## 7-8. よくあるミス集😇💦

![Common Mistakes Signs](./picture/hc_lc_ts_study_007_common_mistakes.png)

### ❌ ミス1：分割したけど、名前が弱い

`handle()` `process()` `doIt()` …みたいなのが増えると迷子になるよ🧭💦
👉 **責務を1文で言う名前**にしよ📛✨

### ❌ ミス2：関数を作りすぎて、逆に追いにくい

“意味が薄い1行関数”が10個…は読みにくいこともある😵
👉 **「まとめたほうがストーリーが読みやすい」ならまとめてOK**🙆‍♀️

### ❌ ミス3：分割したのに順番がバラバラ

準備→実行→検証→整形…みたいに並ぶと、読み手の脳が転ぶ🤸‍♀️💥
👉 テンプレ順（準備/検証/判断/実行/整形）へ📖✨

---

## 章末ミニ課題🎒✨（10〜20分でOK）

1. 自分のコードから「ちょい長い関数」を1つ選ぶ🔎
2. 責務ラベルを貼る🏷️
3. Extract Function で 3〜5個に分ける✂️
4. “ストーリー順”に並べる📖
5. 最後にAIへ：

   * 「責務混在してるところある？危険点を3つ」って聞く🤖✅

---


[1]: https://github.com/microsoft/typescript/releases "Releases · microsoft/TypeScript · GitHub"
[2]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html?utm_source=chatgpt.com "Documentation - TypeScript 5.9"
[3]: https://code.visualstudio.com/docs/typescript/typescript-refactoring?utm_source=chatgpt.com "Refactoring TypeScript"
[4]: https://docs.github.com/en/copilot/get-started/features?utm_source=chatgpt.com "GitHub Copilot features"
