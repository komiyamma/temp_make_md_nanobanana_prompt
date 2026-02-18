# 第04章：最小セットアップ（CLI初期化→1個デプロイ）🌱

## この章のゴール🎯

* `firebase init` で Functions を初期化できる🧰
* HelloなHTTP関数を **1つだけ** デプロイできる🌐
* 出てきたURLをブラウザで叩いて「動いた！」を確認できる😆✅

---

## 0) 先に知っておく“最重要”ポイント💡

* **デプロイには Blaze（従量課金）プランが必要**です（無料枠だけだとデプロイ自体が進みません）💸🧯 ([Firebase][1])
* Firebase Functions の Node.js ランタイムは **20 / 22 が現役**で、**18 は非推奨**の扱いです（なので迷ったら22寄りが安心）🟩 ([Firebase][1])
* 2nd gen でデプロイされるかどうかは、コード側の import が **`firebase-functions/v2/...`** かどうかで決まります（ここ大事！）🧠✨ ([Firebase][2])

---

## 1) 準備：Node.js と Firebase CLI を入れる🧰（Windows）

## 1-1. Node.js の確認✅

ターミナル（PowerShellでもOK）で👇

```bash
node -v
npm -v
```

Node.js は **20 または 22** ならOKです🟢（18は避ける） ([Firebase][1])

## 1-2. Firebase CLI を入れる（または更新）⬆️

```bash
npm install -g firebase-tools
```

その後👇

```bash
firebase --version
```

2nd gen を扱うには CLI と `firebase-functions` を新しめに保つのが大事で、公式ガイドでも一定以上のバージョンを前提に説明されています🔧 ([Firebase][2])

## 1-3. ログイン🔑

```bash
firebase login
```

ブラウザが開くので認証して戻ってきたらOKです👍

---

## 2) 初期化：`firebase init` で Functions を作る🌱

## 2-1. 作業フォルダ作成📁

```bash
mkdir my-firebase-functions
cd my-firebase-functions
```

## 2-2. 初期化コマンド🛠️

```bash
firebase init functions
```

だいたいこんな質問が来ます（選ぶ内容のおすすめ）👇🙂

* **Project**：既存プロジェクトを選択（なければ先にConsoleで作成）
* **Language**：TypeScript を選ぶ🟦（この教材の中心！） ([Firebase][3])
* **ESLint**：最初は ON 推奨（ミスが早く見つかる🧯）
* **Install deps now?**：Yes（あとで詰まらない）

> 🔸 **codebase って何？**
> Functions を将来「複数の塊」に分けて管理できる仕組みです（例：`api` と `batch` を分ける、など）🧩
> Firebase の docs でも “Functions の整理” として codebase 前提の書き方が紹介されています📚 ([Firebase][4])

初期化が終わると、だいたい👇みたいな構成になります（超ざっくり）📦

* `firebase.json`
* `functions/`（ここがサーバー側コード）
* `functions/src/index.ts`（メイン入口） ([Firebase][3])

---

## 3) Hello HTTP 関数を書く👋🌐（2nd gen）

`functions/src/index.ts` を開いて、まずは最小の1個だけ書きます✍️
（**v2 import** を使うので 2nd gen になります🔥） ([Firebase][2])

```ts
import { onRequest } from "firebase-functions/v2/https";
import { logger } from "firebase-functions/logger";

// 迷ったら日本(東京)寄りに置くと体感が良くなりやすいよ👍
// regionは必要に応じて変更OK（例：asia-northeast1）
export const hello = onRequest({ region: "asia-northeast1" }, (req, res) => {
  logger.info("hello called!", { method: req.method, path: req.path });

  res.status(200).json({
    ok: true,
    message: "Hello from Firebase Functions 👋",
    now: new Date().toISOString(),
  });
});
```

* `logger` を使うと、あとで運用（ログ追跡）がめちゃ楽になります🧯👀 ([Firebase][5])
* `region` の指定は「ユーザーに近い場所」に寄せる基本ムーブです📍（この形式でオプション指定できます） ([Firebase][2])

---

## 4) デプロイする🚀（最初の1回を通す）

## 4-1. まず Functions だけ deploy

```bash
firebase deploy --only functions
```

初回は裏でいろいろ有効化が走るので、ログがちょい長めに出ることがあります（普通です😌）
そして、成功すると **URL が表示**されます🌐 ([Firebase][1])

## 4-2. 動作確認✅

出てきたURLをブラウザで開いて、👇みたいなJSONが返れば勝ち🎉

* `ok: true`
* `message: "Hello ..."`
* `now: "..."`

---

## 5) つまずきポイント集🧯（ここだけ見れば復帰できる）

## A) 「Blazeにして」系のエラー💸

Functions のデプロイは **Blaze必須**です（無料のままだと止まります） ([Firebase][1])

## B) Nodeバージョンで怒られる🟩

Node は **20/22** を使うのが安全です（18は非推奨） ([Firebase][1])

## C) 「2nd gen になってない？」🤔

import が `firebase-functions/v2/...` になってるか確認！
ここで CLI が “第1世代としてデプロイする/第2世代としてデプロイする” を判断します🧠 ([Firebase][2])

## D) ESLintで止まる😵

初学者あるある！
一旦はログを読んで、直せない時は **AIに「エラー貼って、直して」**が最短です🤖（後述）

---

## 6) AIで“初期化〜デプロイ”を爆速にする🤖⚡（Antigravity / Gemini CLI）

## 6-1. Antigravity で Firebase を直結する🛸

Firebase MCP server は Antigravity から入れられて、設定も自動で入ります🧩
手順の要点👇 ([Firebase][6])

* Agent pane > MCP Servers から Firebase を Install
* すると内部で `npx -y firebase-tools@latest mcp` を使う設定が入ります🧰 ([Firebase][6])

## 6-2. Gemini CLI で Firebase 拡張を入れる🧰

Gemini CLI の Firebase 拡張を入れるのが推奨ルートです👇 ([Firebase][6])

```bash
gemini extensions install https://github.com/gemini-cli-extensions/firebase/
```

この拡張は MCP server の設定もまとめてやってくれて、Firebase開発の精度が上がる “context file” も付いてきます📎 ([Firebase][6])

## 6-3. “AIに頼む時の指示”テンプレ📝

たとえば Gemini CLI / Antigravity にこう頼むと速いです😆

* 「`firebase init functions` の選択肢をこのプロジェクトに合わせて提案して」
* 「2nd gen の `onRequest` で hello 関数を書いて、最小でデプロイまでのコマンド列を出して」
* 「デプロイエラーが出た。ログ貼るから原因と直し方を“コピペで”ちょうだい」

さらに、Firebase MCP server の docs でも **`/firebase:init` や `/firebase:deploy`** のようなプロンプトより、**agent skills の併用が効率的**な場面（Auth/Firestore/AI Logic 等のセットアップなど）があるよ、と案内されています🤝 ([Firebase][6])

---

## 7) ちょい補足：Python / C#(.NET) はどう扱う？🐍🟣

* Firebase Functions は **Python 3.10〜3.13（デフォルト3.13）** が案内されています🐍 ([Firebase][1])
* C# を “関数ランタイムとして” やりたい場合は、現実的には **Cloud Run functions + .NET** 側で作るルートが強いです🟣
  例：Cloud Run の .NET runtime には **.NET 8** などが用意されています（.NET 10 preview も見えます） ([Google Cloud Documentation][7])

---

## ミニ課題🎒（5〜10分でOK）

1. `hello` の返すJSONに `query`（`req.query`）を混ぜて返す📦
2. `message` を自分の好きな文に変える（絵文字もOK😆）
3. もう一回 `firebase deploy --only functions:hello` して差分反映できたら完了🎉

---

## チェック✅

* `firebase init functions` ができた
* `firebase-functions/v2/https` の `onRequest` で関数を書けた ([Firebase][2])
* `firebase deploy --only functions` が成功し、URLでJSONが返った ([Firebase][1])

---

次の第5章では、この `functions/` の中身を「初心者でも崩れない分割ルール」に整えて、HTTP/イベント/共通処理で迷子にならない土台を作るよ🧱✨

[1]: https://firebase.google.com/docs/functions/get-started "Get started: write, test, and deploy your first functions  |  Cloud Functions for Firebase"
[2]: https://firebase.google.com/docs/functions/2nd-gen-upgrade?hl=ja "第 1 世代の Node.js 関数を第 2 世代にアップグレードする  |  Cloud Functions for Firebase"
[3]: https://firebase.google.com/docs/functions/http-events "Call functions via HTTP requests  |  Cloud Functions for Firebase"
[4]: https://firebase.google.com/docs/functions/organize-functions "Organize multiple functions  |  Cloud Functions for Firebase"
[5]: https://firebase.google.com/docs/functions/typescript "Use TypeScript for Cloud Functions  |  Cloud Functions for Firebase"
[6]: https://firebase.google.com/docs/ai-assistance/mcp-server "Firebase MCP server  |  Develop with AI assistance"
[7]: https://docs.cloud.google.com/run/docs/runtimes/dotnet "The .NET runtime  |  Cloud Run  |  Google Cloud Documentation"
