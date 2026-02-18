# 第03章：reCAPTCHA v3 入門（スコアとしきい値）🤖📊

この章は「App Check（WebのreCAPTCHA v3）」の**いちばん大事な調整つまみ＝“しきい値”**を理解して、**安全とUXを両立**できるようになる回だよ〜🧿✨

---

## 1) まずイメージ：スコアとしきい値って何？🎛️

![reCAPTCHA Score Scale](./picture/firebase_abuse_prevention_ts_study_003_01_score_scale.png)

reCAPTCHA v3 は、アクセス（操作）が **人っぽいか／ボットっぽいか**を 0.0〜1.0 のスコアで返す仕組みだよ🤖

* **1.0 に近いほど人っぽい**
* **0.0 に近いほどボットっぽい** ([Firebase][1])

そして **しきい値（App risk threshold）**はこう👇

> **「このスコア未満は怪しいので落とす（拒否する）ライン」**

Firebase App Check は、設定した **しきい値を“最低合格点”**として扱い、**それ未満のスコアは拒否**する（＝正規として認めない）よ、という仕様になってる🛡️ ([Firebase][1])

![Threshold Filter](./picture/firebase_abuse_prevention_ts_study_003_02_filtering.png)

---

## 2) しきい値は “上げるほど安全” だけど “痛い”😇

![Threshold Trade-off](./picture/firebase_abuse_prevention_ts_study_003_03_tradeoff.png)

しきい値を **高く**すると（例：0.7→0.9）

* ✅ ボットを落としやすい（安全↑）
* ❌ まじめなユーザーも落ちる可能性が増える（UX事故↑） ([Firebase][1])

逆に **低く**すると（例：0.5→0.3）

* ✅ ユーザーは通りやすい（UX↑）
* ❌ 悪いのも通りやすい（乱用リスク↑） ([Firebase][1])

さらに極端な例として、Firebase公式でも注意がある👇

* **1.0 はおすすめしない**（正規ユーザーまで弾き得る）
* **0.0 もおすすめしない**（保護が実質OFF） ([Firebase][1])

---

## 3) まずは 0.5 で始めるのが基本線👍（理由つき）

![Starting Point](./picture/firebase_abuse_prevention_ts_study_003_04_default_setting.png)

FirebaseのreCAPTCHA v3（Web）手順では、**デフォルトの 0.5 を推奨**してるよ🎯 ([Firebase][1])
Google側の reCAPTCHA v3 ドキュメントでも、まずは **0.5 を“デフォルト”として始め、実トラフィック見て調整**が推奨されてる🧠 ([Google for Developers][2])

ここ超大事👇
reCAPTCHA v3 は **実際のトラフィックを見て学習**するので、**導入直後**や**ステージング環境**のスコアはブレやすいよ〜📉📈 ([Google for Developers][2])

---

## 4) 手を動かす：Firebase Consoleで「しきい値」を触ってみる🖱️🧿

この章の実作業は「コード」じゃなくて **コンソール操作**が中心だよ🙆‍♂️✨

## 4-1. しきい値の場所（Firebase Console）🔎

![Firebase Console Setting](./picture/firebase_abuse_prevention_ts_study_003_05_console_ui.png)

Firebase Console → **App Check** → 対象の **Webアプリ** → reCAPTCHA v3 の設定の中に
**App risk threshold（しきい値）**のスライダーがある🎛️ ([Firebase][1])

## 4-2. “上げる/下げる”の考え方（事故らない運用）🧯

Firebase公式の注意として、**しきい値を上げる前**は一度立ち止まるのが安全🧠

> いきなり上げると正規ユーザーを巻き込むので、必要なら一時的に unenforce（強制OFF）して影響を抑えつつ、メトリクス監視してから戻す
> …みたいな運用が推奨されてるよ👀 ([Firebase][1])

---

## 5) “決め方テンプレ”：しきい値はこうやって育てる🌱📈

## ステップA：まず 0.5（デフォルト）で開始🎯

* まずはここからでOK ([Firebase][1])

## ステップB：分布を見る（reCAPTCHA側）📊

* **reCAPTCHA Admin console** でスコア分布を見られるよ（公式でも案内あり） ([Firebase][1])
  「ログイン」「投稿」「画像アップロード」みたいに、**操作（action）別**に傾向が変わるのもポイント✨ ([Google for Developers][2])

## ステップC：徐々に調整（0.1刻みイメージ）🎛️

* 0.5 → 0.6 のようにちょい上げして
* App Checkのリクエスト状況（拒否増えてない？）と
* ユーザーからの「通らない😭」が増えてないか
  を見ながら調整するのが現実的🙂‍↕️

---

## 6) 図解っぽく：あなたがやってること（超重要）🧩

![Verification Logic](./picture/firebase_abuse_prevention_ts_study_003_06_flow_diagram.png)

```
ユーザー操作
   ↓
reCAPTCHA v3 がスコアを出す（0.0〜1.0）
   ↓
App Check の「しきい値」と比較
   ↓
スコア >= しきい値  → OK（正規っぽい）
スコア <  しきい値  → NG（拒否される）
```

この「NG」が増えすぎると、**ボット排除＝ユーザー排除**になって詰む😇
だから、しきい値は **セキュリティのスイッチ**というより **UXとのバランス調整ノブ**だと思うと強いよ🎛️✨ ([Firebase][1])

---

## 7) AI活用（Antigravity / Gemini）で“しきい値調整”をラクにする🤖🧠

![AI Operations Assistant](./picture/firebase_abuse_prevention_ts_study_003_07_ai_assistance.png)

ここ、AIがめちゃくちゃ効くところ🔥
たとえば👇

## 7-1. Geminiに「調整手順書」を作らせる🧾

* 現状：しきい値 0.5、いつ・何を見て・どこまで上げるか未定
* 目的：**事故らない運用手順**を文章化（未来の自分を救うやつ）🛟

## 7-2. “通らない時の文言”をAIに作らせる🙂

しきい値を上げたあとに起きる「通らない😭」に備えて、

* 再読み込み案内
* 時間を置く案内
* サポート導線
  を**短く・感じよく**作るのはAIが得意💬✨

（この章ではまだ実装しないけど）**AI整形ボタン（Firebase AI Logic）**みたいにコストが絡む機能は、後の章で **App Check + 回数制御**に繋がるから、ここで“運用の型”を作っておくと後が超ラクだよ🤖💸

---

## 8) ミニ課題📝✨（5〜10分）

**課題A：UX事故を1行で予言する😇**
しきい値を 0.9 にしたら、あなたのアプリで何が起きそう？を1行で書く✍️
例）「ログインが通らない人が増えて離脱が増える」みたいに具体的に！

**課題B：調整ルールを3つ決める🎛️**

* 例）「0.1ずつしか動かさない」
* 例）「上げる前にメトリクスを1日見る」
* 例）「上げたら“通らない導線”を必ず出す」

---

## 9) チェック✅（言えたら勝ち！）

* ✅ reCAPTCHA v3 は **0.0〜1.0 のスコア**で“怪しさ”を返す ([Firebase][1])
* ✅ App Check の **しきい値は最低合格点**で、それ未満は拒否される ([Firebase][1])
* ✅ **0.5開始→実トラフィック見て調整**が基本線 ([Firebase][1])
* ✅ しきい値を上げるほど「安全↑/UX事故↑」を理解してる ([Firebase][1])

---

次の第4章〜第5章で、いよいよ **React側にApp Check（reCAPTCHA v3）を組み込む**よ⚛️🧿
その前に「しきい値＝運用のノブ」って感覚が入ったら、この章はクリア！🎉

[1]: https://firebase.google.com/docs/app-check/web/recaptcha-provider "Get started using App Check with reCAPTCHA v3 in web apps  |  Firebase App Check"
[2]: https://developers.google.com/recaptcha/docs/v3 "reCAPTCHA v3  |  Google for Developers"
