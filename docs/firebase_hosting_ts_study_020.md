# 第20章：AI合体（リリース手順書・自動チェック・最終完成）🏁✨

この最終章は「公開できた！」で終わらせず、**“運用できる公開”**まで持っていく回だよ〜😎🚢
やることは大きく4つ👇

* **リリース手順書（Runbook）**を作って、未来の自分を救う🧾✨
* **PRテンプレ＋チェックリスト**で、確認漏れを減らす✅
* **GitHub Actionsに自動チェック**を足して、事故をPRで止める🧯🤖
* **FirebaseのAI（AI Logic / Genkit / Gemini in Firebase / MCP）**で、詰まりと作業を一気に減らす🤖🔥 ([Firebase][1])

---

## 読む📖（この章の考え方のコツ）🧠✨

## 1) “手順書”は、最強の自動化😇

自動デプロイがあっても、**「何を確認して、ダメならどう戻す？」**が無いと本番は怖い…😱
だからまずRunbook（手順書）を作る！

## 2) “自動チェック”は、PRで落とすのが正義⚖️

本番で落ちるより、**PRで落ちる**ほうが100倍マシ😂
「ビルドできない」「Lintで死ぬ」「環境変数足りない」みたいなのを自動で止める🤖🛑

## 3) AIは「コードを書く」より「詰まり＆漏れ」を潰すのが強い🔥

* コンソールで困った→ **Gemini in Firebase**で状況整理🧯 ([Firebase][2])
* CLIやエージェントでFirebase触る→ **Firebase MCP server / Gemini CLI拡張**で一気にラク🧩 ([Firebase][3])
* アプリのAI機能→ **Firebase AI Logic**で安全に呼ぶ🤖🔐 ([Firebase][4])
* “手順”や“チェック”をフロー化→ **Genkit**で型にする🧰 ([Firebase][5])

---

## 手を動かす🛠️（やる順番どおり）🚀

## 0) まず道具を最新にする🔧⬆️

Firebase CLIは更新が速いので、最初にサクッと上げちゃおう💨
（2026-01-29時点のFirebase CLIは **v15.5.1** が出てるよ）([Firebase][6])

```powershell
npm i -g firebase-tools@latest
firebase --version
```

---

## 1) Runbook（手順書）をリポジトリに置く🧾📦

おすすめは `docs/RUNBOOK_RELEASE.md` みたいに「いつも同じ場所」に固定✨

## 1-1) ひな形（コピペOK）📝

```markdown
## RUNBOOK: リリース手順（Hosting / App Hosting）

## 0. 今日の目的
- 何を出す？（機能名 / PR / issue）

## 1. 事前チェック（PRが通っている前提）
- [ ] PRプレビューURLで主要画面OK
- [ ] 主要導線（ログイン/ログアウト/設定/課金など）OK
- [ ] 404/リロード問題なし（SPA）
- [ ] キャッシュが壊れてない（更新されるべきJS/CSSが更新される）
- [ ] 環境変数（staging/prod）事故なし

## 2. デプロイ手順（本番）
1) main にマージ
2) GitHub Actions の本番デプロイが成功しているか確認
3) 本番URLで動作確認（シークレットウィンドウ推奨）

## 3. ロールバック（戻し方）
- どのコミット/タグに戻す？
- 戻したあと、どこを再確認する？

## 4. 緊急停止（事故った時）
- 「今すぐ止める」選択肢（例：公開を戻す / 機能フラグOFF / 入口を塞ぐ等）
- 連絡先メモ（自分でもOK）

## 5. 監視（リリース直後の5分）
- まず見る場所（ログ/エラー/アクセス）
- “いつもと違う”の判断基準
```

## 1-2) AIに“下書き”を作らせるプロンプト例🤖🧾

AntigravityのエージェントやGemini Chatに、こう投げると速い👇
（ポイント：**あなたのアプリの導線**を書かせる）

* 「このリポジトリはReact + Firebase Hosting。PRプレビュー→本番のRunbookを上のひな形に沿って埋めて。ログイン/プロフィール更新/画像表示が重要。ロールバックと緊急停止も入れて。」

---

## 2) PRテンプレを入れて“確認漏れ”を潰す✅🧷

GitHubのPRテンプレは、地味だけど効くよ〜😂
`.github/PULL_REQUEST_TEMPLATE.md` を作るのが定番！

```markdown
## 変更内容
- 

## 動作確認
- [ ] PRプレビューURLで確認した
- [ ] 主要画面（/ /login /settings 等）OK
- [ ] リロードしても404にならない（SPA）
- [ ] 画像/API/外部通信がOK
- [ ] キャッシュが原因の表示崩れがない

## リスク
- 

## ロールバック案
- もしダメなら：mainを「どの状態」に戻す？
```

---

## 3) GitHub Actionsに「自動チェック（Preflight）」を足す🤖✅

すでに **プレビュー**と**本番デプロイ**が動いてる前提で、
その前に “落ちるべきもの” を落とすジョブを追加する感じ！

## 3-1) 追加するチェック（最低ライン）🧯

* `npm ci` → 依存が入る
* `npm run lint` → 変なコードを止める
* `npm test`（あるなら）→ 壊れてないか
* `npm run build` → 本番ビルドできるか

※ ここで落ちるのは「正常」だよ😆（本番で落ちるより最高）

## 3-2) YAML例（イメージ）🧩

既存workflowに近いところへ足してね（“例”なので名前は合わせてOK）👇

```yaml
jobs:
  preflight:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 22

      - run: npm ci
      - run: npm run lint
      - run: npm test --if-present
      - run: npm run build
```

Cloud Functions（使うなら）のNodeは **20 / 22がフルサポート**で、18は非推奨（deprecated）扱いになってるので、CIも22に寄せるのが気持ちいい👍🟩 ([Firebase][7])

---

## 4) Firebase MCP server を入れて「調査と作業」をショートカット🧩🤖

これ、**最終章にめちゃくちゃ相性いい**やつ！

* MCPを入れると、AIツール側から **Firebase操作・調査**がやりやすくなる🧠
* Antigravity / Gemini CLI などから使える（MCPクライアントならOK）([Firebase][3])
* MCPは **Firebase CLIと同じ認証**を使う（つまりログインが超大事🔐）([Firebase][3])

## 4-1) Antigravityなら（超ラク）⚡

AntigravityのMCP設定でFirebaseをInstallすると、内部的にこういう設定が入る感じ👇 ([Firebase][3])

```json
{
  "mcpServers": {
    "firebase-mcp-server": {
      "command": "npx",
      "args": ["-y", "firebase-tools@latest", "mcp"]
    }
  }
}
```

## 4-2) Gemini CLIなら（拡張入れるのが推奨）🧩

Firebase拡張を入れると、MCP設定もまとめて入って便利👏 ([Firebase][3])

```bash
gemini extensions install https://github.com/gemini-cli-extensions/firebase/
```

## 4-3) 使いどころ（プロンプト例）🧠🧯

* 「本番デプロイで事故りやすいポイントを、このリポジトリ構成から洗い出してRunbookに追記して」
* 「今のFirebaseプロジェクトの状態を整理して。触る前に危険ポイントも教えて」
* 「Security Rulesや設定ファイル周りで、やらかしそうな箇所をチェックして」

MCPには `firebase:deploy` みたいな“用意されたプロンプト”もあるので、**手順書づくりに直撃**するよ🧾💥 ([Firebase][3])

---

## 5) Firebase AI Logicで「リリースノート生成」ミニ機能を作る📝🤖

ここで “FirebaseのAIサービスそのもの” をアプリに合体させる🔥
AI Logicは、Web SDKでも `getAI()` → `getGenerativeModel()` → `generateContent()` みたいに呼べるよ。([Firebase][4])

## 5-1) 例：入力した箇条書きを「リリースノートっぽい文章」にする✨

（※UIは簡単でOK！ “運用っぽさ” が出る😆）

```ts
import { initializeApp } from "firebase/app";
import { getAI, getGenerativeModel, GoogleAIBackend } from "firebase/ai";

// Firebase初期化（firebaseConfigは自分のプロジェクトの値）
const app = initializeApp(firebaseConfig);

// Gemini Developer API を使う例
const ai = getAI(app, { backend: new GoogleAIBackend() });
const model = getGenerativeModel(ai, { model: "gemini-2.5-flash" });

export async function generateReleaseNote(bullets: string) {
  const prompt = `
あなたはプロダクト担当です。
以下の箇条書きを、ユーザー向けのリリースノートとして読みやすく整形して。
- 200〜400文字
- 見出し＋箇条書き
- 破壊的変更があれば最後に注意を書いて

箇条書き:
${bullets}
  `.trim();

  const result = await model.generateContent(prompt);
  return result.response.text();
}
```

## 5-2) 実務っぽくする小ワザ🧠✨

* **モデル名は後から変えたくなる**ので、Remote Configで切り替えできる設計が推奨されてるよ📌 ([Firebase][4])
* モデルにも世代交代がある。たとえばドキュメント内で、**Gemini 2.0 Flash / Flash-Liteの提供終了が 2026-03-31** と案内されてるので、固定は危険⚠️ ([Firebase][4])
* 本番では **App Check** などの保護が強く推奨（乱用対策）🔐 ([Firebase][4])

---

## 6) Genkitで「リリース前チェック」を“フロー化”する🧰🤖（おまけだけど強い）

「チェック項目」って毎回同じになりがちなので、**フローとして型にする**のが気持ちいい✨

たとえば：

* 入力：今回の変更点（短文）＋注意してほしい箇所
* 出力：リリース前のチェックリスト、リスク、ロールバック案

GenkitフローはCloud Functionsから呼べる（`onCallGenkit`）ので、管理画面のボタンで実行…みたいな“実務っぽい道”も作れるよ🚀 ([Firebase][5])
※本番で使うなら課金プラン（Blaze）が必要、という注意もあるよ⚠️ ([Firebase][5])

---

## ミニ課題🎒（30分で“完成”させる）🔥

1. `docs/RUNBOOK_RELEASE.md` を作って、**あなたのアプリの導線**で埋める🧾
2. PRテンプレを入れる✅
3. Actionsに `preflight` を足して、**ビルド失敗をPRで止める**🤖🛑
4. AI Logicで「リリースノート生成」関数を1個だけ作る📝🤖

---

## チェック✅（ここまでできたら勝ち🏆）

* [ ] Runbookがあり、**本番で迷わない**
* [ ] PRにチェックリストが出て、**確認漏れが減る**
* [ ] CIが「壊れてるPR」を止める🧯
* [ ] AIで「手順・チェック・文章化」が速くなる🤖⚡
* [ ] AI機能（AI Logic）がアプリに1つ入ってる✨

---

## これで“リリース体験”カテゴリは完全クリアだよ〜！🎉🚢

次に進むなら、流れ的におすすめは👇

* 「Emulatorで統合テスト」🧪
* 「Functions / Cloud Run functions で画像処理・API化」⚙️（Cloud Run functionsのランタイムは Node 24/22/20、Python 3.13、.NET 8 などが選べる）([Google Cloud Documentation][8])

必要なら、この第20章の成果物（Runbook / PRテンプレ / Actions / AI LogicのUI）を「あなたの今の構成（Vite？Next？）に合わせた完成版」に寄せて、まるごと書き起こすよ😆🛠️

[1]: https://firebase.google.com/docs/ai-assistance "Develop with AI assistance  |  Firebase"
[2]: https://firebase.google.com/docs/ai-assistance/gemini-in-firebase?utm_source=chatgpt.com "Gemini in Firebase - Google"
[3]: https://firebase.google.com/docs/ai-assistance/mcp-server "Firebase MCP server  |  Develop with AI assistance"
[4]: https://firebase.google.com/docs/ai-logic/get-started "Get started with the Gemini API using the Firebase AI Logic SDKs  |  Firebase AI Logic"
[5]: https://firebase.google.com/docs/functions/oncallgenkit "Invoke Genkit flows from your App  |  Cloud Functions for Firebase"
[6]: https://firebase.google.com/docs/ai-assistance/mcp-server?utm_source=chatgpt.com "Firebase MCP server | Develop with AI assistance - Google"
[7]: https://firebase.google.com/docs/functions/get-started?utm_source=chatgpt.com "Get started: write, test, and deploy your first functions - Firebase"
[8]: https://docs.cloud.google.com/run/docs/runtimes/function-runtimes?hl=ja "Cloud Run functions ランタイム  |  Google Cloud Documentation"
