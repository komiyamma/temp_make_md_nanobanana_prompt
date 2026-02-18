# 第02章：プロジェクト雛形を作る ⚡🧱（Vite × React × TypeScript）

この章では「まず動く！」を最速で作ります😆✨
React+TSの雛形を作って、開発サーバーを起動して、編集が即反映（ホットリロード）されるところまでいきます🔥

---

## 1) まずは超ざっくり理解（読む📖）🧠✨

**Reactのコンポーネント**＝「画面の部品」🧩
ボタン、カード、ヘッダー…全部コンポーネントとして分けられます。

**状態（state）**＝「画面が覚えてる値」🧠
たとえば「ログイン中か」「読み込み中か」「入力フォームの中身」みたいなやつです。
状態が変わると、Reactがいい感じに画面を更新します🔁✨

---

## 2) 手を動かす🛠️：Windowsで雛形を作って起動する（最短ルート）🚀

### 2-1. Node.js が入ってるか確認する🟢

PowerShell（またはWindows Terminal）で👇を実行：

```bash
node -v
npm -v
```

* **Node 24 が “Active LTS（安定枠）”** なので、学習・開発はここを基準にすると安心です🧱🟢（Node 25は “Current” 扱い）([nodejs.org][1])
* Viteは **Node 20.19+ または 22.12+** が最低ライン、という案内があります（でも今なら24でOK）([vitejs][2])

---

### 2-2. Viteで React + TypeScript の雛形を作る⚡

基本はこれだけ👇（公式の案内にも載ってます）([vitejs][2])

```bash
npm create vite@latest
```

すると質問が出るので、だいたいこんな感じで選びます👇（表示は少し変わることがあります）

* Project name: `my-admin-ui`（好きな名前でOK）
* Framework: **React**
* Variant: **TypeScript**（または **TypeScript + SWC**）

  * SWC は「速い変換エンジン」くらいの気持ちでOKです⚡
  * Vite側で `react-ts` / `react-swc-ts` みたいなテンプレも用意されています([vitejs][2])

**コマンド1発で作る（コピペ向け）**もOK👇（React公式の案内例）([react.dev][3])

```bash
npm create vite@latest my-admin-ui -- --template react-ts
```

---

### 2-3. インストールして起動する🌱

```bash
cd my-admin-ui
npm install
npm run dev
```

ブラウザで表示されたURL（だいたい `http://localhost:5173`）を開くと、Viteの初期画面が出ます🎉

---

## 3) “ホットリロード” を体験する🔥（これが気持ちいいやつ）

`src/App.tsx` を開いて、タイトルを「管理画面っぽく」してみます😎✨
いったんこのサンプルに置き換えちゃってOK👇

```tsx
export default function App() {
  return (
    <div style={{ padding: 24, fontFamily: "system-ui" }}>
      <header style={{ marginBottom: 16 }}>
        <h1 style={{ fontSize: 28, margin: 0 }}>🧩 Admin Dashboard</h1>
        <p style={{ margin: "8px 0 0", opacity: 0.75 }}>
          まずは雛形完成！ここから管理画面UIを育てる🌱
        </p>
      </header>

      <main style={{ display: "grid", gap: 12, maxWidth: 720 }}>
        <section style={{ padding: 16, border: "1px solid #ddd", borderRadius: 12 }}>
          <h2 style={{ margin: 0, fontSize: 18 }}>📊 今日の状態</h2>
          <p style={{ marginTop: 8, opacity: 0.8 }}>
            まだデータはないけど、UIの枠ができた！
          </p>
        </section>

        <section style={{ padding: 16, border: "1px solid #ddd", borderRadius: 12 }}>
          <h2 style={{ margin: 0, fontSize: 18 }}>📝 次にやること</h2>
          <ul style={{ margin: "8px 0 0", paddingLeft: 18 }}>
            <li>Tailwindで見た目を整える🎽</li>
            <li>ページ分割（ルーティング）する🧭</li>
            <li>Firebaseにつなぐ🔌🔥</li>
          </ul>
        </section>
      </main>
    </div>
  );
}
```

保存した瞬間にブラウザが即更新されたら勝ちです✅🎉
これが **HMR（ホットリロード）** の快感です😆🔥

---

## 4) AIで爆速にする🤖⚡（Antigravity / Gemini CLI）

ここから先、AIがいると“詰まりポイント”がマジで減ります🧯✨

### 4-1. Gemini CLI：エラー即解決の使い方🧑‍🔧

**Gemini CLIはターミナルで使えるオープンソースのAIエージェント**で、バグ修正や機能追加、テスト改善までやってくれる設計です([Google Cloud Documentation][4])
詰まったら、エラー全文をそのまま貼って👇みたいに聞くのが最強です💪

* 「このエラーを直して。最短の手順で、Windows向けに」
* 「いまの `package.json` 見て、初心者向けに危ない依存がないかチェックして」
* 「`src/App.tsx` を “管理画面っぽい見た目” にして。まずはTailwindなしでOK」

### 4-2. Antigravity：エージェントに“作業”を任せる🛸

Antigravityは “エージェント管理（Mission Control）” が前提の開発環境で、計画→実装→検証まで回す思想です([Google Codelabs][5])
この章だと、例えば👇を任せると強いです😋

* 「ViteでReact+TS作って起動、動作確認までのチェックリスト作って」✅
* 「このプロジェクトを“管理画面っぽいUI”にするためのフォルダ設計案を出して」📦
* 「次章のTailwind導入で迷わないよう、最小の作業手順を先に下書きして」🎽

---

## 5) ミニ課題🎯（3〜5分でOK）

次の3つをやってみてください🙂✨

1. タイトルを好きな管理画面っぽい名前に変える（例：`🦊 Komiyamma Admin`）🦊
2. サブタイトル（小さい説明文）を1行足す✍️
3. 「次にやること」のリストを、自分のアプリ案に合わせて3つ書く🧠

---

## 6) チェック✅（ここまでできたら第2章クリア）

* `npm run dev` で起動できた？✅
* `src/App.tsx` を編集したらブラウザが即変わった？🔥✅
* `my-admin-ui` フォルダの中に `src/` と `package.json` がある？📦✅

---

## 7) よくある詰まりポイント🧯（先に潰す！）

* **`node` が見つからない** → Node.jsが未インストール or 再起動待ちのことが多いです🔁
* **ポートが使われてる**（5173など）→ すでに別の `npm run dev` が動いてるかも。ターミナルを閉じて再実行でOKなこと多いです🧹
* **社内/セキュリティでnpmが落ちる** → まずはエラー全文をGemini CLIに貼るのが最短です🤖🧯([Google Cloud Documentation][4])

---

## 次章予告👀✨

次は **Tailwind v4系で“最低限きれい”にする** に入ります🎽✨
ここまでできてると、見た目が一気に「それっぽい管理画面」になります😆📊

[1]: https://nodejs.org/en/about/previous-releases "Node.js — Node.js Releases"
[2]: https://vite.dev/guide/ "Getting Started | Vite"
[3]: https://react.dev/learn/build-a-react-app-from-scratch "Build a React app from Scratch – React"
[4]: https://docs.cloud.google.com/gemini/docs/codeassist/gemini-cli "Gemini CLI  |  Gemini for Google Cloud  |  Google Cloud Documentation"
[5]: https://codelabs.developers.google.com/getting-started-google-antigravity "Getting Started with Google Antigravity  |  Google Codelabs"
