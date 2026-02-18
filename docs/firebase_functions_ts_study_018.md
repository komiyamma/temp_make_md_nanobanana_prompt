# 第18章：AIで開発を速くする（Antigravity / Gemini CLI）🛸💻

## この章のゴール🎯

* AIに **「調査」「ひな形生成」「手順書化」「設定の棚卸し」「ログ読み」** をやらせて爆速にする⚡
* ただし **丸投げはしない**（最後は人間が差分レビュー＆実行判断）👀✅
* Firebase MCP server を理解して「AIに手足が生える」感覚を掴む🦾🤖([Firebase][1])

---

## 1) まずイメージ：AIは“副操縦士＋作業員”✈️🧰

AIに向いてるのは、ざっくりこの3つです👇

1. **作業の圧縮**：初期化・設定・コマンド手順を短縮する🧱→🚀
2. **確認の自動化**：設定漏れ・ルールの穴・セキュリティの危険を洗う🧯
3. **検索＆要約**：公式ドキュメントを素早く引いて要点にする📚⚡

ここで効いてくるのが **MCP（Model Context Protocol）** です。AIが「喋るだけ」じゃなくて、**Firebaseに対してツール実行できる**ようになります🔧🤖([Firebase][2])

---

## 2) 今日の主役：Gemini CLI + Firebase拡張 🧑‍💻✨

## Firebase拡張って何がうれしいの？🎁

Firebase extension for Gemini CLI を入れると、ざっくりこれが“自動で”付いてきます👇([Firebase][1])

* **Firebase MCP server を自動インストール＆設定**してくれる🛠️
* すぐ使える **スラッシュコマンド（定型プロンプト）** が増える（例：`/firebase:init` など）⌨️
* AIが **FirebaseのドキュメントをLLM向け形式で参照**できる📚
* プロジェクトに **Firebase向けの context file（ヒント集）** も追加されて、精度が上がる📌([Firebase][1])

---

## 3) セットアップ（Windowsで最短）🪟⚡

まず CLI 側を最新にします（拡張設定機能が v0.28+ で入ってます）🧩([Google Developers Blog][3])

```powershell
npm install -g @google/gemini-cli@latest
```

次に Firebase 拡張をインストール👇（これは **Gemini CLIの外の通常シェル**で実行）([Firebase][1])

```powershell
gemini extensions install https://github.com/gemini-cli-extensions/firebase/
```

アップデートも定期的に👇（拡張は頻繁に更新されます）([Firebase][1])

```powershell
gemini extensions update firebase
```

さらに便利なのが **拡張の設定（Extension settings）**。APIキーみたいな機密値を「手作業で環境変数に入れて事故る」問題を減らします。**機密設定はOSのキーチェーンに安全に保存**される設計です🔐([Google Developers Blog][3])

---

## 4) まず叩くべきスラッシュコマンド3つ💥⌨️

Gemini CLIを起動したら、以下が“超つよ”です👇（公式が例として挙げてます）([Firebase][1])

## ✅ `/firebase:init`（新規 or 既存プロジェクトの整備）

* Firestore＋Auth などの「土台」作りを手伝う
* **Firebase AI Logic をセットアップして、Gemini API を安全に呼ぶコード**まで書く方向にも誘導できる🤖🧠([Firebase][1])

## ✅ `/firebase:deploy`（ホスティング系の迷いを減らす）

* 静的/フルスタック等を見て「適したFirebaseホスティングサービス」を選ぶ流れを補助してくれる（手作業のミスを減らす）🚀([Firebase][1])

## ✅ `/crashlytics:connect`（モバイル系の不具合整理）

* Crashlytics 連携済みなら、優先度付けや修正方針の下ごしらえに強い🧯📱([Firebase][1])

---

## 5) MCP serverって何？（AIに“手足”を生やす仕組み）🦾🤖

Firebase MCP server は、AIが Firebase を扱いやすくなるための仕組みで、ざっくり3カテゴリあります👇([Firebase][2])

* **Prompts**：定型プロンプト（= slash commands）のセット
* **Tools**：Firebaseへ実際に操作できる道具（プロジェクト作成、Firestore操作、デプロイ、ログ取得など）
* **Resources**：FirebaseドキュメントをAIが参照しやすい形式で引ける

大事ポイント⚠️：
MCP server のツール操作は **Firebase CLIと同じユーザー認証**で動くので、AIの操作＝あなたの権限で実行されます。だから **実行前レビューが超重要**です👀🔒([Firebase][2])

---

## 6) Antigravityで“任務”として回す🛰️🧑‍🚀

Google Antigravity は、いわゆる「エージェント開発プラットフォーム」。普通の補完じゃなくて、**計画→実装→検証→反復**までやれる“自律エージェント”を **Mission Control** 的に扱えるのがウリです🛸🎛️([Google Codelabs][4])

さらに、Antigravity も MCP クライアントになれるので、Firebase MCP server をつなぐと強いです。
公式の MCP ドキュメントでは、Antigravity のエージェントペインから MCP Servers を追加し、Firebase MCP server をインストールする流れが案内されています🧩([Firebase][2])

---

## 7) ハンズオン：Functions開発をAIで爆速にする「3本勝負」⚔️🔥

ここ、コピペで使えるように **“指示テンプレ”** を置きます✍️✨
（Gemini CLI でも Antigravity でも、考え方は同じです）

## ① まず「手順書」をAIに作らせる📄🤖

狙い：**迷いゼロで進める**（人間はレビューだけ）

```text
このリポジトリの現状を見て、Cloud Functions for Firebase（2nd gen）を安全にデプロイする手順書を作って。
- 事前チェック（secret / env / billing / APIs）
- 本番に触る前の安全策（git、emulator、影響範囲）
- デプロイコマンドと、成功確認のやり方
- 失敗したときの切り分け手順（ログの見方も）
出力はチェックリスト形式で。
```

✅ 期待する成果：

* 手順が“一本道”になる🛣️
* 抜け漏れが減る🧯

---

## ② セキュリティの穴を先に潰す（Rules/設定チェック）🧱🔒

MCP server にはセキュリティルールを検証する系のツールもあります（例：`firebase_validate_security_rules`）。([Firebase][2])
なので AI にはこう頼むのが強い👇

```text
Firestore/Storage の Rules を確認して、次を満たすように改善提案して。
- 認証ユーザーだけ許可
- ユーザー自身のデータだけ許可（パスやuid一致）
- 曖昧な allow read, write を作らない
- テスト観点（どういうケースを弾くべきか）も書いて
提案は “差分” と “理由” をセットで。
```

✅ 期待する成果：

* “なんとなく許可”が消える🙅‍♂️
* ルールが説明できる形になる🧠

---

## ③ ログをAIに読ませて、原因候補を絞る🧯👀

MCP server はログ取得や状態確認系のツールも持っています（例：Functions のログ取得など）。([Firebase][2])
AIにこう頼む👇

```text
直近の Functions の失敗ログを見て、原因候補を3つに絞って。
それぞれについて
- 可能性が高い根拠（ログのどこ）
- まず最初に試す修正（最小変更）
- 再発防止の観点（監視/アラート/入力検証）
もセットで出して。
```

✅ 期待する成果：

* “手当たり次第修正”が減る🔧
* 次に見る場所が明確になる🗺️

---

## 8) FirebaseのAIサービスも絡める：AI Logic を「初期化で混ぜる」🤖🧩

`/firebase:init` の中で **「Add AI features」** を選ぶと、**Firebase AI Logic のセットアップ**と、アプリから Gemini API を安全に呼ぶコード作成までを支援してくれます。([Firebase][1])

そして注意ポイント⚠️
Firebase AI Logic にはモデルの更新・退役もあるので、**古いモデル固定で運用しない**のが大事です。たとえば公式ページでは、特定モデルの retirement 日（例：2026-03-31）に触れて注意喚起があります📅🧯([Firebase][5])

---

## 9) 事故らないための「AI運用ルール」5つ🧯✅

1. **AIの提案は“差分”で見る**（丸ごと置換しない）👀
2. **実行系（作成/削除/デプロイ）は、必ず人間が最終判断**🛑
3. **機密はコードに書かない**：拡張設定や Secret Manager を使う🔐([Google Developers Blog][3])
4. **権限が強いことを忘れない**：MCPの操作はあなたの権限で動く⚠️([Firebase][2])
5. **チェックリスト化して再利用**：AIに作らせた手順書を“資産”にする📄✨

---

## 10) ちょい補足：この教材の言語バージョン感（Functions周辺）🔢🧩

* Firebase Functions は **Node が主軸**、Python もサポート（**3.10〜3.13、デフォルト 3.13**）🐍([Firebase][6])
* C# を“関数ランタイム”としてやるなら、現実的には **Cloud Run functions / Cloud Functions 2nd gen の .NET 8** 側で扱うのが筋が良い（.NET 8 GA の記載あり）🧩([Google Cloud Documentation][7])

---

## ミニ課題（第18章）🏁✨

## お題：AIで「Functions運用手順書 v1」を作れ📄🤖

あなたのリポジトリを対象に、AIに作らせて、人間が整えて完成させます👍

**作るもの（納品物）**

* ✅ デプロイ前チェックリスト
* ✅ 本番デプロイ手順（1回で迷わない）
* ✅ 失敗時の切り分け手順（ログ→原因候補→対処）
* ✅ Secrets の置き場所ルール（どこに何を置かないか）🔐

**合格ライン**

* 初見の自分が読んでも、30分以内に再現できる⌛
* 「この操作は危険」ポイントが明記されている🧯

---

## この章のチェック✅

* `gemini extensions install …firebase…` が言える＆更新できる🧰([Firebase][1])
* `/firebase:init` と `/firebase:deploy` の役割が説明できる⌨️([Firebase][1])
* MCP server が **prompts / tools / resources** の3つで理解できる🦾([Firebase][2])
* AIの提案を“差分レビュー前提”で回す運用ルールがある👀✅

---

必要なら次のメッセージで、あなたの **第19章（Slack通知）** を見据えて、
第18章で作った「手順書v1」を **Slack通知のデプロイまで含めた“運用Runbook”** に育てるテンプレも作れます📨🔥

[1]: https://firebase.google.com/docs/ai-assistance/gcli-extension "Firebase extension for the Gemini CLI  |  Develop with AI assistance"
[2]: https://firebase.google.com/docs/ai-assistance/mcp-server "Firebase MCP server  |  Develop with AI assistance"
[3]: https://developers.googleblog.com/making-gemini-cli-extensions-easier-to-use/ "
            
            Making Gemini CLI extensions easier to use
            
            
            \- Google Developers Blog
            
        "
[4]: https://codelabs.developers.google.com/getting-started-google-antigravity "Getting Started with Google Antigravity  |  Google Codelabs"
[5]: https://firebase.google.com/docs/ai-logic/solutions/overview?utm_source=chatgpt.com "Overview: Firebase AI Logic solutions - Google"
[6]: https://firebase.google.com/docs/functions/get-started?utm_source=chatgpt.com "Get started: write, test, and deploy your first functions - Firebase"
[7]: https://docs.cloud.google.com/functions/docs/release-notes?utm_source=chatgpt.com "Cloud Run functions (formerly known as Cloud Functions ..."
