# 第03章：Tailwindで最低限きれいにする ✨🎽

この章のゴールはシンプルです👇😆
**「見た目が“管理画面っぽい”ダッシュボード（カード3枚）」を、Tailwindだけでサクッと作れる**ようになります📊✨

---

## 3-0 今日つくる完成イメージ 🏁

* 画面の背景がうっすらグレー 🩶
* 中央にコンテンツ幅（読みやすい）📏
* 角丸＋影＋境界線の“カード”が3枚 🧱✨
* 文字サイズと余白が整っていて「それっぽい」😎

---

## 3-1 Tailwindの考え方（超ざっくり）🧠✨

Tailwindは「CSSをゴリゴリ書く」より、**クラス名を組み合わせてUIを組む**方式です🧩
しかも、使ったクラスだけを拾ってCSSを生成するので、最終的なCSSがムダに膨らみにくいのが強みです⚡（仕組みとして“ソースをスキャンして必要な分だけ生成”します）([tailwindcss.com][1])

> 例）`p-6`（余白）＋`rounded-xl`（角丸）＋`shadow-sm`（影）…みたいに、レゴ感覚で積んでいきます🧱🧱🧱

---

## 3-2 導入手順（Tailwind v4.1 / Vite）🛠️⚡

Tailwind公式の「Viteプラグイン」手順がいちばんスムーズです✅([tailwindcss.com][2])

## (1) パッケージを入れる 📦

プロジェクト直下で👇

```bash
npm install tailwindcss @tailwindcss/vite
```

（この2つを入れるのが公式手順です）([tailwindcss.com][2])

## (2) ViteにTailwindプラグインを足す 🔌

`vite.config.ts` をこうします👇（すでにReactプラグインがある想定）

```ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
});
```

`@tailwindcss/vite` を plugins に入れるのがポイントです✅([tailwindcss.com][2])

## (3) CSSでTailwindを読み込む 🎽

たとえば `src/index.css`（または `src/style.css`）に👇

```css
@import "tailwindcss";
```

これがv4系の“最短ルート”です✅([tailwindcss.com][2])

## (4) CSSをアプリに読み込む（忘れがち）🧯

`src/main.tsx` に `index.css` が import されてるか確認👀

```ts
import "./index.css";
```

> ここが抜けてると、**Tailwindを入れたのに何も効かない**が起きます😭

## (5) 起動して確認 🚀

```bash
npm run dev
```

公式もこの流れ（install → plugin → import → dev）になってます✅([tailwindcss.com][2])

---

## 3-3 “最低限きれい”の黄金ルール（まずこれだけ）✨📐

「デザイン苦手…😵」でも大丈夫。まずはこの4点だけ守ると一気に“それっぽく”なります👇😆

1. **余白はケチらない**（`p-6` / `gap-6` など）🫶
2. **文字サイズに段差をつける**（タイトル大・説明小）🔠
3. **背景 → カード → 中身** の順で作る 🧱
4. **角丸＋薄い境界線＋控えめ影** でUIが締まる ✨

---

## 3-4 手を動かす：カード3枚ダッシュボードを作る 📊🛠️

`src/App.tsx` を、いったんこうしてみてください👇

```tsx
type StatCardProps = {
  title: string;
  value: string;
  hint?: string;
};

function StatCard({ title, value, hint }: StatCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <div className="text-sm font-medium text-gray-600">{title}</div>
      <div className="mt-2 text-3xl font-semibold tracking-tight text-gray-900">
        {value}
      </div>
      {hint ? <div className="mt-2 text-sm text-gray-500">{hint}</div> : null}
    </div>
  );
}

export default function App() {
  return (
    <div className="min-h-dvh bg-gray-50">
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <div className="text-lg font-semibold text-gray-900">
            Mini Admin Dashboard
          </div>
          <button className="rounded-lg bg-gray-900 px-3 py-2 text-sm font-medium text-white hover:bg-gray-800">
            新規作成
          </button>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-6 py-8">
        <h1 className="text-2xl font-semibold text-gray-900">
          ダッシュボード
        </h1>
        <p className="mt-2 text-sm text-gray-600">
          余白・文字・カードだけで“管理画面っぽさ”を作る練習🎽✨
        </p>

        <div className="mt-6 grid gap-6 md:grid-cols-3">
          <StatCard title="ユーザー数" value="1,248" hint="前日比 +12" />
          <StatCard title="売上" value="¥98,300" hint="今月の累計" />
          <StatCard title="エラー" value="0" hint="直近24時間" />
        </div>
      </main>
    </div>
  );
}
```

✅ ここで見てほしいポイントはこれ👇

* 背景：`bg-gray-50` 🩶
* コンテンツ幅：`max-w-5xl` ＋ `mx-auto` 📏
* カード：`rounded-xl border shadow-sm bg-white p-6` 🧱✨
* 3列：`grid gap-6 md:grid-cols-3` 📊

---

## 3-5 つまずきポイント集（あるある）🧯😇

## A) 「何も効かない」😱

チェック順はこれ👇

* `vite.config.ts` に `tailwindcss()` 入ってる？([tailwindcss.com][2])
* CSSに `@import "tailwindcss";` 書いた？([tailwindcss.com][2])
* `main.tsx` でそのCSS importしてる？
* 変更後に dev サーバ再起動した？（たまに必要）🔁

## B) 「クラスを動的に組んだら効かない」🤯

Tailwindはソースを“テキストとして”見てクラスを拾うので、
`bg-${color}-600` みたいな **文字列合成は基本ダメ**です🙅‍♂️([tailwindcss.com][1])

代わりに👇みたいに **静的な候補をマップ**にしましょう✅([tailwindcss.com][1])

```ts
const colorVariants: Record<string, string> = {
  blue: "bg-blue-600 hover:bg-blue-500 text-white",
  red: "bg-red-600 hover:bg-red-500 text-white",
};
```

---

## 3-6 ミニ課題 🎯✨「カード3枚」を“ちゃんと管理画面”に寄せる

次を追加して、UIをもう一段それっぽくしてください😆

* カードに **小さなアイコン置き場**（右上に丸背景）🟦
* 数字に **単位**（人 / 件 / ¥）をつける 💴
* `hover:shadow-md` を足して“触れる感”🖱️✨

ヒント👇（カードの外枠だけ例）

```tsx
<div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm hover:shadow-md transition-shadow">
  ...
</div>
```

---

## 3-7 AIで“見た目調整”を爆速にする（安全な使い方）🤖✨

ここは「デザイン苦手」をAIでカバーするコーナーです😆

## ① Antigravity / Gemini CLI に“お願いの型”を渡す 🧠📝

Antigravityはエージェントで計画→実装→検証まで回せる前提の開発プラットフォームで、Web閲覧も含めて支援できます🛸（プレビューでWindows対応の案内もあります）([Google Codelabs][3])
さらに、Firebase側は **Firebase MCP server** を用意していて、Antigravity や Gemini CLI などのMCPクライアントからFirebase操作を支援できることが明記されています🔌([Firebase][4])

たとえば、こんな依頼が強いです👇

* 「この画面を“管理画面っぽく”したい。**余白・文字サイズ・色のバランスだけ**直して。Tailwindのクラスだけで」🎽
* 「カードを3パターン提案して。**アクセシビリティ（コントラスト）も気にして**」👀
* 「差分を小さくして、`App.tsx` だけ変更で」🧩

## ② 将来の“AIボタン”は Firebase AI Logic が安全ルート 🔥🤖

後の章でやる「AI整形ボタン」は、ブラウザから直接Gemini/Imagenを叩くなら **Firebase AI Logic のWeb SDK**を使う設計がきれいです。
クライアント向けSDKで、App Check などと組み合わせて保護しやすいこと、キーをコードに埋めない設計にできることが説明されています🔐([Firebase][5])

---

## 3-8 チェック ✅（ここまでできたら勝ち🎉）

* [ ] 背景 → コンテンツ幅 → カード の順で組めた？🧱
* [ ] `p-6 / gap-6` で余白が気持ちいい？📐
* [ ] `text-2xl` と `text-sm` で文字に段差がある？🔠
* [ ] カードが **3枚** で、`md:grid-cols-3` で横並びになる？📊
* [ ] “効かない”ときの原因を自分で潰せる？🧯

---

次の章（ルーティング）に行くと、このダッシュボードが `/dashboard` になって、`/users` や `/settings` に分割されて一気にアプリっぽくなります🧭✨

[1]: https://tailwindcss.com/docs/detecting-classes-in-source-files "Detecting classes in source files - Core concepts - Tailwind CSS"
[2]: https://tailwindcss.com/docs "Installing Tailwind CSS with Vite - Tailwind CSS"
[3]: https://codelabs.developers.google.com/getting-started-google-antigravity "Getting Started with Google Antigravity  |  Google Codelabs"
[4]: https://firebase.google.com/docs/ai-assistance/mcp-server "Firebase MCP server  |  Develop with AI assistance"
[5]: https://firebase.google.com/docs/ai-logic "Gemini API using Firebase AI Logic  |  Firebase AI Logic"
