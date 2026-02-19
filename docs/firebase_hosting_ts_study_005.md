# 第05章：SPAルーティング（リロードで404になる問題）🔁

この章は **「Reactの画面で `/about` みたいなURLを直叩き（またはリロード）すると404になる」** を、Firebase Hosting側の設定でスッキリ直す回だよ〜🧯✨
いったんここを越えると「公開したSPAが“ちゃんとしたWebアプリ”っぽく」なるので気持ちいい👍🌐

---

## 1) まず何が起きてるの？😵‍💫

![The SPA 404 Problem](./picture/firebase_hosting_ts_study_005_01_404_problem.png)

## 症状あるある

* 画面内リンク（例：Home → About）で移動はできる ✅
* でも `/about` で **ブラウザ更新（F5）** すると 404 ❌
* あるいは、URL欄に `/about` を直接入れて開くと 404 ❌

## 原因（超ざっくり）🧠

SPA（Single Page Application）は、画面遷移を **ブラウザ内のJSルーター**（React Routerなど）で捌くよね🧩
でも **リロード/直叩き** は、最初にサーバー（Hosting）へ「`/about` のファイルください！」って来る📨
Hosting側は「そんなファイルないよ？じゃあ404ね🙅‍♂️」となる…って流れ。

---

## 2) 解決方針はこれ！✅「全部 index.html に書き換えて返す」

![The Rewrite Solution](./picture/firebase_hosting_ts_study_005_02_rewrite_solution.png)

SPAは基本、**どのパスで来ても `index.html` を返して**、その後はSPAルーターが画面を決めるのが王道だよ🔁✨
Firebase Hostingだとこれを **rewrites（リライト）** で実現する🧾

Firebase公式でも「one-page app（= SPA）」では、全リクエストを `index.html` に向ける設定が出てくるよ📌([Firebase][1])

---

## 3) redirect と rewrite の違い（ここ超大事）⚠️

![Redirect vs Rewrite](./picture/firebase_hosting_ts_study_005_03_redirect_vs_rewrite.png)

## redirect（リダイレクト）🚦

* **ブラウザに「別のURLへ行ってね」** と返す（301/302みたいな感じ）➡️
* つまり、ブラウザが **もう一回リクエスト** し直す
* Firebase Hostingでは、redirect は **リクエスト開始時に先に判定**される（＝静的ファイルがあるかどうかを見る前）([Firebase][2])

## rewrite（リライト）🪄

* **URLはそのまま**（例：`/about` のまま）
* でも **中身は `index.html` を返す**（見せるコンテンツだけ差し替え）
* Firebase Hostingでは rewrite は **そのURLに該当するファイル/ディレクトリが存在しない場合だけ** 適用される ([Firebase][2])
  → だから `assets/` とかの静的ファイル配信を壊しにくい👍

結論：SPAの404対策は **rewrite** を使うのが基本！✨

---

## 4) 実装：firebase.json に rewrites を追加しよう🛠️

![Catch-All Configuration](./picture/firebase_hosting_ts_study_005_04_config_catch_all.png)

## ✅ 最小の“SPA 404対策”テンプレ

`firebase.json` の Hosting 設定に、**catch-all**（全部マッチ）を最後に入れるよ🔚

```json
{
  "hosting": {
    "public": "dist",
    "rewrites": [
      { "source": "**", "destination": "/index.html" }
    ]
  }
}
```

* `public` は **ビルド成果物が出るフォルダ**（Viteなら `dist` が多い）📦
* `source: "**"` は「全部のパス」🎯
* `destination: "/index.html"` は「index.htmlを返す」🏠

> ルールは「上から順」で、**最初に一致したものが採用**されるよ。だから catch-all は最後が鉄則！🧠([Firebase][2])

---

## 5) ローカルで確認（いきなり本番に出さない！）🧪

![Hosting Emulator](./picture/firebase_hosting_ts_study_005_08_emulator.png)


Firebase公式の手順だと、Hosting Emulatorでサクッと確認できるよ💡
基本はこれ👇 ([Firebase][3])

1. Reactアプリをビルド📦

```bash
npm run build
```

2. エミュレータ起動🚀

```bash
firebase emulators:start
```

3. ブラウザで開く（だいたいここ）🌐

* `http://localhost:5000` ([Firebase][3])

## ✅ チェックするURL（ここが肝）👀

* `http://localhost:5000/about` を **直で開く**
* その状態で **F5**（更新）
* ちゃんと `/about` の画面が出続けたら勝ち🏆✨

---

## 6) 本番へ反映（Hostingだけデプロイ）🚢

![Hosting Deploy Command](./picture/firebase_hosting_ts_study_005_06_deployment_flow.png)

ローカルでOKなら、Hostingだけ出す！🎯

```bash
firebase deploy --only hosting
```

---

## 7) ありがち罠＆直し方（ここで詰まりやすい）🧯

## 罠1：rewrites を入れたのにまだ404 😭

* `public` が **ビルド成果物と一致してない** パターンが多い

  * 例：本当は `build/` や `dist/` なのに違う
* `index.html` がその `public` 直下にない

  * `public/dist/index.html` みたいになってたらズレてるかも

## 罠2：APIや特殊パスまでSPAに吸い込まれる😵

![Rule Priority](./picture/firebase_hosting_ts_study_005_05_rule_order.png)

将来 `/api/**` を Functions/Cloud Run に振る予定があるなら、**先にそれを置いてから** 最後に `** → index.html` を置くと安全だよ🔐
（ルールは上から順・最初に一致が採用なので）([Firebase][2])

例（イメージ）：

```json
{
  "hosting": {
    "rewrites": [
      { "source": "/api/**", "function": "api" },
      { "source": "**", "destination": "/index.html" }
    ]
  }
}
```

## 罠3：redirect を雑に `**` で書いて資産配信が壊れる💥

redirect は静的ファイル判定より先に走るので、雑に広く当てると事故りやすいよ⚠️([Firebase][2])
SPA対策は redirect じゃなく rewrite が基本だね✨

---

## 8) AIで“詰まり”を秒速で潰す🤖🧯

## A) Firebaseコンソールで相談（Gemini in Firebase）💬

Firebaseの画面上で、Geminiのペインを開いて相談できて、開いたペインはページ移動しても保持されるよ🧠([Firebase][4])
おすすめの聞き方👇

* 「Firebase HostingでSPAを出したら `/about` リロードで404。`firebase.json` の rewrites を最小構成で教えて。redirectとrewriteの違いと、ルール順の注意も込みで！」

## B) Antigravity / Gemini CLI × Firebase MCP server で“設定レビュー”🧩

![AI Configuration Review](./picture/firebase_hosting_ts_study_005_07_ai_review.png)

Firebase MCP server は **Antigravity や Gemini CLI** など、MCPクライアントになるツールと一緒に使えるよ([Firebase][5])
Gemini CLI なら Firebase拡張を入れて MCP server を自動設定できる案内がある（contextファイルも付いてくる）([Firebase][5])

```bash
gemini extensions install https://github.com/gemini-cli-extensions/firebase/
```

これが入ると、例えばこんなお願いがしやすい👇

* 「このリポジトリの `firebase.json` を見て、SPAリロード404が起きない rewrites に直して。`/api/**` 予約も考えてルール順も整えて」

> 「AIが提案 → 自分が理解して採用」の形にすると、学習の定着がめちゃ良いよ💪📚

## C) ついでに：将来のAI機能も“安全に”組み込みやすいルート🧠

Firebase AI Logic は、Gemini/Imagen を **モバイルやWebアプリに組み込むための仕組み**として案内されてるよ（クライアントSDK＋保護の考え方込み）([Firebase][6])
この章で「URL設計が整う」→ 次に「AI機能を載せる」って流れが作りやすくなる👍✨

---

## 9) ミニ課題🎯（5〜15分）

![Mini Assignment](./picture/firebase_hosting_ts_study_005_09_assignment.png)


1. React側で `/about` ルートを用意（表示は「Aboutページです！」だけでOK）🧩
2. `firebase.json` に SPA rewrites を入れる🧾
3. Hosting Emulatorで `/about` を直叩き → F5 を3回押しても表示が崩れないことを確認🔁✅
4. できたら `firebase deploy --only hosting` で本番反映🚢✨

---

## 10) チェックリスト✅

![Checklist](./picture/firebase_hosting_ts_study_005_10_checklist.png)


* [ ] `/about` をURL直打ちで開ける
* [ ] `/about` でF5しても404にならない
* [ ] 画像・JS・CSSなどの静的ファイルが壊れてない（404が出てない）
* [ ] rewrites の catch-all（`"**"`）が一番下にある ([Firebase][2])
* [ ] ローカル（Hosting Emulator）で確認してからデプロイした ([Firebase][3])

---

次の章（第6章）は **Preview Channel** で「この修正を“プレビューURLで共有”」していく流れに入るよ🔎🔁
第5章で直した rewrites は、PRプレビューでも超効いてくるので、ここはガッチリ固めとこ〜😆🚀

[1]: https://firebase.google.com/docs/hosting/quickstart "Get started with Firebase Hosting"
[2]: https://firebase.google.com/docs/hosting/full-config "Configure Hosting behavior  |  Firebase Hosting"
[3]: https://firebase.google.com/docs/emulator-suite/use_hosting "Prototype and test web apps with the Firebase Hosting Emulator  |  Firebase Local Emulator Suite"
[4]: https://firebase.google.com/docs/ai-assistance/gemini-in-firebase/try-gemini "Try Gemini in the Firebase console  |  Gemini in Firebase"
[5]: https://firebase.google.com/docs/ai-assistance/mcp-server "Firebase MCP server  |  Develop with AI assistance"
[6]: https://firebase.google.com/docs/ai-logic "Gemini API using Firebase AI Logic  |  Firebase AI Logic"
