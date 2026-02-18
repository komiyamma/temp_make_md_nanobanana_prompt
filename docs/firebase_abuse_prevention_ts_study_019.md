# 第19章：AIで“守りの実装”を加速（Antigravity / Gemini CLI / Studio）🚀🤖

この章は「守り（App Check / ボット耐性）を、AIで“速く・漏れなく・安全に”仕上げる」回だよ〜😆🧿
Google と Firebase の公式情報ベースで、2026-02-17時点で“いま使える現実解”に寄せて組み立てるね。([Google Codelabs][1])

---

## この章のゴール 🎯✨

* AIに「守りタスク」を分解させて、実装の抜け漏れを減らす🧠🧩
* リポジトリをAIに“監査”させて、App Checkの初期化漏れや直アクセスを炙り出す🔎🧿
* AI機能（生成AI）を **App Check + レート制限** で“破産しない設計”に寄せる💸🚧 ([Firebase][2])
* ついでに「モデル廃止（retire）」の地雷も踏まないようにする💣😇 ([Firebase][2])

---

## まず“AIの使い分け”だけ覚える 🧠🧰

* **Antigravity**：AIが「計画→実装→検証」まで走れる“エージェント型IDE”。Mission Controlで複数エージェントを動かせて、必要ならWeb調査もできる📋🤖🌐 ([Google Codelabs][1])
* **Gemini CLI**：ターミナルで動くオープンソースAIエージェント。雑に言うと「速攻でリポジトリを読ませて指摘させる係」💻⚡ ([GitHub][3])
* **Firebase Studio**：ブラウザ上の開発環境。`.idx/dev.nix` で環境が宣言できて、再現性が高い☁️🧬 ([Firebase][4])

---

## 読む 📚👀（この章の“事実”ポイント）

## 1) AI機能は最優先でApp Checkを噛ませたい 🧿

Firebase AI Logicは、生成AIモデルAPIを「正規アプリ以外」から叩かれるのを防ぐために **App Check統合（プロキシゲートウェイ）** を用意していて、早い段階から入れるのを強く推奨してるよ。([Firebase][2])

## 2) 生成AIは“回数制限”が超重要 💸

Firebase AI Logicは **ユーザーごとのレート制限** を持っていて、デフォルトは **1ユーザーあたり100 RPM**。ただし、裏側のGemini APIプロバイダ側の制限も優先されるから、両方見るのが大事。([Firebase][5])

## 3) モデルのretireに注意（これ超やりがち）⚠️

AI Logicのドキュメント上で、**Gemini 2.0 Flash / Flash-Lite が 2026-03-31 にretire**予定、代替として `gemini-2.5-flash-lite` などへの更新が案内されてるよ。
→ つまり「AIに実装を任せる」なら、**モデル名の棚卸しもAIにやらせる**のがコスパ最強😆🧾 ([Firebase][2])

## 4) Functionsのランタイムの現実（地味に詰まる）🧱

* Cloud Functions for Firebase は **Node.js 20/22 を完全サポート**（18は2025初頭にdeprecated）。([Firebase][6])
* Pythonは **3.10〜3.13** がサポートされ、**3.13がデフォルト**。([Firebase][6])
* いっぽうでNode本体の“世間の最新版”は別で、2026-02時点だと **Node 24がActive LTS**。ローカル開発は新しめでもOKだけど、Functionsの実行ランタイムは「Firebaseが対応してる範囲」が正義だよ〜。🧠✅ ([Node.js][7])

---

## 手を動かす 🔥🛠️（3本立て）

## Step 1：Gemini CLIで“守り監査”を秒速で回す 💻🔎

Gemini CLIは **Node.js 20+** が前提で、Windows向けの手順もまとまってる。インストールはnpmでOK。([Gemini CLI][8])

```bash
npm install -g @google/gemini-cli
gemini
```

1発だけ投げたい時は `npx` でも動くよ。([Gemini CLI][8])

```bash
npx @google/gemini-cli
```

## 監査プロンプト例（コピペOK）🧠🧿

Gemini CLIに貼る文章はこんな感じが強いよ👇（あなたのリポジトリ前提で）

* **App Check初期化漏れチェック**

  * 「Reactの起動点から見て、App Check初期化が“必ず1回だけ”走る設計になってる？ 初期化箇所と、漏れてる可能性のあるパスを列挙して」

* **危険な直アクセス箇所の洗い出し**

  * 「Firestore/Storage/Functions/AI Logic への呼び出し箇所を全部一覧化して、“App Checkが無いと危ない呼び出し”に印を付けて」

* **AIモデルの棚卸し（retire対策）**

  * 「AI Logicで使ってるモデル名を全部抜き出して。`Gemini 2.0 Flash/Flash-Lite` が含まれてたら、2026-03-31 retire を踏まえて置き換え案も出して」([Firebase][2])

* **レート制限・破産耐性チェック**

  * 「AI機能の“濫用パターン”を3つ想定して、Firebase AI Logicの“ユーザーごとのレート制限”（デフォルト100 RPM）をどう調整するべきか提案して」([Firebase][5])

> コツ😺：Gemini CLIは“結論だけ”じゃなく、**「どのファイルのどの箇所が怪しい？」**を出させると、修正が速いよ⚡

---

## Step 2：Antigravityで“守り実装ミッション”を組む 📋🤖🌐

Antigravityは「Mission Controlで自律エージェントを管理でき、計画・実装・Web調査までできる」って公式に書かれてる。([Google Codelabs][1])
なのでこの章は、こういう“ミッション文章”を作って流し込むのが勝ち筋🏁

## ミッション文章テンプレ（そのまま使える）🧩

* 目的：App Check + ボット耐性を“漏れなく”適用
* 制約：UIは壊さない、鍵や秘密情報は出さない、差分は小さく、必ずテスト/動作確認を書く
* タスク分割（例）：

  1. App Check初期化の一元化（React）🧿
  2. AI Logic 呼び出しの保護（App Check）🤖🧿 ([Firebase][2])
  3. AI Logic のユーザー別レート制限設計（100 RPMを起点に）🚦💸 ([Firebase][5])
  4. “モデル名の棚卸し”とretire対応🧨🧾 ([Firebase][2])
  5. 変更点の説明（運用メモ）📝

Antigravity側がWeb調査もできるから、**「その提案の根拠URLも一緒に出して」**って一言添えると、レビューが超ラクになるよ🙂‍↕️🌐 ([Google Codelabs][1])

---

## Step 3：Firebase Studioで“再現できる作業場”を固定する ☁️🧬

Firebase Studioは **Nixで環境定義**できて、`.idx/dev.nix` がその設定ファイル。環境を共有・複製しやすいのが強み。([Firebase][4])

たとえば、最低限こんな感じ（公式例の形に寄せた“ミニ版”）👇 ([Firebase][4])

```nix
{ pkgs, ... }: {
  channel = "stable-23.11";

  packages = [
    pkgs.nodejs_20
  ];

  env = {
    # 例：必要なら環境変数をここに
    SOME_ENV_VAR = "hello";
  };

  idx.previews = {
    enable = true;
  };
}
```

> ポイント🧠：Functions側のNodeは20/22が“完全サポート”なので、StudioのNodeもそこに寄せると事故りにくいよ。([Firebase][6])

---

## 仕上げ：AI Logicの“守り2点セット”を固める 🧿🚦

ここはAIに任せつつ、あなたが最後に握るところ🔥

1. **AI LogicをApp Checkで保護**（早め推奨）
   “正規アプリ以外からのAI API叩き”を防ぐための基本セット。([Firebase][2])

2. **ユーザー別レート制限を設定**（まずは小さめで）
   デフォルトは100 RPM/ユーザー。最初は控えめ→メトリクス見て調整が安全。([Firebase][5])

3. **モデルretire対応**
   2026-03-31のretire予定が明記されてるから、使ってたら早めに置き換える🧯([Firebase][2])

---

## ミニ課題 🧪📝（“AIが作った差分”を人間が締める）

AI（AntigravityかGemini CLI）にこう依頼して、出てきた差分をあなたがレビューしてね👀

* 「App Check / AI Logic / レート制限 / モデル棚卸し を含む“守り強化PR”を作って。
  ただし、**秘密情報をコミットしない**、差分は小さく、変更理由をコメントで残して」

✅ あなたの仕事：**AIの提案から“危ない点”を1つ見つけて直す**（例：モデル名が古い／例外時UIが無い／制限がキツすぎる 等）

---

## チェック✅（この章を終えた合格ライン）

* Antigravityに「守りタスク」を分解させ、根拠付きで実装計画を出せる📋🤖 ([Google Codelabs][1])
* Gemini CLIで「怪しい箇所」を特定し、修正の当たりを付けられる🔎💻 ([GitHub][3])
* AI Logicは **App Check + レート制限** の2段で守る発想になってる🧿🚦 ([Firebase][2])
* モデルretire（2026-03-31）みたいな運用地雷を踏まない設計にできる💣🧯 ([Firebase][2])
* Functionsのランタイム事情（Node 20/22、Python 3.10〜3.13）を踏まえてAIの提案を取捨選択できる🧠✅ ([Firebase][6])

---

次は（第20章の前に）おすすめとして、**「AI Logicのレート制限値を“現実的な数”に落とす」小演習**を挟むと、破産耐性が一気に上がって気持ちいいよ〜😆💸🚧

[1]: https://codelabs.developers.google.com/getting-started-google-antigravity "Getting Started with Google Antigravity  |  Google Codelabs"
[2]: https://firebase.google.com/docs/ai-logic/app-check "Implement Firebase App Check to protect APIs from unauthorized clients  |  Firebase AI Logic"
[3]: https://github.com/google-gemini/gemini-cli "GitHub - google-gemini/gemini-cli: An open-source AI agent that brings the power of Gemini directly into your terminal."
[4]: https://firebase.google.com/docs/studio/get-started-workspace "About Firebase Studio workspaces"
[5]: https://firebase.google.com/docs/ai-logic/quotas "Rate limits and quotas  |  Firebase AI Logic"
[6]: https://firebase.google.com/docs/functions/get-started "Get started: write, test, and deploy your first functions  |  Cloud Functions for Firebase"
[7]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[8]: https://geminicli.com/docs/get-started/installation/ "Gemini CLI installation, execution, and releases | Gemini CLI"
