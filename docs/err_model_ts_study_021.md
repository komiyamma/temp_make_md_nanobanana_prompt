# 第21章：フォームの項目別エラー設計（UX）🫶📝

## この章のゴール🎯

フォームで失敗したときに、ユーザーが **「どこが悪いか一瞬で分かって、すぐ直せる」** 形を作れるようになるよ😊💪
具体的には👇

* **fieldErrors（項目別）**：どの入力欄がダメかをピンポイントで伝える🎯
* **formError（全体）**：フォーム全体の問題（例：送信できない、矛盾がある）を伝える🧾
* **再入力ガイド**：直し方まで短く案内する🗺️✨

![フォームアシスト：入力欄の横で優しくガイドする妖精[(./picture/err_model_ts_study_021_form_assist.png)

---

## 1) まず大前提：エラー表示は「設計」だよ🧠🎀

フォームのエラーは、ただ出せばOKじゃなくて、

* **見つけやすさ**（どこ？）👀
* **直しやすさ**（どう直す？）🛠️
* **安心感**（怒られない＆責めない）🥹
* **アクセシビリティ**（誰でも使える）♿✨

が大事！

GOV.UKのデザインガイドでも、**入力欄の近くのエラーメッセージ＋ページ上部の要約（Error summary）** をセットで出すのを推奨してるよ📌([GOV.UK Design System][1])

---

## 2) エラーの置き場所は3つだけ覚えればOK🧺✨

### A. fieldErrors（項目別）🧷

* 「メールが変」「パスワード短い」みたいな **入力欄に紐づく失敗**
* できれば **その入力欄のすぐ近く** に表示💡
* さらに、ページ上部の **エラー要約** にも同じ文言で載せると迷子になりにくいよ🗺️([GOV.UK Design System][1])

### B. formError（全体）🧾

* 「送信に失敗しました（通信）」みたいな **フォーム全体の問題**
* 「パスワードと確認用が一致しない」みたいな **複数項目にまたがる矛盾**（※どこかの項目に寄せられるなら寄せるのが基本🙆‍♀️）

### C. 再入力ガイド（直し方）🧭

* 「正しい形式で」だけだと冷たい＆分かりにくい😢
* 「@を含むメールアドレスを入力してね」みたいに **次の行動** がわかる文にする✨

---

## 3) TypeScriptで「エラーの形」を決めよう🏗️🎁

ここでは、フォームのエラー状態を **毎回ブレない形** に固定するよ😊
おすすめは「文字列だけ」より、**code（機械向け）＋message（表示向け）** の二段構え✨

```ts
// ① どのフィールドがあるか（例：サインアップ）
type SignUpField = "email" | "password" | "passwordConfirm";

// ② 項目別エラー（1項目に複数あり得る）
type FieldIssue = {
  code:
    | "REQUIRED"
    | "INVALID_FORMAT"
    | "TOO_SHORT"
    | "TOO_LONG"
    | "NOT_MATCH"
    | "DUPLICATE";
  message: string;        // 画面に出す文（最終的に日本語）
  hint?: string;          // 直し方ガイド（任意）
};

// ③ フォーム全体エラー（ページ上部バナー等）
type FormIssue = {
  code: "CROSS_FIELD" | "SUBMIT_FAILED" | "NETWORK" | "SERVER";
  message: string;
  actionHint?: string;    // 例：「時間をおいて再試行してね」など
};

// ④ これが「フォームエラーの標準形」✨
type FormProblems<F extends string> = {
  fieldErrors: Partial<Record<F, FieldIssue[]>>;
  formError?: FormIssue;
};

// ⑤ Resultっぽく返す（この教材の流れに合わせて）
type Ok<T> = { ok: true; value: T };
type Err<E> = { ok: false; error: E };
type Result<T, E> = Ok<T> | Err<E>;
```

ポイント💡

* **1フィールド＝1エラーとは限らない**（「必須」「形式」「長さ」など）
* でも全部出すとウザいときもあるので、**出す数の戦略**が必要（後でやるよ😆）

---

## 4) 「同じ失敗」をfieldErrorsとformErrorで出し分ける練習💡📝

### 例題：パスワード確認が一致しない🔁

* **本質**：2項目にまたがる矛盾（Cross-field）
* でもユーザーにとっては「どこ直すの？」が大事！

おすすめ設計👇

* **passwordConfirm に fieldErrors を出す**（直す場所が明確）
* 必要なら **formError は出さない**（二重に言われると疲れる🥺）

```ts
function validatePasswordMatch(
  password: string,
  confirm: string
): FormProblems<SignUpField> | null {
  if (password === confirm) return null;

  return {
    fieldErrors: {
      passwordConfirm: [
        {
          code: "NOT_MATCH",
          message: "パスワードが一致していないよ😣",
          hint: "もう一度、同じパスワードを入力してね✍️",
        },
      ],
    },
  };
}
```

---

## 5) バリデーションライブラリのエラーを「標準形」に変換する🧼✨

### Zod v4の最新：`z.treeifyError()` / `z.flattenError()` が主役🌳🧾

Zod v4では **ZodErrorの `.flatten()` が非推奨** になっていて、代わりに **トップレベル関数**を使うのが今の流れだよ📌([Zod][2])
特にフォーム用途なら `z.flattenError()` がちょうど良い！
`formErrors`（全体）と `fieldErrors`（項目別）が分かれて返ってくるのが強い💪✨([Zod][3])

```ts
import * as z from "zod";

const SignUpSchema = z.object({
  email: z.string().email({ error: "メールの形がちがうよ📧💦" }),
  password: z.string().min(8, { error: "パスワードは8文字以上だよ🔐" }),
  passwordConfirm: z.string(),
}).refine((v) => v.password === v.passwordConfirm, {
  path: ["passwordConfirm"],
  message: "パスワードが一致していないよ😣",
});

type SignUpInput = z.infer<typeof SignUpSchema>;

function validateSignUp(input: unknown): Result<SignUpInput, FormProblems<SignUpField>> {
  const r = SignUpSchema.safeParse(input);
  if (r.success) return { ok: true, value: r.data };

  const flat = z.flattenError(r.error); // v4の推奨ルート🧾✨
  const fieldErrors: FormProblems<SignUpField>["fieldErrors"] = {};

  // flat.fieldErrors は { [key: string]: string[] } みたいな形
  for (const [key, messages] of Object.entries(flat.fieldErrors)) {
    // 必要なら code 付与（ここでは簡易に全部 INVALID_FORMAT にしてる）
    fieldErrors[key as SignUpField] = messages.map((m) => ({
      code: "INVALID_FORMAT",
      message: m,
    }));
  }

  const formError = flat.formErrors.length
    ? { code: "CROSS_FIELD", message: flat.formErrors[0] }
    : undefined;

  return { ok: false, error: { fieldErrors, formError } };
}
```

### Valibotも「flatten」があるよ🧻✨

Valibotも issues を `flatten` して **root（全体）／nested（項目）** を取り出せる設計になってるよ🧩([Valibot][4])

---

## 6) UIに出すときの「アクセシブル設計」超重要♿✨

### 基本セット🎒

* 入力が無効なら **`aria-invalid`** を使う（無効状態を支援技術に伝える）([MDN Web Docs][5])
* エラーメッセージは **`aria-describedby`** で入力欄に紐づける([MDN Web Docs][6])
* `aria-errormessage` を使うなら **aria-invalid が true のときだけ**＆参照先は **表示されている必要**があるよ📌([MDN Web Docs][7])

```tsx
type Props = {
  id: string;
  label: string;
  value: string;
  onChange: (v: string) => void;
  issues?: FieldIssue[];
};

export function TextField({ id, label, value, onChange, issues }: Props) {
  const errorId = `${id}-error`;
  const hasError = !!issues?.length;

  return (
    <div>
      <label htmlFor={id}>{label}</label>

      <input
        id={id}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        aria-invalid={hasError ? "true" : undefined}
        aria-describedby={hasError ? errorId : undefined}
      />

      {hasError && (
        <p id={errorId}>
          {/* まず1件だけ出す戦略（後で説明するね） */}
          {issues![0].message} {issues![0].hint ? `（${issues![0].hint}）` : ""}
        </p>
      )}
    </div>
  );
}
```

---

## 7) UXで事故らないための鉄板ルール集🧷✨

### ✅ ルール1：項目の近く＋上部の要約（エラーサマリ）📌

「上にエラーあります」だけだと探すの大変🥺
GOV.UKは **エラー要約＋各項目のエラーメッセージ** をセットで出す方針だよ([GOV.UK Design System][8])

### ✅ ルール2：同じ文言を使う（上と下で違うと混乱）🔁

GOV.UKも「一貫性」を強く言ってるよ🧠✨([GOV.UK Design System][1])

### ✅ ルール3：入力内容を消さない🧽❌

直すために必要な情報まで消えると地獄😇
「消さない」も明確に推奨されてるよ([GOV.UK Design System][1])

### ✅ ルール4：ふわっとした言葉を避ける🙅‍♀️

「無効です」「正しくありません」だけは弱い…
何がダメで、どう直すかが分かる文にしよ💬✨([GOV.UK Design System][1])

---

## 8) 「複数エラー」をどう見せる？戦略を決めよ😵‍💫➡️😌

### 戦略A：1項目につき最初の1件だけ（初心者向け・優しい）🌷

* 例：「必須」→直したら次のエラーが出る
* UIがスッキリ✨

### 戦略B：1項目に最大2件まで（バランス型）⚖️

* 「必須」＋「形式」みたいに関連が強いものだけ

### 戦略C：全部出す（上級者向け・業務フォームでたまに）📚

* ただし圧が強いので注意😇

この教材ではおすすめは **AかB** 😊👍

---

## 9) ミニ演習📝🎀（同じ失敗を“項目別”と“全体”で表現し分ける）

### 演習1：次の失敗を分類してね🏷️

1. メールが空
2. メール形式が変
3. パスワード8文字未満
4. パスワード確認が一致しない
5. 「登録」押したら通信エラー
6. すでに使われているメール（サーバで判明）

👉 それぞれ **fieldErrors / formError** のどっち？（両方はなるべく避ける✨）

### 演習2：やさしい文言にリライト💬✨

「Invalid input」「Required」「Error 0x000...」みたいな文を、
**女子大生の友だちに言う感じ**で直してみてね🥰🌸

---

## 10) AI活用テンプレ🤖✨（そのままコピペOK！）

* 「このフォーム（項目：email/password/passwordConfirm）の失敗ケースを、fieldErrors と formError に分けて列挙して😊」
* 「“責めない日本語”で、短くて分かりやすいエラーメッセージに直して！絵文字も少し入れて✨」
* 「このエラー文言、ユーザーが次に何をすればいいか分かる？改善案3つちょうだい🧭」
* 「アクセシビリティ的に aria-invalid / aria-describedby の付け方、落とし穴ある？チェックして✅」([MDN Web Docs][5])
* 「Zod v4 の z.flattenError の出力を FormProblems 型に変換する関数を書いて（型も丁寧に）🧾」([Zod][3])

---

## まとめ🎉

この章で一番大事なのはこれだよ👇✨

* エラーは **「項目別」と「全体」** に分ける🧺
* 表示は **近く＋上部要約** が強い🗺️([GOV.UK Design System][8])
* アクセシビリティは **aria-invalid＋aria-describedby** が基本セット♿([MDN Web Docs][5])
* バリデーション結果は **標準形（FormProblems）** に正規化して、UIをシンプルに保つ🧼✨

次の章（第22章）では、**HTTP失敗（通信 vs HTTPステータス）** を同じノリで「混ぜない」設計にしていくよ🌐🚦💕

[1]: https://design-system.service.gov.uk/components/error-message/ "Error message – GOV.UK Design System"
[2]: https://zod.dev/v4/changelog "Migration guide | Zod"
[3]: https://zod.dev/error-formatting "Formatting errors | Zod"
[4]: https://valibot.dev/api/flatten/?utm_source=chatgpt.com "flatten"
[5]: https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Attributes/aria-invalid?utm_source=chatgpt.com "ARIA: aria-invalid attribute - MDN Web Docs - Mozilla"
[6]: https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Attributes/aria-describedby?utm_source=chatgpt.com "ARIA: aria-describedby attribute - MDN Web Docs - Mozilla"
[7]: https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Attributes/aria-errormessage?utm_source=chatgpt.com "ARIA: aria-errormessage attribute - MDN Web Docs - Mozilla"
[8]: https://design-system.service.gov.uk/components/error-summary/ "Error summary – GOV.UK Design System"
