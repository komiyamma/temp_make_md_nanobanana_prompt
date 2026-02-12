# 第56章：卒業制作：小アプリを“TDDで完成”＋CI導入✅

![卒業おめでとう](./picture/tdd_ts_study_056_graduation.png)

ここは“総まとめ回”だよ〜！🎉
**仕様→テスト→実装→リファクタ→運用（CI）**まで、1人で回して「作りきる」体験をするよ🧪💪

---

## 🧭 0) 今日の“最新版メモ”（2026/1/19時点）🗓️✨

* **Node.js：v24 が LTS（Active LTS）**になってるよ🟩（例：v24.13.0 が 2026-01-13 公開） ([Node.js][1])
* **TypeScript：v5.9.3**が最新リリース（2025-10-01） ([GitHub][2])
* **Vitest：v4.0.17 が Latest（2026-01-12）** ([GitHub][3])
* **GitHub Actions：actions/checkout は v6 系**（例：v6.0.1 が 2025-12-02） ([GitHub][4])
* **actions/setup-node は v6 系**で、依存キャッシュ（npm/yarn/pnpm）もサポートしてるよ🧰 ([GitHub][5])

---

## 🎯 1) ゴール（この章の合格ライン）✅🎀

**“小さくても完成したアプリ”**を作るよ✨

### ✅ 合格の定義（Definition of Done）

* 重要ユースケース **3つ**が **TDDで完成**してる🧪
* ローカルで **テスト＆型チェックが安定して通る**🔁
* GitHub Actions で **テスト＋型チェックが自動実行**される🤖✅
* README に **実行手順・テスト手順・仕様の概要**が書いてある📘

---

## 🧁 2) 作品テーマ（おすすめ3つ）🎨

どれでもOK！でもこの章では **例として「推し活グッズ管理🎀」**で進めるね😊

* 🎀 推し活グッズ管理：買ったもの／カテゴリ／合計金額
* 💰 かんたん家計簿：収支入力／月別集計／カテゴリ別
* 🍙 学食注文：注文カート／合計／注文確定（在庫は発展）

---

## 🧩 3) “重要ユースケース3つ”を決める（ここ超大事！）📝✨

まず **増やさない**のがコツだよ〜！😵‍💫➡️😌

### 🎀 推し活グッズ管理（例）

1. **追加する**：名前・価格・カテゴリを入力して登録する➕
2. **一覧する**：カテゴリで絞って表示する📋
3. **集計する**：カテゴリ別の合計金額を出す📊

### ✅ 受け入れ条件（Given/When/Then）を1行ずつ書く

例：

* Given 正しい名前と価格, When 追加する, Then 一覧に増えている
* Given 価格がマイナス, When 追加する, Then エラーが返る（保存されない）

---

## 🏗️ 4) “崩れない形”の最小アーキ（超かんたん版）🧱✨

ポイントはこれだけ👇
**ドメイン（中心のルール）を、UIやファイル保存から守る**🛡️

```text
src/
  domain/        ← ルールと型（ここが主役✨）
  usecases/      ← 3ユースケース（アプリの動き）
  ports/         ← 依存の“口”（Repositoryなど）
  adapters/      ← ファイル保存や in-memory 実装
  ui/            ← CLIとか（最小でOK）
tests/
```

---

## 🧪 5) まずは「追加する」をTDDで完成させよう（例）🎀➕✅

### 📚 学ぶ

* “まずテストで仕様を固定”→最小実装→整理 の流れ
* 失敗（エラー）も仕様にする🚫✨

### 🧪 手を動かす：最小の型＆Result（例）

```ts
// src/domain/result.ts
export type Result<T, E> =
  | { ok: true; value: T }
  | { ok: false; error: E };

export const ok = <T>(value: T): Result<T, never> => ({ ok: true, value });
export const err = <E>(error: E): Result<never, E> => ({ ok: false, error });
```

### 🧪 手を動かす：ユースケースのテスト（先に書く！）

```ts
// tests/addItem.test.ts
import { describe, it, expect } from "vitest";
import { addItem } from "../src/usecases/addItem";
import { InMemoryItemRepo } from "../src/adapters/inMemoryItemRepo";

describe("addItem", () => {
  it("正しい入力なら保存され、okが返る🎀", async () => {
    const repo = new InMemoryItemRepo();
    const r = await addItem(
      { name: "アクスタ", priceYen: 2500, category: "goods" },
      { repo }
    );

    expect(r.ok).toBe(true);
    if (r.ok) {
      const all = await repo.listAll();
      expect(all.length).toBe(1);
      expect(all[0].name).toBe("アクスタ");
      expect(all[0].priceYen).toBe(2500);
    }
  });

  it("価格がマイナスならerrで、保存されない🚫", async () => {
    const repo = new InMemoryItemRepo();
    const r = await addItem(
      { name: "アクスタ", priceYen: -1, category: "goods" },
      { repo }
    );

    expect(r.ok).toBe(false);
    const all = await repo.listAll();
    expect(all.length).toBe(0);
  });
});
```

### ✅ 最小実装（テストが通るだけでOK）

```ts
// src/ports/itemRepo.ts
export type Item = {
  id: string;
  name: string;
  priceYen: number;
  category: "goods" | "ticket" | "other";
};

export interface ItemRepo {
  save(item: Item): Promise<void>;
  listAll(): Promise<Item[]>;
}
```

```ts
// src/adapters/inMemoryItemRepo.ts
import { ItemRepo, Item } from "../ports/itemRepo";

export class InMemoryItemRepo implements ItemRepo {
  private items: Item[] = [];

  async save(item: Item) {
    this.items.push(item);
  }

  async listAll() {
    return [...this.items];
  }
}
```

```ts
// src/usecases/addItem.ts
import { ItemRepo, Item } from "../ports/itemRepo";
import { Result, ok, err } from "../domain/result";

type AddItemInput = {
  name: string;
  priceYen: number;
  category: Item["category"];
};

type AddItemError =
  | { type: "InvalidName" }
  | { type: "InvalidPrice" };

export async function addItem(
  input: AddItemInput,
  deps: { repo: ItemRepo }
): Promise<Result<Item, AddItemError>> {
  if (input.name.trim().length === 0) return err({ type: "InvalidName" });
  if (!Number.isInteger(input.priceYen) || input.priceYen < 0) {
    return err({ type: "InvalidPrice" });
  }

  const item: Item = {
    id: crypto.randomUUID(),
    name: input.name,
    priceYen: input.priceYen,
    category: input.category,
  };

  await deps.repo.save(item);
  return ok(item);
}
```

### 🧹 Refactor（この順でやると安全💡）

* テスト名を “仕様の文章” にする📝
* `Item` の生成を `domain/` 側に寄せる（入力チェックもそこへ）🧠
* `AddItemError` を増やしても壊れない形にする（unionの出番✨）

---

## 📋 6) ユースケース②「一覧する（絞り込み）」を追加🧪✨

### 🎯 仕様例

* カテゴリ指定があればそれだけ返す
* なければ全部返す

ここは **パラメータ化テスト**が気持ちいいよ🔁💕

（例：`[{ filter: "goods", expected: 2 }, ...]` みたいに）

---

## 📊 7) ユースケース③「集計する（カテゴリ別合計）」🧪💰

### 🎯 仕様例

* `goods: 5000, ticket: 12000, other: 0` みたいな集計結果
* “順序”が仕様じゃないなら、**オブジェクト比較**でOK🧸

ここは「境界値」も入れやすい✨

* 0件
* 1件
* 同カテゴリ複数
* 大きい数（合計）

---

## 📁 8) （発展）ファイル保存を“アダプタ”で足す✨

やることは1つだけ👇
**ドメイン＆ユースケースには触らない。Repositoryの実装だけ増やす。**🔌

* `FileItemRepo` を作る（JSONで保存/読み込み）
* ユースケースのテストは **in-memory のまま**（速い＆安定⚡）
* ファイル保存は **統合テストを1〜2本だけ**（少数精鋭⭐）

---

## 🤖 9) CI（GitHub Actions）を入れる✅🎉

### 📚 学ぶ

* push / PR のたびに **テスト＋型チェック**が走る
* actions/setup-node は **依存キャッシュ**もできる🧰 ([GitHub][5])
* checkout は v6 系が現行だよ📦 ([GitHub][4])

### 🧪 例：`.github/workflows/ci.yml`

```yaml
name: ci

on:
  push:
  pull_request:

permissions:
  contents: read

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [windows-latest]
        node: [24]

    steps:
      - uses: actions/checkout@v6

      - uses: actions/setup-node@v6
        with:
          node-version: ${{ matrix.node }}
          cache: npm

      - run: npm ci
      - run: npm run typecheck
      - run: npm test -- --run
```

> Node は v24 が LTS（Active LTS）なので、この章は `24` で固定しちゃうのがラクだよ🟩 ([Node.js][1])

---

## 🧾 10) package.json の最小スクリプト例🧪✨

```json
{
  "type": "module",
  "scripts": {
    "test": "vitest",
    "test:watch": "vitest --watch",
    "typecheck": "tsc -p tsconfig.json --noEmit"
  },
  "devDependencies": {
    "typescript": "^5.9.3",
    "vitest": "^4.0.17"
  }
}
```

（TypeScript v5.9.3 / Vitest v4.0.17 は本日時点の参照だよ。） ([GitHub][2])

---

## 🤖 11) AIの使い方（この章専用テンプレ）📌✨

### ✅ 仕様を固める（最初だけ）

* 「ユースケース3つを Given/When/Then で1行ずつにして。抜けや曖昧さも指摘して」

### ✅ テストの観点抜けチェック（超便利）

* 「このテスト群の“抜け観点”を列挙して。追加するなら優先度順に3つ」

### ✅ リファクタ安全運転

* 「この変更を3コミットに分けるなら、分割案とそれぞれのテストの守り方は？」

### ✅ PRレビュー役（最後に強い）

* 「仕様に対してテストが弱いところ、命名が誤解されそうなところを厳しめに指摘して」

---

## ✅ 12) 提出物（これが揃ったら卒業🎓🎉）

* ✅ リポジトリ（ソース一式）
* ✅ テスト（ユースケース3つ＋異常系）
* ✅ CI（Actionsが緑💚）
* ✅ README（1枚でOK）

  * 何のアプリ？
  * できること（ユースケース3つ）
  * 実行方法 / テスト方法
  * 仕様メモ（制約・今後の改善案）

---

## ✅ 最終チェックリスト（詰まったらここを見る）🧯✨

* 🧪 テストが落ちた：**仕様が変わった？実装が壊れた？**を先に分ける
* 🐢 遅い：ファイルI/Oがユニットに混ざってない？（混ざってたら境界へ🚪）
* 💥 たまに落ちる：時間・乱数・共有状態が混ざってない？（注入＆固定！）
* 🧹 リファクタ怖い：**テストを守りながら3回に分ける**（命名→抽出→整理）

---

必要なら、次のどれかで「第56章」をさらに教材っぽく整えるよ😊💕

* ✅ 章内の“コミット単位”まで分解した進行表（1〜3コミット×数セット）
* ✅ 「推し活グッズ管理🎀」の完成版を、**ユースケース3つぶん**まるっとサンプル実装
* ✅ UI（CLI or ちいさなWeb）をどこまでやるか、最小の選び方ガイド🧭

[1]: https://nodejs.org/en/blog/release/v24.13.0 "Node.js — Node.js 24.13.0 (LTS)"
[2]: https://github.com/microsoft/typescript/releases "Releases · microsoft/TypeScript · GitHub"
[3]: https://github.com/vitest-dev/vitest/releases "Releases · vitest-dev/vitest · GitHub"
[4]: https://github.com/actions/checkout "GitHub - actions/checkout: Action for checking out a repo"
[5]: https://github.com/actions/setup-node "GitHub - actions/setup-node: Set up your GitHub Actions workflow with a specific version of node.js"
