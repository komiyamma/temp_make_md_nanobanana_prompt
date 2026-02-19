# 第07章：GitHub連携（PRごとに自動プレビュー）🤝

この章は「Pull Request（PR）を出したら、自動で“プレビューURL”が生えて、レビューがワンクリックになる」状態を作ります😆✨
しかもそのURL、**コミットを積んでも同じURLのまま更新**されるので、レビューが超ラクになります🔁🌐 ([Firebase][1])

---

## 1) この章でできるようになること🏁🎯

* PRを作るだけで **Preview Channel（プレビュー用の“場所”）** が自動作成される🧩 ([Firebase][1])
* PRに **プレビューURLがコメントで自動投稿**される💬🔗 ([Firebase][1])
* PRに新しいコミットを積むと、**同じプレビューURLが更新**される🔁✨ ([Firebase][1])
* （注意）プレビューURLでも **本物のFirebaseバックエンド**に接続するので、うっかり本番データを壊さない意識が持てる🧯 ([Firebase][1])

---

## 2) 仕組みを超ざっくり理解しよ🧠🗺️

![PR Preview Automation](./picture/firebase_hosting_ts_study_007_01_automation_concept.png)

イメージはこれ👇

1. あなたがPRを作る 🧑‍💻➡️ GitHub
2. GitHub Actions が動く 🤖
3. Hosting の **Preview Channel** にデプロイされる🚀
4. PRに「このURL見てね！」ってコメントが付く💬🔗 ([Firebase][1])

ポイントは「**Preview Channel = PR専用の一時公開枠**」ってことです🏷️
期限（デフォルト7日）もあるので、放置しても勝手に消えていきます⏳ ([GitHub][2])

---

## 3) 手を動かす🛠️（Windowsでいくよ💻✨）

## 3-1. まずはFirebase CLIを使える状態にする⚙️

PowerShellでOKです🙆‍♂️

```bash
npm i -g firebase-tools
firebase --version
firebase login
```

## 3-2. リポジトリ直下で GitHub連携セットアップ🤝

![CLI Setup Wizard](./picture/firebase_hosting_ts_study_007_02_cli_wizard.png)

Hostingは既に初期化済みでもOK。**GitHub連携だけ**ならこれ👇

```bash
firebase init hosting:github
```

するとCLIが対話でいろいろ聞いてきます（だいたいこんな感じ）👇

* どのFirebaseプロジェクト？（複数あるなら選ぶ）🧩
* どのGitHubリポジトリ？📦
* PRプレビュー作る？✅
* マージでliveへ自動デプロイも作る？（これは第8章で本番運用するので、ここではONでもOK）🚢

CLIがやってくれる“すごいこと”👇（ここ重要！）

* Hostingデプロイ用の**サービスアカウント**を作る🔐
* そのJSONキーを暗号化して **GitHub Secretsに自動登録**する🗝️
* そして `.github/workflows/*.yml` を自動生成してくれる🤖🧾 ([Firebase][1])

> ※この自動セットアップには、リポジトリの管理権限が必要です👑（権限が弱いとSecrets登録でコケがち） ([Firebase][1])

## 3-3. 生成されたworkflowをコミットしてpush🧾➡️📤

CLIが生成したファイル（例）：

* `.github/workflows/firebase-hosting-pull-request.yml`（PR用）
* `.github/workflows/firebase-hosting-merge.yml`（マージ用）

コミットしてpushします👇

```bash
git checkout -b setup/hosting-preview
git add .
git commit -m "chore: set up Firebase Hosting preview deploy"
git push -u origin setup/hosting-preview
```

## 3-4. PRを作って“プレビューURLが生える”のを確認👀🔗

![PR Comment UI](./picture/firebase_hosting_ts_study_007_03_pr_comment.png)

GitHub上でPRを作成すると…

* Actionsが走る🏃‍♂️💨
* PRにプレビューURLがコメントされる💬🔗 ([Firebase][1])

さらにPRに追コミットすると、**同じURLが更新**されます🔁✨ ([Firebase][1])
![Persistent URL on Update](./picture/firebase_hosting_ts_study_007_04_update_flow.png)

---

## 4) 生成されるYAMLの中身（最低限だけ読む）👀🧾

![YAML Config Anatomy](./picture/firebase_hosting_ts_study_007_05_yaml_anatomy.png)

CLIが作るワークフローは、中でだいたいこのActionを使ってます👇
`FirebaseExtended/action-hosting-deploy@v0` ([GitHub][2])

ざっくり重要パラメータはこれ👇

* `repoToken: ${{ secrets.GITHUB_TOKEN }}` → PRにコメントするため💬（GitHubが自動で用意） ([GitHub][2])
* `firebaseServiceAccount: ${{ secrets.（なにか） }}` → Firebaseにデプロイする鍵🔐 ([GitHub][2])
* `expires: 7d/30d` → プレビューの寿命⏳（デフォは7日） ([GitHub][2])

---

## 5) よくある詰まりポイント集🧯（ここで時間を溶かさない！）

## 5-1. PRにプレビューURLコメントが付かない😢

よくある原因👇

* workflowに `repoToken` が無い / PRコメントが無効化されている
* GitHub Actions側の権限が弱くてPRに書けない

`repoToken` を入れるとPRにコメントできる、という仕様です💬 ([GitHub][2])
（入れない場合は、ActionsログにURLが出るのでそこを見る形になります👀） ([GitHub][2])

## 5-2. forkからのPRだとプレビューが動かない🧊

![Fork Secret Limitation](./picture/firebase_hosting_ts_study_007_06_fork_issue.png)

これは仕様寄りです🥶
fork由来のPRは、Secretsが渡らないことが多く、`firebaseServiceAccount` が空になって失敗します。 ([GitHub][3])

👉 対策の定番は「**同一リポジトリ内のブランチPRで回す**」です（学習はこれが一番ラク）✨

---

## 6) AIで爆速にする🤖⚡（Antigravity / Gemini CLI を“ちゃんと使う”）

![AI Debugging Workflow](./picture/firebase_hosting_ts_study_007_07_ai_fix.png)

## 6-1. Gemini CLIにFirebase拡張を入れて、詰まりを即相談🧠💬

Firebase拡張は、**Firebase MCP server を自動で入れてくれて**、Firebase操作・ドキュメント参照・定型プロンプトが強化されます🧩 ([Firebase][4])

インストール👇

```bash
gemini extensions install https://github.com/gemini-cli-extensions/firebase/
```

入ったら、たとえば `/firebase:` まで打つと使えるコマンド候補が出ます（定型プロンプトが使える）🧰 ([Firebase][5])

おすすめの使い方（この章向け）👇

* 「このworkflowが何をしてるか、初心者向けに説明して」📘
* 「PRコメントが付かない。どこを見ればいい？」🧯
* 「expiresを30日にしたい。安全に変えて」⏳

> 生成AIは間違えることがあるので、**変更前にコミットでスナップショット**を取る癖をつけると安全です🧯 ([Firebase][5])

## 6-2. AntigravityでもMCPで“Firebaseに触れるAI”にできる🧩🤖

Firebase MCP server は Antigravity からも使えます。設定例は公式に載っていて、内部的には `firebase-tools@latest mcp` を使う形です⚙️ ([Firebase][6])

---

## 7) ミニ課題🎒✅（提出物はこれだけ！）

## ミニ課題A：PRプレビューを1回通す🔁

1. 画面の文言を1つ変える（例：ヘッダに「preview test」）✍️
2. PRを作る🧾
3. PRコメントに出たプレビューURLへアクセス👀🔗
4. 追コミットでも同じURLが更新されるのを確認🔁✨

## ミニ課題B：プレビューの寿命を言語化する⏳

* 「プレビューが何日で消えるか」
* 「消えたら困る？困らない？（運用方針）」
  を2行でメモ📝
  （Actionのデフォルトは7日、設定で変えられます） ([GitHub][2])

---

## 8) チェック✅（できたら次章へGO🚢）

* PRを作ると自動でPreview Channelが作られる✅ ([Firebase][1])
* PRにプレビューURLがコメントされる✅ ([Firebase][1])
* 追コミットで同じURLが更新される✅ ([Firebase][1])
* 「プレビューでも本物バックエンドに触れる」注意点が言える✅ ([Firebase][1])

---

## おまけ：AIサービスも絡める小ネタ🤖✨

このロードマップ全体でAIも使う前提なので、今のうちに1個だけ意識しておくと良い話👇
Firebase AI Logic はモデルの世代交代があるので、**“動いてたのに急に止まる”を避けるために、モデル名を棚卸し**する癖が役立ちます🧯（例：特定モデルが 2026-03-31 に退役予定） ([Firebase][7])

---

次の第8章で、**「マージしたらliveへ自動デプロイ」**まで完成させると、いきなり“実務っぽい開発”になりますよ😎🚢

[1]: https://firebase.google.com/docs/hosting/github-integration "Deploy to live & preview channels via GitHub pull requests  |  Firebase Hosting"
[2]: https://github.com/FirebaseExtended/action-hosting-deploy "GitHub - FirebaseExtended/action-hosting-deploy: Automatically deploy shareable previews for your Firebase Hosting sites"
[3]: https://github.com/FirebaseExtended/action-hosting-deploy/issues/17?utm_source=chatgpt.com "Add note about PRs from Forks · Issue #17"
[4]: https://firebase.google.com/docs/ai-assistance/gcli-extension "Firebase extension for the Gemini CLI  |  Develop with AI assistance"
[5]: https://firebase.google.com/docs/ai-assistance/prompt-catalog?hl=ja "Firebase の AI プロンプト カタログ  |  Develop with AI assistance"
[6]: https://firebase.google.com/docs/ai-assistance/mcp-server "Firebase MCP server  |  Develop with AI assistance"
[7]: https://firebase.google.com/docs/ai-logic?utm_source=chatgpt.com "Gemini API using Firebase AI Logic - Google"
