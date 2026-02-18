# 第16章：App Hostingを動かす（GitHub接続〜初回デプロイ）🔌

この章が終わると…👇

* リポジトリ（GitHub）を **App Hosting に接続**できる🤝
* **初回デプロイ**して、公開URLで動作確認できる🌐✨
* つまずきポイント（リポジトリが出ない・ビルド落ちる等）を **最短で切り分け**できる🧯
* Antigravity / Gemini CLI / MCP を使って「調査→修正」を加速できる🤖💨

---

## 1) まず“どう動いてるか”を1枚で🗺️

App Hosting は「Git のコミット」を起点に、だいたいこう動きます👇

* コミット検知 → **Cloud Build でビルド** 🏗️
* できた成果物 → **Cloud Run で実行** 🏃‍♂️
* 配信高速化 → **Cloud CDN でキャッシュ** ⚡
* 秘密情報 → **Secret Manager で保護** 🔐

この構成が“全部まとめて面倒見てくれる”のが App Hosting の強みです💪✨ ([Firebase][1])

---

## 2) 先にチェック✅（ここで詰まると後がしんどい）

## ✅ 課金プラン（重要）

App Hosting を始める手順の中で **Blaze へのアップグレードが必要**です💳（初回だけの壁） ([Firebase][2])

## ✅ 対応フレームワーク

公式が “しっかり面倒みるよ” と言ってるのは **Next.js と Angular** が中心。
それ以外も「アダプター」や「Nodeアプリ（build/startがある）」なら試せるけど、成功保証は弱めです⚠️ ([Firebase][3])

## ✅ Node.js（Windows）

2026-02-18 時点の Node.js は **v24 が Active LTS** 扱いです🟢 ([nodejs.org][4])
Next.js 側の最低要件としては **Node 20.9+** が明記されています（なので Node 24 ならOK寄り）([Firebase][5])

---

## 3) ルート選択🧭：最短で行くなら「Next.js」がおすすめ😆

あなたは React が中心なので、App Hosting の“動的Web/SSR”の入口として **Next.js** がいちばん自然です🧩
（Angular でもOKだけど、React勢は Next.js から入ると脳がラク🍀）

---

## 4) 手を動かす🛠️：GitHub にリポジトリを用意する（Windows）

## A. 新規で Next.js を作って push（いちばん分かりやすい）

PowerShell でOKです🪟✨

```powershell
## 1) プロジェクト作成（質問が出たら TypeScript = Yes がおすすめ）
npx create-next-app@latest my-app

cd my-app

## 2) Git 初期化 → コミット
git init
git add .
git commit -m "init"

## 3) GitHub 側で空リポジトリを作ってから、remote を追加して push
## （remote のURLはあなたのリポジトリに置き換えてね）
git branch -M main
git remote add origin <YOUR_REPO_URL>
git push -u origin main
```

> ポイント💡
>
> * monorepo（1つのリポジトリに複数アプリ）の場合でもOK。あとで「root directory」を指定できるよ👌 ([Firebase][2])

---

## 5) Firebase コンソールで App Hosting を作る🏗️（GitHub接続〜初回デプロイ）

ここからが本題！やることは大きく3つだけ👇

1. プロジェクト作成（Blaze）
2. App Hosting バックエンド作成（GitHub接続）
3. ロールアウト（初回デプロイ）

## 5-1. バックエンド作成の流れ（超重要）🧠

公式の「Get started」に沿うと、だいたいこうです👇 ([Firebase][2])

* Firebase コンソール → App Hosting → **Get started**
* **リージョン選択**（後で変えにくいので丁寧に）
* **GitHub 接続**（アプリ連携の許可）
* **リポジトリ選択**（見つからないときの対処は後述）
* **live branch** を選ぶ（たいてい `main`）
* monorepoなら **root directory** を選ぶ
* 作成 → 自動で初回ビルド/デプロイが走る🚀

## 5-2. リージョンはどう選ぶ？🌏

App Hosting は対応リージョンが増えていくタイプです。2026-02 時点の例として、
`us-central1 / us-west1 / europe-west4 / asia-east1 / asia-southeast1` などが挙げられています📍 ([Firebase][6])

日本からの体感を狙うなら、まずは **asia-east1（台湾）** や **asia-southeast1（シンガポール）** を候補にしやすいです🗾➡️🌏
（※最新の対応は拡張されるので、都度“locations”を確認してね） ([Firebase][3])

---

## 6) 初回デプロイ後の確認👀✨（ここで“達成感”が来る）

## ✅ まずはURLを開く🌐

App Hosting はデプロイ後に **専用の hosted.app ドメイン**で見えるようになります（コンソールに表示される）✨ ([Firebase][2])

## ✅ “2回目デプロイ”で動作が腹落ちする🧠

初回が出たら、次は軽く変更して push してみて👇

* 例：トップに「v2」って文字を追加
* `main` に push
* するとまた Cloud Build → Cloud Run で更新されます🔁 ([Firebase][1])

---

## 7) よくある詰まりポイント🧯（ここだけ覚えれば勝ち）

## 7-1. 「リポジトリが一覧に出ない」😇

まず **Refresh list**。それでもダメなら **GitHub 側で Grant access**（App にリポジトリ権限を追加）をやります。 ([Firebase][3])
さらに GitHub の Settings → Applications から、Firebase App Hosting アプリの **Configure** で管理できます🔧 ([Firebase][3])

## 7-2. 「GitHub以外（GitLab等）使いたい」🥲

現時点では **GitHub以外は不可**（長期ロードマップにはある）です。 ([Firebase][3])

## 7-3. 「別のGitHubアカウントに変えたい」🔄

Cloud 側の **Developer Connect** で接続を消してからやり直す流れになります。
削除対象の接続名まで公式に書いてあります（`firebase-app-hosting-github-oath` と `apphosting-github-conn-...`）。 ([Firebase][3])

## 7-4. 「App Hostingでは失敗してるのに、Cloud Buildでは平気に見える」🤔

原因が **Cloud Run 側**から来てるケースがあるので、ロールアウトの状態を確認します👀 ([Firebase][3])

---

## 8) “デプロイ前にローカルで試す”もできる🧪（安心感UP）

App Hosting には **App Hosting emulator** があって、デプロイ前のローカル検証に使えます🏠✨ ([Firebase][3])
（第16章の範囲では「存在を知っておく」だけでも十分👍）

---

## 9) AIで“詰まり”を潰す🤖🧯（Antigravity / Gemini CLI / MCP を活かす）

## 9-1. MCP server をつなぐと何が嬉しい？🧩

Firebase MCP server は、AIエージェントが Firebase を扱いやすくするための仕組みです。
公式が **Gemini CLI からの利用**も前提に説明しています。 ([Firebase][7])

たとえばこんな使い方ができます👇

* 「ビルド失敗ログの要点まとめて」📝
* 「原因っぽい設定箇所を推理して、直す手順を提案して」🧠
* 「次章の apphosting.yaml に入れる環境変数案つくって」🔐

## 9-2. MCP server の導入イメージ（コマンド例）🛠️

公式に載っている例（npm / bun）です👇 ([Firebase][7])

```powershell
## npm の例
npm install -g @firebase/mcp-server
```

```powershell
## bun の例（入っているなら）
bun add -g @firebase/mcp-server
```

> そのうえで、Gemini CLI / エージェント側に MCP を登録して使う、という流れです（設定例も公式にあります）([Firebase][7])

## 9-3. “会話”で解決するためのプロンプト例💬

詰まったとき、ログやエラー文を貼ってこう聞くと強いです👇

* 「App Hosting のロールアウトが失敗。原因の候補を3つに絞って、確認順で手順書いて」
* 「このエラー、Cloud Build由来？Cloud Run由来？切り分け方を教えて」 ([Firebase][3])
* 「GitHubのリポジトリが出ない。Grant access までの手順を短く」 ([Firebase][3])

## 9-4. FirebaseのAI（AI Logic）も“公開体験”に混ぜる🔥

App Hosting 自体が「他のFirebase製品（AI Logic含む）と一緒に使いやすい」方向で作られています。 ([Firebase][8])
この章ではまずデプロイ成功がゴールだけど、次の一手として👇

* “デプロイできた記念”に **AIで一言生成するページ**を作る（UIが一気に今っぽくなる😎）
* その後、Genkit で「リリース前チェック」を自動化（第20章で合体💥）

---

## 10) ミニ課題🎯（5〜15分）

1. App Hosting で初回デプロイ完了🚀
2. 画面のどこかに `deployed!` を入れて push 🔁
3. 変更が反映されたら、**“どのコミットが出てるか”** をメモ📝
4. 詰まったら、エラー文を AI に貼って「確認順」を作らせる🤖

---

## 11) チェック✅（できたら次章へGO！）

* [ ] GitHub 接続が完了している🤝 ([Firebase][2])
* [ ] リージョンを選べた（候補と理由が言える）🌏 ([Firebase][6])
* [ ] 初回デプロイのURLにアクセスできる🌐 ([Firebase][2])
* [ ] 1回修正→push→更新反映まで確認できた🔁 ([Firebase][1])
* [ ] リポジトリが見つからない時の対処を言える🧯 ([Firebase][3])

---

## 次の第17章へ👉✨

次は **`apphosting.yaml`** で「環境変数」「VPC」「秘密情報（Secret Manager）」「本番/検証の差分」みたいな“運用のツボ”に入ります🔐🧩
ここまで来たら、もう“それっぽい”運用が見えてくるよ〜😆🚢

[1]: https://firebase.google.com/docs/app-hosting/about-app-hosting?utm_source=chatgpt.com "Understand App Hosting and how it works - Firebase - Google"
[2]: https://firebase.google.com/docs/app-hosting/get-started "Get started with App Hosting  |  Firebase App Hosting"
[3]: https://firebase.google.com/docs/app-hosting/troubleshooting "FAQ and troubleshooting  |  Firebase App Hosting"
[4]: https://nodejs.org/en/about/previous-releases "Node.js — Node.js Releases"
[5]: https://firebase.google.com/support/release-notes/cli "Firebase CLI Release Notes"
[6]: https://firebase.google.com/docs/app-hosting/about-app-hosting "Understand App Hosting and how it works  |  Firebase App Hosting"
[7]: https://firebase.google.com/docs/ai-assistance/mcp-server "Firebase MCP server  |  Develop with AI assistance"
[8]: https://firebase.google.com/docs/app-hosting?utm_source=chatgpt.com "Firebase App Hosting"
