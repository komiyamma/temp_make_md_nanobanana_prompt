# 第08章：本番（live）自動デプロイ（マージで反映）🚢

この章は **「PRでプレビュー確認 → マージしたら本番URLが自動で更新」** を完成させる回です！
“世に出す” 感が一気に出ます😆🌍

---

## 1) まずイメージをつかもう🧠🔁

![CI/CD Pipeline Concept](./picture/firebase_hosting_ts_study_008_01_pipeline_concept.png)

## PRのとき（プレビュー）🧪

* PRを作る → **プレビューURL** ができる
* そこで動作確認＆レビューできる👀✨
  （※プレビューも本番も、基本は “実在のバックエンド資源” を触り得るので、やらかし防止は意識しようね⚠️）([Firebase][1])

## マージしたとき（本番 live）🚀

* PRを **main**（または master）にマージ
* すると **main に push が発生**
* その push をトリガーに **GitHub Actions が動いて、live へデプロイ** 🎉
  「マージ＝本番反映」まで自動化されます🤖([Firebase][1])

---

## 2) 手を動かす🛠️🔥（“マージでlive反映”を完成させる）

## Step 0：まずは「本番デプロイ用ワークフロー」があるか確認👀

![Action Trigger Logic](./picture/firebase_hosting_ts_study_008_02_trigger_config.png)

リポジトリのここ👇を見てね：

* `.github/workflows/`

だいたい、以下みたいな **“merge / prod / live”** 系の yml が入ってます（CLIが作ることも多い）([Firebase][1])

ポイントは2つ👇

* `on: push` で `branches: [main]`（main に push されたら走る）
* `FirebaseExtended/action-hosting-deploy` で `channelId: live`（liveへ出す）([GitHub][2])

---

## Step 1：CIの Node.js は「24 LTS」を基準にしよう🟩

![Node.js Version Policy](./picture/firebase_hosting_ts_study_008_03_node_version.png)

2026年2月時点だと **Node 24 が Active LTS** です。([nodejs.org][3])
さらに GitHub 側も **runnerの既定Nodeが 2026-03-04 から Node24 へ寄る** 動きがあるので、ワークフローでバージョン固定しておくのが安心です🧷([The GitHub Blog][4])

---

## Step 2：本番デプロイ用 workflow（例）📄

![YAML Code](./picture/firebase_hosting_ts_study_008_08_yaml_code.png)


あなたの yml がすでにあるなら「確認＆調整」が中心。無いなら、雰囲気はこう👇
（※コードブロックは例だよ。手元の構成に合わせてね）

```yaml
name: Deploy to Live Channel

on:
  push:
    branches:
      - main

jobs:
  deploy_live:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v6
        with:
          node-version: 24
          cache: npm

      - run: npm ci
      - run: npm run build

      - uses: FirebaseExtended/action-hosting-deploy@v0
        with:
          firebaseServiceAccount: ${{ secrets.FIREBASE_SERVICE_ACCOUNT }}
          projectId: your-firebase-project-id
          channelId: live
```

この形の“根拠”は、Actionの公式READMEに **「push to main で live に出す例」** が明記されてます。([GitHub][2])

---

## Step 3：Secrets（鍵）が入ってるか確認🔐

![Secrets Management](./picture/firebase_hosting_ts_study_008_04_secrets_vault.png)

`FIREBASE_SERVICE_ACCOUNT` は **サービスアカウントJSONキー** で、GitHubの **Encrypted Secrets** に入れて使います。
（漏れると普通に危険😇）([GitHub][2])

> ここが無い／名前が違うと、ほぼ確実に本番デプロイが落ちます💥

---

## Step 4：実際に「PR→マージ→本番更新」を回す🔁🚢

![Merge to Deploy Flow](./picture/firebase_hosting_ts_study_008_05_merge_deploy.png)

Windows での流れはこんな感じ（GitHub操作でもOK）👇

1. ちょい変更を入れる（例：ヘッダー文言を変える）✏️
2. PRを作る → プレビューURLで確認👀
3. PRを main にマージ🎯
4. GitHub の Actions タブで “Deploy to Live” が走るのを確認🏃‍♂️💨
5. 本番URLをリロードして反映確認🌐✨

ローカルからやるなら例👇

```powershell
git checkout -b feature/live-banner
## 何か1行だけUI変更する（src/App.tsx とか）
git add .
git commit -m "Update banner text"
git push -u origin feature/live-banner
```

---

## 3) 反映できたか確認するコツ✅📸

## いちばん確実なのは「見た目でわかる差分」を入れる👀

![Visual Verification](./picture/firebase_hosting_ts_study_008_06_visual_diff.png)

* 例：ページ上部に「v1」「v2」みたいな文字を一瞬入れる
* マージ前（プレビュー）と、マージ後（本番）の **スクショ比較** が強い📸✨

## もう一段ちゃんと見るなら

* GitHub Actions のログで「デプロイ完了」まで到達しているか確認🧾
* Firebase Hosting 側の “リリース履歴” で更新時刻を見る（UIで確認）⌚

---

## 4) よくある詰まりポイント集🧯（初心者がハマりがち）

## ❌ 「Actionsは成功なのに、本番の表示が変わらない」

* **ビルド成果物の置き場所** と `firebase.json` の `public`（または設定）がズレてる可能性大📦🌀
* 「ビルドして生成されるフォルダ（例：`dist` や `build`）」が、Hostingが配る対象になってるか確認しよう

## ❌ 「Secretsがない/名前違いでコケる」

* `FIREBASE_SERVICE_ACCOUNT` の名前がズレてると即死しがち💥([GitHub][2])

## ❌ 「mainじゃなくてmaster運用」

* workflow の `branches:` が **今の運用ブランチ名** と一致してないと発火しないよ⚠️

## ❌ 「モノレポで関係ない変更でも毎回デプロイされる」

![Monorepo Path Filter](./picture/firebase_hosting_ts_study_008_07_monorepo_filter.png)

* `paths:` で絞ると気持ちいい😌

```yaml
on:
  push:
    branches: [main]
    paths:
      - "web/**"
      - ".github/workflows/**"
```

---

## 5) AIで“詰まり”を即解決🤖🧯（この章のうま味ポイント）

## A) Antigravity × Firebase MCP：デプロイ作業をAIに寄せられる🧩🚀

Antigravity は Firebase MCP server を使って、Hosting へのデプロイ計画→実行まで支援できます（`firebase deploy --only hosting` を含む流れをAIが案内）([The Firebase Blog][5])

使い方イメージ（プロンプト例）💬✨

* 「PRをマージしたらliveに出るはず。GitHub Actionsのymlを見て、発火条件とデプロイ先が正しいか点検して」
* 「`channelId: live` になってる？ Secrets名は合ってる？」([GitHub][2])

## B) Gemini in Firebase：コンソール内で“詰まり相談”できる🧠💡

Firebase コンソール右上の ✦ から Gemini ペインを開いて相談できます。([Firebase][6])
（エラー文を貼って「原因候補→次の確認手順」を出させるのが強い💪）

## C) Gemini CLI：Firebase拡張（MCP）で調査を寄せる🔎💻

Firebase MCP server は **Gemini CLI とも相性よく作られてる** ので、CLI上での調査・操作がやりやすいです。([Firebase][7])

---

## 6) ミニ課題🎯（10〜20分）

## 課題：PR→マージ→本番反映を“証拠付き”で完了しよう📸✅

![Assignment Evidence](./picture/firebase_hosting_ts_study_008_09_assignment.png)


1. 画面のどこかに「Hello Live v1」みたいな表示を追加✍️
2. PR作成 → プレビューURLで表示確認👀
3. mainへマージ🚢
4. Actions成功ログを確認🧾
5. 本番URLで「Hello Live v1」が出るスクショ撮影📸
6. PR画面に “証拠” としてスクショ貼る（自分用メモでOK）📝

---

## 7) チェック✅（できたら合格！）

![Final Check](./picture/firebase_hosting_ts_study_008_10_check.png)


* [ ] PRでプレビューURLを見れて、変更が確認できた👀
* [ ] マージ後に GitHub Actions が **push(main)** で動いた🏃‍♂️([GitHub][2])
* [ ] live（本番URL）が更新された🌍✨
* [ ] `FIREBASE_SERVICE_ACCOUNT` が Secrets に入っていて、漏らしちゃいけない理解がある🔐([GitHub][2])
* [ ] （できれば）“見た目でわかる差分”＋スクショで証拠が残せた📸

---

次の第9章は「Secrets・権限・事故防止」をガッツリ固める回だけど、
第8章が回るだけで **“自動リリース体験”が一気に現実になります** 😎🚢✨

[1]: https://firebase.google.com/docs/hosting/github-integration "Deploy to live & preview channels via GitHub pull requests  |  Firebase Hosting"
[2]: https://github.com/FirebaseExtended/action-hosting-deploy "GitHub - FirebaseExtended/action-hosting-deploy: Automatically deploy shareable previews for your Firebase Hosting sites"
[3]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[4]: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/?utm_source=chatgpt.com "Deprecation of Node 20 on GitHub Actions runners"
[5]: https://firebase.blog/posts/2025/11/firebase-mcp-and-antigravity/ "Antigravity and Firebase MCP accelerate app development"
[6]: https://firebase.google.com/docs/ai-assistance/gemini-in-firebase/try-gemini?utm_source=chatgpt.com "Try Gemini in the Firebase console"
[7]: https://firebase.google.com/docs/ai-assistance/mcp-server "Firebase MCP server  |  Develop with AI assistance"
