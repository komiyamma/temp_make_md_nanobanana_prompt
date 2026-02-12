# 第01章：はじめに（この講座のゴール）🎯😊

![testable_ts_study_001_intro_tree.png](./picture/testable_ts_study_001_intro_tree.png)

この章は「テスタブル設計って、結局なにが嬉しいの？🤔」を**体感**して、次章からの学習がスッと入るようにする回だよ〜！🌸✨
まだテストを書けなくても全然OK🙆‍♀️ まずは「つらい気持ち😵‍💫」をちゃんと知るのが最短ルート！

---

## 1) この講座のゴールはこれ！

🎓🌈### ゴール（最終的にこうなりたい）* 変更が来ても「怖くない😌」コードを書けるようになる


* 「中心（ロジック）」と「外側（I/O）」を分けて、**中心はユニットテストで守る🧪**
* 外部都合（DB/HTTP/ファイル/時刻/環境変数/ログ…）に振り回されない設計にする💪✨

### まず最初のゴール（今日の到達点）* 「I/O境界の分離ってこういうことね！

」が**言葉で説明できる**🗣️✨


* そして **“テストしにくいコード”を見て、どこがつらいか分かる**😵‍💫➡️😮‍💨

---

## 2) テスタブル設計ってなに？🧪✨

（ざっくり超大事）テスタブル設計は、ひとことで言うと…

> **「テストを書きやすい形に整えておく設計」＝「変更が怖くない設計」**🎀

ここでいう「怖い変更」って、たとえば👇

* ちょっと直しただけで、どこが壊れるか分からない😱
* 動作確認が手作業だらけで、ミスしやすい😵
* 外部APIやDBが絡むと、再現ができない（たまに落ちる）🎲💥

これを減らすために、次の考え方が登場！

---

## 3) I/O境界の分離って何？🚪

⚡（この講座の主役）### I/Oってなに？I/Oは「外の世界」とのやり取りだよ🌍
たとえば👇

* HTTP（fetch）🌐
* DB 🗄️
* ファイル📁
* 時刻（Date）⏰
* 乱数🎲
* 環境変数⚙️
* ログ出力📝

### 分離ってなに？**ロジック（中心）**と**I/O（外側）**を分けること！

✂️✨
イメージはこんな感じ👇

* 🧠 **中心（ロジック）**：できれば“純粋”に近い（同じ入力→同じ出力）
* 🌍 **外側（I/O）**：現実世界に触る（ネット、DB、ファイル、時刻など）
* 🚪 **境界（インターフェース）**：中心が外側にお願いするときの“窓口”

---

## 4) 今どき（本日時点）

のTSテスト環境ってどんな感じ？🧰✨この講座では「中心を速く回せる」ことを重視するよ⚡
いまの定番感はこんなイメージ👇

* TypeScriptは **5.9** 系が最新クラス（ドキュメントが継続更新されてる）📘✨ ([TypeScript][1])
* Node.js は **24系がActive LTS**、25系がCurrent という位置づけ🟩🟨 ([nodejs.org][2])
* テストは

  * **Vitest 4**（2025年10月にメジャー）🧪⚡ ([vitest.dev][3])
  * **Jest 30**（最新版系）🧪📦 ([jestjs.io][4])
    みたいな選択肢があるよ〜！

※この章では「へぇ〜そうなんだ🙂」でOK！本格的に触るのは後の章でやるよ🫶

---

## 5) ハンズオン：テストしにくいコードを“眺めて”つらさを体験😵‍💫👀ここは、**あえて直さない**よ！
「どこがつらいのか」を観察する練習✨

### サンプル：いろいろ混ざっちゃったコード例🍝💥

```ts
// orderService.ts（※わざと混ぜ混ぜの例）
type Order = { userId: string; items: Array<{ id: string; price: number; qty: number }> };

export async function createReceiptText(order: Order): Promise<string> {
  // 環境変数（I/O）
  const taxRate = Number(process.env.TAX_RATE ?? "0.1");

  // 時刻（I/O）
  const now = new Date();

  // HTTP（I/O）
  const res = await fetch(`https://example.com/users/${order.userId}`);
  if (!res.ok) throw new Error("User API failed");
  const user = await res.json() as { name: string };

  // ログ（I/O）
  console.log("creating receipt for", user.name);

  // 乱数（I/O）
  const receiptNo = Math.floor(Math.random() * 1_000_000);

  // ロジック（計算）
  const subtotal = order.items.reduce((sum, it) => sum + it.price * it.qty, 0);
  const tax = Math.floor(subtotal * taxRate);
  const total = subtotal + tax;

  // 文字列整形（ロジック寄り）
  return [
    `Receipt No: ${receiptNo}`,
    `Name: ${user.name}`,
    `Date: ${now.toISOString()}`,
    `Subtotal: ${subtotal}`,
    `Tax: ${tax}`,
    `Total: ${total}`,
  ].join("\n");
}
```

### やること（3分）

⏱️📝次のルールで「赤ペン」してみてね🖍️✨

1. **I/Oっぽい行**に ✅ を付ける

* `process.env`、`new Date()`、`fetch`、`console.log`、`Math.random` …など！

2. 「ここが変わると壊れそう…」と思うところに ⚠️

* APIのURLとか、レスポンス形とか、税率の読み方とか…

3. 「テストしたいのに困る理由」を3つ書く😵‍💫
   例👇

* 時刻と乱数が毎回変わるから、期待結果が固定できない⏰🎲
* APIが落ちたらテストも落ちる（ネット依存）🌧️
* 環境変数がないと動かない⚙️

### ここが今日の“気づきポイント”💡このコード、ロジック自体（小計・税・合計）

はテストしたいのに、
**I/Oが混ざってて、中心だけを取り出してテストできない**のがつらいの😵‍💫💥

---

## 6) AI（Copilot/Codex）

を使って“観察”してみよう🤖🎀（短いお遊び）AIに「修正」じゃなくて「分類」を頼むのがコツだよ✨
たとえばこんな感じ👇

* 「この関数の中でI/O（外部依存）っぽい部分を箇条書きして」
* 「純粋ロジックっぽい部分はどこ？」
* 「テストが不安定になりそうな要因を3つ挙げて」

**注意**：この章はまだ“直さない”ので、提案は眺めるだけでOK🙆‍♀️✨

---

## 7) まとめ（今日の1分）

⏱️🌸* テスタブル設計は「変更が怖くない」を作るための設計🎯


* I/O境界の分離は「中心（ロジック）」と「外側（I/O）」を分けること🚪✨
* つらいコードは **I/Oが混ざって中心をテストできない**😵‍💫
* まずは「I/Oっぽさ」を見抜けるようになるのが第一歩👀✅

---

## 次章予告：第2章「I/Oと副作用ってなに？」⚡🚪

次は、今日✅を付けたやつをちゃんと言語化していくよ〜！
「I/Oって何を含むの？」をスパッと言えるようになろうね🫶✨

[1]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html?utm_source=chatgpt.com "Documentation - TypeScript 5.9"
[2]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[3]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
[4]: https://jestjs.io/versions?utm_source=chatgpt.com "Jest Versions"
