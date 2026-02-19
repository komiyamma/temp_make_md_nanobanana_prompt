# 第10章：失敗しても焦らない（ログの見方＆典型エラー）🧯

この章は「CI/CDがコケた😇→でも最短で復旧できる💪」を身につける回です！
コツは **“どこで失敗したか” を切り分けて、当たりをつけて直す** だけ🕵️‍♀️✨
（公式の GitHub 連携ドキュメントは 2026-02-05 更新で内容が新しめです📚）([Firebase][1])

---

## この章のゴール🏁✨

* GitHub Actions の **どのステップが赤いか** を見て、原因を3分で特定する⏱️🔍
* よくある失敗（Secrets/権限/プロジェクト指定/プレビュー期限など）を “辞書” で潰せる📕🧯
* わざと壊して→直して→復旧までを体験して、心が折れなくなる🧠💪
* AI（Gemini / Antigravity / Gemini CLI / MCP）で **ログ読解を爆速** にする🤖⚡ ([Firebase][2])

---

## 読む📚：トラブル対応は「3段ロケット」で勝てる🚀🚀🚀

CI/CDの失敗は、だいたいこの3つのどれかです👇

![Troubleshooting Categories](./picture/firebase_hosting_ts_study_010_01_failure_types.png)

1. **ビルドで失敗**（依存関係/TypeScript/テスト/Nodeの差）🏗️💥
2. **デプロイで失敗**（Firebase認証/Secrets/プロジェクト指定/権限）🚢💥
3. **デプロイ成功なのに挙動が変**（publicフォルダ違い/キャッシュ/設定ミス）😵‍💫

なので、見る順番は固定でOK👇✨

## ① Actionsの「赤い行」を1個だけ探す🔴👀

![Finding the Error Source](./picture/firebase_hosting_ts_study_010_02_red_line_check.png)

* リポジトリの **Actions** タブ → 失敗した Run を開く
* 左側の Job で赤い❌をクリック
* ログの中で **一番最初に出たエラー行** を探す（下に行くほど二次被害ログなので注意）🧠

## ② “ビルド” か “デプロイ” かを決める⚖️

![Build vs Deploy Logic](./picture/firebase_hosting_ts_study_010_03_build_vs_deploy.png)

* `npm ci` / `npm install` / `npm run build` が落ちてる → **ビルド系**
* `firebase deploy` / `action-hosting-deploy` が落ちてる → **デプロイ系**

## ③ 同じ失敗を「ローカルで再現」できると勝ち確🎯

CIのログだけだとツラいので、ローカル（Windows）で👇を試すと一気にラクになります。

```powershell
npm ci
npm run build
```

ここで再現したら、もうほぼ勝ちです😎✨

---

## 手を動かす🛠️：ログの「見る場所マップ」を体に入れる🧭

## 1) “デプロイ先” の情報を押さえる（どこへ出してる？）🗺️

![Configuration Map](./picture/firebase_hosting_ts_study_010_04_config_locations.png)

GitHub連携は、CLIがいろいろ自動で作ってくれます👇([Firebase][1])

* Hosting にデプロイできる **サービスアカウント** を作る
* その鍵（JSON）を **GitHub Secrets** に入れる
* `.github/workflows/*.yml` を生成する

つまり、困ったら見る場所はこの3つ👇

* `.github/workflows/`（Actionsの手順書📄）
* GitHub Secrets（鍵🔐）
* `.firebaserc`（どのFirebaseプロジェクトか🎯）

---

## 2) “プロジェクト指定ミス” を最速で見抜く🎯🧠

![Missing Project ID](./picture/firebase_hosting_ts_study_010_05_project_id_check.png)

デプロイActionには `projectId` があって、**未指定なら `.firebaserc` が必要**です。([GitHub][3])

なので、典型パターンはこのどちらか👇

* **A**：workflow に `projectId:` を書く
* **B**：`.firebaserc` をコミットしておく（CIが参照できるようにする）

「.firebaserc が無いのに projectId も無い」だと、CIが迷子になって落ちやすいです😵‍💫

---

## 3) Preview の期限が短すぎ問題（7日デフォ）⏳🧨

![Preview Channel Lifecycle](./picture/firebase_hosting_ts_study_010_06_preview_expiry.png)

プレビューURLが突然消えるの、地味にビビります😂
でもデフォは **7日**、そして延長方法がちゃんとあります。([Firebase][4])

* Action側：`expires`（空なら7日）([GitHub][3])
* CLI側：`--expires 7d`（最大30日）([Firebase][4])

---

## 典型エラー辞典📕🧯（よく出る順）

ここからは “見たらこれ” のやつだけ集めます💡
※ログの全文をAIに貼る時は **Secretsは絶対に消してから**ね！🔐🧼（後でAI活用でやります）

---

## エラー1：Secrets が見つからない／空っぽ🔐❌

![Fork PR Security Block](./picture/firebase_hosting_ts_study_010_07_fork_secrets_block.png)

**症状**

* `FIREBASE_SERVICE_ACCOUNT_...` が無い
* `Error: Failed to authenticate` 系

**原因あるある**

* Secrets名を変えちゃった
* workflowが Secrets を参照してない
* PRが **fork から来てる**（重要！）

**対処**

* GitHubの「Settings → Secrets」を確認
* fork PR の場合：**fork由来の `pull_request` では Secrets が渡らない**のが仕様です。([GitHub Docs][5])

  * 学習では「同一リポジトリ内ブランチでPR」を基本にすると安全＆簡単👍

---

## エラー2：`Resource not accessible by integration`（PRコメントできない等）🧷❌

**症状**

* 途中まで動くのに、PRへのコメントや更新で落ちる

**原因あるある**

* GitHub Actionsの権限が “読み取りだけ” になってる

**対処（定番）**

* リポジトリ設定で Actions の Workflow permissions を **Read and write** にする（画面から）([Stack Overflow][6])
* workflow 側にも `permissions:` を書く（例：PRにコメントするなら `pull-requests: write`）✍️

---

## エラー3：プレビューが増えすぎて `quota reached` / 429 💣

**症状**

* `channel quota reached`
* `429` 系でプレビュー作れない

**原因あるある**

* PRが大量（Dependabot祭り🎉）でプレビューチャンネルが溜まる

**対処**

* 古いプレビューを消す（CLIでもコンソールでもOK）🧹

  * チャンネル削除コマンドは公式にあります。([Firebase][4])
* 期限を短くする / 必要なPRだけプレビューにする（運用でコントロール）🧠

（「だいたい50くらいで当たる」系の話もありますが、まずは “不要チャンネル削除” が正攻法です🧹）([Stack Overflow][7])

---

## エラー4：プレビュー期限が切れてURLが死んだ😇⏳

**症状**

* 昨日まで見れてたプレビューURLが 404

**原因あるある**

* 7日で自動失効（デフォ）([Firebase][4])

**対処**

* `expires` を延長（ただし最大30日）([Firebase][4])
* そもそも「レビュー終わったPRは閉じたらプレビュー消す」運用にするとスッキリ✨

---

## エラー5：Node/依存関係が合わずビルドが死ぬ🏗️💥

**症状**

* `npm ci` が失敗（lockfile不一致など）
* `npm run build` が失敗（TypeScriptエラーなど）

**対処の型**

* CIとローカルで Node のバージョンを揃える（LTS推し）🟩

  * 2026-02時点だと Node は v24 が Active LTS、v25 が Current です。([nodejs.org][8])
* TypeScriptは安定版（5.9系）を使うのが無難、6.0 betaも出てるので遊ぶなら分離が安全🎮
  ([Microsoft for Developers][9])

---

## ミニ課題📝：わざと壊して、ログから復旧せよ🧨➡️🧯

目的は「失敗しても大丈夫」を体に入れること💪✨

## お題：TypeScriptエラーを1個入れて、CIを落として、直して復旧する😈

1. 新しいブランチ作る🌿
2. Reactのどこかで、わざと型エラーを作る（例：numberに文字列）
3. PR作る → Actionsが落ちるのを確認🔴
4. Actionsログで「どのステップが赤いか」を特定🔍
5. エラーを直してpush → PRが復旧🟢

型エラー例（イメージ）👇

```ts
const x: number = "nope"; // わざと
```

---

## チェック✅：この章を終えたら言えること🎤✨

* 「CIが落ちたら、まず **赤いステップ** を見る」って言える👀
* 「ビルド落ち / デプロイ落ち / 成功したのに挙動変」へ仕分けできる🧠
* `.firebaserc` と `projectId` の関係を説明できる🎯([GitHub][3])
* プレビューは7日で消える＆伸ばせる（最大30日）って言える⏳([Firebase][4])
* fork PR では Secrets が渡らない仕様を知ってる🔐([GitHub Docs][5])

---

## AI活用🤖⚡：ログ読解を “1分” にするコツ

## 1) Firebaseコンソールの Gemini を「相談役」にする🧯💬

コンソール右上の ✦Gemini からチャットできます。([Firebase][10])
おすすめの聞き方👇

* 「この Actions ログのエラー行（※Secrets消した）から、原因候補を3つに絞って。優先順位も。」
* 「`.firebaserc` がない時に `projectId` をどう指定するのが安全？」([GitHub][3])

## 2) Antigravity × Firebase MCP で “調査→操作” をまとめる🧩🤝

Firebase MCP は Antigravity や Gemini CLI から使えます。([Firebase][2])
Antigravity 側は MCP Store から入れられる流れが紹介されています。([The Firebase Blog][11])

たとえば Antigravity のエージェントにこう言う感じ👇

* 「Hosting のプレビューチャンネル一覧を見て、古いのを消して。quota 対策も提案して」🧹
  （※実体は `firebase hosting:channel:*` を叩く流れになりやすいです。削除コマンド自体は公式にあります。）([Firebase][4])

## 3) Gemini CLI も “Firebase拡張” で寄り道が減る🧠🧰

Firebase MCP のページでは、Gemini CLI には Firebase拡張を入れるのが推奨されています。([Firebase][2])

---

## ⚠️ 超大事：AIに貼っていい情報／ダメな情報🔐🧼

* ✅貼ってOK：エラー行、スタックトレース、workflowの一部（Secrets参照部分は伏せる）
* ❌貼っちゃダメ：秘密鍵、サービスアカウントJSON、APIキーそのまま、トークン類

Firebase AI Logic を使うなら、APIキーの制限など “本番チェックリスト” も目を通すと安全度が上がります🛡️([Firebase][12])
（AI系はモデルの入れ替わりもあるので、固定してると将来ハマることがあるよ〜！）([Firebase][13])

---

次の章（第11章）は **HTTPS＋カスタムドメインで“ちゃんとしたサイト感”** を出す回ですね🔒🌐
第10章の内容をベースに、次は「DNSで詰まってもログとAIで解く」って流れに繋げられます😆🚀

[1]: https://firebase.google.com/docs/hosting/github-integration "Deploy to live & preview channels via GitHub pull requests  |  Firebase Hosting"
[2]: https://firebase.google.com/docs/ai-assistance/mcp-server "Firebase MCP server  |  Develop with AI assistance"
[3]: https://github.com/marketplace/actions/deploy-to-firebase-hosting "Deploy to Firebase Hosting · Actions · GitHub Marketplace · GitHub"
[4]: https://firebase.google.com/docs/hosting/manage-hosting-resources "Manage live & preview channels, releases, and versions for your site  |  Firebase Hosting"
[5]: https://docs.github.com/actions/security-guides/using-secrets-in-github-actions?utm_source=chatgpt.com "Using secrets in GitHub Actions"
[6]: https://stackoverflow.com/questions/75514653/firebase-action-hosting-deploy-fails-with-requesterror-resource-not-accessible?utm_source=chatgpt.com "Firebase action-hosting-deploy fails with RequestError ..."
[7]: https://stackoverflow.com/questions/64832404/firebase-preview-channels-quota-reached?utm_source=chatgpt.com "Firebase preview channels quota reached"
[8]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[9]: https://devblogs.microsoft.com/typescript/?utm_source=chatgpt.com "TypeScript"
[10]: https://firebase.google.com/docs/ai-assistance/gemini-in-firebase/try-gemini?utm_source=chatgpt.com "Try Gemini in the Firebase console"
[11]: https://firebase.blog/posts/2025/11/firebase-mcp-and-antigravity/ "Antigravity and Firebase MCP accelerate app development"
[12]: https://firebase.google.com/docs/ai-logic/production-checklist?hl=ja&utm_source=chatgpt.com "Firebase AI Logic を使用するための本番環境チェックリスト"
[13]: https://firebase.google.com/docs/ai-logic?utm_source=chatgpt.com "Gemini API using Firebase AI Logic - Google"
