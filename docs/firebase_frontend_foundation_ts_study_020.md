# 第20章：デプロイと運用の入口 🌍🚀（Hosting / App Hosting / CI/CD / 監視 / ロールバック）

この章では「作った管理画面っぽいReactアプリ」を **ネットに公開して**、**安全に更新して**、**困ったら戻せる** ところまでやります 😆✨
“作れた！”から“動かし続けられる！”へ進化させよう〜💪🔥

---

## 0) 今日のゴール 🎯

* ✅ Vite+ReactのSPAを **Firebase Hosting** に公開する 🌐
* ✅ “レビュー用URL” を作れる **Preview Channel** を使う 🧪🔗
* ✅ GitHub と連携して **PRでプレビュー → マージで本番** の入口を作る 🤝🚀 ([Firebase][1])
* ✅ 失敗しても **ロールバック**できる運用を覚える ⏪🛟 ([Firebase][2])
* ✅ SSR/フルスタックやAIをやりたくなった時の **App Hosting分岐** がわかる 🌿🧠 ([Firebase][3])

---

## 1) まず結論：Hosting と App Hosting、どっち？🤔

ざっくりこうです👇

## Firebase Hosting が向いてる 🏠✨

* React/Viteの **静的SPA**（HTML/CSS/JSを配る）
* URL直打ち・React Routerでも崩れないように **rewrites** を設定しやすい 🧭
* **Preview Channel** で「このURLで見て〜！」がすぐできる 🔗🧪 ([Firebase][2])
* Google Cloud のCDNで高速配信（gzip/Brotliなども自動）🚄💨 ([Firebase][4])

## Firebase App Hosting が向いてる 🧩🚀

* Next.js / Angular Universal など **SSR/フルスタック**（サーバーが必要）
* GitHubの “本番ブランチ更新” をトリガーに **自動ロールアウト**（裏側は Cloud Build → Cloud Run → CDN）🧠⚙️ ([Firebase][3])
* `apphosting.yaml` で **環境変数/シークレット** を扱う発想（サーバー側の設定っぽい）🔐 ([Firebase][5])

> いま作ってる「管理画面っぽいSPA」なら、まず **Firebase Hosting** が一番スムーズだよ〜😄
> SSRをやりたくなったら、その時に App Hosting を選べばOK🙆‍♂️

---

## 2) 手を動かす：Firebase Hosting に手動デプロイして公開 🌐🚀

## 2-1) ビルド（公開用のファイルを作る）📦

Viteなら基本これ👇

```bash
npm run build
```

成功すると `dist/` ができるはず！✨

---

## 2-2) Firebase CLI を入れる（または更新）🧰

いちばん定番はこれ👇（Firebase公式もこの流れ） ([Firebase][6])

```bash
npm install -g firebase-tools
firebase --version
```

`firebase-tools` は頻繁に更新されるので、詰まったらまず更新が効くこと多いよ🙏✨ ([npm][7])

---

## 2-3) ログイン & プロジェクト紐づけ 🔐

```bash
firebase login
firebase projects:list
firebase use --add
```

---

## 2-4) Hosting 初期化（Viteのdistを指定）🏗️

```bash
firebase init hosting
```

質問でよく出るポイント👇

* **public directory** → `dist`
* **single-page app**（全部index.htmlへ）→ **Yes**（React RouterするならほぼYes）
  これで `firebase.json` に rewrites が入って、URL直打ち404を回避できるやつ！🧭✨ ([Firebase][8])

（設定イメージ）

```json
{
  "hosting": {
    "public": "dist",
    "rewrites": [{ "source": "**", "destination": "/index.html" }]
  }
}
```

---

## 2-5) デプロイ！🌍🚀

```bash
firebase deploy --only hosting
```

終わると Hosting のURLが出るので、開いて表示確認だ〜😆🎉

---

## 3) “レビュー用URL” を作る：Preview Channel 🧪🔗

これがめちゃ便利！
本番を壊さずに、**別URLで見せられる**やつです😎✨ ([Firebase][2])

## 3-1) 例：`dev` チャンネルにデプロイ

```bash
firebase hosting:channel:deploy dev
```

* これで `dev` 用のURLが発行される👍
* チャンネルは期限付きにもできる（消し忘れ防止）🧹✨ ([Firebase][2])

## 3-2) 片付け（不要になったら削除）

```bash
firebase hosting:channel:delete dev
```

---

## 4) 失敗しても大丈夫：リリース履歴 & ロールバック ⏪🛟

Hostingは「デプロイ＝リリースが積み上がる」感じなので、戻せるのが安心ポイント😌✨ ([Firebase][2])

CLIで戻すなら（代表例）👇

```bash
firebase hosting:rollback
```

（細かい指定や確認もCLIリファレンスにまとまってるよ） ([Firebase][9])

---

## 5) 自動化：PRでプレビュー、マージで本番（GitHub連携）🤝🚀

Firebase Hostingは **GitHubのPRと連携してプレビューURLをコメントしてくれる** 流れが用意されてます👏 ([Firebase][1])

## 5-1) いちばん楽な作り方（推奨）🧠✨

```bash
firebase init hosting:github
```

これで、リポジトリにGitHub Actionsのワークフローが生成されて👇

* PRを作る → **プレビューURLがPRにコメント**される
* commitを積む → 同じプレビューURLが更新される
* （設定次第で）マージしたら本番へデプロイ
  という動きになるよ！ ([Firebase][1])

---

## 6) “運用”で一番やらかしやすい：環境変数と秘密情報 🔐😱

## 6-1) フロント（Vite）の環境変数は「ビルド時」⚠️

Viteの環境変数は基本 `VITE_` プレフィックスで、**ビルド成果物に埋め込まれる**発想だよね🧠
つまり…

* ❌ 秘密鍵やAIの本当のシークレットを入れるのはNG
* ✅ 表に出てもOKな設定だけ（例：公開しても困らないID類）にする

## 6-2) AIを本番で安全に使うコツ 🤖🛡️

* クライアントから直接AIを呼ぶなら **Firebase AI Logic** を使う（App Checkなど“守り”と組み合わせやすい）🧩✨ ([Firebase][10])
* 「これは絶対に漏らせない」系は、**Functions側でSecret Manager** を使うのが王道 🔐🏰
  `functions.config` は非推奨で、将来的にデプロイ失敗の原因になるので移行推奨だよ〜（公式） ([Firebase][11])

---

## 7) App Hosting分岐：SSRやフルスタックに行きたくなったら 🌿🚀

App Hostingは “中で何が起きてるか” が分かると怖くない😆

* GitHubのコミット → Cloud Buildでビルド → コンテナがArtifact Registryへ → Cloud Runで新Revision → CDN/ロードバランサ経由で配信
  っていう流れをよしなにやってくれる💨 ([Firebase][3])
* ロールアウト状況はコンソールやGitHubチェックで見れる 👀✅ ([Firebase][12])
* ログ/メトリクスも Cloud Run / Cloud Build / CDN 側に繋がって見える 📈🪵 ([Firebase][13])
* `apphosting.yaml` で環境変数やシークレットを設定する 🧾🔐 ([Firebase][5])

> “静的SPA”の世界は Hosting、
> “サーバーも含めて面倒みてほしい”世界は App Hosting、
> って覚えるとスッキリするよ〜😄✨

---

## 8) Functionsも一緒に運用する時の「バージョン感」⚙️📌

フロント章だけど、運用視点でここだけ押さえると強い💪

* Cloud Functions for Firebase は **Node.js 20 / 22 をフルサポート**、18はdeprecated（公式） ([Firebase][6])
* Firebase CLIの最近の更新で **Pythonのデフォルトランタイムが3.13** になった旨も出てる（CLIリリースノート） ([Firebase][14])
* さらに下回りのCloud Run Functions側では **Python 3.13がGA** になってる（Google側のリリースノート） ([Google Cloud Documentation][15])
* .NETは “最新LTSは .NET 10” だけど、サーバレス実行環境側は対応状況が別ラインなので、使う時は「そのサービスが対応してるランタイム」を必ず見るのが安全（例：Cloud Run Functionsのリリースノートで .NET 8 GA が明記）🟦🧠 ([Firebase][1])

---

## 9) AIでデプロイ運用を加速する 🚀🤖

## 9-1) Firebase Studio：環境ごと“再現”できるの強い 🧪🧰

Firebase Studio は Nixベースで環境を定義できて、ワークスペースも共有しやすい💡
しかも Gemini in Firebase がワークスペース内で手伝ってくれる！ ([Firebase][16])

## 9-2) Firebase CLIの “AI連携” も増えてる 🛠️🤝

Firebase CLI には `firebase experimental:mcp`（MCPサーバー）みたいな **AIアシスタント連携**の動きも出てきてるよ（リリースノート） ([Firebase][14])

---

## 10) ミニ課題 🎯🔥（20〜40分）

1. **Hostingに手動デプロイ**してURLを開く 🌍
2. **Preview Channel `dev`** を作って、`dev` のURLも開く 🧪
3. GitHub連携を `firebase init hosting:github` で入れて、PRを作って **プレビューURLがコメントされる**のを確認 🤝✨ ([Firebase][1])
4. わざと表示を壊してデプロイ → **rollback** で戻す ⏪🛟 ([Firebase][9])

---

## 11) チェックリスト ✅🧠

* [ ] `npm run build` が通る（`dist/` ができる）📦
* [ ] `firebase init hosting` の public が `dist` になってる 🏗️
* [ ] SPAの rewrites が入ってて、URL直打ちで404にならない 🧭 ([Firebase][8])
* [ ] Preview Channel で本番と別URLが作れる 🧪 ([Firebase][2])
* [ ] PRプレビューの仕組みが動く 🤝 ([Firebase][1])
* [ ] 秘密情報をフロントに入れない（AIはAI Logic/Functions側へ）🔐🤖 ([Firebase][10])

---

必要なら次に、**「Hostingのキャッシュ最適化（headers）」「独自ドメイン」「本番/開発のサイト分割（複数site運用）」「App Hostingへ移行する時の設計メモ」**まで、運用寄りにもう一段深掘りもできるよ〜😆✨

[1]: https://firebase.google.com/docs/hosting/github-integration?utm_source=chatgpt.com "Deploy to live & preview channels via GitHub pull requests"
[2]: https://firebase.google.com/docs/hosting/manage-hosting-resources?utm_source=chatgpt.com "Manage live & preview channels, releases, and versions for ..."
[3]: https://firebase.google.com/docs/app-hosting?utm_source=chatgpt.com "Firebase App Hosting"
[4]: https://firebase.google.com/products/hosting?utm_source=chatgpt.com "Fast, secure hosting for static websites - Firebase - Google"
[5]: https://firebase.google.com/docs/app-hosting/configure?utm_source=chatgpt.com "Configure and manage App Hosting backends - Firebase"
[6]: https://firebase.google.com/docs/functions/get-started?utm_source=chatgpt.com "Get started: write, test, and deploy your first functions - Firebase"
[7]: https://www.npmjs.com/package/firebase-tools?utm_source=chatgpt.com "firebase-tools - Command-Line Interface for Firebase"
[8]: https://firebase.google.com/docs/hosting/full-config?utm_source=chatgpt.com "Configure Hosting behavior - Firebase - Google"
[9]: https://firebase.google.com/docs/cli?utm_source=chatgpt.com "Firebase CLI reference"
[10]: https://firebase.google.com/docs/ai-logic?utm_source=chatgpt.com "Gemini API using Firebase AI Logic - Google"
[11]: https://firebase.google.com/docs/functions/config-env?utm_source=chatgpt.com "Configure your environment | Cloud Functions for Firebase"
[12]: https://firebase.google.com/docs/app-hosting/rollouts?utm_source=chatgpt.com "Manage rollouts and releases | Firebase App Hosting - Google"
[13]: https://firebase.google.com/docs/app-hosting/logging?utm_source=chatgpt.com "View logs and metrics | Firebase App Hosting - Google"
[14]: https://firebase.google.com/support/release-notes/cli?utm_source=chatgpt.com "Firebase CLI Release Notes"
[15]: https://docs.cloud.google.com/functions/docs/release-notes?utm_source=chatgpt.com "Cloud Run functions (formerly known as Cloud Functions ..."
[16]: https://firebase.google.com/docs/studio/get-started-workspace?utm_source=chatgpt.com "About Firebase Studio workspaces"
