# 第09章：UIに一貫性を出すコツ 🎨✨（色・余白・角丸・影を“固定ルール”にする）

この章のゴールはシンプルです🙂
**「どの画面を見ても同じアプリに見える」**ように、**見た目のルールを決めて、コードでブレにくくする**ことです💪✨
（Firestoreの一覧、Storageのアップロード、Functionsの結果表示、AIの出力…全部ここが効いてきます🔥）

---

## 0) まず結論：一貫性は “3点セット” で作る 🧰✨

![Design Pillars](./picture/firebase_frontend_foundation_ts_study_009_design_pillars.png)

1. **デザイントークン**（色/余白/角丸/影/文字）を固定する🎯
2. **共通コンポーネント**（Button/Input/Card…）に寄せる🧱
3. **状態の見た目**（hover/focus/disabled/loading/error）を統一する🚦

Tailwind v4 は、デザイントークンを **`@theme` でCSS変数として宣言**して、そこからユーティリティ（`bg-*` とか）を生やせます🌱
この「トークン→クラス」構造が、一貫性づくりと相性バツグンです✨ ([Tailwind CSS][1])

---

## 1) “UIガイド（見た目ルール表）” を作る 📄🖊️

まずは **アプリ内ルール**を短く決めます。おすすめはこの程度👇（5分でOK）

* **色🎨**：Primary / Secondary / Danger / Background / Text
* **余白📏**：基本は `p-4`、カード間は `gap-4` みたいに固定
* **角丸🟠**：カードは `rounded-xl`、入力は `rounded-lg`、ボタンは `rounded-lg`
* **影🌫️**：カードは `shadow-sm`（濃い影は禁止🙅‍♂️）
* **文字🔤**：見出しは `text-lg font-semibold`、本文は `text-sm` など固定

ここで大事なのは「おしゃれ」より **“迷わない”** です😆✨
迷わない＝実装スピードが上がる＝Firebase繋ぎが早くなる🚀

---

## 2) Tailwind v4 の `@theme` で “色と角丸と影” を1か所に集約 🧩✨

![Tailwind Theme](./picture/firebase_frontend_foundation_ts_study_009_tailwind_theme.png)

Tailwind v4 では、`@theme` の **namespace**（`--color-*`, `--radius-*`, `--shadow-*` など）を使うと、それに対応したクラスが使えるようになります💡 ([Tailwind CSS][1])

例：`--color-primary` を作ると `bg-primary` / `text-primary` が使える感じです🎨

## ✅ まずは “シンプル版” （最短で統一したい人向け）

```css
/* src/styles/tokens.css (例) */
@import "tailwindcss";

/* ここで「アプリの色」を決め打ち（あとで調整OK） */
@theme {
  /* 色（semanticに命名すると迷いにくい） */
  --color-background: #0b1020;
  --color-surface: #111a33;
  --color-text: #e8eefc;

  --color-primary: #4f7cff;
  --color-primary-hover: #3f6df6;

  --color-secondary: #2a355a;
  --color-secondary-hover: #243052;

  --color-danger: #ff4d4d;
  --color-danger-hover: #f13f3f;

  /* 角丸・影（Tailwind v4 のnamespace） */
  --radius-card: 1rem;     /* rounded-card */
  --radius-control: 0.75rem; /* rounded-control */
  --shadow-card: 0 1px 2px rgb(0 0 0 / 0.25); /* shadow-card */
}
```

* `bg-background` / `bg-surface` / `text-text` みたいに書けます🎉
* 角丸は `rounded-card`、影は `shadow-card` が使えます（`--radius-*`, `--shadow-*` の仕組み） ([Tailwind CSS][1])
* v4 はトークンが **CSS変数としても扱える**ので、必要なら `var(--color-primary)` 的な参照も可能です🧠 ([Tailwind CSS][1])

> 💡「ダークモードもやりたい！」は、次の章でやるUI基盤（状態やガード）を固めてからでOK👌
> 先に “統一感” を勝たせるのが正解です✨

---

## 3) “ボタン3兄弟” を共通コンポーネントで固定する 🔘🔘🔘

![Button Variants](./picture/firebase_frontend_foundation_ts_study_009_button_variants.png)

この章のミニ課題にも直結します🎯
「主（Primary）/ 副（Secondary）/ 危険（Danger）」の3種だけを、**Buttonコンポーネントに閉じ込めます**📦✨

```tsx
// src/components/ui/Button.tsx
import type { ButtonHTMLAttributes } from "react";

type Variant = "primary" | "secondary" | "danger";

function cn(...xs: Array<string | undefined | false>) {
  return xs.filter(Boolean).join(" ");
}

const base =
  "inline-flex items-center justify-center gap-2 " +
  "px-4 py-2 text-sm font-medium " +
  "rounded-control " +
  "transition " +
  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary " +
  "disabled:opacity-50 disabled:pointer-events-none";

const variants: Record<Variant, string> = {
  primary: "bg-primary text-white hover:bg-primary-hover",
  secondary: "bg-secondary text-text hover:bg-secondary-hover",
  danger: "bg-danger text-white hover:bg-danger-hover",
};

export function Button({
  variant = "primary",
  className,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant }) {
  return <button {...props} className={cn(base, variants[variant], className)} />;
}
```

## ✅ これで何が嬉しい？😆

* 画面ごとの「ボタンの形違う問題」消滅💥
* `loading` や `disabled` の見た目を **Button側で一発管理**できる
* Firebaseの処理（Firestore保存中、Storageアップロード中、Functions待ち、AI生成中）でブレない🚀

---

## 4) “状態の見た目” を統一する（ここがUIの格を上げる）🚦✨

![UI States](./picture/firebase_frontend_foundation_ts_study_009_ui_states.png)

最低限この4つは **全コンポーネントで統一**しましょ👇

* **hover**：色がちょい変わる
* **focus**：キーボード操作でも見失わない（`focus-visible:ring-2`）
* **disabled**：押せないのが一目で分かる（薄くする＋クリック無効）
* **loading**：UIが固まったように見えない（スピナー＋押せない）

> 🔥 Firebase AIを入れる時、**AI生成中**がいちばんユーザー不安になります

![AI Loading State UI](./picture/firebase_frontend_foundation_ts_study_009_ai_loading_state.png)
> だから「AI中は必ずloading表示する」ルールをここで決めると勝ちです🤖✨
> クライアントからGemini/Imagenを呼ぶ場合は、FirebaseのクライアントSDKでAI機能を組み込みつつ、App Checkやレート制限で守る設計が前提になります🛡️ ([Firebase][2])

---

## 5) AIで “UIのブレ探し” を一気にやる 🛸🔍（Antigravity / Gemini CLI）

## Antigravity（エージェントIDE）でできること 🧠✨

![Antigravity Check](./picture/firebase_frontend_foundation_ts_study_009_antigravity_check.png)

Antigravityは、複数エージェントを“Mission Control”で動かして、調査→修正→検証まで寄せられる設計です🛰️ ([Google Codelabs][3])
この章だと、例えばこんな依頼が強いです👇

* 「`rounded-*` と `shadow-*` がバラついてる箇所を全部リスト化して、統一案を出して」
* 「ボタンっぽい要素が `button` じゃない箇所を探して、アクセシビリティ含め改善案を出して」

## Gemini CLI（ターミナルAI）でできること ⌨️🤖

Gemini CLIは、ターミナル上で“考えて→実行する（ReAct）”タイプのオープンソースAIエージェントです🧠🔁 ([Google Cloud Documentation][4])

* 「`bg-blue-*` を使ってるところを `bg-primary` に寄せるPR差分を作って」
* 「UIガイドに反してるclassNameだけ抽出して」

みたいな“地味だけど面倒”を削れます💪✨
（ただし **差分レビューは必須**ね！AIは勢いで壊すことある😂）

---

## ミニ課題 🎯：UIガイドページを作って、3種ボタンを並べる 📚✨

![UI Guide Page](./picture/firebase_frontend_foundation_ts_study_009_ui_guide_page.png)

1. `/ui-guide` ページを作る🧭
2. 背景＝`bg-background`、カード＝`bg-surface rounded-card shadow-card` に固定📌
3. `Button` を **Primary / Secondary / Danger** の3つ並べる🔘🔘🔘
4. `disabled` と `loading` 状態も表示して「見た目のルール」を完成させる🚦

---

## チェック✅（ここ通れば“統一感”クリア！）

* ボタンの角丸・高さ・文字サイズが、全ページ同じ？🔘
* フォーカスリング（キーボード操作）で迷子にならない？⌨️
* 保存中 / 生成中 / 読み込み中 が “無言” になってない？😵‍💫
* Danger（削除）だけは、どの画面でも同じ赤ルール？🟥

---

## つまづきポイント集 🧯🙂

* **Q. 画面ごとに `text-sm` と `text-base` が混ざる…**
  → 見出し/本文/補足の3階層だけに決めて、共通コンポーネント（`PageTitle` とか）に寄せる👌

* **Q. `@theme` って :root と何が違うの？**
  → `@theme` は「クラスを増やすための宣言」でもあるのが大きいです✨（色・余白・角丸などのnamespaceがクラスAPIに直結） ([Tailwind CSS][1])

* **Q. 参照したい変数が別の変数参照になって困る…**
  → v4は `@theme inline` が用意されてて、変数参照を“展開した形”で扱える設計になってます🧠 ([Tailwind CSS][1])
  （shadcn/uiのTailwind v4手順も、この考え方で説明されてます） ([ui.shadcn.com][5])

---

## おまけ：この章の “今どき感” メモ 📝✨（2026/02/16時点）

* Reactのドキュメント上の最新メジャーは **19.2** です📌 ([react.dev][6])
* Tailwind v4 は **CSS-first**（`@theme` でトークン管理）に大きく寄ったのがポイントです🎽 ([Tailwind CSS][7])
* shadcn/ui も **Tailwind v4 + React 19** 対応を明言していて、`@theme inline` の話まで含めて手順化されています🧩 ([ui.shadcn.com][5])

---

次の章（第10章）に行くと、Firebase初期化やサービスの入口を1か所にまとめて「UIとデータ」を結線し始めます🔌🔥
その前にこの第9章で、**見た目の軸**を作っておくと、後がめちゃラクです😆✨

参考（最近の動き・読み物）

* [theverge.com](https://www.theverge.com/news/822833/google-antigravity-ide-coding-agent-gemini-3-pro?utm_source=chatgpt.com)
* [theverge.com](https://www.theverge.com/news/692517/google-gemini-cli-ai-agent-dev-terminal?utm_source=chatgpt.com)

[1]: https://tailwindcss.com/docs/theme "Theme variables - Core concepts - Tailwind CSS"
[2]: https://firebase.google.com/docs/ai-logic "Gemini API using Firebase AI Logic  |  Firebase AI Logic"
[3]: https://codelabs.developers.google.com/getting-started-google-antigravity "Getting Started with Google Antigravity  |  Google Codelabs"
[4]: https://docs.cloud.google.com/gemini/docs/codeassist/gemini-cli "Gemini CLI  |  Gemini for Google Cloud  |  Google Cloud Documentation"
[5]: https://ui.shadcn.com/docs/tailwind-v4 "Tailwind v4 - shadcn/ui"
[6]: https://react.dev/versions "React Versions – React"
[7]: https://tailwindcss.com/blog/tailwindcss-v4 "Tailwind CSS v4.0 - Tailwind CSS"
