# 第06章：Preview Channel入門（プレビューURLを作る）🔎

この章では、**本番（live）を触らずに**「見せてOKなURL」をサクッと作ります✨
Firebase Hosting には **live チャンネル**と、追加で作れる**preview チャンネル**があり、preview は **一時的な共有URL**（`SITE_ID--CHANNEL_ID-RANDOM_HASH.web.app` みたいな形）で配れます📮([Firebase][1])

---

## まず理解：Preview Channelってなに？🤔🧠

* **live チャンネル**：本番サイト（普段見られてるURL）🏟️
* **preview チャンネル**：開発版サイト（期限付きの共有URL）🧪⏳
* preview URL は **ランダムハッシュ入りで推測されにくい**けど、**公開URL**なので「知ってる人はアクセスできる」点は要注意⚠️([Firebase][2])
* さらに大事：preview URL のアプリは、**基本的に“本物のバックエンド”に接続**します（Firestore/Auth/Storage など）。例外は rewrite で **pinTag された関数**などだけです🧨([Firebase][2])

※ preview channels は **beta 扱い**で、仕様が変わる可能性があります🧪([Firebase][1])

---

## 今日のゴール🏁✨

1. preview チャンネルを作って、**プレビューURLを表示できる**🌐
2. 期限（expires）を付けて、**放置事故を防ぐ**⏳
3. list / open / delete で、**チャンネル管理ができる**🧹

---

## 手を動かす：プレビューURLを作る（Windows / PowerShell想定）🛠️💻

## 0) 30秒の事前チェック✅

「CLI が動く・ログインできてる」だけ確認します。

```powershell
firebase --version
firebase projects:list
```

* もしログインが必要なら `firebase login`（ブラウザが開きます）🔐
* プロジェクトを切り替えるなら `firebase use`（候補が出ます）🎯

---

## 1) Reactをビルドする🏗️📦

preview チャンネルは「いまのビルド成果物」を配るので、まずビルドします。

```powershell
npm install
npm run build
```

> ここで生成されるフォルダ（例：`dist` や `build`）が、前章までで設定した `firebase.json` の `hosting.public` と合ってる前提です📁

---

## 2) preview チャンネルへデプロイする🚀🔎

`CHANNEL_ID` は **スペースなし**でOK（例：`pr-123`、`feature-login` など）🏷️([Firebase][2])

```powershell
firebase hosting:channel:deploy pr-123 --expires 7d
```

* `--expires` は **最大 30日**まで（`h`/`d`/`w` が使える）⏰([Firebase][1])
* 何も付けない場合、**デフォルトは7日**で期限切れになります📅([Firebase][1])
* CLIが **プレビューURL** を返します（`PROJECT_ID--CHANNEL_ID-RANDOM_HASH.web.app` の形）🌐([Firebase][2])

💡ポイント：このコマンドは **チャンネルが無ければ作ってからデプロイ**してくれます（create不要）✨([Firebase][1])

---

## 3) すぐブラウザで開く👀🧭

```powershell
firebase hosting:channel:open pr-123
```

* ブラウザが開けない状況でも **URLを返してくれる**ので、それをコピペでOKです📋([Firebase][1])

---

## 4) ちょい修正して「同じURL」に上書きする🔁✨

preview は “使い捨てURL” というより、**同じチャンネルIDに何回でも載せ替え**できます。

1. Reactを少し直す ✏️
2. またビルド 🏗️
3. 同じIDへデプロイ 🚀

```powershell
npm run build
firebase hosting:channel:deploy pr-123 --expires 7d
```

---

## チャンネル管理（覚えると運用っぽくなる）🧹📋

## 一覧を見る📜

```powershell
firebase hosting:channel:list
```

live も preview も一覧に出ます👀([Firebase][1])

## 期限の挙動（地味に大事）⏳

* 期限が来ると、チャンネルと関連リリース/バージョンは **24時間以内に削除予定**になります🗑️([Firebase][1])
* 既存チャンネルに `--expires` を付けずにデプロイしても、**期限が近いと自動延長**される挙動があります（「新デプロイから7日」へ）📆([Firebase][1])

## 消す（掃除）🧼

```powershell
firebase hosting:channel:delete pr-123
```

削除も **24時間以内に整理される**イメージです🗑️([Firebase][1])

---

## よくあるハマりどころ（先回り）🧯😵‍💫

## ❶ 「プレビューで動かしたら、DBの中身が変わった！」💥

preview URL は基本 **本物のバックエンド**につながるので、テストでも書き込み処理があると普通に反映されます⚠️([Firebase][2])
対策アイデア👇

* テスト用データ（コレクション名に `dev_` を付ける等）に寄せる🧪
* 重要な操作（削除/課金/送信）には確認ダイアログを入れる🛡️
* 将来は staging プロジェクト運用（第14章へ）🏗️

## ❷ 「期限切れでURLが死んだ」🪦

デフォルト7日です。長めに残すなら最初から付けちゃうのが安全🙆‍♂️([Firebase][1])

## ❸ 「Functions/Cloud Run への rewrite がプレビューで思ったのと違う」🤯

Hosting の rewrite 先（Functions/Cloud Run）は、基本 **本物に当たりがち**です。
preview チャンネルでも rewrite をちゃんと “プレビュー” したいときは、`pinTag` を使うと「静的ファイル＋rewrite先」を同期して確認しやすくなります📌([Firebase][3])

---

## AI活用：Preview Channelを“詰まらず”回す🤖⚡

## 1) Firebase MCP server を入れると、AIからFirebase操作がやりやすい🧩

Firebase MCP server は **Antigravity / Gemini CLI / Firebase Studio** などのMCPクライアントで使えます🛠️([Firebase][4])

**Gemini CLI** なら、公式の Firebase 拡張を入れるルートが推奨されています👇([Firebase][4])

```bash
gemini extensions install https://github.com/gemini-cli-extensions/firebase/
```

すると例えば👇みたいなお願いが通しやすくなります💬✨

* 「いまのリポジトリ用に、preview チャンネルの命名規則を提案して」🏷️
* 「`firebase hosting:channel:*` の運用手順をRunbookにして」🧾
* 「プレビューURLは公開扱いだよね？注意点まとめて」⚠️

## 2) コンソールの Gemini in Firebase で詰まりを相談🧯

権限・有効化などのセットアップ導線が公式にまとまってます（プロジェクト単位・ユーザー単位で有効化）🧠([Firebase][5])
デプロイ失敗時の「ログの読み方」「権限の不足」あたりは、チャットで相談すると立て直しが速いです🚑

## 3) Firebase AI Logic を“プレビューで”試す（安全にUX確認）🤖🧪

AI機能（文章生成/要約など）を入れてる場合、まず preview URL で

* UIが破綻しないか
* 料金や制限にひっかからないか
  を確認しやすいです✨（AI Logic 自体の概要）([Firebase][6])

---

## ミニ課題（10〜15分）🧩📝

1. preview チャンネルを2つ作る

* `pr-1`（期限 1日）
* `try-cache`（期限 12時間）

```powershell
firebase hosting:channel:deploy pr-1 --expires 1d
firebase hosting:channel:deploy try-cache --expires 12h
```

2. `firebase hosting:channel:list` で **live と一緒に並んでる**のを確認👀([Firebase][1])
3. `pr-1` を `firebase hosting:channel:delete pr-1` で消してお掃除🧼([Firebase][1])

---

## チェック✅（言えたら勝ち🏆）

* preview チャンネルは **一時的な共有URL**を作る仕組みだと言える🌐([Firebase][2])
* preview URL は **推測されにくいが公開URL**だと言える⚠️([Firebase][2])
* `firebase hosting:channel:deploy/open/list/delete` を使い分けできる🛠️([Firebase][1])
* 期限（7日デフォルト、最大30日、`--expires`）を説明できる⏳([Firebase][1])
* preview は **本物バックエンドに接続しがち**なので注意できる🔥([Firebase][2])

---

## 次章へのつなぎ🎬🤝

第6章で「手動でプレビューURLを作れた」ので、次の第7章ではそれを **GitHub のPRごとに自動化**して、URLが勝手に生える世界に入ります🤖🔁

---

必要なら、第6章の最後に「チャンネル命名ルール（チーム用テンプレ）」も、**3パターン**くらい（小規模/個人・チーム・公開OSS）で作って載せられます🏷️✨

[1]: https://firebase.google.com/docs/hosting/manage-hosting-resources "Manage live & preview channels, releases, and versions for your site  |  Firebase Hosting"
[2]: https://firebase.google.com/docs/hosting/test-preview-deploy "Test your web app locally, share changes with others, then deploy live  |  Firebase Hosting"
[3]: https://firebase.google.com/docs/hosting/full-config "Configure Hosting behavior  |  Firebase Hosting"
[4]: https://firebase.google.com/docs/ai-assistance/mcp-server "Firebase MCP server  |  Develop with AI assistance"
[5]: https://firebase.google.com/docs/ai-assistance/gemini-in-firebase/set-up-gemini "Set up Gemini in Firebase"
[6]: https://firebase.google.com/docs/ai-logic?utm_source=chatgpt.com "Gemini API using Firebase AI Logic - Google"
