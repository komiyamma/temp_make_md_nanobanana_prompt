# 第03章：ReactをHostingへ“手動”デプロイしてみる🚀

今日やることはシンプル！
**①ビルドして（静的ファイル作る）→②Firebase Hostingにアップして（公開）→③URLで確認** です🌐✨
手動デプロイを一回やっておくと、この後の **PRプレビュー→本番自動反映** がめちゃ理解しやすくなります😆

---

## 1) 読む📚：手動デプロイって何をしてるの？🤔

## ビルド＝「配る用の完成品」を作る🧁

開発中は `npm run dev` で“開発サーバー”が動いてるけど、それは**自分のPC用**なんだよね🖥️
公開するときは、**誰でも見れる“静的ファイル”**（HTML/CSS/JS/画像など）にまとめます📦

* Vite（Reactの定番構成のひとつ）だと、ビルド結果は既定で `dist/` に出ます📁([endoflife.date][1])

## デプロイ＝「完成品をサーバーに置く」🚚

Firebase Hosting は、静的ファイルをアップすると **グローバルCDNで配信**してくれて、HTTPS(SSL)も基本おまかせで“それっぽい公開”ができます🔒⚡([Firebase][2])
手動デプロイはその第一歩。ここで “公開の全体像” をつかみます🗺️

---

## 2) 手を動かす🛠️：最短で「公開URLが出る」まで行こう🏃‍♂️💨

以下は **Windows（PowerShell想定）** で進めます🪟✨
（すでに第2章でプロジェクト作成＆`firebase init hosting`済みなら、途中は読み飛ばしてOK👌）

---

## Step 0：Nodeのバージョンだけ軽くチェック✅

Firebase CLI（`firebase-tools`）は **Node 24対応**が入っていて、Node 18はサポート対象から外れています🧠
なので迷ったら **Node 24（Active LTS）** を使うのが安全寄りです🟩([Firebase][3])

---

## Step 1：Reactアプリを用意する（無ければ作る）🧩

すでにアプリがあるなら、このStepは飛ばしてOK🙆‍♂️

```powershell
npm create vite@latest my-app -- --template react-ts
cd my-app
npm install
```

---

## Step 2：ビルドして `dist/` を作る📦✨

```powershell
npm run build
```

成功すると、プロジェクト内に `dist/` ができます📁（ここが“配る用の完成品”）([endoflife.date][1])

---

## Step 3：Hostingの初期化（第2章で済ならスキップ）🧱

まだ `firebase.json` がない場合だけやってね！

```powershell
firebase login
firebase init hosting
```

ここで聞かれる「公開するフォルダ（public directory）」は、Viteなら **`dist`** を指定するのが基本です📌
Hostingは `firebase.json` の **`hosting.public` に指定されたディレクトリだけ** をデプロイします。([Firebase][4])

---

## Step 4：`firebase.json` を確認（大事ポイント）🧾👀

`firebase.json` にこういう感じで書かれていればOK！（例）

```json
{
  "hosting": {
    "public": "dist",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ]
  }
}
```

`public` は「どのフォルダを出すか」なので超重要🔥
`ignore` は「アップしないもの」で、`node_modules` を除外するのが基本形です🧹([Firebase][4])

---

## Step 5：いよいよ手動デプロイ！🚀🌐

```powershell
firebase deploy --only hosting
```

これで Hosting だけをデプロイします🎯
完了すると、ターミナルに **公開URL（`...web.app` や `...firebaseapp.com`）** が出るはず！🕺✨([Firebase][5])

---

## Step 6：更新→再ビルド→再デプロイ（“公開更新”を体に覚えさせる）🔁🔥

1. どこでもいいのでUIをちょっと変える（例：見出しの文字を変える）✍️
2. もう一回ビルド📦
3. もう一回デプロイ🚀

```powershell
npm run build
firebase deploy --only hosting
```

ブラウザを更新して、変更が反映されたら勝ち🏆✨

---

## 3) ミニ課題📝：公開URLを“自分の資産”にする💎

1. 公開URLをメモ（Notionでもメモ帳でもOK）🗒️
2. **「何を変えたか」→「ビルドしたか」→「デプロイしたか」** を1行ログに残す✍️

   * 例）`h1を変更 → npm run build → firebase deploy --only hosting`

この“自分用ログ”、後でめちゃ助かるよ😇✨

---

## 4) チェック✅：ここまでで言えると強い💪

* 「ビルド」と「デプロイ」の違いを一言で説明できる？🧠
* Hostingで公開されるのは `firebase.json` のどの設定？（ヒント：`public`）🧾([Firebase][4])
* 手動デプロイのコマンドを言える？🚀（ヒント：`firebase deploy --only hosting`）([Firebase][5])

---

## 5) つまずき救急箱🧯（よくあるやつだけ！）

## 😵「デプロイしたのにFirebaseのデフォルトページが出る」

だいたいこれ👇

* `public` が `public/` のままで、`dist/` を出してない
  → `firebase.json` の `public` を `dist` にして、**ビルド→デプロイ**し直し！([Firebase][4])

## 😵「dist が無いって怒られる」

* `npm run build` を忘れてる
* もしくは別ツールで出力先が違う
  → **出力フォルダ名**と `public` が一致してるか確認👀([endoflife.date][1])

## 😵「Nodeのバージョンでコケる」

* Nodeが古い/合わない
  → Firebase CLIはNode 24対応が入っていて、Node 18は対象外なので、ここを揃えると安定しやすいよ🧩([Firebase][3])

---

## 6) AIで“詰まり”を秒速で潰す🤖🧯（第3章のうちに味見しよう）

## A) Firebaseコンソール内のAI相談💬

Firebaseには **コンソール上で相談できるAI支援（Gemini in Firebase）** が用意されています🧯
「Hostingの設定どこ？」「このエラー何？」をその場で聞けるのが強み💪

---

## B) Firebase MCP serverで“AIからFirebase作業”を触りやすくする🧩

Firebase MCP server を使うと、AI支援ツール側からFirebase関連の作業を“道具として”扱いやすくなります🔧
公式ドキュメントで案内されています📚

たとえば（イメージ例）MCPの設定に `firebase-tools` を登録する形が紹介されています🧠（下は例）

```json
{
  "mcpServers": {
    "firebase": {
      "command": "npx",
      "args": ["-y", "firebase-tools@latest", "experimental:mcp"]
    }
  }
}
```

※ここまで第3章でガチ設定しなくてもOK！
「こういう“AIとFirebaseをつなぐ公式の道”がある」ってだけ掴めれば十分🙆‍♂️([Firebase][3])

---

## C) Gemini CLI と Google Antigravityの使い分け🧠✨

**2026-02-04のGoogle Cloud公式ブログ**だと、ざっくりこう整理されています👇

* Antigravity：**IDE＋複数エージェント管理の“司令塔”**っぽい🥷
* Gemini CLI：**ターミナルで使う/ヘッドレス実行**に強い🧑‍💻
* Gemini CLI は `npm install -g @google/gemini-cli` の形で入れる説明もあります📦([Google Cloud][6])
  さらにAntigravityは **Windowsでもプレビュー利用できる**案内があります🪟([Google Codelabs][7])

**第3章でのおすすめの使い方（超現実的）**👇😎

* デプロイ失敗時：ログを貼って「原因候補と直し方」をAIに出させる
* `firebase.json` 迷子：`public` や SPA設定の意味を質問して理解を固める

**投げると強いプロンプト例**🧠（コピペOK）

* 「この `firebase deploy --only hosting` のエラーを読んで、原因トップ3と手順で直し方を教えて」
* 「Viteの `dist` をHostingで公開したい。`firebase.json` の最小構成を教えて」

---

## 7) 次章へのつながり🔗✨

第3章で「手動で出せた！」ができたら、次は **`firebase.json` をちゃんと理解して調整**（第4章）に行くと気持ちいいです🧾🔥
公開が安定すると、CI/CDの自動化も一気に楽しくなるよ😆🚢

[1]: https://endoflife.date/nodejs "Node.js | endoflife.date"
[2]: https://firebase.google.com/docs/hosting "Firebase Hosting"
[3]: https://firebase.google.com/support/release-notes/cli "Firebase CLI Release Notes"
[4]: https://firebase.google.com/docs/hosting/full-config?utm_source=chatgpt.com "Configure Hosting behavior - Firebase - Google"
[5]: https://firebase.google.com/docs/hosting/quickstart "Get started with Firebase Hosting"
[6]: https://cloud.google.com/blog/topics/developers-practitioners/choosing-antigravity-or-gemini-cli "Choosing Antigravity or Gemini CLI | Google Cloud Blog"
[7]: https://codelabs.developers.google.com/getting-started-google-antigravity "Getting Started with Google Antigravity  |  Google Codelabs"
