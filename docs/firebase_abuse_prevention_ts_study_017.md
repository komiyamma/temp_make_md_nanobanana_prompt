# 第17章：Functionsの言語とバージョン感（Node/Python/.NET）🧰🔢

この章は「**Functions を何の言語で書く？どのバージョンにする？**」で迷わなくなる回です🙂
App Check を“ちゃんと効かせる”前提だと、**言語選び＝守り方の選び方**にも直結します🧿✨

---

## 1) まず結論：初心者が迷ったらこう！🧭

![Language Decision Tree](./picture/firebase_abuse_prevention_ts_study_017_01_language_tree.png)

* **王道（おすすめ）**：**Node.js + TypeScript** ✅
  App Check 強制（`enforceAppCheck`）も手堅いし、最新の Firebase 周辺エコシステムが一番揃ってます☎️🔒 ([Firebase][1])
* **Python**：できるけど、現状は「できること/できないこと」を知って選ぶ ⚠️
  App Check 強制は **Python は preview 扱い**、さらに **リプレイ対策（consume）は Node のみ**です♻️🚫 ([Firebase][1])
* **.NET**：**Firebase Functions そのもの**で書くより、**Cloud Run functions 側でやる**のが現実的（= Firebase と“連携”）🧩
  Cloud Run functions は **.NET 8** や **.NET 10 preview** などランタイム選択肢があります🧱✨ ([Google Cloud Documentation][2])

---

## 2) “バージョン感”の最新まとめ（2026/02/17 時点）🔢🆕

## Node.js（Firebase Functions）

* 公式の入門ページでは **Node.js 20 / 22 をフルサポート**、**Node 18 は deprecated** と明記されています📌
* さらに **Firebase CLI のリリースノート**では、既に **デフォルト runtime を nodejs22 に変更**済みです（新規は基本 22 でOK）✅ ([Firebase][3])
* そして同じく CLI リリースノートで **nodejs24 runtime のサポート追加**も入っています（ただし、初学者は 22 で安定が吉）🚀 ([Firebase][3])

## 「Node 20 って今から選んでいいの？」問題😇

![Node Version Timeline](./picture/firebase_abuse_prevention_ts_study_017_02_node_timeline.png)

Cloud Run functions 側のランタイム表だと、**Node 20 は 2026-04-30 に deprecate**予定（= もうすぐ）です📅💦
新規で今から作るなら **22（または状況により 24）**に寄せるのが安全です🛡️ ([Google Cloud Documentation][2])

## Python（Firebase Functions）

![Python Limitations](./picture/firebase_abuse_prevention_ts_study_017_03_python_limits.png)

* 公式入門ページに **Python 3.10〜3.13 がサポート、デフォルトは 3.13** と書かれています🐍✨
* ただし App Check 強制は **Python preview**扱いなので、守りの主戦場にするなら「制限も理解して使う」感じです⚠️ ([Firebase][1])

## “AI系（Genkit）を Functions に載せたい”なら…

![Genkit Ecosystem](./picture/firebase_abuse_prevention_ts_study_017_04_genkit_ecosystem.png)

* Genkit を Firebase でデプロイする導線は **JavaScript（Node）中心**で、**Genkit Python は Firebase へのデプロイが未対応**と明記があります🤖📦 ([Firebase][4])
  → **AI を Functions 側で育てたいなら Node/TS が強い**です💪

## .NET（Cloud Run functions）

* Cloud Run functions のランタイムとして **dotnet8** や **dotnet10 preview** が載っています🧱✨ ([Google Cloud Documentation][2])
* そして「Cloud Run functions と Firebase の関係」のページでも、Cloud Run functions は **（Firebase の外にも持っていける）ポータブルな関数**として説明されています🧩 ([Firebase][5])

---

## 3) “読む”パート：バージョン迷子の正体🧠🌀

![Runtime vs SDK](./picture/firebase_abuse_prevention_ts_study_017_05_runtime_vs_sdk.png)

迷うポイントはだいたいこの2つです👇

1. **ランタイム（Node 22 とか Python 3.13 とか）**
   → 「どの言語の、どの実行環境で動くか」
2. **SDK/ライブラリ（firebase-functions のバージョン等）**
   → 「App Check 強制できる？リプレイ対策できる？Genkit 使える？」がここで決まる

たとえば App Check の強制は、Node 2nd gen なら `firebase-functions >= 4.0.0` が目安として示されています☎️🔒 ([Firebase][1])
Python は preview で書けるけど、リプレイ対策は Node だけ…みたいに差が出ます♻️🚫 ([Firebase][1])

---

## 4) “手を動かす”パート：自分のプロジェクトを「今どのランタイム？」って確認しよう🔍🧪

## ステップA：Node/TS（王道）で runtime を固定する✅

![JSON Config Check](./picture/firebase_abuse_prevention_ts_study_017_06_json_check.png)

`functions/package.json` に Node の指定があるかチェックして、なければ入れます👇

```json
{
  "engines": {
    "node": "22"
  }
}
```

* もし「最新に寄せたい/新機能も試したい」なら 24 を検討（ただし最初は 22 推奨）🚀 ([Firebase][3])

## ステップB：Python で作る場合は runtime を firebase.json 側で見る🐍

（プロジェクト構成によって置き方が違うので、まず “あるかどうか” を見るのがコツ🙂）

例（イメージ）👇

```json
{
  "functions": [
    {
      "source": "functions",
      "runtime": "python313"
    }
  ]
}
```

* Python は 3.10〜3.13 がサポート、デフォルトは 3.13 です🐍✨

## ステップC：App Check 強制の“対応度”をざっくり把握🧿

* Node：`enforceAppCheck` で強制できる（2nd gen 例あり）☎️🔒 ([Firebase][1])
* Python：`enforce_app_check=True` で強制できる（ただし preview）🐍⚠️ ([Firebase][1])
* リプレイ対策（consume）は Node のみ♻️🚫 ([Firebase][1])

---

## 5) 「AI導入済み」前提の時短ルート：Antigravity / Gemini CLI で“バージョン確認”を自動化🤖⚡

![MCP Scanner](./picture/firebase_abuse_prevention_ts_study_017_07_mcp_scanner.png)

ここ、2026年の強い武器です🧰✨
**Firebase MCP server** を使うと、AI ツールが Firebase プロジェクトやコードベースを扱えるようになります（Antigravity / Gemini CLI など対応）🤝 ([Firebase][6])

## できること（この章に効くやつ）

* 「このリポジトリ、Functions の runtime 何？」を自動で把握🔍
* 「Node 18 残ってない？」「node 20 を 22 に上げると壊れる依存ある？」を点検🧯
* 「App Check 強制してる関数どれ？」を棚卸し🧿

## MCP を使う最短イメージ（Gemini CLI 側）

公式ドキュメントに、Gemini CLI で Firebase MCP server を使うための導線（拡張の導入など）が載っています🧩 ([Firebase][6])

---

## 6) ミニ課題🎯：あなたの“線引き”を1枚にする📝

次の3つを、各1行で書いてみてください🙂

1. **私は Functions は基本（Node / Python / .NET）で行く**：理由は◯◯
2. **AI をサーバー側でやるなら（Node / Cloud Run）**：理由は◯◯
3. **App Check 強制＆リプレイ対策が必要な場所**：◯◯（例：課金・管理者操作）

---

## 7) チェック✅（言えたら勝ち！）

* 「ランタイム」と「SDKバージョン」の違いを説明できる🙂
* 新規 Functions は **Node 22（安定）**に寄せる理由を言える🛡️ ([Firebase][3])
* Python は **できるけど preview が混ざる**ので、守りの主軸にするなら注意点も言える🐍⚠️ ([Firebase][1])
* Genkit を Functions で育てたいなら **Node が強い**と説明できる🤖💪 ([Firebase][4])
* .NET は **Cloud Run functions でやって Firebase と連携**、が自然と言える🧱🧩 ([Google Cloud Documentation][2])

---

次の第18章で「.NET でも自前バックエンドでも App Check で守れる（`X-Firebase-AppCheck` 検証）」に入るので、**第17章で “言語選択の軸” を固めておく**と気持ちよく進みます😆🔥

[1]: https://firebase.google.com/docs/app-check/cloud-functions "Enable App Check enforcement for Cloud Functions  |  Firebase App Check"
[2]: https://docs.cloud.google.com/functions/docs/runtime-support "Runtime support  |  Cloud Run functions  |  Google Cloud Documentation"
[3]: https://firebase.google.com/support/release-notes/cli "Firebase CLI Release Notes"
[4]: https://firebase.google.com/docs/genkit/firebase "Deploy with Firebase | Genkit"
[5]: https://firebase.google.com/docs/functions/functions-and-firebase "Cloud Run functions and Firebase  |  Cloud Functions for Firebase"
[6]: https://firebase.google.com/docs/ai-assistance/mcp-server "Firebase MCP server  |  Develop with AI assistance"
