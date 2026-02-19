# 第02章：最短で土台づくり（プロジェクト＆初期化）🧱

この章のゴールはシンプルです👇
**「Firebase側の“置き場”を作って、ローカルのフォルダとつないで、最初の1回デプロイできる状態」にする**こと！🚀

---

## 0) この章でできるようになること🎯

* Firebase コンソールで **プロジェクトを作れる** 🧩
* Windows で **Firebase CLI を使える**（ログインもOK）🔑
* `firebase init hosting` で **設定ファイルが自動生成**される📄
* `public` が何者か説明できる（＝アップロード対象の“箱”）📦
* **初回デプロイ**してURLで見れる🌐

---

## 1) まず “全体像” を頭に入れる🧠🗺️

![Hosting Deployment Flow](./picture/firebase_hosting_ts_study_002_01_process_overview.png)

イメージはこれ👇

* **Firebaseプロジェクト**：クラウド上の「公開先の土地」🏝️
* **あなたのPCのフォルダ**：アップする「荷物の箱」📦
* **Firebase CLI**：箱を土地に運ぶ「引っ越し業者」🚚

`firebase init hosting` をすると、フォルダの中に **2つの超重要ファイル** が生まれます👇

* `firebase.json`：Hostingの設定（何を出す？何を無視？など）📄
* `.firebaserc`：どのFirebaseプロジェクトに紐づける？（エイリアス）🔗 ([Firebase][1])

---

## 2) 手を動かす：Windowsで “初期化→初回デプロイ” まで一気に🧰⚡

ここからは **Windows（PowerShell）前提**でいきます💪

---

## Step A：作業フォルダを作る📁

```powershell
mkdir firebase-hosting-lesson
cd firebase-hosting-lesson
```

---

## Step B：Firebaseコンソールでプロジェクトを作る🏗️

Firebaseコンソールで「プロジェクトを追加」して作成します🧩
プロジェクトID（英数字のやつ）は後で使うので、メモしておくと安心📝

> ここは画面操作だけなのでサクッとでOK！次でCLIから触れるようにします😆

---

## Step C：Node.js を入れる（CLIの土台）🟩

![Node.js Version Selection](./picture/firebase_hosting_ts_study_002_02_node_selection.png)

Firebase CLIは、最近の構成だと **Node.jsが新しめ**じゃないとつまずきやすいです🥺
Node.js は **v24 が Active LTS**（安定枠）なので、まずこれを選ぶのが安全です✅
（v25は“Current”＝最新機能枠、安定より新しさ寄り） ([Node.js][2])

---

## Step D：Firebase CLI をインストールする🧰

![Firebase CLI Install](./picture/firebase_hosting_ts_study_002_03_cli_install.png)

基本はこれでOK👇

```powershell
npm i -g firebase-tools
firebase --version
```

## もし `npm i -g firebase-tools` で “Nodeのバージョンが古い” と怒られたら😵

`firebase-tools` 側が要求する Node の範囲に入ってない可能性が高いです。
実際、`firebase-tools` の `package.json` では **node >=20 / >=22 / >=24** のように指定されています。 ([GitHub][3])
→ この場合は **Node.js を v24 に上げる**のが最短ルートです🛠️

---

## Step E：Firebase にログインする🔑

![Login](./picture/firebase_hosting_ts_study_002_08_login.png)


```powershell
firebase login
```

ブラウザが開いてGoogleアカウント認証が出ます🌐
成功したらOK！

確認もできます👇

```powershell
firebase projects:list
```

---

## Step F：Hosting を初期化する（ここが本章のメイン！）🧱✨

![Init Wizard](./picture/firebase_hosting_ts_study_002_04_init_wizard.png)

```powershell
firebase init hosting
```

対話で聞かれる内容（おすすめの選び方）👇

1. **どのプロジェクトを使う？**
   → さっき作ったFirebaseプロジェクトを選ぶ🎯

2. **Public directory（公開フォルダ）は？**
   → いったん `public` でOK（あとでReactのビルド先に変える）📦

3. **SPA（シングルページアプリ）？**
   → React を想定するなら **Yes** でOK（リロード404対策の rewrites を自動で入れてくれる）🔁 ([Firebase][1])

初期化が終わると、さっき言った2ファイルが生えます👇

* `firebase.json`（Hostingの設定）
* `.firebaserc`（プロジェクトのエイリアス） ([Firebase][1])

---

## Step G：初回デプロイして “URLで見れる” を体験する🌐🚀

![First Deploy](./picture/firebase_hosting_ts_study_002_09_first_deploy.png)


```powershell
firebase deploy --only hosting
```

成功すると、コンソールにURLが出ます（`…web.app` みたいなやつ）✨
そこを開いて、ページが出たら勝ち🏆

---

## 3) `public` ディレクトリって何？📦（ここが超重要）

![Public Directory Concept](./picture/firebase_hosting_ts_study_002_05_public_folder.png)

超ざっくり言うと👇
**「Firebase Hostingにアップロードされるファイル置き場」**です📦✨

Hosting は `firebase.json` の `hosting.public` を見て、
そのフォルダの中身をアップロードします。 ([Firebase][4])

たとえば初期状態はだいたいこんな感じ👇（例）

```json
{
  "hosting": {
    "public": "public",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ]
  }
}
```

* `public`: 「どこをアップする？」📤
* `ignore`: 「これはアップしないで！」🙅‍♂️（不要物を混ぜないための安全装置）

⚠️注意：`firebase init` をやり直すと、`firebase.json` の hosting 設定がデフォルトに戻ることがあります（上書き注意） ([Firebase][4])

---

## 4) AIショートカット：詰まる前にAIへ投げる🤖🧯

## 4-1) コンソールの「Gemini in Firebase」で聞く🗣️✨

Firebaseコンソール上で有効化して、困ったらその場で質問できます。 ([Firebase][5])
たとえば👇

* 「React(Vite)をHostingで公開したい。`public` は何にすべき？」
* 「今の `firebase.json` の設定でSPAリロード404になる？」

---

## 4-2) Antigravity / Gemini CLI から Firebase を“会話で操作しやすくする”🧩

![Firebase MCP Server](./picture/firebase_hosting_ts_study_002_06_mcp_server.png)

ここで効いてくるのが **Firebase MCP server** です💡
MCPを入れると、AIツール側がFirebase操作の“道具（ツール）”を持てるようになります。しかも **Antigravity** や **Gemini CLI** でも使える、と公式に書かれています。 ([Firebase][6])

## ✅ Gemini CLI なら（推奨）「Firebase extension」インストール

```bash
gemini extensions install https://github.com/gemini-cli-extensions/firebase/
```

これでMCPの設定もまとめて入りやすいです。 ([Firebase][6])

## ✅ Antigravity なら（MCP Servers から Firebase をInstall）

MCP Servers 画面から Firebase を入れると `mcp_config.json` が自動更新され、内部的に `npx … firebase-tools@latest mcp` を使う構成が入ります。 ([Firebase][6])

> この章だと、AIに「このフォルダをHosting初期化して、最小の `firebase.json` を作って」みたいに頼むと、迷子が激減します😆

---

## 5) ミニ課題✍️🎒

![Assignment](./picture/firebase_hosting_ts_study_002_10_assignment.png)


次の2つを、あなたの言葉でメモしてみてください📝

1. **`public` ディレクトリは何？**（一文で）
2. **この章で作ったファイル2つ**（`firebase.json` / `.firebaserc`）の役割を一言ずつ

---

## 6) チェック✅✅

* `firebase --version` が表示できる
* `firebase login` が通っている
* `firebase init hosting` でファイルが生えている（`firebase.json` / `.firebaserc`） ([Firebase][1])
* `firebase deploy --only hosting` が成功してURLで見れる

---

## 7) よくある詰まりポイント🧯（速攻で抜けるやつ）

![Common Errors](./picture/firebase_hosting_ts_study_002_07_troubleshooting.png)

* **npmで “Nodeのバージョンが違う” 系のエラー**
  → Node.js を v24（Active LTS）に揃えるのがラク ✅ ([Node.js][2])

* **ログインできない/ブラウザが開かない**
  → まず `firebase login` をもう一回。会社PCならブラウザの制限が原因のことも多い🥺

* **違うプロジェクトにデプロイしちゃう**
  → `.firebaserc` が「どのプロジェクト？」を持つので、ここを意識すると事故が減ります 🔗 ([Firebase][1])

---

次の第3章で、いよいよ **React（Vite）をビルドして手動デプロイ**に入ります🚀
そのとき「`public` を `dist` に変える」みたいな話が出てくるので、第2章は **“Firebase側の土台ができてること”**が最重要です😎✨

[1]: https://firebase.google.com/docs/hosting/quickstart?utm_source=chatgpt.com "Get started with Firebase Hosting"
[2]: https://nodejs.org/ja/about/previous-releases?utm_source=chatgpt.com "Node.js リリース"
[3]: https://raw.githubusercontent.com/firebase/firebase-tools/main/package.json "raw.githubusercontent.com"
[4]: https://firebase.google.com/docs/hosting/full-config?utm_source=chatgpt.com "Configure Hosting behavior - Firebase - Google"
[5]: https://firebase.google.com/docs/ai-assistance/gemini-in-firebase/set-up-gemini?utm_source=chatgpt.com "Set up Gemini in Firebase - Google"
[6]: https://firebase.google.com/docs/ai-assistance/mcp-server "Firebase MCP server  |  Develop with AI assistance"
