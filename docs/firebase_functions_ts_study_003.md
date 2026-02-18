# 第03章：ランタイムと言語の選び方（Node / Python / それ以外）🧩

この章は「何で書くのが一番ラクで、事故りにくい？」を決める回です🙂✨
ここで迷いが消えると、以降の **HTTP / イベント / スケジューラー** がスイスイ進みます🚀

---

## 1) そもそも「ランタイム」って何？🤔

ざっくり言うと、

* **クラウド上で関数が動く“実行環境のバージョン”** のことです⚙️
* 例：Node.js 22 で動かす／Python 3.13 で動かす…みたいに指定できます👀

そして重要ポイント👇
**ローカル（あなたのPC）で動くバージョン** と **クラウド（Functions）で動くバージョン** を “同じ系統” に寄せると、トラブルが激減します🧯✨

---

## 2) 迷わない結論：まずは Node.js（TypeScript）でOK ✅🟦

Cloud Functions（FirebaseのFunctions）は、現時点で **Node.js 20 と 22 をフルサポート**していて、**Node.js 18 は 2025年初頭に deprecated** になっています📌([Firebase][1])
さらに公式の管理ドキュメントでも、サポート対象は **22 / 20 /（18はdeprecated）** と明記されています。([Firebase][2])

なのでこの教材では基本方針をこうします👇

* **迷ったら Node.js 22**（新規ならこれでOK）🟩
* もし依存ライブラリ都合で慎重にいきたいなら **Node.js 20** 🟨
* **Node.js 18は避ける**（移行対象）🟥([Firebase][1])

---

## 3) Node.js（TypeScript）を選ぶと何が嬉しい？🎁

### ✅ 情報量が圧倒的に多い（詰まりにくい）📚

Functionsの例・記事・サンプルが多くて、困ったときにすぐ解決しやすいです🙂

### ✅ FirebaseのAI連携（Genkit）と相性が良い 🤖🔥

FunctionsからAIフローを呼ぶ導線（例：`onCallGenkit`）が用意されていて、**AIを“裏側”に組み込む**のがやりやすいです✨([Firebase][3])

### ✅ 「Gemini in Firebase」などAI支援も絡めやすい 🧠

Firebase側でもAI支援（Gemini）を有効化できる導線が案内されています。([Firebase][1])

---

## 4) Node.js のランタイム指定（超重要）🔧

Functions（Node）のランタイム指定は、主に2つのやり方があります👇

### A. `functions/package.json` の `engines` で指定（いちばん王道）🧱

```json
{
  "engines": { "node": "22" }
}
```

この `engines` が「クラウドで動くNodeのバージョン」を決めます🧠([Firebase][2])

### B. `firebase.json` の `functions.runtime` で指定（Yarn運用などで便利）🧰

```json
{
  "functions": {
    "runtime": "nodejs22"
  }
}
```

`firebase.json` を使うと、CLIは **package.jsonより firebase.json を優先**します。([Firebase][2])

---

## 5) Python を選ぶのはどんな時？🐍✨

Pythonもちゃんと使えます！
公式に **Python 3.10〜3.13 がサポート**されていて、**デフォルトは 3.13** と書かれています。([Firebase][1])

Pythonが向くのは例えば👇

* 既にPython資産がある（処理ロジックがある）📦
* データ処理・解析系のライブラリを使いたい📊
* どうしてもPythonで書きたい理由が明確🐍

ただしこの教材では「迷子にならない」が最優先なので、**中心はTS/Node**、必要になったらPythonを“選べる”状態を作るのがゴールです🙂

### Python のランタイム指定（firebase.json）🔧

管理ドキュメント上は `firebase.json` で指定できます👇([Firebase][2])

```json
{
  "functions": {
    "runtime": "python313"
  }
}
```

※例として `python310` / `python311` の記載がありますが、Python自体は 3.10〜3.13 がサポートされていて 3.13 がデフォルトです。([Firebase][1])
（ランタイムIDの表記は “python313” のように3桁で並ぶのが一般的です👀([Google Cloud Documentation][4])）

---

## 6) 「それ以外の言語」…C#/.NET はどうする？🟪

ここが超大事ポイントです👇

* FirebaseのFunctions（Cloud Functions for Firebase）では **Node/TS が主軸**（＋Python対応）です([Firebase][1])
* じゃあ **C#/.NETで関数を書きたい**ときはどうする？
  → 現実解は **Google Cloud の Cloud Run functions（= Cloud Functions v2系）側**に置いて、HTTPで連携するのがスッキリです🙂([Google Cloud Documentation][4])

Cloud Run functions 側だと、.NETランタイムとして例えば👇が選べます：

* **.NET 8（dotnet8）**
* **.NET 10 Preview（dotnet10）**
* **.NET 6（dotnet6）**
  みたいに “ランタイムID” が表で提示されています。([Google Cloud Documentation][5])

つまり設計としてはこう👇

* Firebase Functions（Node/TS）＝ **Firebaseの世界に密着**（Auth連携、Firestoreトリガー、Callable、Genkitなど）🤝
* Cloud Run functions（.NET）＝ **C#で書きたい処理をHTTP関数として用意**し、必要なところから呼ぶ🌐

この「役割分担」ができると、TS中心で進めつつ、C#も活かせます💪✨

---

## 7) AIを使って“ランタイム選び”を秒速で終わらせる🤖⚡

ここからが2026っぽいところ😎

### ✅ Gemini CLI で「おすすめ構成」を作らせる🛠️

Firebaseは **Gemini CLI向けのFirebase拡張**を案内しています。([Firebase][2])
ここに、こんなお願いを投げると超ラクです👇

* 「Functionsは Node 22 と 20 どっちが無難？理由も3つで」
* 「TSで始める前提で、package.json engines と firebase.json runtime の最小例を出して」
* 「Pythonに寄せるなら、依存管理（venv）含めた最小設計は？」

### ✅ MCP server 経由で「Firebase周りの作業」をAIに補助させる🧰

Firebase側で **MCP server** の案内があり、AI開発支援と組み合わせられる方向性が公式に示されています。([Firebase][2])
「調べる→まとめる→設定案を作る」が一気に進みます🚀

### ✅ AI機能を“使う側”としても見据える（Genkit）🔥

この後の章でやりますが、FunctionsにAIを組み込むなら、公式に `onCallGenkit` などの導線が用意されています。([Firebase][3])
だからランタイム選びでも「Node/TSが堅い」って話に繋がります🙂

---

## 8) ミニ演習（手を動かす）✍️🧪

### 演習A：自分の結論を1行で書く📝

次のテンプレを埋めてください👇

* 「私は Functions は **Node.js（22/20）** で始める。理由は（　　）」

理由は「迷子にならない」「情報が多い」「Genkit/AI連携が楽」あたりでOKです😆

### 演習B：ランタイム指定の“見本”を作る🧱

どっちか片方でOK！

* `package.json` に `engines.node` を書く（Node 22推奨）([Firebase][2])
* `firebase.json` に `functions.runtime` を書く（nodejs22 / python313 など）([Firebase][2])

---

## 9) 理解チェック（言えたら勝ち）✅🏁

* Node.js 18 が「今は避けたい」理由を一言で言える？（ヒント：deprecated）([Firebase][1])
* Nodeのランタイム指定はどこでやる？（`package.json engines` or `firebase.json runtime`）([Firebase][2])
* Pythonはどの範囲がサポート？ デフォルトはいくつ？([Firebase][1])
* C#/.NETで“関数”を書きたいとき、どこに置くのが現実的？（ヒント：Cloud Run functions）([Google Cloud Documentation][5])

---

次の第4章は、いよいよ **CLI初期化→関数1個デプロイ**で「動いた！」を作ります🌱🔥
第3章で決めたランタイムが、そのまま土台になりますよ〜😄

[1]: https://firebase.google.com/docs/functions/get-started "Get started: write, test, and deploy your first functions  |  Cloud Functions for Firebase"
[2]: https://firebase.google.com/docs/functions/manage-functions "Manage functions  |  Cloud Functions for Firebase"
[3]: https://firebase.google.com/docs/functions/oncallgenkit?utm_source=chatgpt.com "Invoke Genkit flows from your App | Cloud Functions for Firebase"
[4]: https://docs.cloud.google.com/functions/docs/runtime-support "Runtime support  |  Cloud Run functions  |  Google Cloud Documentation"
[5]: https://docs.cloud.google.com/run/docs/runtimes/dotnet "The .NET runtime  |  Cloud Run  |  Google Cloud Documentation"
