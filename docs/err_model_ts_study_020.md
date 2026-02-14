# 第20章：入力チェックは“実行時”だよ🧪🫥

この章のゴールはシンプル👇
**「外から来たデータ（フォーム/URL/JSON/APIレスポンス）を、境界でちゃんと検証して、ドメインエラーとして返せる」**ようになることだよ😊💪

---

## 20-1. なんで“実行時チェック”が必要なの？🫥➡️🧪

![runtime_ghost_knight](./picture/err_model_ts_study_020_runtime_ghost_knight.png)

TypeScriptの型は、**コンパイル後に消える**（= 実行時には守ってくれない）からだよ😳💦
つまり…

![実行時チェック：未知のデータを通す検問[(./picture/err_model_ts_study_020_border_control.png)

* `fetch()`で受け取ったJSON
* フォーム入力
* `URLSearchParams` の値
* 外部APIのレスポンス

これ全部、実行時には **「何が入ってるか分からない箱（unknown）」** みたいなもの📦🫥
だから **境界（入口）で validation/parse が必要**になるよ🚪✨

---

## 20-2. “validate” と “parse” を分けて考えよう🍳✨

![validate_vs_parse](./picture/err_model_ts_study_020_validate_vs_parse.png)

ここ、設計が一気にラクになるポイント💡

### ✅ validate（検証）

* 「形・型・制約が合ってる？」をチェックするだけ👀
* 合ってなければ **入力エラー（ドメイン）**として返す🎁

### ✅ parse（変換＋検証）

* 文字列 `"123"` → 数値 `123` にする、空白トリムする、デフォルト値を入れる…など
* **“使える形に整えてから” 型付けされた値を返す**🧼✨

> 実務だと「parse = 入口での正規化」って感覚がすごく強いよ😊
> （第15章の“正規化”の入力版って感じ！）

---

## 20-3. 入力チェック設計の鉄板ルール3つ🔩✨

![input_rules_pillars](./picture/err_model_ts_study_020_input_rules_pillars.png)

### ルール①：境界の入力はまず `unknown` として扱う🫥

「信用しない」から始めるのが安全🥹🛡️

### ルール②：入力エラーは “例外” じゃなく “ドメインエラー” にする💗

入力ミスはユーザーが直せる“想定内の失敗”だよね🙂
だから **Resultで返す**のが相性◎🎁

### ルール③：エラーメッセージは「表示用」と「ログ用」を分ける🧾🔒

* 表示：やさしい言葉💬🌸
* ログ：開発者が調査できる情報🔎🧑‍💻

---

## 20-4. まずは王道：スキーマバリデーション（Zod例）🧪🧩

![zod_scanner](./picture/err_model_ts_study_020_zod_scanner.png)

フォーム/JSONの検証で超よく使われる形だよ🙂
Zodは **`safeParse`** で「例外にしない検証」ができて、さらに **`flatten()`** で **formErrors / fieldErrors** に整形できるのが強い✨ ([Zod][1])

### 20-4-1. 例：会員登録入力を“入口で”パースする🎀

![error_sorting_flatten](./picture/err_model_ts_study_020_error_sorting_flatten.png)

```ts
import { z } from "zod";

// 1) 入力スキーマ（入口の期待値）
const RegisterSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
  age: z.coerce.number().int().min(18).max(120), // "20" みたいな文字列も数値化したい例
});

// 2) 型はスキーマから作る（重複を避ける）
type RegisterInput = z.infer<typeof RegisterSchema>;

// 3) 入力エラー（ドメイン）
type InvalidInputError = {
  kind: "InvalidInput";
  formErrors: string[];
  fieldErrors: Record<string, string[]>;
};

// 4) Result（超ミニ版）
type Ok<T> = { ok: true; value: T };
type Err<E> = { ok: false; error: E };
type Result<T, E> = Ok<T> | Err<E>;
const ok = <T>(value: T): Ok<T> => ({ ok: true, value });
const err = <E>(error: E): Err<E> => ({ ok: false, error });

// 5) 入口の正規化関数（parse）
export function parseRegisterInput(raw: unknown): Result<RegisterInput, InvalidInputError> {
  const r = RegisterSchema.safeParse(raw);

  if (!r.success) {
    const flat = r.error.flatten(); // formErrors / fieldErrors に分かれる
    return err({
      kind: "InvalidInput",
      formErrors: flat.formErrors,
      fieldErrors: flat.fieldErrors,
    });
  }

  return ok(r.data);
}
```

`flatten()` で **フォーム全体のエラー（formErrors）** と **項目別（fieldErrors）** に分かれるのがめっちゃ便利だよ🫶✨（次の第21章に直結！） ([Zod][1])

---

## 20-5. もう1つの有力：Valibot（軽量・モジュール型）🪶✨

Valibotは **型安全＆モジュール指向**を押してるスキーマライブラリで、`safeParse` が用意されてるよ🙂 ([Valibot][2])

「必要な機能だけ取り込む」思想なので、用途によってはかなり相性いい🧩✨

```ts
import * as v from "valibot";

const RegisterSchema = v.object({
  email: v.pipe(v.string(), v.email()),
  password: v.pipe(v.string(), v.minLength(8)),
  age: v.pipe(v.number(), v.minValue(18), v.maxValue(120)),
});

export function parseRegisterInput(raw: unknown) {
  const r = v.safeParse(RegisterSchema, raw); // 例外にしない
  if (!r.success) {
    // ここで「自分のInvalidInputError形式」に変換して返す
  }
  return r.output;
}
```

`safeParse` が公式APIとして用意されてるのがポイントだよ😊 ([Valibot][3])

---

## 20-6. API/契約が絡むなら：JSON Schema（Ajv）＋TypeBox も強い🌐📜

「APIの契約」「OpenAPI」「JSON Schemaでの共有」をやるなら、この系統が便利✨

* **Ajv**：JSON Schema validator（TypeScript向けの型サポート解説もある） ([Ajv][4])
* **TypeBox**：TypeScriptっぽく書いて **JSON Schema を生成**できる ([GitHub][5])

> “スキーマを中心に契約を回す” 系の設計で活躍しがちだよ🙂

---

## 20-7. 「入力エラー」を“ドメインエラー”として美しく扱うコツ🎀🧠

![fortress_boundary](./picture/err_model_ts_study_020_fortress_boundary.png)

### ✅ 入口関数はこう分けると超運用しやすい

* `parseXxx(raw: unknown)`：入口の正規化（Resultで返す）
* `usecase(input: Xxx)`：中では「型がある前提」で進める

こうすると、ユースケース内に「型チェック地獄」が侵入しない🚫😵‍💫
**境界で止める**のが勝ち✌️✨

---

## 20-8. ミニ演習📝✨（15〜30分）

![search_query_filter](./picture/err_model_ts_study_020_search_query_filter.png)

### お題：検索条件（クエリ）を検証して “入力エラー” で返そう🔎

入力（例）：

* `q`：検索文字列（1〜50文字）
* `page`：1以上
* `sort`：`"new"` | `"popular"` のどっちか

やること👇

1. スキーマを作る🧩
2. `parseSearchQuery(raw: unknown)` を作る🚪
3. 失敗したら `InvalidInput` で返す🎁
4. 成功したら “型付き” で返す✨

**追加ミッション（強い）💪**：
境界値テストケースを10個作る（空文字、長すぎ、`page=0`、`sort=hoge`…など）🧪📋
この「境界値リスト作り」、第20章の一番おいしい筋トレだよ😆🔥

---

## 20-9. AI活用🤖✨（そのままコピペOK）

### ① 境界値を網羅したい📋

「`q/page/sort` の入力について、ありえる境界値・異常値を30個、理由つきで出して」

### ② エラー文言をやさしくしたい💬🌸

「この fieldErrors を、ユーザーが直しやすい日本語に言い換えて（短く・丁寧に・責めない）」

### ③ スキーマ設計レビューしてほしい👀

「このスキーマ設計の穴（通ってしまう変な入力）を指摘して、改善案を出して」

---

## 20-10. 今どきTypeScript事情（軽くメモ）🧠✨

* TypeScript 5.9系が現行安定版として提供されていて、`import defer` などの新しめ仕様も追ってるよ ([Microsoft for Developers][6])
* さらに次の大きな流れとして TypeScript 6/7（ネイティブ移行の話）が公式に進捗共有されてるよ ([Microsoft for Developers][7])

この章の結論（入力チェック）は、TypeScriptのバージョンが進んでも **ずっと重要なまま**🥹✨

---

## まとめ🎁✨（この章で持ち帰ること）

* 外部入力はまず `unknown` 🫥
* 境界で **parse/validate** して、成功だけを中に通す🚪
* 入力ミスは例外じゃなく **ドメインエラー（Result）** 💗
* `fieldErrors/formErrors` 形式に落とすと、次章（フォームUX）で爆伸びする🫶 ([Zod][1])

---

次は第21章で、この `fieldErrors` を使って **“どこが悪いか一瞬で分かるUX”** を作っていくよ🫶📝✨
（第20章で作った `InvalidInputError` が、そのまま武器になる！⚔️😊）

[1]: https://zod.dev/error-formatting?utm_source=chatgpt.com "Formatting errors"
[2]: https://valibot.dev/?utm_source=chatgpt.com "Valibot: The modular and type safe schema library"
[3]: https://valibot.dev/api/safeParse/?utm_source=chatgpt.com "safeParse"
[4]: https://ajv.js.org/guide/typescript.html?utm_source=chatgpt.com "Using with TypeScript"
[5]: https://github.com/sinclairzx81/typebox?utm_source=chatgpt.com "sinclairzx81/typebox: JSON Schema Type Builder ..."
[6]: https://devblogs.microsoft.com/typescript/announcing-typescript-5-9/?utm_source=chatgpt.com "Announcing TypeScript 5.9"
[7]: https://devblogs.microsoft.com/typescript/progress-on-typescript-7-december-2025/?utm_source=chatgpt.com "Progress on TypeScript 7 - December 2025"
