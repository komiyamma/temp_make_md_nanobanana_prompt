# 第06章：コンポーネント分割のルールを決める 📦✨

この章のゴールはシンプルです👇
**「コピペ地獄を防ぐための“置き場所ルール”を決めて、共通UI（Button / Input / Card）を作る」**です😆🧱

---

## 6-0 今日の完成イメージ 🏁

* `pages/`（ページ）と `components/`（部品）と `services/`（外部と話す）を分ける
* Tailwindのクラスが長くなりがちな **ボタン・入力・カード** を “共通部品化” してスッキリさせる✨🎽
* 後の章で **Firestore / Storage / AI（Firebase AI Logic）** を足していくときに、迷子にならない構造にする🧭

![react_study_006_01_folder_struct](./picture/react_study_006_01_folder_struct.png)

---

## 6-1 まず決める「4つの箱」ルール 🧺🧠

迷ったらこの4つに分類します👇

## ① pages（ページ）📄

* ルーティング（URL）と直結する “画面単位”
* **ページ固有の組み立て**をする場所（レイアウト＋部品を並べる）
* 例：`UsersPage.tsx` / `SettingsPage.tsx`

## ② components（部品）🧩

* 何度も使うUIを置く場所
* “見た目中心”で、できるだけ**外部通信はしない**（FirebaseやAI呼び出しはここに直書きしない）
* 例：`Button` / `Input` / `UserTable`

## ③ hooks（状態ロジック）🪝

* `useXxx` の “状態・手順” をまとめる場所
* 例：`useUserForm()` / `useAuthState()`
  （Reactの「propsで受け渡す」「状態を親に持ち上げる」感覚が大事になります🙂）([React][1])

## ④ services（外部と話す）🔌☁️

* Firebase / AI / 外部API など “外の世界” とやり取りする場所
* **Reactを使わない**（`useState`とかを書かない）
* ここにまとめると、UI側がスッキリして事故が減ります💥

![react_study_006_02_four_boxes](./picture/react_study_006_02_four_boxes.png)

> FirebaseのWeb SDKも「バージョン混在で壊れる」みたいな落とし穴があるので、外部系をまとめるのはかなり効きます🧯([Firebase][2])

---

## 6-2 おすすめフォルダ構成（まずはこれでOK）📁✨

（あとで増やしていいので、最初はこのくらいの粒度で👍）

```text
src/
  pages/
    DashboardPage.tsx
    UsersPage.tsx
    SettingsPage.tsx

  layouts/
    AppShell.tsx
    Sidebar.tsx
    TopBar.tsx

  components/
    ui/
      Button.tsx
      Input.tsx
      Card.tsx
      index.ts

  services/
    ai/
      aiClient.ts   // ここにAI呼び出しを寄せる（後の章で育てる）
    firebase/
      index.ts      // 後の章でSDK初期化を集約する予定

  lib/
    cn.ts           // className結合の小道具（任意）

  types/
    index.ts
```

---

## 6-3 迷った時の「置き場所フローチャート」🧭🤔

**Q1. URL（ルート）に対応する？**
→ Yes ✅：`pages/`
→ No ❌：次へ

**Q2. 見た目（UI）を再利用したい？**
→ Yes ✅：`components/`（とくに `components/ui`）
→ No ❌：次へ

**Q3. useState / useEffect を含む “手順や状態” を再利用したい？**
→ Yes ✅：`hooks/`
→ No ❌：次へ

**Q4. Firebase / AI / HTTP など “外部通信” が中心？**
→ Yes ✅：`services/`
→ No ❌：`lib/`（小道具） or `types/`（型）

---

## 6-4 手を動かす：共通UI（Button / Input / Card）を作る 🛠️🎨

## Step 1：フォルダを作る📁

* `src/components/ui`
* `src/layouts`
* `src/services/ai`
* `src/services/firebase`
* `src/lib`
* `src/types`

## Step 2：className結合ヘルパー（任意だけど便利）🧪

`src/lib/cn.ts`

```ts
export function cn(...values: Array<string | undefined | false | null>) {
  return values.filter(Boolean).join(" ");
}
```

## Step 3：Button（共通部品）🔘✨

`src/components/ui/Button.tsx`

```tsx
import type { ButtonHTMLAttributes } from "react";
import { cn } from "../../lib/cn";

type Variant = "primary" | "secondary" | "danger";

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: Variant;
  isLoading?: boolean;
};

const base =
  "inline-flex items-center justify-center rounded-md px-3 py-2 text-sm font-medium " +
  "transition focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-60 disabled:cursor-not-allowed";

const variants: Record<Variant, string> = {
  primary: "bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500",
  secondary: "bg-slate-200 text-slate-900 hover:bg-slate-300 focus:ring-slate-400",
  danger: "bg-red-600 text-white hover:bg-red-700 focus:ring-red-500",
};

export function Button({
  variant = "primary",
  className,
  isLoading,
  children,
  disabled,
  ...rest
}: Props) {
  return (
    <button
      className={cn(base, variants[variant], className)}
      disabled={disabled || isLoading}
      {...rest}
    >
      {isLoading ? "処理中…" : children}
    </button>
  );
}
```

ポイント👇

* `children` と `props` の受け渡しが基本動作です（Reactの基本）🙂([React][1])

![react_study_006_03_button_variants](./picture/react_study_006_03_button_variants.png)

## Step 4：Input（共通部品）⌨️✨

`src/components/ui/Input.tsx`

```tsx
import type { InputHTMLAttributes } from "react";
import { cn } from "../../lib/cn";

type Props = InputHTMLAttributes<HTMLInputElement> & {
  label?: string;
  error?: string;
};

export function Input({ label, error, className, ...rest }: Props) {
  return (
    <label className="block">
      {label && <div className="mb-1 text-sm font-medium text-slate-700">{label}</div>}
      <input
        className={cn(
          "w-full rounded-md border px-3 py-2 text-sm outline-none",
          "focus:ring-2 focus:ring-blue-500",
          error ? "border-red-500" : "border-slate-300",
          className
        )}
        {...rest}
      />
      {error && <div className="mt-1 text-xs text-red-600">{error}</div>}
    </label>
  );
}
```

![react_study_006_04_input_states](./picture/react_study_006_04_input_states.png)

## Step 5：Card（共通部品）🪪✨

`src/components/ui/Card.tsx`

```tsx
import type { ReactNode } from "react";
import { cn } from "../../lib/cn";

export function Card({ className, children }: { className?: string; children: ReactNode }) {
  return (
    <div className={cn("rounded-lg border border-slate-200 bg-white p-4 shadow-sm", className)}>
      {children}
    </div>
  );
}

export function CardTitle({ children }: { children: ReactNode }) {
  return <h2 className="mb-2 text-base font-semibold text-slate-900">{children}</h2>;
}

export function CardBody({ children }: { children: ReactNode }) {
  return <div className="text-sm text-slate-700">{children}</div>;
}
```

![react_study_006_05_card_structure](./picture/react_study_006_05_card_structure.png)

## Step 6：まとめてexport（使う側が楽になる）📦

`src/components/ui/index.ts`

```ts
export * from "./Button";
export * from "./Input";
export * from "./Card";
```

---

## 6-5 レイアウトを “layouts/” に移す（第5章の続き）🧱➡️📦

たとえば、今まで `App.tsx` にベタ書きしてた「サイドバー＋ヘッダー＋メイン枠」を
`src/layouts/AppShell.tsx` に移します🙂

```tsx
import type { ReactNode } from "react";

export function AppShell({ sidebar, topbar, children }: {
  sidebar: ReactNode;
  topbar: ReactNode;
  children: ReactNode;
}) {
  return (
    <div className="min-h-dvh bg-slate-50">
      <div className="flex">
        <aside className="w-64 border-r bg-white">{sidebar}</aside>
        <div className="flex-1">
          <header className="border-b bg-white">{topbar}</header>
          <main className="p-4">{children}</main>
        </div>
      </div>
    </div>
  );
}
```

こういう “組み立て部品” は `children` を受け取ると強いです💪
（ただし `Children` API を濫用すると壊れやすいので、まずは普通に `children` を受け取る感じでOKです🙂）([React][3])

---

## 6-6 services に「AIの入口」を用意しておく 🤖🚪

ここがこの章のちょい未来ポイントです✨
後の章で **Firebase AI Logic** を使って “文章整形ボタン” とかをやる予定なので、**呼び出し口を services 側に寄せる**クセを今から付けます👍

`src/services/ai/aiClient.ts`（今はダミーでOK）

```ts
export type NormalizeTextResult = {
  text: string;
};

export async function normalizeText(input: string): Promise<NormalizeTextResult> {
  // 第18章あたりで Firebase AI Logic（Gemini/Imagen）接続に差し替える予定✨
  // いまは“それっぽい戻り”にしてUIを先に作れるようにする
  return { text: input.trim() };
}
```

Firebase AI Logic は、Web/モバイルから **Gemini や Imagen** を呼ぶためのクライアントSDKや、App Checkなどの保護と組み合わせる前提で用意されています🛡️([Firebase][4])
あと地味に重要なんですが、**モデル名や提供状況は更新が入る**ので、公式の注意書き（例：一部モデルの提供終了日）を章を進めるたびに見るクセを付けると強いです🧠([Firebase][4])

---

## 6-7 仕上げ：import を楽にする（パス別名）🧭✨

相対パス `../../components/ui/Button` って増えると地味にストレスです😇
Vite は `resolve.alias` が使えます（**ファイルシステムへのaliasは絶対パス推奨**）([vitejs][5])

`vite.config.ts`（例：`@` を `src` に）

```ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
  },
});
```

これで `@/components/ui` みたいに書けます🎉

![react_study_006_06_path_alias](./picture/react_study_006_06_path_alias.png)
※ tsconfig の `paths` を Vite が解釈する機能もありますが、パフォーマンスコストの注意があるので、最初は alias 方式が無難です🙂([vitejs][6])

---

## 6-8 AI（Antigravity / Gemini CLI）でリファクタを加速する 🛸💻

## Antigravity の使いどころ（この章で超相性いい）🤝

* 「今の `src/` を見て、上の構成に移す作業」を**まるごと任せやすい**です
* Antigravity は “ミッション管理＋ブラウザ＋エージェント” 前提の開発プラットフォームとして紹介されています([Google Codelabs][7])

おすすめの投げ方（コピペ用）👇

* 「このプロジェクトを `pages/layouts/components/hooks/services` に整理して」
* 「Button/Input/Card を作って、既存画面のコピペ箇所を置換して」
* 「変更点を “ファイル単位の差分” で出して」
* 「動作確認チェックリストも作って」

## Gemini CLI の使いどころ（差分生成が便利）🧰✨

Gemini CLI はターミナルで使えるAIエージェントで、ReAct ループや MCP サーバー対応などが説明されています([Google Cloud Documentation][8])
おすすめは **“いきなり全部変更” じゃなくて、まず計画→差分→適用** の順です🙂

投げ方テンプレ👇

1. 「現状の `src/` 構造を読み取って、移動計画を出して」
2. 「次に、Button/Input/Card を追加する差分を生成して」
3. 「最後に、既存のコピペUIを置換する差分を生成して」
4. 「壊れやすい点（import / export / 循環参照）をチェックして」

---

## 6-9 ミニ課題 🎯✨

✅ **「同じ見た目のボタン」を3箇所見つけて**、全部 `Button` に置き換える
✅ 置換したら、`variant="secondary"` と `variant="danger"` も最低1回使う
✅ できたら `Input` を1個導入して、`error` を表示してみる（わざとエラー文字を入れてOK）😆

---

## 6-10 チェック✅（ここまで出来たら勝ち！）🏆

* [ ] `pages/` と `components/` が分かれてる
* [ ] `Button / Input / Card` が `components/ui` にある
* [ ] `components/ui/index.ts` からまとめてimportできる
* [ ] 同じUIのコピペが減った（少なくともボタンは共通化できた）
* [ ] `services/ai` の “入口ファイル” ができてる（中身はダミーでOK）([Firebase][4])

---

## 6-11 よくあるつまずき 😵‍💫🧯

* **export/import が噛み合わない**
  → `export function Button` なのに `import Button` してる、みたいなやつ。
  → 迷ったら `components/ui/index.ts` に寄せて、そこから import すると安定👍

* **分割しすぎて逆に迷子**
  → “同じUIを2回以上” になったら共通化、くらいの温度感でOK🔥
  → 早すぎる抽象化は罠です🪤😇

* **services に React を持ち込む**
  → `services/` は “純粋な関数” っぽくしておくと後で強いです💪

---

次の第7章は、UIに「loading / error / data」の三兄弟を入れて、**“待ち時間でも気持ちいい管理画面”**にしていきます🔁✨
第6章がキレイにできるほど、第7章以降がめちゃ楽になりますよ〜😆🚀

[1]: https://react.dev/learn/passing-props-to-a-component "Passing Props to a Component – React"
[2]: https://firebase.google.com/docs/web/best-practices "Firebase JavaScript SDK best practices  |  Firebase for web platforms"
[3]: https://react.dev/reference/react/Children "Children – React"
[4]: https://firebase.google.com/docs/ai-logic "Gemini API using Firebase AI Logic  |  Firebase AI Logic"
[5]: https://vite.dev/config/shared-options "Shared Options | Vite"
[6]: https://ja.vite.dev/guide/features "特徴 | Vite"
[7]: https://codelabs.developers.google.com/getting-started-google-antigravity "Getting Started with Google Antigravity  |  Google Codelabs"
[8]: https://docs.cloud.google.com/gemini/docs/codeassist/gemini-cli "Gemini CLI  |  Gemini for Google Cloud  |  Google Cloud Documentation"
