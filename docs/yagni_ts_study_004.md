# 第04章：YAGNIを支える実装スタイル（小さく作って育てる）🧱🌿

この章は「作らない勇気」を、**“後で詰まない”形でやるための実装スタイル**を身につける回だよ〜！🙂✨
ポイントはこれ👇

* ✅ **まず動く**（最小でOK）
* ✅ **名前を整える**（読みやすさUP）
* ✅ **小さく分ける**（後で足しやすくする）
* ✅ **ロジックだけテスト**（最低限の安心🧪）

---

## 0. 2026/01/11 時点の “いま” 情報メモ 🗓️✨（超重要）

この章の手順は、今の主流ツール前提で組み立ててるよ👇

* TypeScript：**5.9**（公式リリースノート） ([typescriptlang.org][1])
* React：**19.2 が最新**（公式 “Versions”） ([React][2])
* Vite：**7.3.1 が最新**（npm） ([npm][3])
* Vitest：**4.0**（公式ブログ） ([Vitest][4])
* Node.js：Vite の要件は **Node 20.19+ / 22.12+**（公式ガイド） ([vitejs][5])
  参考：Node 24.x が LTS へ移行（公式リリース） ([Node.js][6])

---

## 1. “後で足せる最小設計”ってなに？🧰🙂

YAGNIって「作らない」だけど、雑にサボるのとは違うよね😅
じゃあ、何を作ればいいの？ってなる。

結論：**“拡張ポイントを作り込む”んじゃなくて、**
**“あとから触りやすい形”にしておく**のがコツ！🌿

### “触りやすい形”の正体（この章の合言葉）🔑✨

* 🧠 **状態（データ）**が素直（変な抽象化なし）
* 🧼 **関数**が短い（読める）
* 🧩 **ロジックが UI から分離**されてる（テストできる）
* 🧪 **最低限テスト**で「壊れてない」を確認できる

「未来のための超スゴ設計」じゃなくて、
「未来の自分が修正しやすい設計」を目指すよ〜！💪🙂

---

## 2. 例題：推し活メモ（第4章バージョン）📝🎀

この章では機能を**2つだけ**に絞るよ✂️✨

* ✅ メモを追加する
* ✅ メモを一覧で見る

やらない（今は）🙅‍♀️

* 🔍 検索、🏷️ タグ、⭐ ピン留め、☁️ 同期、📦 DB、🔐 認証、などなど…

---

## 3. 作り方の流れ（YAGNI実装スタイルの型）🧱✨

![Implementation Stones](./picture/yagni_ts_study_004_step_stones.png)

### ステップA：まず動く（1ファイルでOK）🏃‍♀️💨

* とにかく UI を作って **追加→一覧** を成立させる

### ステップB：名前を整える（読みやすさ最優先）🧼🪥

* 変数名 / 関数名 / コンポーネント名を素直に

### ステップC：小さく分ける（ロジックだけ外へ）🧩📦

![小さく分ける](./picture/yagni_ts_study_004_logic_separation.png)

* **UI** と **ロジック** を分離（テストしやすくする）

### ステップD：ロジックだけテスト（1〜2個でOK）🧪✨

![ロジックだけテスト](./picture/yagni_ts_study_004_test_breakwater.png)

* 「追加すると増える」「空文字は弾く」くらいで十分！

---

## 4. セットアップ（Vite + React + TS）💻✨

（PowerShell でも OK）

```bash
npm create vite@latest oshi-memo -- --template react-ts
cd oshi-memo
npm install
npm run dev
```

Vite は Node のバージョン条件があるから、警告が出たら Node を新しめにするのが安全だよ〜🙂 ([vitejs][5])

---

## 5. ステップA：まず動く（最小 App）✅🧱

![Single File Icon](./picture/yagni_ts_study_004_single_file.png)

まずは **App.tsx だけ**で作っちゃおう！
（この段階で “分割” とか考えない！YAGNI！✂️）

`src/App.tsx`

```tsx
import { useMemo, useState } from "react";

type Memo = {
  id: string;
  title: string;
  createdAt: number;
};

function newId(): string {
  // “今は” これで十分（将来UUIDが必要になったら変える）
  return Math.random().toString(16).slice(2);
}

export default function App() {
  const [title, setTitle] = useState("");
  const [memos, setMemos] = useState<Memo[]>([]);

  const sorted = useMemo(() => {
    // “今は” 新しい順に並べるだけ
    return [...memos].sort((a, b) => b.createdAt - a.createdAt);
  }, [memos]);

  function addMemo() {
    const trimmed = title.trim();
    if (trimmed.length === 0) return;

    const next: Memo = { id: newId(), title: trimmed, createdAt: Date.now() };
    setMemos((prev) => [...prev, next]);
    setTitle("");
  }

  return (
    <div style={{ maxWidth: 560, margin: "40px auto", padding: 16 }}>
      <h1>推し活メモ 📝🎀</h1>

      <div style={{ display: "flex", gap: 8 }}>
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="例）ライブ配信の感想を書く！"
          style={{ flex: 1, padding: 8 }}
        />
        <button onClick={addMemo}>追加 ➕</button>
      </div>

      <ul style={{ marginTop: 16 }}>
        {sorted.map((m) => (
          <li key={m.id}>
            {m.title} <small>({new Date(m.createdAt).toLocaleString()})</small>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

### ✅ チェック（ここまでで勝ち！）🏆✨

* 「追加」押すと増える？
* 空白だけの入力は増えない？
* それだけでOK！🙂

> ここでありがちミス😇
> 「将来 DB にするかも…」「API にするかも…」で設計を始めちゃう
> → **今は “動く” まで一直線！**🛣️💨

---

## 6. ステップB：名前を整える（リファクタは“軽く”）🧼✨

![Name Polishing](./picture/yagni_ts_study_004_name_polish.png)

YAGNIって、リファクタしないって意味じゃないよ🙅‍♀️
むしろ **“小さく作って、小さく整える”** が大事！🌿

この段階でやるのは **これだけ**👇

* `title` → `draftTitle`（入力途中の文字だな〜って分かる）
* `addMemo` の中身を少し整理（読みやすく）

例：関数の中に「意図」が見えるようにする🙂✨
（この章では “正しさ” より “読みやすさ” を優先でOK！）

---

## 7. ステップC：ロジックを外へ（YAGNIに強い分離）🧩📦

ここがこの章のキモ！🔥
**UI から “ロジック” を抜く**と、未来に強くなるよ〜🙂

### フォルダ構成（最小）📁✨

![Simple Folder Tree](./picture/yagni_ts_study_004_folder_tree.png)

* `src/domain/memo.ts`（ロジック）
* `src/domain/memo.test.ts`（テスト）
* `src/App.tsx`（UI）

「いきなり巨大アーキ」は禁止〜！🙅‍♀️
このくらいがちょうどいい🌿

---

### `src/domain/memo.ts`（UIと切り離したロジック）🧠✨

```ts
export type Memo = {
  id: string;
  title: string;
  createdAt: number;
};

export type AddMemoInput = {
  title: string;
};

export function validateTitle(title: string): { ok: true } | { ok: false; reason: string } {
  const trimmed = title.trim();
  if (trimmed.length === 0) return { ok: false, reason: "空っぽはダメだよ〜🙂" };
  if (trimmed.length > 80) return { ok: false, reason: "ちょっと長すぎ！80文字以内にしてね✨" };
  return { ok: true };
}

export function addMemo(list: Memo[], input: AddMemoInput, now: number, id: string): Memo[] {
  const v = validateTitle(input.title);
  if (!v.ok) return list;

  const next: Memo = {
    id,
    title: input.title.trim(),
    createdAt: now,
  };

  return [...list, next];
}
```

> ここもYAGNIポイント✂️
>
> * `id生成` や `Date.now()` は **外から渡す**
>   → テストがラクになる（将来の変更にも強い）🧪✨
> * でも DI コンテナとかは作らない🙅‍♀️（盛りすぎ注意！）

---

### `src/App.tsx`（UIは薄くする）🪶✨

```tsx
import { useMemo, useState } from "react";
import { addMemo, type Memo } from "./domain/memo";

function newId(): string {
  return Math.random().toString(16).slice(2);
}

export default function App() {
  const [draftTitle, setDraftTitle] = useState("");
  const [memos, setMemos] = useState<Memo[]>([]);

  const sorted = useMemo(() => [...memos].sort((a, b) => b.createdAt - a.createdAt), [memos]);

  function onAdd() {
    setMemos((prev) => addMemo(prev, { title: draftTitle }, Date.now(), newId()));
    setDraftTitle("");
  }

  return (
    <div style={{ maxWidth: 560, margin: "40px auto", padding: 16 }}>
      <h1>推し活メモ 📝🎀</h1>

      <div style={{ display: "flex", gap: 8 }}>
        <input
          value={draftTitle}
          onChange={(e) => setDraftTitle(e.target.value)}
          placeholder="例）ライブ配信の感想を書く！"
          style={{ flex: 1, padding: 8 }}
        />
        <button onClick={onAdd}>追加 ➕</button>
      </div>

      <ul style={{ marginTop: 16 }}>
        {sorted.map((m) => (
          <li key={m.id}>
            {m.title} <small>({new Date(m.createdAt).toLocaleString()})</small>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

UI 側が **スッキリ**してきたよね！🥳✨
これが「後で詰まないYAGNI」🌿

---

## 8. ステップD：Vitestで “ロジックだけ” テスト 🧪✨

Vitest は 4.0 が出てて、Vite と相性よしだよ〜🙂 ([Vitest][4])
（テスト環境は `node` / `jsdom` など選べるけど、ロジックだけなら `node` で十分！） ([Vitest][7])

### インストール

```bash
npm i -D vitest
```

`package.json` に追加（scripts）

```json
{
  "scripts": {
    "test": "vitest"
  }
}
```

### `src/domain/memo.test.ts`

```ts
import { describe, expect, test } from "vitest";
import { addMemo } from "./memo";

describe("addMemo", () => {
  test("タイトルが有効なら、1件増える", () => {
    const list = [];
    const next = addMemo(list, { title: "推しが最高だった😭✨" }, 1700000000000, "id1");

    expect(next).toHaveLength(1);
    expect(next[0].id).toBe("id1");
    expect(next[0].title).toBe("推しが最高だった😭✨");
  });

  test("空文字なら、増えない", () => {
    const list = [];
    const next = addMemo(list, { title: "   " }, 1700000000000, "id1");

    expect(next).toHaveLength(0);
  });
});
```

実行：

```bash
npm test
```

### ✅ テストは「少なくていい」けど「効くところだけ」🧪💘

この章は **2本で満点**！💯
「UIは薄い」＝UIのテストを無理に頑張らなくていい、ってなるよ🙂

---

## 9. この章の “YAGNI実装ルール” まとめ（コピペOK）🧾✨

* ✅ まず1ファイルで動かす（分割は後）
* ✅ 2回目で名前を整える（読みやすさ最優先）
* ✅ 3回目でロジックだけ外に出す（UIは薄く）
* ✅ テストはロジックにだけ付ける（1〜2本でOK）
* ❌ 「いつか差し替え」前提の interface 乱立しない
* ❌ utils フォルダを先に作らない（重複が増えてから！）

---

## 10. ミニ演習（この章の宿題）📝🎀

### 演習1：動く最小を作る（10〜20分）⏱️

* 追加→一覧ができるまで作る

### 演習2：ロジックを `domain` に逃がす（10分）🧩

* `validateTitle` と `addMemo` を作る

### 演習3：Vitestでテスト2本（10分）🧪

* 「増える」「増えない」

---

## 11. AI活用（盛らせない指示）🤖🧯✨

![AI Logic Assistant](./picture/yagni_ts_study_004_ai_logic.png)

AIは放っておくと盛りがち🎈😇
だから最初に **縛り**を渡すのがコツ！

### Copilot / Codex に出すプロンプト例（そのまま使ってOK）🧾

* 「要件は *追加と一覧だけ*。検索・タグ・永続化・API・状態管理ライブラリは入れないで。読みやすさ優先で、ファイル分割は `domain/memo.ts` まで。」
* 「`addMemo` は純粋関数（引数→戻り値）で。`Date.now()` と `id生成` は外から渡す形にしてテストしやすくして。」
* 「Vitestでテストは2本だけ。過剰な網羅はしない。」

---

## 12. 成果物📦✨

この章が終わったら、手元にこれが残ってればOK！🥳

* ✅ 推し活メモ（追加・一覧）
* ✅ `domain/memo.ts` にロジック分離
* ✅ Vitest テスト 2本 🧪

---

次の章（第5章）では、「型盛り」「utils地獄」「ジェネリクス芸」みたいな **TypeScript特有の未来用設計**を、もっと安全に先送りするやり方へ進むよ〜✂️🧠✨

[1]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html?utm_source=chatgpt.com "Documentation - TypeScript 5.9"
[2]: https://react.dev/versions?utm_source=chatgpt.com "React Versions"
[3]: https://www.npmjs.com/package/vite?utm_source=chatgpt.com "vite"
[4]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
[5]: https://vite.dev/guide/?utm_source=chatgpt.com "Getting Started"
[6]: https://nodejs.org/en/blog/release/v24.11.0?utm_source=chatgpt.com "Node.js 24.11.0 (LTS)"
[7]: https://vitest.dev/guide/environment?utm_source=chatgpt.com "Test Environment | Guide"
