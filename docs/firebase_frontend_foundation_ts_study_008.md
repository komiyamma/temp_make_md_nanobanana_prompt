# 第08章：フォーム入力とバリデーション 📝🚦（プロフィール編集フォームを作る）

この章のゴールはコレです👇✨
**「入力 → 検証 → エラー表示 → 保存」**が、気持ちよく一通りできるフォームを完成させます😆

![Form Validation Flow](./picture/firebase_frontend_foundation_ts_study_008_form_validation_flow.png)

---

## 今日作る完成物 🧩✨

**プロフィール編集フォーム**（管理画面っぽいやつ）を作ります👇

* 表示名（必須・文字数）🙂
* メール（形式チェック）✉️
* 自己紹介（最大文字数）📝
* WebサイトURL（URL形式・任意）🌍
* 保存ボタン（保存中は無効・スピナー）⏳
* エラーは「どこがダメか」ピンポイント表示🚨

さらにオマケで👇

* **AIで自己紹介を読みやすく整形ボタン**🤖✨（フォームのUXが一気に“それっぽく”なります）

---

## まず大事な考え方（超シンプル）🧠

フォームは基本この3点セットです👇

1. **入力を集める**（どの入力欄に何が入った？）🧺
2. **ルールで検証する**（必須？長さ？形式？）📏
3. **人間に分かる形で伝える**（エラー文・色・場所）🗣️

そして、めちゃ大事⚠️
**クライアントのバリデーションは“親切機能”で、最終防衛線じゃない**です🛡️
（最終的な安全はFirestoreのRulesやサーバー側で守るイメージ）

---

## 今回のおすすめ構成（2026の王道）🏆

![Tech Stack](./picture/firebase_frontend_foundation_ts_study_008_tech_stack.png)

* フォーム管理：**React Hook Form**（v7系が安定）📦 ([npm][1])
* ルール定義：**Zod**（最新 4.3.6）🧩 ([npm][2])
* 橋渡し：**@hookform/resolvers**（最新 5.2.2 / Zod v4対応）🌉 ([npm][3])

---

## 手を動かす 1️⃣：必要パッケージを入れる 📦

```bash
npm i react-hook-form zod @hookform/resolvers
```

---

## 手を動かす 2️⃣：Zodで「入力ルール」を1枚の紙にする 📄✨

`src/features/profile/profileSchema.ts` を作るイメージです👇

```ts
// src/features/profile/profileSchema.ts
![Zod Schema](./picture/firebase_frontend_foundation_ts_study_008_zod_schema.png)
import { z } from "zod";

export const profileSchema = z.object({
  displayName: z
    .string()
    .min(1, "表示名は必須です🙂")
    .max(30, "表示名は30文字までです🙏"),

  email: z.string().email("メールアドレスの形が変です✉️"),

  bio: z
    .string()
    .max(200, "自己紹介は200文字までにしてね📝")
    .optional()
    .or(z.literal("")),

  website: z
    .string()
    .url("URLの形にしてね🌍（https://〜）")
    .optional()
    .or(z.literal("")),
});

export type ProfileForm = z.infer<typeof profileSchema>;
```

ポイント🎯

* **型（TypeScript）とルール（バリデーション）を同じ場所に置ける**のが気持ちいいです😆
* `optional().or("")` にしておくと「未入力」と「空文字」を許せます（地味に便利）✨

---

## 手を動かす 3️⃣：React Hook FormにZodをつなぐ 🔌

![Form UI State](./picture/firebase_frontend_foundation_ts_study_008_form_ui_state.png)

`src/features/profile/ProfileEditPage.tsx` みたいな感じ👇
（UIはTailwindで最低限それっぽくしてます🎽）

```tsx
import { useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import type { ProfileForm } from "./profileSchema";
import { profileSchema } from "./profileSchema";

type Props = {
  initial?: Partial<ProfileForm>;
  onSave?: (data: ProfileForm) => Promise<void>;
};

export function ProfileEditPage({ initial, onSave }: Props) {
  const [savedMessage, setSavedMessage] = useState<string>("");

  const defaultValues = useMemo(
    () => ({
      displayName: initial?.displayName ?? "",
      email: initial?.email ?? "",
      bio: initial?.bio ?? "",
      website: initial?.website ?? "",
    }),
    [initial]
  );

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting, isDirty, isValid },
  } = useForm<ProfileForm>({
    resolver: zodResolver(profileSchema),
    defaultValues,
    mode: "onBlur",          // 目を離した時にチェック（初心者に優しい）
    reValidateMode: "onChange",
  });

  const submit = handleSubmit(async (data) => {
    setSavedMessage("");
    await onSave?.(data);
    setSavedMessage("保存しました✅");
  });

  return (
    <div className="max-w-xl">
      <h1 className="text-xl font-bold mb-4">プロフィール編集 📝</h1>

      <form onSubmit={submit} className="space-y-4">
        <Field
          label="表示名"
          required
          error={errors.displayName?.message}
        >
          <input
            className={inputClass(!!errors.displayName)}
            {...register("displayName")}
            placeholder="例：こみやんま"
            aria-invalid={!!errors.displayName}
          />
        </Field>

        <Field label="メール" required error={errors.email?.message}>
          <input
            className={inputClass(!!errors.email)}
            {...register("email")}
            placeholder="example@mail.com"
            inputMode="email"
            aria-invalid={!!errors.email}
          />
        </Field>

        <Field label="自己紹介" error={errors.bio?.message}>
          <textarea
            className={textareaClass(!!errors.bio)}
            {...register("bio")}
            placeholder="200文字まで📝"
            rows={4}
            aria-invalid={!!errors.bio}
          />
        </Field>

        <Field label="Webサイト" error={errors.website?.message}>
          <input
            className={inputClass(!!errors.website)}
            {...register("website")}
            placeholder="https://example.com"
            aria-invalid={!!errors.website}
          />
        </Field>

        <div className="flex items-center gap-3">
          <button
            type="submit"
            className="px-4 py-2 rounded-lg bg-black text-white disabled:opacity-50"
            disabled={isSubmitting || !isDirty || !isValid}
          >
            {isSubmitting ? "保存中..." : "保存"}
          </button>

          {savedMessage && (
            <span className="text-sm text-green-700">{savedMessage}</span>
          )}
        </div>

        <p className="text-xs text-gray-500">
          ヒント💡：保存ボタンは「変更あり」かつ「エラーなし」の時だけ押せるようにしてます🙂
        </p>
      </form>
    </div>
  );
}

function inputClass(isError: boolean) {
  return [
    "w-full px-3 py-2 rounded-lg border outline-none",
    isError ? "border-red-500" : "border-gray-300",
    "focus:ring-2 focus:ring-black/20",
  ].join(" ");
}

function textareaClass(isError: boolean) {
  return [
    "w-full px-3 py-2 rounded-lg border outline-none",
    isError ? "border-red-500" : "border-gray-300",
    "focus:ring-2 focus:ring-black/20",
  ].join(" ");
}

function Field({
  label,
  required,
  error,
  children,
}: {
  label: string;
  required?: boolean;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-1">
      <label className="text-sm font-medium">
        {label} {required && <span className="text-red-600">*</span>}
      </label>
      {children}
      {error && <p className="text-sm text-red-600">{error}</p>}
    </div>
  );
}
```

![Button Logic](./picture/firebase_frontend_foundation_ts_study_008_button_logic.png)

ここで覚えることは少なくてOKです🙂✨

* `resolver: zodResolver(profileSchema)` ← **Zodのルールをフォームに接続**
* `errors.xxx?.message` ← **エラー文をそのまま表示**
* `isSubmitting / isDirty / isValid` ← **気持ちいいUXの材料**

---

## つまづきポイント集 😵‍💫➡️😆

![Validation Modes](./picture/firebase_frontend_foundation_ts_study_008_validation_modes.png)

## ① エラーが出ないんだけど？

* `mode: "onBlur"` だと **入力中は出ない**です🙂
  → いったん別の場所をクリック（フォーカス外す）すると出ます👆

## ② `isValid` が true にならない…

* `useForm` の初期設定だと `isValid` 更新が期待通り動かないことがあります
  → 今回みたいに `mode` / `reValidateMode` をちゃんと指定するのが安定です✅

## ③ Tailwindで入力がダサい…🎽

* `@tailwindcss/forms` を使うとベースが整いやすいです✨
  v4系ではCSSに `@plugin "@tailwindcss/forms";` を入れる流れです。([GitHub][4])
  （ただし今の実装でも最低限はOK！この章では必須じゃないよ🙂）

---

## ミニ課題 🎯（できたら強い！）

## ミニ課題A：パスワード変更（確認用フィールド付き）🔐

* `password` と `passwordConfirm` を追加
* Zodで「一致してる？」チェック（`superRefine`）🧠

## ミニ課題B：URLは `https://` 強制にする 🌍

* `http://` ならエラーにする（または自動補正）
* “親切バリデーション”の練習にちょうどいいです🙂

---

## チェック✅（この章の合格ライン）

* 必須・文字数・形式チェックが入ってる🙂
* エラーが「どこがダメか」分かる場所に出る👀
* 保存中にボタン連打できない⛔
* 変更してないのに保存できないようになってる（`isDirty`）🧠
* エラー0なら保存できる（`isValid`）✅

---

## ここからAIをフォームに混ぜる（面白ゾーン）🤖✨

「自己紹介」って、だいたい書きづらいんですよね😂
そこで **“AIで読みやすく”ボタン** を付けると、一気に管理画面っぽくなります📊✨

## 例：AIで自己紹介を整形して、入力欄に反映する🪄

![AI Bio Rewrite](./picture/firebase_frontend_foundation_ts_study_008_ai_bio_rewrite.png)

Firebase AI Logic（Web）だとこんな感じで呼べます👇 ([Firebase][5])

```ts
import { getAI, getGenerativeModel, GoogleAIBackend } from "firebase/ai";
import { initializeApp } from "firebase/app";

// 既に firebaseApp があるならそれを使ってOK
const firebaseApp = initializeApp({ /* your config */ });

const ai = getAI(firebaseApp, { backend: new GoogleAIBackend() });
const model = getGenerativeModel(ai, { model: "gemini-2.5-flash" });

export async function rewriteBio(original: string) {
  const prompt =
    `次の自己紹介文を、丁寧で読みやすい日本語に整形して。` +
    `\n\n---\n${original}\n---\n` +
    `\n条件：200文字以内、箇条書きNG、敬語は軽め🙂`;

  const result = await model.generateContent(prompt);
  return result.response.text();
}
```

フォーム側では👇みたいに

* AI実行中はボタン無効
* 結果を**いきなり保存せず**、入力欄へ反映（ユーザーが確認できる）
  が安心です🙂✨

> ちなみにFirebase AI Logicのガイドでは、**本番ではRemote Configでモデル名を切り替えられるようにする**のが強く推奨されています（将来のモデル変更に耐えるため）🧠([Firebase][5])

---

## AIで開発を速くする小技（Gemini CLI / Antigravity）🛸💨

* Antigravityは「エージェントが計画→実装→検証」まで回せる“Mission Control”型の開発環境、という位置づけです🧑‍✈️([Google Codelabs][6])
* Gemini CLIは Cloud Shell だと追加設定なしで使える案内があります☁️([Google Cloud Documentation][7])

フォーム開発で便利なのは例えば👇

* フィールド一覧を書いて「Zodスキーマ案を作って」
* 「エラーメッセージをユーザー向けに日本語で統一して」
* 「このフォームのテスト観点を10個出して」
  みたいな“下準備”をAIにやらせると爆速です⚡

---

## 次の章（第9章）につながる伏線 🎨✨

第8章でフォームができたら、次は👇が気になってくるはずです🙂

* 「ボタンの見た目がページごとに違う…」😵‍💫
* 「余白とか角丸とか、統一ルール作りたい」📐

なので次の第9章は **UIの一貫性** がめちゃハマります👍✨

---

必要なら、この第8章の続きとして👇も一気に書けますよ😆

* Firestoreに実際に `onSave` で保存する版（サービス層 `services/profile.ts` まで含める）🗃️
* AI整形の結果を「差分表示してOKなら反映」みたいな管理画面っぽいUI（モーダル付き）🪟✨

[1]: https://www.npmjs.com/package/react-hook-form?utm_source=chatgpt.com "react-hook-form"
[2]: https://www.npmjs.com/package/zod?utm_source=chatgpt.com "Zod"
[3]: https://www.npmjs.com/package/%40hookform/resolvers?utm_source=chatgpt.com "hookform/resolvers"
[4]: https://github.com/tailwindlabs/tailwindcss-forms?utm_source=chatgpt.com "tailwindlabs/tailwindcss-forms"
[5]: https://firebase.google.com/docs/ai-logic/get-started "Get started with the Gemini API using the Firebase AI Logic SDKs  |  Firebase AI Logic"
[6]: https://codelabs.developers.google.com/getting-started-google-antigravity?utm_source=chatgpt.com "Getting Started with Google Antigravity"
[7]: https://docs.cloud.google.com/gemini/docs/codeassist/gemini-cli?utm_source=chatgpt.com "Gemini CLI | Gemini for Google Cloud"
