# 第09章：CI/CDの秘密の箱（Secrets・権限・事故防止）🧰🔐

この章は「自動デプロイが動いた！🎉」の次に、**安全に運用できる人**になるための回です😎✨
CI/CDは便利だけど、**鍵（Secrets）**と**権限（IAM）**を雑にすると事故りやすいので、ここで“防具”を装備します🛡️

---

## この章のゴール🏁（できるようになること）

* Actionsで使っている **Secretsがどこにあり、何が入っているか**説明できる🗝️
* **サービスアカウント（=自動デプロイ専用のロボ）**の権限を、必要最小限に近づけられる✂️
* 「やっちゃダメな運用」＝**事故るパターン**を避けられる🚫💥
* もし漏れた時も、**回復手順（ローテーション）**が分かる🧯

---

## まず全体像🗺️（CI/CDの“鍵”は2種類ある）

![Two Types of Keys](./picture/firebase_hosting_ts_study_009_01_two_keys.png)

CI/CDの安全は、だいたいこの2つで決まります👇

1. **GitHub側の鍵**：Secrets（暗号化保管）
2. **Firebase/Google Cloud側の鍵**：サービスアカウント（IAMロールで権限が決まる）

そして重要ポイント👇
プレビューURLは便利だけど、**本番と同じバックエンド資源に触れることがある**ので「検証だから安全〜」ではないです⚠️ ([Firebase][1])

---

## 用語ミニ辞典📖

* **Secret**：Actionsの中でだけ使える「秘密の値」🔒（APIキー、JSON鍵など）
* **サービスアカウント**：自動化用の“ロボアカウント”🤖（人間じゃない）
* **IAMロール**：権限セット🎫（できることの範囲）
* **GITHUB_TOKEN**：GitHubが自動で用意するトークン🪪（PRコメント等に使う） ([GitHub][2])
* **FIREBASE_SERVICE_ACCOUNT**：Hostingデプロイ用のサービスアカウントJSON鍵（超重要）🧨 ([GitHub][2])

---

## 読むパート📚：今回の「秘密の箱」は何が入ってる？

![Secret Storage Flow](./picture/firebase_hosting_ts_study_009_02_secret_flow.png)

HostingのGitHub連携は、セットアップ時に **サービスアカウントを作って、そのJSON鍵をGitHubのSecretsに入れる**流れになります🔐
Firebase CLIのセットアップでは、サービスアカウント作成 → GitHubに暗号化して保存（Secrets）→ workflowファイル作成、まで面倒を見てくれます🤖🧰 ([Firebase][1])

また、Action側の説明でも「サービスアカウントJSON鍵は暗号化Secretとして保存してね」と強調されています🔒 ([GitHub][2])

---

## 手を動かすパート🛠️：Secretsの場所と使われ方を確認しよう（WindowsでOK💻）

## 1) GitHubのSecretsが“存在するか”確認👀

![GitHub Secrets UI](./picture/firebase_hosting_ts_study_009_03_github_ui_mock.png)

GitHub のあなたのリポジトリで👇へ移動します🏃‍♂️💨

* Repository → **Settings**
* **Secrets and variables** → **Actions**
* **Repository secrets** を開く

ここに、だいたいこんな名前のSecretがあるはずです👇

* **FIREBASE_SERVICE_ACCOUNT**（重要🔥）

> ✅ ポイント
> **中身（JSON鍵）は表示されません**（それでOK）
> “存在していること”と“名前が合ってること”を確認するのが目的です👍

---

## 2) workflow（.github/workflows）で「どのSecretを使ってるか」確認🔍

リポジトリの `.github/workflows/` に、プレビュー用と本番用のYAMLがあるはずです📁

Actionの基本形はこんな感じ（例）👇
（※あなたの実ファイルを“読む”ための参考。コピペより確認が大事👀）

```yaml
## PRごとのプレビュー
- uses: FirebaseExtended/action-hosting-deploy@v0
  with:
    repoToken: "${{ secrets.GITHUB_TOKEN }}"
    firebaseServiceAccount: "${{ secrets.FIREBASE_SERVICE_ACCOUNT }}"
    expires: 30d

## main へpushされたら本番(live)
- uses: FirebaseExtended/action-hosting-deploy@v0
  with:
    firebaseServiceAccount: "${{ secrets.FIREBASE_SERVICE_ACCOUNT }}"
    channelId: live
```

この形自体が、公式のAction説明に沿っています🧩 ([GitHub][2])

> ✅ ここで分かること
>
> * **GITHUB_TOKEN**：PRにコメント（プレビューURL貼る）するために使う📝 ([GitHub][2])
> * **FIREBASE_SERVICE_ACCOUNT**：Firebaseにデプロイするための“鍵”🗝️ ([GitHub][2])
> * **liveデプロイはmain pushだけ**、みたいに分けると事故りにくい🚢💡 ([GitHub][2])

---

## 3) サービスアカウントの権限（IAM）を“必要最小限”に寄せる✂️

![Least Privilege Principle](./picture/firebase_hosting_ts_study_009_04_least_privilege.png)

セキュリティの基本は **最小権限（Least Privilege）** です🛡️
Firebase公式でも「必要最低限だけ付けようね」がベストプラクティスとして書かれています📌 ([GitHub][2])

Hosting GitHub Actionの手動設定ガイドでは、サービスアカウントに付けるロール例として👇が挙がっています（必要に応じて）🧾 ([GitHub][3])

* Firebase Hosting Admin（Hostingへデプロイ）
* Firebase Authentication Admin（HostingがAuthドメイン周りを触るケース用）
* Cloud Run Viewer（Cloud Runへrewrite等が絡むケース用）
* API Keys Viewer（API keyの参照が必要になるケース用） ([GitHub][3])

> ✅ 初学者のコツ
> まずは「自分の構成で何が必要か」を知るのが大事です🙂
> 追加ロールは“困った時に足す”のが安全（最初から盛り盛りにしない）🍚❌

---

## 事故防止パート🧯：よくある“やらかし”と対策

## 事故①：PR（特にfork）からSecretsが漏れる😱

![PR Target Risk](./picture/firebase_hosting_ts_study_009_05_pr_target_risk.png)

基本的に、**forkから来たPRのワークフローにはSecretsが渡らない**ので、そこは守られています🔒 ([GitHub Docs][4])
でも！例外的に危険パターンがあります👇

* **pull_request_target** を使うと、PRのコード次第でSecretsが読まれる事故の可能性が上がる⚠️ ([GitHub Docs][4])

> ✅ 対策
>
> * 公式セットアップのまま（むやみにイベントを変えない）🧠
> * 不特定多数のPRを受けるOSSは、デプロイ系ワークフローを特に慎重に🧨

---

## 事故②：本番へ“うっかり自動デプロイ”🚨

「PRでもliveへ出しちゃう」構成は事故りやすいです💥
Actionの例のように👇が基本の安全設計です👍 ([GitHub][2])

* PR：preview channel にだけ出す🔎
* main：push（=マージ後）で live に出す🚢

---

## 事故③：ログに秘密が出る📜💣

Secretsは**値を表示しない**のが鉄則です🙅‍♂️
とくに危険なのが👇

* デバッグ目的で `echo` してしまう
* シェルのデバッグ出力をONにして、環境変数がダダ漏れ

> ✅ 対策
>
> * “秘密は出力しない”をチームルール化📌
> * Actionsログにそれっぽい文字列が出てないか、失敗時に一応チェック👀

---

## ミニ課題✍️：「漏れたらヤバい／別にOK」を仕分けしよう🧠

次の2カテゴリに分けて、自分の言葉で1行メモしてみてください🙂📝

## 🔥 漏れたらヤバい（基本Secret）

* **FIREBASE_SERVICE_ACCOUNT（サービスアカウントJSON鍵）** 🧨 ([GitHub][2])
* 外部APIの“課金できる”キー（例：生成AIプロバイダのキー）💳

## 🙂 別にOK（ただし運用は丁寧に）

* FirebaseのWeb APIキー（※一般に“完全な秘密”ではないが、制限は大事）🔑 ([Firebase][5])
* 公開URL、プロジェクトID、チャンネルIDなど（公開情報）🌐

---

## 漏れた時の回復手順🧯（これだけ覚えとけば勝てる）

![Key Rotation Cycle](./picture/firebase_hosting_ts_study_009_06_key_rotation.png)

もし「やば、鍵貼っちゃった😨」となったら、順番はこれ👇

1. **GitHubのSecretを差し替える（新しい鍵にする）**🔁
2. 古いサービスアカウント鍵を **無効化/削除**（ローテーション）🗑️
3. Actionsのログや履歴を見て「いつから漏れたか」ざっくり確認👀
4. 念のため、Firebase側の不審なデプロイ/操作がないか確認🕵️

---

## AIも絡める🤖✨：Secrets・権限チェックを“AIにレビューさせる”

ここからAI機能が効いてきます🔥

## 1) コンソールで詰まったら、Geminiに聞く🧯

Gemini in Firebase は、利用に必要な権限（ロール）があり、プロジェクトの権限設計にも関係します👤🔐 ([Firebase][6])
「このサービスアカウントに何のロールが付いてる？」「最小権限にするとしたらどれ？」みたいな質問が相性いいです🙂

## 2) Antigravity / Gemini CLI × Firebase MCP server で“点検を自動化”🧩

![AI Security Audit](./picture/firebase_hosting_ts_study_009_07_ai_audit.png)

Firebase MCP server は **Antigravity や Gemini CLI** などのMCPクライアントと一緒に使えます🤝 ([Firebase][7])
さらに、Antigravity側にFirebase MCP serverを追加する手順も公式で案内されています🧰 ([Firebase][8])

> できること（イメージ）
>
> * 「今あるHostingのチャンネル一覧出して」📄
> * 「最近のデプロイの失敗理由を要約して」🧠
> * 「workflowのYAML、Secretsの扱いが危険じゃないかチェックして」🔍

（※“本番操作”を自動でやらせる前に、まずは**調査・点検**用途から始めるのが安全です👍）

---

## さらに一歩：AIキー等の“アプリ側Secrets”はどこに置く？🤔🔐

CI/CDのSecrets（GitHub側）とは別に、今後 **Functions + AI（Genkitなど）**をやると「実行環境のSecrets」が増えます📈

Cloud Functionsは **環境変数**や **Secret Manager** を使った安全な管理方法が公式で用意されています🔒 ([Firebase][9])
→ 「GitHub Secretsに全部入れる」より、**実行環境の仕組みで守る**ほうが設計としてきれいになりやすいです🧠✨

---

## 最終チェック✅（この章の合格ライン）

* Actionsで **FIREBASE_SERVICE_ACCOUNT** を参照している箇所を見つけられる🗝️ ([GitHub][2])
* サービスアカウントのロールを「必要なら足す」方針で説明できる✂️ ([GitHub][3])
* **pull_request_targetは危険寄り**と分かる⚠️ ([GitHub Docs][4])
* 「漏れたらローテーション！」の手順を言える🔁🧯

---

次の第10章は「ログの見方＆典型エラー」なので、ここで作った“安全土台”がそのまま効きます🧯✨
もしよければ、あなたの `.github/workflows`（中身のSecret値は消した状態でOK🙆‍♂️）を貼ってくれたら、**事故りにくい形になってるか**チェック観点で一緒に見れます👀🔍

[1]: https://firebase.google.com/docs/hosting/github-integration "Deploy to live & preview channels via GitHub pull requests  |  Firebase Hosting"
[2]: https://github.com/marketplace/actions/deploy-to-firebase-hosting "Deploy to Firebase Hosting · Actions · GitHub Marketplace · GitHub"
[3]: https://raw.githubusercontent.com/FirebaseExtended/action-hosting-deploy/main/docs/service-account.md "raw.githubusercontent.com"
[4]: https://docs.github.com/ja/actions/reference/workflows-and-actions/events-that-trigger-workflows "ワークフローをトリガーするイベント - GitHub ドキュメント"
[5]: https://firebase.google.com/docs/projects/api-keys?utm_source=chatgpt.com "Learn about using and managing API keys for Firebase - Google"
[6]: https://firebase.google.com/docs/ai-assistance/gemini-in-firebase/set-up-gemini?utm_source=chatgpt.com "Set up Gemini in Firebase - Google"
[7]: https://firebase.google.com/docs/ai-assistance/mcp-server?utm_source=chatgpt.com "Firebase MCP server | Develop with AI assistance - Google"
[8]: https://firebase.google.com/docs/crashlytics/ai-assistance-mcp?utm_source=chatgpt.com "AI assistance for Crashlytics via MCP - Firebase"
[9]: https://firebase.google.com/docs/functions/config-env?utm_source=chatgpt.com "Configure your environment | Cloud Functions for Firebase"
