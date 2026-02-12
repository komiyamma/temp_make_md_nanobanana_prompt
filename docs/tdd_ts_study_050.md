# 第50章：入力検証（スキーマ/バリデーションの入口）🧷

![バリデーションの盾](./picture/tdd_ts_study_050_input_shield.png)

API や JSON、フォーム入力って、**「型があるっぽく見える」けど実は `unknown`** なんだよね😵‍💫
TypeScript の型は *実行時* には守ってくれないから、入口でコケると「どこで壊れたの!?」ってなる…💥

この章では、**入口で “壊れたデータ” を止める**（そして **内部モデルを汚さない**）やり方を、TDDで手に入れます🧪💕

---

## 🎯この章のゴール

* 外部から来る `unknown` を、**スキーマで検証**して安全にする🛡️
* 「検証 → 変換 → 内部型（ドメイン）」の流れを固定する🔄
* 欠損/型違い/余計なキーに対して、**落ち方（エラーの出し方）**を設計できる🧯

※ここで使うスキーマは、2026/01/19時点で **Zod 4 が安定版**なので、それ前提で進めるよ〜✨ ([Zod][1])
（TypeScript の公式リリースノートは 5.9 が 2026-01-12 更新だよ、って状況も確認済み🧠） ([TypeScript][2])

---

## 📚まず “入口で守る” ってどういうこと？🚪🛡️

### ✅ 重要ポイントはこれだけ！

* 外部データは **ぜんぶ疑う**（`unknown` から始める）😈
* **入口で検証（Validation）**して、ダメならそこで止める🧱
* OKなら **変換（Transformation）**して、内部モデルは綺麗な型のまま保つ🧼✨

この「入口ガード」を固定すると、あとが超ラクになるよ🥰

---

## 🧪手を動かす：APIレスポンスを “安全に取り込む” をTDDで作るよ💪✨

今回のお題：外部APIがこんな JSON を返す想定ね👇
（※APIは気まぐれで壊れたデータを返すことがある…って前提😇）

* 正常例 ✅
  `{ id: "uuid", name: "Mika", age: 19, joinedAt: "2026-01-01T10:00:00Z" }`
* 壊れ例 ❌

  * `name` 欠損
  * `age` が `"19"`（文字列）
  * `joinedAt` が変な文字列
  * 余計なキー `isAdmin: true` が混ざる

---

## 🧩今回作る構成（おすすめ分離）📁

* `src/boundary/profileSchema.ts`（スキーマ＝入口のルール）
* `src/boundary/parseProfile.ts`（検証→変換の関数）
* `src/domain/profile.ts`（内部モデル：綺麗な型）
* `tests/parseProfile.test.ts`（TDDのテスト）

---

## 1) まずテストを書く（Red）🚦🔴

```ts
// tests/parseProfile.test.ts
import { describe, it, expect } from "vitest";
import { parseProfile } from "../src/boundary/parseProfile";

describe("parseProfile（入力検証の入口）", () => {
  it("正常な入力を内部モデルに変換できる ✅", () => {
    const input = {
      id: "550e8400-e29b-41d4-a716-446655440000",
      name: "Mika",
      age: 19,
      joinedAt: "2026-01-01T10:00:00Z",
    };

    const result = parseProfile(input);

    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.value.id).toBe(input.id);
      expect(result.value.name).toBe("Mika");
      expect(result.value.age).toBe(19);
      expect(result.value.joinedAt.toISOString()).toBe("2026-01-01T10:00:00.000Z");
    }
  });

  it("nameが欠損ならエラーになる ❌", () => {
    const input = {
      id: "550e8400-e29b-41d4-a716-446655440000",
      age: 19,
      joinedAt: "2026-01-01T10:00:00Z",
    };

    const result = parseProfile(input);

    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.error.kind).toBe("ValidationError");
      expect(result.error.messages.join("\n")).toContain("name");
    }
  });

  it("ageが文字列でも受け入れて数値に直す（coerce）🔄", () => {
    const input = {
      id: "550e8400-e29b-41d4-a716-446655440000",
      name: "Mika",
      age: "19",
      joinedAt: "2026-01-01T10:00:00Z",
    };

    const result = parseProfile(input);

    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.value.age).toBe(19);
    }
  });

  it("joinedAtがISO datetimeじゃないならエラー ❌", () => {
    const input = {
      id: "550e8400-e29b-41d4-a716-446655440000",
      name: "Mika",
      age: 19,
      joinedAt: "yesterday",
    };

    const result = parseProfile(input);

    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.error.messages.join("\n")).toContain("joinedAt");
    }
  });

  it("余計なキーは“無視して捨てる”（デフォルト挙動）🧹", () => {
    const input = {
      id: "550e8400-e29b-41d4-a716-446655440000",
      name: "Mika",
      age: 19,
      joinedAt: "2026-01-01T10:00:00Z",
      isAdmin: true,
    };

    const result = parseProfile(input);

    expect(result.ok).toBe(true);
    if (result.ok) {
      // 内部モデルに isAdmin は存在しない（混入防止）
      expect((result.value as any).isAdmin).toBeUndefined();
    }
  });
});
```

---

## 2) まだ実装がないので、最小の型（ドメイン）を用意（Greenの準備）🧼✨

```ts
// src/domain/profile.ts
export type ProfileId = string;

export type Profile = {
  id: ProfileId;
  name: string;
  age: number;
  joinedAt: Date;
};
```

---

## 3) スキーマを書く（入口のルール）🧷📜

Zod 4 の要点：

* `z.coerce.number()` で「文字列→数値」みたいな変換ができるよ🔄 ([Zod][3])
* `z.iso.datetime()` で ISO datetime をチェックできるよ⏰ ([Zod][3])
* **余計なキーはデフォルトで削除（strip）**されるよ🧹（混入防止に強い） ([Zod][3])

```ts
// src/boundary/profileSchema.ts
import * as z from "zod";

export const ProfileDtoSchema = z.object({
  id: z.uuid(),
  name: z.string().min(1),
  age: z.coerce.number().int().min(0),
  joinedAt: z.iso.datetime(),
});

export type ProfileDto = z.infer<typeof ProfileDtoSchema>;
```

---

## 4) 検証→変換を書く（Green）✅

ここが “入口” の本体だよ🚪✨
`unknown` を受け取って、ダメなら **ValidationError** にして返す！

```ts
// src/boundary/parseProfile.ts
import * as z from "zod";
import { Profile } from "../domain/profile";
import { ProfileDtoSchema } from "./profileSchema";

type Ok<T> = { ok: true; value: T };
type Err<E> = { ok: false; error: E };

export type ValidationError = {
  kind: "ValidationError";
  messages: string[];
};

export type Result<T> = Ok<T> | Err<ValidationError>;

export function parseProfile(input: unknown): Result<Profile> {
  const parsed = ProfileDtoSchema.safeParse(input);

  if (!parsed.success) {
    return {
      ok: false,
      error: {
        kind: "ValidationError",
        messages: formatZodError(parsed.error),
      },
    };
  }

  // ✅ 検証済み DTO → 内部モデルへ変換（joinedAtだけDate化）
  const dto = parsed.data;

  return {
    ok: true,
    value: {
      id: dto.id,
      name: dto.name,
      age: dto.age,
      joinedAt: new Date(dto.joinedAt),
    },
  };
}

function formatZodError(error: z.ZodError): string[] {
  return error.issues.map((i) => {
    const path = i.path.join(".");
    return path ? `${path}: ${i.message}` : i.message;
  });
}
```

これでテスト通るはず！🎉（Green✅）

---

## 5) Refactor：入口の “方針” を言語化しよう🧠✨

### ✅余計なキー、どうする？🤔

Zodは **デフォルトで未知キーを削除**するよ（＝混入しにくい） ([Zod][3])
ただし方針は2択で、プロダクトによって選ぶのが正解🙆‍♀️

* 🧹 **削除（デフォルト）**：安全寄り、移行に強い
* 🚫 **拒否（strict）**：契約に厳密、バグに気づきやすい
  `z.strictObject({...})` が使えるよ ([Zod][3])
* 🎁 **通す（loose）**：柔軟だけど混入リスクあり
  `z.looseObject({...})` ([Zod][3])

> 迷ったら：まず削除（デフォルト）→ 必要なら strict に寄せる、が事故りにくい🥺✨

---

## 🤖AIの使いどころ（この章での “正しいお願い”）💡

### ① テストケース増やし案だけ出してもらう🧪

* 「欠損パターン」
* 「型違いパターン」
* 「境界値（age=0、age=999など）」
* 「余計なキー混入」

💬 例プロンプト：

```text
次のスキーマ（id uuid / name string / age number(coerce) / joinedAt iso datetime）に対して、
「壊れた入力」のテストケース案を10個。理由も1行ずつ。
ただし実装には触れず、入力と期待（ok/err）だけ書いて。
```

### ② エラー表示文の改善案をもらう🪄

「ユーザー向け」か「開発者向け」かでメッセージ変わるから、方針も一緒に考えてね😊

---

## ✅チェックリスト（できてたら合格💮）

* `parseProfile(input: unknown)` から始めてる？（`as Profile` で誤魔化してない？）😇
* 欠損/型違い/形式違いのテストがある？🧪
* 「検証」と「変換」が分離できてる？🔄
* 内部モデル（ドメイン）に余計なキーが混ざらない？🧼
* エラーの内容が “どこがダメか” 分かる？🧯

---

## 🌸おまけ：この章の “一言まとめ” 📝💖

**外から来るものは全部 `unknown`。入口でスキーマ検証して、内部はずっとキレイな型で生きる！** 🧷✨

[1]: https://zod.dev/v4 "Release notes | Zod"
[2]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html "TypeScript: Documentation - TypeScript 5.9"
[3]: https://zod.dev/api "Defining schemas | Zod"
