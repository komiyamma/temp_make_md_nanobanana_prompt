# 第07章：まずはメトリクス監視だけ（いきなり強制しない）👀📈

この章は「**App Check は入れた。でもまだ強制しない**」がテーマです🧿
先にメトリクスを見て、**“強制ONで誰が困るか / どれが怪しいか” を数字で把握**してから次へ進みます🙂
（公式も「SDKを入れた後、強制の前に影響を確認しよう」と明言してます）([Firebase][1])

---

## 1) まず超重要な前提：メトリクスは「強制ONの事故防止装置」🧯✨

App Check は、SDK を入れるだけなら“多くの場合”は動き続けます。
でも **強制（enforcement）をONにした瞬間**、そのプロダクトへの **未検証リクエストは拒否**されます😇([Firebase][2])

だからやる順番はこう👇

1. ✅ App Check SDK を入れる
2. 👀 **メトリクスで様子見**（この章）
3. 🎛️ 問題なさそうなら **強制ON**（次の章以降）

---

## 2) どこを見る？Firebase コンソールの App Check メトリクス画面👀

見る場所はシンプルです👇
**Firebase コンソール → App Check →（守りたいプロダクトを展開）→ メトリクスを見る**([Firebase][1])

この画面が強い理由は、**プロダクト別**（例：Firestore / Storage / AI Logic …）に見られるからです🛡️
公式も、Firebase AI Logic / Firestore / Storage / Authentication など複数プロダクトで “この画面で判断しよう” と書いてます([Firebase][1])

---

## 3) メトリクスの「4分類」を覚えよう（ここが心臓）🫀🧠

メトリクスは、リクエストを次の4つに分類します👇([Firebase][1])

## ✅ Verified requests（検証OK）

有効な App Check トークン付き。
**強制ON後に成功するのは基本これだけ**です。([Firebase][1])

## 🧓 Outdated client requests（古いクライアント）

**トークンが付いてない**けど、古いSDK版など「古い正規アプリ」かも。
強制ONすると **古い版が壊れる**ので、ここが多いと要注意です⚠️([Firebase][1])

## 🕵️ Unknown origin requests（出所不明）

**トークンが付いてない**＋Firebase SDKっぽくもない。
APIキー盗用や、SDKを使わない偽造リクエストの可能性があるやつ👿([Firebase][1])

## ❌ Invalid requests（不正トークン）

トークンはあるが **無効**。
偽装クライアント、あるいはエミュレート環境由来の可能性…など。([Firebase][1])

---

## 4) 「いつ強制ONできる？」判断の目安（公式のガイドライン）🧭

公式がそのまま指針を出してます👇([Firebase][1])

* **最近のリクエストのほとんどが Verified** → 強制ONを検討してOK✅([Firebase][1])
* **Outdated がそこそこ居る** → その人たちが更新するまで待つのも手（強制すると古い版が壊れる）🧓⚠️([Firebase][1])
* **まだ未リリース** → 古いクライアントが存在しないので、基本すぐ強制ONでOK🏁([Firebase][1])

---

## 5) 手を動かす：まずは“観察用リクエスト”を作る🧪👀

この教材のミニアプリ（メモ＋画像＋AI整形）なら、観察ポイントは超わかりやすいです👇

## Step A：アプリで3つ操作して、リクエストを発生させる📝📷🤖

* 📝 Firestore：メモを作成 or 更新
* 📷 Storage：画像をアップロード
* 🤖 AI：整形ボタンを押す（Firebase AI Logic）

## Step B：コンソールで App Check → メトリクスを見る👀

* Firestore / Storage / AI Logic をそれぞれ展開して、
  ✅Verified が増えているか？
  🧓Outdated / 🕵️Unknown / ❌Invalid が混ざってないか？
  を見るだけです([Firebase][1])

> コツ：この章の目的は「0%にする」じゃなくて、**“強制ONしたら何が起きるか”を事前に知る**ことです🙂

---

## 6) すぐ効く！「原因あたり」を雑に切り分ける早見表🧠⚡

* ✅Verified が少ない
  → App Check 初期化のタイミング漏れ（Firestore/Storage を触る前に初期化できてない）などの可能性📦
* 🧓Outdated が多い
  → 古いデプロイが生きてる / キャッシュが残ってる / 古いビルドを使ってる人がいる、などの可能性🧓
* 🕵️Unknown origin が出る
  → ボット/偽造/キー盗用など“怪しいアクセス”が混ざってるサインになり得る👿([Firebase][1])
* ❌Invalid が出る
  → 無効トークン（偽装 or エミュレート環境など）っぽいサインになり得る🚫([Firebase][1])

（※ここは“可能性”の話。断定じゃなく、次の調査の方向を決めるためのものです🙂）

---

## 7) ミニ課題：「強制ONにする前のチェック項目」5つ作ろう🧾✨

あなた用のチェックリストを作ります✍️
テンプレを置くので、コピって自分の言葉にしてOKです😆

## ✅ 強制ON前チェックリスト（例）

1. 👀 直近のメトリクスで **Verified がほとんど**（守る予定の各プロダクトごと）([Firebase][1])
2. 🧓 Outdated が居るなら「それは誰？（古いデプロイ？古いビルド？）」の仮説がある
3. 🕵️ Unknown origin / ❌Invalid が出てるなら「強制ONで止まる見込み」を理解してる([Firebase][1])
4. 🧪 ローカル開発・CI で詰まらない道（Debug Providerなど）を次章で整える予定がある
5. 🧯 強制ON後に困ったら戻せる/対応できる運用メモ（誰がいつONするか等）がある

---

## 8) ここだけ先に知っておく：強制ONは“あとで”コンソールから3クリック🎛️

まだこの章ではやりません🙅‍♂️（事故防止のため）
ただ、仕組みだけ知っておくと安心です🙂

**App Check → 対象プロダクトを展開 → Enforce → 確認**
これで「未検証リクエストは拒否」になります。反映に最大15分かかることがあります。([Firebase][2])

---

## 9) AIで爆速：メトリクス監視を“作業化”しよう🤖🚀

## 🛰️ Antigravity（ミッション化のイメージ）

Antigravity は “Mission Control でエージェントが計画・実装・Web調査まで” みたいな思想の開発体験が紹介されています([Google Codelabs][3])
なので、この章はこういうミッションにすると強いです👇

* 🎯 ミッション名：`App Check メトリクス監査`
* ✅ 成果物：

  * 「プロダクト別（Firestore/Storage/AI）に Verified% をメモ」
  * 「Outdated/Unknown/Invalid が出たら原因仮説を3つ」
  * 「強制ONの順番案（Firestore→Storage→AI など）」

## 🧰 Gemini CLI（ターミナルで“まとめ役”）

Gemini CLI は、Gemini をターミナルに統合する **オープンソースAIエージェント**として紹介されています([blog.google][4])
「調査」「タスク管理」みたいな用途も想定されています([blog.google][4])

たとえば、こう聞くと便利👇（例）

```text
あなたはFirebase App Checkの運用担当です。
今から私が「Firestore/Storage/AI Logic」のApp Checkメトリクス（Verified/Outdated/Unknown/Invalidの割合）を貼ります。
1) それぞれの意味を短く説明
2) 強制ONのGo/No-Go判断
3) もしNoなら、考えられる原因と次の確認手順を箇条書き
4) 強制ONするなら順番案と、強制後の監視ポイント
を出してください。
```

## 🤖 AI Logic のコストも忘れずに💸

Firebase AI Logic は「プロジェクトのクォータ（レート制限）」で制御できて、**デフォルトは 1ユーザーあたり 100 RPM** と説明されています([Firebase][5])
App Check メトリクスで AI への “怪しい流入” が見えてきたら、**強制ON＋レート見直し**のセットが効きます🙂

---

## 10) チェック✅（この章を終えたら言えること）

* 「強制ONの前にメトリクスを見る理由」を説明できる🙂([Firebase][1])
* Verified / Outdated / Unknown / Invalid の意味をざっくり言える🧠([Firebase][1])
* 自分のアプリで「強制ON前チェックリスト」が5個できた🧾✨

---

次の章（第8章）でいよいよ **Firestore を守る**に入ると、ここで作ったチェックリストがそのまま効いてきます🛡️🔥

[1]: https://firebase.google.com/docs/app-check/monitor-metrics "Monitor App Check request metrics  |  Firebase App Check"
[2]: https://firebase.google.com/docs/app-check/enable-enforcement "Enable App Check enforcement  |  Firebase App Check"
[3]: https://codelabs.developers.google.com/getting-started-google-antigravity?utm_source=chatgpt.com "Getting Started with Google Antigravity"
[4]: https://blog.google/innovation-and-ai/technology/developers-tools/introducing-gemini-cli-open-source-ai-agent/ "Google announces Gemini CLI: your open-source AI agent"
[5]: https://firebase.google.com/docs/ai-logic/quotas "Rate limits and quotas  |  Firebase AI Logic"
