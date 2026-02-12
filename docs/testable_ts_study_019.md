# 第19章：ファイルI/Oを外に押し出す📁🚪

![testable_ts_study_019_virtual_files.png](./picture/testable_ts_study_019_virtual_files.png)

この章はひとことで言うと……

**「ファイルの読み書き」と「中身の計算」を別居させる🏠➡️🏠**
これだけで、テストがめちゃラク＆速くなります🧪⚡

---

## 1) まずは“あるある地獄”を見よう😵‍💫💥たとえば、こんなコード👇（※わざとダメな例）



```ts
import { readFileSync, writeFileSync } from "node:fs";

export function summarizeCsvFile(inputPath: string, outputPath: string) {
  const text = readFileSync(inputPath, "utf8"); // ←I/Oがいきなり混ざる
  const lines = text.split("\n");              // ←改行差分とかも混ざる
  const rows = lines.slice(1).filter(Boolean).map(line => {
    const [date, category, amountStr] = line.split(",");
    return { date, category, amount: Number(amountStr) };
  });

  const totals: Record<string, number> = {};
  for (const r of rows) {
    totals[r.category] = (totals[r.category] ?? 0) + r.amount;
  }

  writeFileSync(outputPath, JSON.stringify(totals, null, 2), "utf8"); // ←またI/O
}
```

これだと何がツラい？🥺

* テストするたびに **ファイル用意** が必要📁😇
* Windowsの改行 `\r\n` とかで **地味にコケる**💥
* テストが遅い＆不安定になりがち🐢⚡
* ロジックを直したいだけなのにI/Oが絡んで怖い😱

---

## 2) 今日のゴール🎯🌈

✅ **中心（ロジック）**：文字列を解析して集計する（I/Oゼロ）🍰✨
✅ **外側（I/O）**：ファイルを読む・書く（薄く）📁🚪
✅ **境界（interface）**：中心が「読んで〜」ってお願いできる窓口🪟📌

こうすると、中心は **文字列だけでテスト**できるから超ラクです🧪💕

---

## 3) 設計の完成図（ミニ地図）

🗺️✨### 🧠中心（pure）* `parseCsvLike(text)`：CSVっぽい文字列 → 行データ


* `summarize(rows)`：行データ → 集計結果

### 🚪

境界（port）* `TextFileIO`：`readText(path)` / `writeText(path, content)` だけ！



### 🌍外側（adapter）* `NodeTextFileIO`：`node:fs/promises` で実ファイルを読む・書く📁
  ※Promise版のfsは公式にあります ([Node.js][1])

---

## 4) ハンズオン：CSVっぽい入力 → 集計ロジックを中心へ📊✨

題材は「支出CSV」💸🍩
CSV（っぽい）例：

```text
date,category,amount
2026-01-01,food,1200
2026-01-01,book,1800
2026-01-02,food,900
```

やること👇

* **中心**：集計 `food: 2100`, `book: 1800` を作る
* **外側**：ファイルから読んで、結果をJSONで保存する

---

## 5) フォルダ構成（おすすめ）

📁✨

```text
project/
  src/
    core/
      parse.ts
      summarize.ts
      types.ts
    ports/
      TextFileIO.ts
    adapters/
      NodeTextFileIO.ts
    app/
      runSummary.ts
    main.ts
  test/
    parse.test.ts
    summarize.test.ts
    runSummary.test.ts
    NodeTextFileIO.int.test.ts   (任意)
  package.json
  tsconfig.json
```

---

## 6) 実装していくよ〜✍️

😊### 6-1) core/types.ts（中心の型）

📘🧸

```ts
export type ExpenseRow = {
  date: string;
  category: string;
  amount: number;
};

export type ParseError = {
  lineNo: number;
  reason: string;
  line: string;
};

export type ParseResult = {
  rows: ExpenseRow[];
  errors: ParseError[];
};

export type Summary = {
  byCategory: Record<string, number>;
  total: number;
  count: number;
};
```

---

### 6-2) core/parse.ts（中心：文字列を解析）

🧼✨ポイント💡



* Windowsの `\r\n` にも強い（`\r?`）🪟
* BOM（たまに付く謎の先頭文字）も除去🧙‍♀️
* 失敗は `errors` にためる（テストしやすい！）🧪

```ts
import { ExpenseRow, ParseResult } from "./types";

export function parseCsvLike(text: string): ParseResult {
  const cleaned = text.replace(/^\uFEFF/, ""); // BOM除去
  const lines = cleaned.split(/\r?\n/).filter((l) => l.trim().length > 0);

  const errors: ParseResult["errors"] = [];
  const rows: ExpenseRow[] = [];

  if (lines.length === 0) return { rows, errors };

  // 先頭がヘッダっぽかったら捨てる
  const startIndex = lines[0].startsWith("date,") ? 1 : 0;

  for (let i = startIndex; i < lines.length; i++) {
    const lineNo = i + 1;
    const line = lines[i];

    const parts = line.split(",");
    if (parts.length !== 3) {
      errors.push({ lineNo, reason: "カンマ区切りが3つじゃないよ", line });
      continue;
    }

    const [date, category, amountStr] = parts.map((p) => p.trim());
    const amount = Number(amountStr);

    if (!date || !category || !Number.isFinite(amount)) {
      errors.push({ lineNo, reason: "date/category/amountが変だよ", line });
      continue;
    }

    rows.push({ date, category, amount });
  }

  return { rows, errors };
}
```

> ここまで、**ファイルは一切触ってない**🍰✨
> だからテストは文字列だけでOK🧪💕

---

### 6-3) core/summarize.ts（中心：集計）

📊💕

```ts
import { ExpenseRow, Summary } from "./types";

export function summarize(rows: ExpenseRow[]): Summary {
  const byCategory: Record<string, number> = {};
  let total = 0;

  for (const r of rows) {
    byCategory[r.category] = (byCategory[r.category] ?? 0) + r.amount;
    total += r.amount;
  }

  return {
    byCategory,
    total,
    count: rows.length,
  };
}
```

---

## 7) 境界（port）

を作る📜🚪### ports/TextFileIO.ts

```ts
export interface TextFileIO {
  readText(path: string): Promise<string>;
  writeText(path: string, content: string): Promise<void>;
}
```

**最小の約束だけ**にするのがコツ✂️✨
（`exists` とか `listDir` とか増やし始めると、中心がI/Oの都合を吸い始めます😵‍💫）

---

## 8) 外側（adapter）

：Nodeで実ファイル読み書き📁🧩NodeのPromise版 `fs` を使うよ〜（公式）([Node.js][1])
※複数の同一ファイル更新を並列でやると危ないよ、って注意も公式に書いてあります([Node.js][1])

### adapters/NodeTextFileIO.ts

```ts
import { readFile, writeFile, mkdir } from "node:fs/promises";
import { dirname } from "node:path";
import { TextFileIO } from "../ports/TextFileIO";

export class NodeTextFileIO implements TextFileIO {
  async readText(path: string): Promise<string> {
    return await readFile(path, "utf8");
  }

  async writeText(path: string, content: string): Promise<void> {
    // 出力先フォルダがなければ作る（地味に便利）
    await mkdir(dirname(path), { recursive: true });
    await writeFile(path, content, "utf8");
  }
}
```

---

## 9) アプリ層：I/Oと中心を“つなぐだけ”🔗😊### app/runSummary.ts

```ts
import { TextFileIO } from "../ports/TextFileIO";
import { parseCsvLike } from "../core/parse";
import { summarize } from "../core/summarize";

export type RunSummaryInput = {
  inputPath: string;
  outputPath: string;
  io: TextFileIO;
};

export async function runSummary(input: RunSummaryInput): Promise<void> {
  const text = await input.io.readText(input.inputPath);

  const parsed = parseCsvLike(text);
  const summary = summarize(parsed.rows);

  const output = {
    summary,
    parseErrors: parsed.errors, // 失敗行も出せる（デバッグ神✨）
  };

  await input.io.writeText(input.outputPath, JSON.stringify(output, null, 2));
}
```

ここが超大事💡
`runSummary` は **fsを知らない**。
だからテストで `io` を差し替えるだけで、ディスク無しで検証できます🧪✨

---

## 10) 組み立て（Composition Root）

🏗️✨### main.ts

```ts
import { NodeTextFileIO } from "./adapters/NodeTextFileIO";
import { runSummary } from "./app/runSummary";

async function main() {
  const io = new NodeTextFileIO();

  await runSummary({
    inputPath: "data/expenses.csv",
    outputPath: "out/summary.json",
    io,
  });

  console.log("完了〜🎉 out/summary.json を見てね😊");
}

main().catch((e) => {
  console.error("失敗😭", e);
  process.exitCode = 1;
});
```

---

## 11) テストが本番だよ🧪🔥（Vitest 4でいく）

Vitestは2025-10-22に4.0が出てるよ〜([Vitest][2])
（軽くて速くて、TSとの相性も◎な流れです🏎️💨 ([Vitest][3])）

## 11-1) 中心のテスト：parse.test.ts（ファイル不要）

📄❌

```ts
import { describe, it, expect } from "vitest";
import { parseCsvLike } from "../src/core/parse";

describe("parseCsvLike", () => {
  it("ヘッダありのCSVっぽい文字列を解析できる😊", () => {
    const input = [
      "date,category,amount",
      "2026-01-01,food,1200",
      "2026-01-01,book,1800",
      "2026-01-02,food,900",
      "",
    ].join("\r\n"); // Windows改行っぽくしてみる🪟

    const result = parseCsvLike(input);

    expect(result.errors).toHaveLength(0);
    expect(result.rows).toHaveLength(3);
    expect(result.rows[0]).toEqual({ date: "2026-01-01", category: "food", amount: 1200 });
  });

  it("壊れた行はerrorsに入る😇", () => {
    const input = [
      "date,category,amount",
      "2026-01-01,food,notNumber",
      "badline",
      "2026-01-02,food,900",
    ].join("\n");

    const result = parseCsvLike(input);

    expect(result.rows).toHaveLength(1);
    expect(result.errors.length).toBeGreaterThan(0);
  });
});
```

---

## 11-2) 中心のテスト：summarize.test.ts📊💕

```ts
import { describe, it, expect } from "vitest";
import { summarize } from "../src/core/summarize";

describe("summarize", () => {
  it("カテゴリ別と合計を出せる🎉", () => {
    const rows = [
      { date: "2026-01-01", category: "food", amount: 1200 },
      { date: "2026-01-01", category: "book", amount: 1800 },
      { date: "2026-01-02", category: "food", amount: 900 },
    ];

    const s = summarize(rows);

    expect(s.byCategory).toEqual({ food: 2100, book: 1800 });
    expect(s.total).toBe(3900);
    expect(s.count).toBe(3);
  });
});
```

---

## 11-3) アプリ層のテスト：runSummary.test.ts（I/Oを偽物にする🧸✨

）偽I/O（メモリ）を作って、ディスクゼロでテストします💪🧪



```ts
import { describe, it, expect } from "vitest";
import { runSummary } from "../src/app/runSummary";
import type { TextFileIO } from "../src/ports/TextFileIO";

class MemoryTextFileIO implements TextFileIO {
  private store = new Map<string, string>();

  set(path: string, content: string) {
    this.store.set(path, content);
  }

  get(path: string) {
    return this.store.get(path);
  }

  async readText(path: string): Promise<string> {
    const v = this.store.get(path);
    if (v == null) throw new Error(`not found: ${path}`);
    return v;
  }

  async writeText(path: string, content: string): Promise<void> {
    this.store.set(path, content);
  }
}

describe("runSummary", () => {
  it("ファイル無しで、全体の流れをテストできる😆✨", async () => {
    const io = new MemoryTextFileIO();
    io.set("in.csv", [
      "date,category,amount",
      "2026-01-01,food,1200",
      "2026-01-02,food,900",
    ].join("\n"));

    await runSummary({ inputPath: "in.csv", outputPath: "out.json", io });

    const out = io.get("out.json");
    expect(out).toBeTruthy();

    const obj = JSON.parse(out!);
    expect(obj.summary.byCategory.food).toBe(2100);
    expect(obj.summary.total).toBe(2100);
  });
});
```

🎉これが「I/O境界の分離」の気持ちよさです！！
**中心＋アプリの9割**は、メモリだけで秒速テスト🧪⚡

---

## 11-4) （任意）

外側の結合テスト：NodeTextFileIO.int.test.ts🔌📁外側は“薄い”から、テストは少数でOK🙆‍♀️
テンポラリフォルダを使うと安全です✨

```ts
import { describe, it, expect } from "vitest";
import { NodeTextFileIO } from "../src/adapters/NodeTextFileIO";
import { mkdtemp } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";

describe("NodeTextFileIO (integration)", () => {
  it("read/writeできる📁✨", async () => {
    const io = new NodeTextFileIO();
    const dir = await mkdtemp(join(tmpdir(), "io-test-"));
    const path = join(dir, "a.txt");

    await io.writeText(path, "hello");
    const text = await io.readText(path);

    expect(text).toBe("hello");
  });
});
```

---

## 12) よくある落とし穴集👃

💥（ここ踏む人多い！）* **改行問題**：Windowsは `\r\n` になりがち
  → `split(/\r?\n/)` が安定✨
* **BOM問題**：UTF-8の先頭に見えない文字が付くことある
  → `text.replace(/^\uFEFF/, "")` ✨
* **“本物CSV”の罠**：ダブルクォートやカンマ含みフィールド
  → ガチCSVならライブラリ推奨（例：`csv-parse`）([npm][4])
* **巨大ファイル**：`readFile` で全部読むとメモリがきつい
  → ストリーム＆CSVライブラリ（`csv-parse`はストリーム対応）([CSV.js][5])

---

## 13) AI拡張で爆速にするコツ🤖🎀AIにお願いすると楽なところ👇✨



* テストケース洗い出し（正常/異常/境界値）🧪
* エラーメッセージ案や命名案📝
* `parse` のバリエーション（ヘッダなし対応など）🔁

おすすめプロンプト例💡

```text
このparseCsvLike(text)に対して、Windows改行/BOM/空行/壊れた行/ヘッダなしを含むテストケースをVitestで10個提案して。
```

⚠️逆に丸投げしないところ👇

* 「境界どこ？」（I/Oを中心に入れない判断）✂️
* 仕様の決定（壊れた行は落とす？止める？）📌

---

## 14) 練習問題（ちょい足し）

🧠✨1. **出力をCSVでも作る**（中心は文字列生成だけ、書き込みは外側）📄➡️📁
2. `category` を正規化（`Food` と `food` を統一）🍔
3. `amount < 0` をエラーにして `errors` に入れる🚧
4. 大きめファイル想定で「中心は1行ずつ処理できる形」に設計してみる（I/Oはストリーム側へ）🌊✨

---

## まとめ🎓🌈

この章の必勝パターンはこれだけ👇✨



* **中心**：文字列→解析→集計（I/Oゼロ🍰）
* **境界**：`TextFileIO`（最小の約束📜）
* **外側**：`NodeTextFileIO`（読む/書くを薄く📁）
* テストは **中心＋アプリはメモリで爆速**、外側だけ少数の結合テスト🧪⚡

ちなみにNodeは2026年1月時点で **24系がActive LTS**、22/20はMaintenance LTS、25はCurrentという並びです([Node.js][6])
（つい最近もセキュリティ更新が出てるので、使うならパッチは上げとくのが安心だよ〜🔒✨ ([Node.js][7])）

---

次の章（第20章：HTTPアクセスを外に押し出す🌐🧩）に行くと、
今日の「File I/Oの分離」がそのまんま刺さって、さらに気持ちよくなります😆💖

[1]: https://nodejs.org/api/fs.html?utm_source=chatgpt.com "File system | Node.js v25.3.0 Documentation"
[2]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
[3]: https://vitest.dev/?utm_source=chatgpt.com "Vitest | Next Generation testing framework"
[4]: https://www.npmjs.com/package/csv-parse?utm_source=chatgpt.com "csv-parse"
[5]: https://csv.js.org/parse/?utm_source=chatgpt.com "CSV Parse - Usage"
[6]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[7]: https://nodejs.org/en/blog/vulnerability/december-2025-security-releases?utm_source=chatgpt.com "Tuesday, January 13, 2026 Security Releases"
