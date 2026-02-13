# 第24章：入力検証と不変条件（入口で守る）🚧🛡️

![testable_ts_study_024_validation_gate.png](./picture/testable_ts_study_024_validation_gate.png)

## この章でできるようになること🎯* 「信用できないデータ（外から来たもの）

」を、**入口でちゃんと止める**ようになる🙅‍♀️


* 中心（ロジック）に入るデータは **“壊れてない前提で扱える”** 状態にできる💎
* ルール（不変条件）を **コードの形で固定**して、テストで守れるようになる🧪🔒

---

## 1) そもそも“入力”ってどこから来るの？🌍📥

![testable_ts_study_024_untrusted_input_attack.png](./picture/testable_ts_study_024_untrusted_input_attack.png)

外から来るデータは、だいたい全部「疑ってかかる」のが正解だよ〜😇



* フォーム入力🧑‍💻
* HTTPリクエスト（JSON）🌐
* クエリパラメータ（文字列…！）🔤
* ファイル（CSV/JSON）📁
* DBから取った値（過去に入った汚いデータがあり得る）🗄️
* 環境変数や設定⚙️

**ポイント：TypeScriptの型は“実行時には消える”**から、`unknown` で受けて **ランタイム検証**が必要になるよ🧯
（2026年1月時点の最新系として TypeScript 5.9 系が公開されてるよ📌） ([npm][1])

---

## 2) 「入力検証」と「不変条件」って何が違うの？🧠✨

![testable_ts_study_024_gate_and_shield.png](./picture/testable_ts_study_024_gate_and_shield.png)

## ✅ 入力検証（Input Validation）**入口でやる**チェック。
「形が合ってる？」「型は？」「必須ある？」「長さは？」「数字っぽい文字列を数値にできる？」みたいなやつ💡

例：

* `email` が文字列で、メール形式っぽい？📧
* `age` が数値（あるいは `"20"` みたいな文字列なら数値へ変換できる）？🔢
* `name` が空じゃない？長すぎない？✍️

## ✅ 不変条件（Invariant）**ドメイン（中心）

のルール**で、いつでも守られていてほしい約束。
「これが破れたら、そのオブジェクトは存在しちゃダメ！」ってやつ😤

例：

* 年齢は 13〜120 の範囲だけ🧓
* 価格は 0 以上💰
* 注文の合計は「明細の合計」と一致する🧾
* 期限は開始日より前にならない📅

**大事な作戦はこれ👇**

* 入口：外のデータを **検証＆整形**して、きれいにしてから渡す🧼
* 中心：入ってきたデータは **信頼してロジックに集中**する🎯

---

## 3) 入口で守る“黄金パイプライン”🌟

![testable_ts_study_024_validation_pipeline.png](./picture/testable_ts_study_024_validation_pipeline.png)

入口の流れは、これでほぼ固定でOKだよ〜💖

1. `unknown` を受ける🙈
2. スキーマで検証する✅
3. 必要なら型変換（coerce）する🔁
4. DTO → Domain へ変換する（不変条件でガード）🛡️
5. 中心ロジックへ渡す🏠✨

---

## 4) 2026年の定番：スキーマ検証ライブラリ🧰✨

入口の検証は「スキーマライブラリ」を使うと超ラクだよ〜💃



* **Zod v4**：型推論が強くて利用者も多い王道👑（2026/1 時点で v4.3.x が出てる） ([npm][2])
* **Valibot**：モジュール構成で軽量志向、最近も活発📦（v1.2 で型変換やAI向けメタデータなど） ([npm][3])
* **ArkType**：TSの型っぽい書き味でランタイム検証する尖り方⚡ ([ArkType][4])

この章のハンズオンは Zod を例にするね（考え方はどれでも同じだよ）😊

---

## 5) ハンズオン：ユーザー登録の「入口で守る」実装🧪✨## お題🎀HTTPからこういうのが来る想定👇



* `name`: string
* `email`: string
* `age`: number（でも `"20"` みたいに文字列で来ることがある）

---

## 5-1. 入口（DTO）

![testable_ts_study_024_zod_blueprint.png](./picture/testable_ts_study_024_zod_blueprint.png)

のスキーマを作る🧾✅

```ts
import { z } from "zod";

// 外から来る “生データ” の検証用スキーマ（DTOスキーマ）
export const RegisterUserDtoSchema = z.object({
  name: z.string().trim().min(1).max(30),
  email: z.string().trim().email(),
  age: z.coerce.number().int().min(13).max(120), // "20" → 20 に寄せる✨
});

export type RegisterUserDto = z.infer<typeof RegisterUserDtoSchema>;
```

ポイント💡

* `z.coerce.number()` で **文字列→数値**を入口で吸収できるのが気持ちいい〜🔁✨
* `trim()` で余計な空白を入口で掃除🧼

---

## 5-2. safeParse で例外じゃなく“結果”で受ける🧯例外だと取り回しが面倒になりがちだから、入口は `safeParse` が便利だよ〜🫶



```ts
import { z } from "zod";
import { RegisterUserDtoSchema, RegisterUserDto } from "./registerUserDto";

export type ValidationIssue = {
  path: string;
  message: string;
};

export type ParseResult<T> =
  | { ok: true; value: T }
  | { ok: false; issues: ValidationIssue[] };

export function parseRegisterUserDto(input: unknown): ParseResult<RegisterUserDto> {
  const parsed = RegisterUserDtoSchema.safeParse(input);

  if (parsed.success) {
    return { ok: true, value: parsed.data };
  }

  return {
    ok: false,
    issues: parsed.error.issues.map((i) => ({
      path: i.path.join("."),
      message: i.message,
    })),
  };
}
```

ここでやってるのは「入口の警備員さん」👮‍♀️✨
壊れた入力はここで止める！

---

## 5-3. ドメイン側：不変条件を“型（オブジェクト）

![testable_ts_study_024_value_object_capsule.png](./picture/testable_ts_study_024_value_object_capsule.png)

”に閉じ込める💎🛡️「中心は前提を信頼したい」ので、**ドメインの値オブジェクト**でガードするよ〜🙆‍♀️



```ts
// domain/emailAddress.ts
export class EmailAddress {
  private constructor(public readonly value: string) {}

  static create(raw: string): EmailAddress | null {
    // 超シンプル版（本格版はより厳密でもOK）
    const v = raw.trim().toLowerCase();
    if (!v.includes("@")) return null;
    return new EmailAddress(v);
  }
}
```

```ts
// domain/age.ts
export class Age {
  private constructor(public readonly value: number) {}

  static create(raw: number): Age | null {
    if (!Number.isInteger(raw)) return null;
    if (raw < 13 || raw > 120) return null;
    return new Age(raw);
  }
}
```

> 入口で min/max してるのに、ドメインでもやるの？🤔
> → **やる！** 入口は“便利のため”、ドメインは“最後の砦”🛡️✨
> （入口の実装が変わっても、中心が壊れないのが強い💪）

---

## 5-4. DTO → Domain 変換（ここが「入口の最後の関所」🚧）

```ts
import { EmailAddress } from "../domain/emailAddress";
import { Age } from "../domain/age";
import { RegisterUserDto } from "./registerUserDto";

export type DomainBuildError =
  | { type: "InvalidEmail" }
  | { type: "InvalidAge" };

export type BuildResult<T> =
  | { ok: true; value: T }
  | { ok: false; error: DomainBuildError };

export type RegisterUserCommand = {
  name: string;          // ここは今回はシンプルにstringのままでもOK
  email: EmailAddress;
  age: Age;
};

export function toRegisterUserCommand(dto: RegisterUserDto): BuildResult<RegisterUserCommand> {
  const email = EmailAddress.create(dto.email);
  if (!email) return { ok: false, error: { type: "InvalidEmail" } };

  const age = Age.create(dto.age);
  if (!age) return { ok: false, error: { type: "InvalidAge" } };

  return {
    ok: true,
    value: {
      name: dto.name, // 必要なら Name 値オブジェクト化もできるよ🧁
      email,
      age,
    },
  };
}
```

これで中心は「EmailAddress と Age は絶対に正しい」前提で扱える💎✨
つまり、中心のロジックがスッキリするよ〜🥹💖

---

## 6) テストで「不正入力の挙動」を固定しよう📌

![testable_ts_study_024_crash_test_input.png](./picture/testable_ts_study_024_crash_test_input.png)

🧪この章のハンズオンのゴールはここ！
「変な入力が来たら、こう返す」をテストで固定するのが強い💪✨

（2026年1月時点で Vitest は v4 系が出てるよ） ([npm][5])

## 6-1. DTO検証のテスト例

```ts
import { describe, it, expect } from "vitest";
import { parseRegisterUserDto } from "./parseRegisterUserDto";

describe("parseRegisterUserDto", () => {
  it("age が '20' でも number に変換して通す", () => {
    const r = parseRegisterUserDto({ name: "A", email: "a@example.com", age: "20" });
    expect(r.ok).toBe(true);
    if (r.ok) expect(r.value.age).toBe(20);
  });

  it("email が壊れてたら issues が返る", () => {
    const r = parseRegisterUserDto({ name: "A", email: "nope", age: 20 });
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.issues.length).toBeGreaterThan(0);
  });
});
```

## 6-2. 不変条件（ドメイン）

のテスト例

```ts
import { describe, it, expect } from "vitest";
import { Age } from "../domain/age";

describe("Age.create", () => {
  it("13未満は作れない", () => {
    expect(Age.create(12)).toBeNull();
  });

  it("整数の範囲なら作れる", () => {
    const a = Age.create(20);
    expect(a?.value).toBe(20);
  });
});
```

---

## 7) よくある落とし穴集😵‍💫（ここだけは避けて〜！

）* **中心で `if (!input.name) ...` を延々やり始める**
  → 入口で止めよう！中心はスッキリが正義✨
* **ドメインがZodに依存しちゃう**
  → スキーマは外側の都合。中心は知らない方が強い💪
* **“型があるから大丈夫”と思って検証しない**
  → 実行時には型がない！`unknown` を疑って！🙈
* **coerceをやりすぎて、変換ミスが静かに通る**
  → “変換していいもの/ダメなもの”は方針を決めよ✍️

---

## 8) 演習（やってみよ〜💪💕）## 演習A：不正入力のテストを増やす🧪次を追加して「挙動を固定」してね📌



* `name = "   "`（空白だけ）
* `age = "abc"`（数値にできない）
* `age = 999`（範囲外）

## 演習B：Nameも値オブジェクトにする🍰* `trim()` 後に空ならNG


* 30文字超えはNG
* 正規化（連続スペースを1個に）を入れてもOK✨

## 演習C：エラーを「フィールドごと」に返す🎯`issues` を `Record<string, string[]>` にまとめて返すようにしてみよ📦

---

## 9) AI拡張の使いどころ（速くなるやつ）

🤖🎀AIに頼むと気持ちよく速いのはここ👇



* バリデーションケースの洗い出し（境界値、空、変換失敗など）🧠
* スキーマの下書き（Zod/Valibot/ArkType）🧾
* テストケースの雛形🧪

## そのまま使えるプロンプト例🪄* 「このDTOの入力検証ルールを列挙して、境界値と異常系のテストケースも出して」


* 「Zodで safeParse を使って、例外を投げないパーサ関数を書いて。返り値は Result 形式で」
* 「DTO→Domain変換で、ドメイン側にZod依存を持ち込まない構成にして」

⚠️ AIのミスあるある

* ドメイン層にZodを持ち込む
* 変換（coerce）を中心でやり始める
* 仕様っぽい不変条件を“なんとなく”決めちゃう（ここは人間が握る！）🙅‍♀️

---

## まとめ🎉* 入口で **検証＆整形**して、中心に“きれいなデータ”だけ渡す🧼✨


* 不変条件は **ドメインの型（値オブジェクト）**で守る🛡️💎
* 「不正入力が来たらこうする」を **テストで固定**すると、変更が怖くなくなるよ🧪🌈

次の章（エラー設計）で、この章の「エラーの返し方」をさらに気持ちよく整理していこ〜😇🚨

[1]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "TypeScript"
[2]: https://www.npmjs.com/package/zod?utm_source=chatgpt.com "Zod"
[3]: https://www.npmjs.com/package/valibot?utm_source=chatgpt.com "valibot"
[4]: https://arktype.io/?utm_source=chatgpt.com "ArkType: TypeScript's 1:1 validator, optimized from editor to ..."
[5]: https://www.npmjs.com/package/vitest?utm_source=chatgpt.com "vitest"
