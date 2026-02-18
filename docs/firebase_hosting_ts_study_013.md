# 第13章：Hostingのルール整理（redirect/rewritesの設計）🗺️

この章は「**URLの交通整理**」がテーマだよ〜🚦
Firebase Hostingは、`firebase.json` の **redirects / rewrites** を上手に並べるだけで、**移転・改名・SPA・API** が全部スムーズになる！✨ ([Firebase][1])

---

## この章でできるようになること🏁✨

* 「redirect と rewrite の違い」を言葉で説明できる📣
* ルールが効く順番（優先順位）を理解して、事故らない構成にできる🧠
* ReactのSPAでありがちな「直URLで404」を、**正しく**回避できる🔁
* 将来のURL変更（/old→/new）に強いサイトにできる💪

---

## まずは超ざっくり：redirect と rewrite の違い🧠✨

## redirect（リダイレクト）🔀

* **ブラウザに「別のURLへ行ってね」**と指示する
* URLバーが **変わる**
* 例：`/old` → `/new`（移転・統一・正規化に強い） ([Firebase][1])

## rewrite（リライト）🪄

* **見た目のURLはそのまま**、中身だけ別のものを返す
* URLバーは **変わらない**
* 例：SPAで `/about` を開いても **`/index.html` を返す**（アプリ側で画面を出す） ([Firebase][1])

---

## 最重要：Hostingの「優先順位」🚦（ここだけ暗記でOK）

Firebase Hostingは、だいたいこの順で処理するよ👇 ([Firebase][1])

1. `/__/*` で始まる **予約済み名前空間**（ここは触れない）
2. `redirects`
3. **完全一致の静的ファイル**（存在するファイルは強い）
4. `rewrites`
5. カスタム404
6. デフォルト404

そして超大事ポイント👇

* `redirects` の中は **上から順に最初に当たったやつが勝ち**
* `rewrites` の中も **上から順に最初に当たったやつが勝ち**
* しかも **redirects は rewrites より必ず優先** ([Firebase][1])

---

## ルール設計のコツ：事故らない並べ方テンプレ🧰✨

おすすめの並び（超実務っぽいやつ）👇

1. **正規化系 redirect**（www統一、末尾スラッシュ統一、古いURL移転）🔁
2. **例外ルール rewrite**（`/api/**` とか `/.well-known/**` とか）🧩
3. **SPAの最終キャッチオール rewrite**（`"source": "**"`）🧹

理由は単純で、SPAの `**` は“全部飲み込む怪物”だから最後！👾💥
（最後に置けば「本当に行き場がないときだけ index.html」を返せる） ([Firebase][1])

---

## ハンズオン🛠️：ルールを入れて動かして理解する（いちばん早い）

ここでは **3つ**やるよ〜✨

1. `/old` → `/new` を redirect
2. `/api/**` を（将来の）Functions/Cloud Run に rewrite（形だけ先に作る）
3. SPA用に `** → /index.html` を最後に入れる

---

## 0) 事前チェック：`firebase init` の上書きに注意⚠️

`firebase init` をやり直すと `firebase.json` の hosting 部分がデフォルトに戻ることがあるよ😇
なので「変更したらコミット」がおすすめ！ ([Firebase][1])

---

## 1) redirect を追加：`/old` → `/new`（移転）🔀

`firebase.json` の `hosting.redirects` に追加👇

```json
{
  "hosting": {
    "redirects": [
      {
        "source": "/old",
        "destination": "/new",
        "type": 301
      }
    ]
  }
}
```

`type: 301` は「恒久移転」だよ📦（移転が確定してるときに使う） ([Firebase][1])

## ちょい応用：`/foo` と `/foo/**` の両方を拾う🧲

Firebase Hostingは glob を強く推してるので、こういう書き方もできるよ〜 ([Firebase][1])

```json
{
  "hosting": {
    "redirects": [
      {
        "source": "/foo{,/**}",
        "destination": "/bar",
        "type": 301
      }
    ]
  }
}
```

---

## 2) rewrite を追加：`/api/**` は SPA に飲ませない🧯

React SPAをHostingで出すと、最後に `** → /index.html` を置きがち。
でもそのままだと `/api/hello` まで index.html が返って「え？」ってなる😵‍💫

なので **先に** `/api/**` を rewrite で逃がす！

## Functions に飛ばす形（例）⚙️

（この章では “形” を先に作るだけでOK。Functions自体は後で！）

```json
{
  "hosting": {
    "rewrites": [
      {
        "source": "/api/**",
        "function": {
          "functionId": "api",
          "region": "us-central1"
        }
      }
    ]
  }
}
```

`region` は省略もできるけど、関係者が増えると明示が安心だよ🧠
あと、2nd gen Functionsなら `pinTag` で Hosting の静的資産と同期させる運用もできる（プレビューでも効く）📌 ([Firebase][1])

## Cloud Run に飛ばす形（例）🚀

「APIはCloud Runに置く」構成でも、同じノリで書けるよ〜 ([Firebase][1])

```json
{
  "hosting": {
    "rewrites": [
      {
        "source": "/api/**",
        "run": {
          "serviceId": "my-api",
          "region": "asia-east1"
        }
      }
    ]
  }
}
```

Cloud Run rewrite は対応メソッドに制限がある（一般的なHTTPメソッドはOK）ので、変なメソッドを使う設計だと注意だよ⚠️ ([Firebase][1])

---

## 3) SPAの最終キャッチ：最後に `** → /index.html` 🧹✨

React SPAなら、最後にこれを置くのが王道！ ([Firebase][1])

```json
{
  "hosting": {
    "rewrites": [
      {
        "source": "/api/**",
        "function": { "functionId": "api", "region": "us-central1" }
      },
      {
        "source": "**",
        "destination": "/index.html"
      }
    ]
  }
}
```

ポイント👇

* `/api/**` が **先**、`**` が **最後**
* それだけで「APIをSPAが飲む事故」が激減する👍

そしてもう1個、地味に大事👇
Hosting は「そのURLに**実ファイルが存在する**」とき、rewriteより静的ファイルを優先するよ。だから `logo.png` みたいな静的は壊れにくい🧠 ([Firebase][1])

---

## ローカルで確認する（いきなり本番に出さない）🧪

## Hosting Emulator でテスト🧪🏠

Hosting Emulatorは公式で案内されてる方法が安心！ ([Firebase][2])
まずはこれでOK👇（Hostingだけ起動）

```bash
firebase emulators:start --only hosting
```

確認してほしいURL👀

* `http://localhost:5000/old` → `/new` に飛ぶ？（redirect）
* `http://localhost:5000/about` → アプリが表示される？（SPA rewrite）
* `http://localhost:5000/api/hello` → index.html 返ってない？（例外 rewrite）

## プレビューURLで確認（人に見せる）🔎🌐

プレビューはCLIで作れて、期限もつけられるよ⏳ ([Firebase][3])

```bash
firebase hosting:channel:deploy chapter13 --expires 2d
```

（プレビューURLが出るので、スマホでも確認できる📱✨）

---

## 🤖 AIの使いどころ：ルール設計こそAIが強い！

## 1) コンソールのAIに「なぜ効かない？」を聞く🧯

Firebase側のAI支援（コンソール内）で「このURLがどのルールに当たってる？」を言語化すると、バグ取りが速いよ🚀 ([Firebase][4])

例：聞き方（コピペ用）📝

* 「`/api/hello` が index.html になっちゃう。`firebase.json` の並び、どこが危険？」
* 「`/old` を redirect したいのに動かない。優先順位的に何が邪魔しうる？」 ([Firebase][1])

## 2) Gemini CLI で “設定案” を作らせる🧰

Firebase は **Gemini CLI向けの拡張**を公式で用意してるよ。
「この構成の `firebase.json` 作って」って頼む用途にちょうどいい👍 ([Firebase][5])

## 3) MCP server で “プロジェクト文脈つき” にする🧩

Firebase MCP server を入れると、AIツールがFirebaseプロジェクトやコードベースに触れやすくなる（＝「このリポジトリの構成ならこう」って提案の精度が上がる）✨ ([Firebase][6])

---

## ミニ課題🎒✨（10〜15分）

あなたのアプリの将来を想像して、URL設計メモを書こう📝

1. いずれ変わりそうなURLを **3つ**挙げる（例：`/news`、`/profile`、`/help`）
2. それぞれについて決める👇

   * redirect（URLも変える）？ rewrite（URLは変えない）？🤔
   * 301（恒久）？302（仮）？🔁 ([Firebase][1])
3. `firebase.json` に「将来のためのコメント付き」でルール案を書いてみる💪

---

## チェック✅（ここまでできたら合格！）

* Hostingの優先順位を言える（redirects が rewrites より先、など）🚦 ([Firebase][1])
* `redirects` / `rewrites` は **上から順で最初に当たったやつが勝ち**って理解してる🧠 ([Firebase][1])
* SPAの `** → /index.html` は **最後**に置ける👾🧹 ([Firebase][1])
* `/api/**` を先に逃がして、SPAに飲ませない設計にできる🧯 ([Firebase][1])
* Emulator or プレビューで動作確認できる🧪🌐 ([Firebase][2])

---

## おまけ：本番の設定が「本当に反映されてる？」の確認🕵️‍♂️

「CI/CDで反映されたはずなのに、挙動が違う…」みたいなときは、**デプロイ済みの firebase.json をHosting REST APIで確認できる**よ🔍 ([Firebase][1])
（“いま本番が何を見てるか” を確定させるのは最強のトラブルシュート！）

---

次の章（第14章：staging/prod運用🏗️）に進む前に、もしよければ今の `firebase.json`（hosting部分だけでOK）を貼ってくれたら、**事故らない並び**に“添削”して返すよ〜😆🛠️

[1]: https://firebase.google.com/docs/hosting/full-config "Configure Hosting behavior  |  Firebase Hosting"
[2]: https://firebase.google.com/docs/emulator-suite/use_hosting?utm_source=chatgpt.com "Prototype and test web apps with the Firebase Hosting Emulator"
[3]: https://firebase.google.com/docs/hosting/test-preview-deploy?utm_source=chatgpt.com "Test your web app locally, share changes with ... - Firebase"
[4]: https://firebase.google.com/docs/ai-assistance/overview?hl=ja&utm_source=chatgpt.com "AI アシスタンスを使用して開発する | Develop with AI assistance"
[5]: https://firebase.google.com/docs/ai-assistance/gcli-extension?utm_source=chatgpt.com "Firebase extension for the Gemini CLI"
[6]: https://firebase.google.com/docs/ai-assistance/mcp-server?utm_source=chatgpt.com "Firebase MCP server | Develop with AI assistance - Google"
