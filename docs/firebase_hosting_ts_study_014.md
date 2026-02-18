# 第14章：複数環境（staging/prod）を運用できる形にする🏗️

この章はひと言でいうと、**「うっかり本番を壊さない仕組み作り」**です😇💥
PRプレビューや自動デプロイが回り始めると、次に必要になるのが **staging（検証）** と **prod（本番）** の分離です🌿🚢

---

## まず押さえる言葉📚✨（ここ超大事！）

* **環境（staging/prod）**：ずっと存在する“運用場所”🏠（検証用・本番用）
* **Hosting の site（サイト）**：同じFirebaseプロジェクト内に複数作れる“公開先”🌐（最大36）
  ただし **同じプロジェクトの他リソース（DB等）にアクセスできる**＝危険もある⚠️
  → **環境をミラーするなら「環境ごとに別プロジェクト推奨」**と公式が明言しています🧯 ([Firebase][1])
* **Preview channel（プレビュー）**：PRなどの一時公開URL（期限つき）🔎⏳
  しかも **プレビューでも本物のFirebaseリソースを触る**ので、使い方を間違えると本番汚染が起きます😱 ([Firebase][2])
* **deploy target**：`firebase.json` から “どのサイトに出すか” を名前で指定できる仕組み🏷️
  `.firebaserc` に設定が保存されます🧩 ([Firebase][3])

---

## 今日のおすすめ運用パターン🍱（結論）

## ✅ パターンA：**プロジェクトを分ける（staging/prod）** ←いちばん安全🛡️

* `myapp-stg`（検証）と `myapp-prod`（本番）みたいに **Firebaseプロジェクトを2つ**作る✨
* 公式も「環境ミラー目的なら、同一プロジェクトで複数サイトより別プロジェクト推奨」と言っています👍 ([Firebase][1])
* App Hostingでも「prod/stagingを別プロジェクトにデプロイ」ガイドが公式で用意されています📘 ([Firebase][4])

## ◇ パターンB：**同一プロジェクト内で複数Hosting site**（マルチサイト）🧩

* “Webの見た目だけ” 変えたいとか、何か理由があるならアリ
* でも **DB/Storage/Functionsなどが同じプロジェクト＝本番データに触れやすい**ので慎重に⚠️ ([Firebase][1])

この章のハンズオンは **A（推奨）→B（応用）** の順でいきます🚀

---

## 読む📖：staging/prod を分けると、何が嬉しい？😆

* **検証で失敗しても本番は無傷**🕊️
* PRプレビューが **“staging側のリソース”** を使うようにできる（本番汚染を防ぐ）🧯 ([Firebase][2])
* Secrets（鍵）や権限も **環境ごとに分離**できる🔐（漏れても被害を局所化）

---

## 手を動かす🛠️（ハンズオンA：別Firebaseプロジェクト方式）🏗️🛡️

## 0) ゴール設定🎯

* `develop` ブランチに push → **stagingへ自動デプロイ**🌿🤖
* `main` ブランチに push → **prodへ自動デプロイ**🚢🤖
* PR → **staging側でプレビューURLを自動作成**🔎✨（本番触らない）

---

## 1) Firebaseプロジェクトを2つ用意する🏗️🏗️

* コンソールで `myapp-stg` と `myapp-prod` を作成
* それぞれ Hosting を有効化🌐

（ここはUI作業なのでサクッとでOK👌）

---

## 2) ローカル（Windows）でCLIに「別名」を登録する🏷️💻

プロジェクトを切り替えミスすると終わるので、**“毎回どっちに出してるか”が見える状態**にします👀✨

PowerShellで👇

```bash
## 例：staging を alias に追加
firebase use --add

## 例：prod を alias に追加
firebase use --add
```

この結果、`.firebaserc` に **複数プロジェクトの紐付け**が入ります（内容は環境で変わるけどイメージはこんな感じ）👇 ([Firebase][5])

```json
{
  "projects": {
    "staging": "myapp-stg",
    "prod": "myapp-prod"
  }
}
```

以後は、デプロイ時にこう書けます👇（ミス防止！）

```bash
## stagingへ
firebase deploy --project staging

## prodへ
firebase deploy --project prod
```

---

## 3) GitHub Actionsを「環境ごと」に分ける🤖🔁

Firebase公式の GitHub 連携は「PRでpreview」「mergeでlive」まで用意してくれます📦✨ ([Firebase][2])
ただ、**staging/prodを分ける**なら、ワークフローも分けると気持ちいいです😌🌿

ここでは GitHub Action の **`FirebaseExtended/action-hosting-deploy`** を使います（公式手順でも出てくる定番）🧰 ([GitHub][6])
このActionは `projectId`（どのプロジェクトか）や `target`（どのサイトか）を指定できます👍 ([GitHub][6])

---

## ✅ staging用（develop → stagingへ自動デプロイ）🌿🤖

`.github/workflows/deploy-staging.yml` 例👇

```yaml
name: Deploy (staging)

on:
  push:
    branches: [develop]

jobs:
  build_and_deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 24

      - run: npm ci
      - run: npm run build

      - uses: FirebaseExtended/action-hosting-deploy@v0
        with:
          repoToken: "${{ secrets.GITHUB_TOKEN }}"
          firebaseServiceAccount: "${{ secrets.FIREBASE_SERVICE_ACCOUNT_STAGING }}"
          projectId: myapp-stg
          channelId: live
```

※ Nodeは 2026-02 時点だと **Node 24 がLTS入り**しているので、CI側は 24 を選ぶのが無難です🟩 ([nodejs.org][7])

---

## ✅ prod用（main → prodへ自動デプロイ）🚢🤖

`.github/workflows/deploy-prod.yml` 例👇

```yaml
name: Deploy (prod)

on:
  push:
    branches: [main]

jobs:
  build_and_deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 24

      - run: npm ci
      - run: npm run build

      - uses: FirebaseExtended/action-hosting-deploy@v0
        with:
          repoToken: "${{ secrets.GITHUB_TOKEN }}"
          firebaseServiceAccount: "${{ secrets.FIREBASE_SERVICE_ACCOUNT_PROD }}"
          projectId: myapp-prod
          channelId: live
```

---

## ✅ PRプレビュー（PR → staging側でpreview URL）🔎✨

ポイントはこれです👇
**プレビューでも本物のFirebaseリソースを触る**ので、**prod側でPRプレビューしない**のが安全です🧯 ([Firebase][2])

`.github/workflows/preview.yml` 例👇

```yaml
name: Preview (staging)

on:
  pull_request:
    branches: [develop]

jobs:
  build_and_preview:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 24

      - run: npm ci
      - run: npm run build

      - uses: FirebaseExtended/action-hosting-deploy@v0
        with:
          repoToken: "${{ secrets.GITHUB_TOKEN }}"
          firebaseServiceAccount: "${{ secrets.FIREBASE_SERVICE_ACCOUNT_STAGING }}"
          projectId: myapp-stg
```

---

## 4) Secrets（鍵）を環境ごとに分ける🔐🧰

* GitHubのSecretsに

  * `FIREBASE_SERVICE_ACCOUNT_STAGING`
  * `FIREBASE_SERVICE_ACCOUNT_PROD`
    を別々に登録します🗝️

GitHub連携のセットアップは、公式手順で「サービスアカウント＋Secrets」を作る流れが説明されています📘 ([Firebase][2])

---

## 手を動かす🛠️（ハンズオンB：同一プロジェクトでマルチサイト＋target）🧩

「同じFirebaseプロジェクト内で、`stg`用サイトと`prod`用サイトを分けたい」場合の型です🏗️
ただし **同一プロジェクト内の他リソースを共有する**点は忘れずに⚠️ ([Firebase][1])

## 1) Hosting site を追加する🌐➕

```bash
firebase hosting:sites:create myapp-stg
firebase hosting:sites:create myapp-prod
```

siteの作成コマンドは公式に載っています✅ ([Firebase][1])

## 2) deploy target を割り当てる🏷️

```bash
firebase target:apply hosting staging myapp-stg
firebase target:apply hosting prod myapp-prod
```

この仕組みとコマンドは公式の “Deploy targets” に明記されています🧩 ([Firebase][3])

## 3) `firebase.json` を “配列” で書く🧾

```json
{
  "hosting": [
    {
      "target": "staging",
      "public": "dist"
    },
    {
      "target": "prod",
      "public": "dist"
    }
  ]
}
```

## 4) デプロイを「ターゲット指定」で打つ🚀

```bash
## stagingサイトだけに出す
firebase deploy --only hosting:staging

## prodサイトだけに出す
firebase deploy --only hosting:prod
```

この `--only hosting:TARGET_NAME` 形式も公式に明記されています✅（しかも更新日が 2026-02-03！） ([Firebase][3])

---

## AIで“事故防止”を加速する🤖🧯（ここが今っぽい！）

## 1) コンソール内で詰まりを即解決：Gemini in Firebase🧠✨

「staging/prodどう分ける？」「この設定で危なくない？」を、コンソールから相談できます🧯
セットアップ手順も公式にあります🧩 ([Firebase][8])

## 2) Antigravity / Gemini CLI を “Firebase操作モード” にする：Firebase MCP server🧩🤝

Firebase MCP server を入れると、AI開発ツール（Gemini CLI など）から **Firebaseプロジェクトや設定を自然文で扱いやすく**なります🔥 ([Firebase][9])
「今どのプロジェクトに向いてる？」「deploy target一覧出して」みたいな確認が、事故防止にめちゃ効きます😆🧯

## 3) “リリース前チェック”をAIでテンプレ化：Firebase AI Logic / Genkit🧰🤖

この章はデプロイ運用の話ですが、実務っぽくするなら

* 「本番デプロイ前にチェックリストをAIに作らせる」✅
* 「PR本文から確認項目を自動生成する」📝
  みたいなことを **Firebase AI Logic**（Gemini/Imagenを安全に呼ぶ）で作れます🔥 ([Firebase][10])

---

## ミニ課題🎒✨（15〜30分）

1. ブランチ戦略を決める🌿

   * 例：`main=prod` / `develop=staging`
2. PRプレビューが **staging側** で出ることを確認する🔎
3. “事故防止ルール”を1枚メモにする📝

   * 例：「本番は main からしか出さない」「Secretsは環境別」「PRプレビューはstagingだけ」など

---

## チェック✅（できたら勝ち！🏆）

* [ ] 「環境（staging/prod）」と「preview channel」の違いを説明できる🙂
* [ ] develop → staging / main → prod が自動で出る🤖
* [ ] PRプレビューが **本番ではなくstaging** で動いている🔎
* [ ] Secretsが環境別で分かれている🔐
* [ ] デプロイ先を間違えない仕組み（project/target指定）がある🧯 ([Firebase][3])

---

次の章（第15章：App Hosting入門）に行くと、SSR/フルスタック側でも同じ発想で **環境を作る**話にスムーズに繋がります🧩🚀 ([Firebase][4])

[1]: https://firebase.google.com/docs/hosting/multisites?hl=ja "複数のサイトでプロジェクトのリソースを共有する  |  Firebase Hosting"
[2]: https://firebase.google.com/docs/hosting/github-integration?utm_source=chatgpt.com "Deploy to live & preview channels via GitHub pull requests"
[3]: https://firebase.google.com/docs/cli/targets "Deploy targets  |  Firebase Documentation"
[4]: https://firebase.google.com/docs/app-hosting/multiple-environments "Deploy multiple environments from a codebase  |  Firebase App Hosting"
[5]: https://firebase.google.com/docs/hosting/quickstart?utm_source=chatgpt.com "Get started with Firebase Hosting"
[6]: https://github.com/marketplace/actions/deploy-to-firebase-hosting "Deploy to Firebase Hosting · Actions · GitHub Marketplace · GitHub"
[7]: https://nodejs.org/en/blog/migrations/v22-to-v24?utm_source=chatgpt.com "Node.js v22 to v24"
[8]: https://firebase.google.com/docs/ai-assistance/gemini-in-firebase?utm_source=chatgpt.com "Gemini in Firebase - Google"
[9]: https://firebase.google.com/docs/ai-assistance/mcp-server?utm_source=chatgpt.com "Firebase MCP server | Develop with AI assistance - Google"
[10]: https://firebase.google.com/docs/ai-logic?utm_source=chatgpt.com "Gemini API using Firebase AI Logic - Google"
