# 第39章：変換層（外部データに汚染されない）🔄

![変換層の門](./picture/tdd_ts_study_039_filter_gate.png)

## 🎯目的

外から来る「信用できないデータ（API/JSON/フォーム/URL/DB）」を、**いったん玄関でチェックしてから**\n\n![Dirty Input](./picture/tdd_ts_study_039_dirty_input.png)、キレイな「中心モデル」に入れられるようになること😊✨
そして、その変換を **テストで固定**して「将来の事故」を減らすよ🧪✅

---

## 📚この章で覚える合言葉（超だいじ）💡

* 外部データは **unknown**（知らない子）🙃
* 玄関で **検証（validate）→変換（map）** してから入れる🏠✨
* 中心モデルに `any` や `?` を増やして「妥協」しない🙅‍♀️
* 変換ルールは **テストが仕様書**📘🧪

※ちなみに今どきのTSは 5.9 が安定版として案内されていて、`tsc --init` もスッキリ更新されてるよ（設定見直しにも追い風）✨ ([Microsoft for Developers][1])
テスト環境も Vitest 4.0 が出て、ブラウザ実行まわりも安定化が進んでる（UIに寄るなら後半で効いてくるやつ）🧪🌐 ([void(0)][2])

---

## 🧠まずイメージ：中心モデルを「清潔ゾーン」にする🚿✨

![画像を挿入予定](./picture/tdd_ts_study_039_clean_zone.png)

外部データって、だいたいこんな罠があるよね😇

* `id` が string のはずなのに numberで来た
* `createdAt` が `"2026/01/19"` みたいな謎形式
* `email` が `"aaa"`（メールじゃない）
* フィールド欠損 / null混入 / 余計なキー山盛り

これを中心モデル側で受け始めると…

* `User.id?: string | number | null` みたいに **ぐちゃぐちゃ**になる🥺
* そして if地獄へ…🌀

だから、**変換層（Adapter/Mapper）**を作って、中心モデルはいつも「正しい形」だけ扱うのが勝ち🏆✨

---

## 🧱今回の完成形（おすすめ構造）📦\n\n![DTO Domain Flow](./picture/tdd_ts_study_039_dto_domain_flow.png)

* `DTO`（外部の形）…汚くてもOK（現実を受け止める係）😌
* `Schema`（検証）…「合格/不合格」を判定する係🧪
* `Mapper`（変換）…DTO → Domain に作り替える係🔄
* `Domain Model`（中心モデル）…清潔ゾーン✨

Zod 4 だと、オブジェクトで **余計なキーをどう扱うか**も選べるよ👇

* デフォルト：余計なキーは落とす（strip）
* `z.strictObject`：余計なキーが来たらエラーにする
* `z.looseObject`：余計なキーも通す（保持する） ([Zod][3])

（この選択、地味に「事故りやすさ」が変わるよ…！😳）

---

## 🧪手を動かす：外部JSON → Domainに変換してテストで固定しよう💪✨

### 今日のお題（例）👤

外部からこんな JSON が来る想定👇

* `id`: string
* `email`: string（メール形式）
* `plan`: `"free" | "pro"`
* `createdAt`: ISO文字列（例: `"2026-01-19T00:00:00.000Z"`）

中心モデルでは👇にしたい：

* `id`: **ブランド型** `UserId`（取り違え防止🏷️）
* `email`: 検証済み `Email`
* `createdAt`: `Date`（文字列のまま残さない⏰）

---

## ✅ステップ0：Result型（失敗を“仕様”にする）🧯

（第37章の復習っぽいやつだよ✨）

```ts
// src/shared/result.ts
export type Result<T, E> =
  | { ok: true; value: T }
  | { ok: false; error: E };

export const ok = <T>(value: T): Result<T, never> => ({ ok: true, value });
export const err = <E>(error: E): Result<never, E> => ({ ok: false, error });
```

---

## ✅ステップ1：中心モデル（Domain）をキレイに定義✨

```ts
// src/domain/user.ts
declare const userIdBrand: unique symbol;
export type UserId = string & { readonly [userIdBrand]: true };

declare const emailBrand: unique symbol;
export type Email = string & { readonly [emailBrand]: true };

export type Plan = "free" | "pro";

export type User = Readonly<{
  id: UserId;
  email: Email;
  plan: Plan;
  createdAt: Date;
}>;

// 生成関数（中心モデルを守る門番💂‍♀️）
export const UserId = (value: string): UserId => value as UserId;
export const Email = (value: string): Email => value as Email;
```

ポイント🫶
中心モデルは「正しい形」しか受けない！
（検証は外でやるから、ここは強気でOK😤✨）

---

## ✅ステップ2：DTO + Schema（玄関チェック）🧪

Zod 4 は v4 として安定扱いになってて、`zod@^4` で入れられるよ✨ ([Zod][4])

```ts
// src/infra/api/userDto.ts\n\n![Zod Gate](./picture/tdd_ts_study_039_zod_gate.png)
import { z } from "zod";

export const UserDtoSchema = z.object({
  id: z.string().min(1),
  email: z.string().email(),
  plan: z.union([z.literal("free"), z.literal("pro")]),
  createdAt: z.string(), // ここは Date へ変換するから一旦 string
});

export type UserDto = z.infer<typeof UserDtoSchema>;
```

※「余計なキー」を弾きたいなら👇もアリ\n\n![Strict vs Loose](./picture/tdd_ts_study_039_strict_loose.png)

* 厳格にしたい: `z.strictObject({...})`
* 余計なキーも保持したい: `z.looseObject({...})` ([Zod][3])

最初は **デフォルト（strip）** でOKにしがちだよ😊

---

## ✅ステップ3：Mapper（DTO → Domain）🔄

```ts
// src/infra/api/userMapper.ts
import { User, UserId, Email } from "../../domain/user";
import { Result, ok, err } from "../../shared/result";
import { UserDtoSchema } from "./userDto";

export type ParseError =
  | { kind: "ValidationError"; message: string }
  | { kind: "MappingError"; message: string };

export const parseUser = (input: unknown): Result<User, ParseError> => {
  const parsed = UserDtoSchema.safeParse(input);
  if (!parsed.success) {
    return err({ kind: "ValidationError", message: "DTO validation failed" });
  }

  const dto = parsed.data;

  const createdAt = new Date(dto.createdAt);
  if (Number.isNaN(createdAt.getTime())) {
    return err({ kind: "MappingError", message: "createdAt is invalid date" });
  }

  // Domainに変換（ここが“変換層”の本体✨）\n\n![Mapper Alchemy](./picture/tdd_ts_study_039_mapper_alchemy.png)
  return ok({
    id: UserId(dto.id),
    email: Email(dto.email),
    plan: dto.plan,
    createdAt,
  });
};
```

---

## ✅ステップ4：テスト（変換ルールを仕様書にする）📘🧪

Vitest 4.0 が出てるので、ここも今どきでOK✨ ([void(0)][2])

```ts
// tests/userMapper.test.ts\n\n![Test Spec](./picture/tdd_ts_study_039_test_spec.png)
import { describe, it, expect } from "vitest";
import { parseUser } from "../src/infra/api/userMapper";

describe("parseUser (DTO -> Domain)", () => {
  it("✅ 正常: DTOをDomainに変換できる", () => {
    const input = {
      id: "u_001",
      email: "[email protected]",
      plan: "free",
      createdAt: "2026-01-19T00:00:00.000Z",
      extraKey: "this will be stripped (default)", // Zodのデフォルト挙動なら落ちる
    };

    const r = parseUser(input);
    expect(r.ok).toBe(true);
    if (!r.ok) return;

    expect(r.value.id).toBe("u_001");
    expect(r.value.email).toBe("[email protected]");
    expect(r.value.plan).toBe("free");
    expect(r.value.createdAt).toBeInstanceOf(Date);
  });

  it("❌ 欠損: emailがないとValidationError", () => {
    const input = {
      id: "u_001",
      plan: "free",
      createdAt: "2026-01-19T00:00:00.000Z",
    };

    const r = parseUser(input);
    expect(r.ok).toBe(false);
    if (r.ok) return;

    expect(r.error.kind).toBe("ValidationError");
  });

  it("❌ 型違い: planが変だとValidationError", () => {
    const input = {
      id: "u_001",
      email: "[email protected]",
      plan: "vip", // ダメ
      createdAt: "2026-01-19T00:00:00.000Z",
    };

    const r = parseUser(input);
    expect(r.ok).toBe(false);
    if (r.ok) return;

    expect(r.error.kind).toBe("ValidationError");
  });

  it("❌ 変換失敗: createdAtが日付にできないとMappingError", () => {
    const input = {
      id: "u_001",
      email: "[email protected]",
      plan: "pro",
      createdAt: "not-a-date",
    };

    const r = parseUser(input);
    expect(r.ok).toBe(false);
    if (r.ok) return;

    expect(r.error.kind).toBe("MappingError");
  });
});
```

🎉これで「外部データが壊れても中心モデルが汚れない」状態になったよ！

---

## 🤖AIの使い方（この章向けテンプレ）💬✨

AIはめっちゃ相性いいけど、**仕様はテストが決める**のを忘れないでね🫶

### ① 欠損/型違いパターン出し

* 「このDTOで想定すべき欠損・型違い・境界値を20個列挙して。ユーザー入力/サーバ不具合/後方互換の3分類で🙏」\n\n![AI Edge Cases](./picture/tdd_ts_study_039_ai_edge_cases.png)

### ② 変換ルールの日本語化（テスト名に使う）

* 「DTO→Domainの変換仕様を、Given/When/Then で5本のテスト名にして😊」

### ③ “中心モデルを汚しそう”警告を出させる

* 「この実装、中心モデルが外部都合に引っ張られてる部分ない？疑わしい点を3つだけ教えて😳」

---

## ✅チェック（できたら合格）🎓💮

* ✅ `parseXxx(input: unknown)` から始めてる（外部は unknown！）
* ✅ **検証→変換** が分かれてる
* ✅ 中心モデルに `any` / `string | null | undefined` を持ち込んでない
* ✅ 欠損・型違い・変換失敗（Date等）をテストで固定した
* ✅ エラーが「ValidationError / MappingError」みたいに分かれてる（原因追跡しやすい🔍）

---

## 🌟よくある設計ミス（あるあるで刺さる😇）

* ❌ Domain の型を DTO に合わせて `?` を増やす
* ❌ 「とりあえず `as User`」で握りつぶす
* ❌ 変換ルールがコードに埋もれてテストがない（未来の自分が泣く😭）

---

## 🧪ミニ課題（提出物）📮✨

1. `OrderDto` を作る（`price` が `"1200"` みたいに文字列で来る想定）
2. Domain 側は `price: number` にする
3. `"1200"` はOK、`"12oo"`（オー混入）はNG のテストを書く
4. 変換層で `number` へ変換して通す

できたら、次の章（40：境界を守る設計ルール📏）がめっちゃ気持ちよく入れるよ〜！😚✨

[1]: https://devblogs.microsoft.com/typescript/announcing-typescript-5-9/ "Announcing TypeScript 5.9 - TypeScript"
[2]: https://voidzero.dev/posts/announcing-vitest-4 "Announcing Vitest 4.0 | VoidZero"
[3]: https://zod.dev/api "Defining schemas | Zod"
[4]: https://zod.dev/v4 "Release notes | Zod"
