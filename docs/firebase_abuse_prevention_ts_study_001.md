# 第01章：なぜApp Checkが必要？“正規アプリ以外から叩かれる”を体感😱🧿

この章は「実装」より前に、**“何が怖いのか”をハッキリさせて、守る優先順位を決める回**だよ〜🧠✨
（ここがフワッとしてると、あとで設定がブレて事故りやすい…！）

---

## 1) まず結論：App Check は「正規アプリの身分証」🎫✨

![App Identity Card](./picture/firebase_abuse_prevention_ts_study_001_01_id_card.png)

App Checkは、Firebaseの各サービス（や自前バックエンド）へのリクエストに **“有効なApp Checkトークン” が付いているか**をチェックして、**正規アプリっぽい通信だけ通す**ための仕組みだよ🧿
「ユーザーが誰か」じゃなくて「**このリクエスト、正規アプリから来てる？**」を見てくれる感じ！ ([Firebase][1])

ざっくり図解すると👇

![Verified vs Unverified Access](./picture/firebase_abuse_prevention_ts_study_001_02_access_flow.png)

* ✅ 正規アプリ（App Checkトークン付き） → Firebase「OKどうぞ」😎
* ❌ それ以外（トークン無し/変なトークン） → Firebase「拒否！」🚫（※強制ONしたら） ([Firebase][2])

---

## 2) “何が起きるの？”：正規アプリ以外から叩かれるとツラいこと3つ😱💸

![Three Abuse Vectors](./picture/firebase_abuse_prevention_ts_study_001_03_abuse_scenarios.png)

この教材のミニアプリ（メモ＋画像＋AI整形）で特にヤバいのはここ👇

## (A) AIが連打されて請求が伸びる🤖💸

生成AIのAPIは、**モロにコストが出やすい**んだよね…。
しかもモバイル/Webアプリから直接呼ぶと「無関係なクライアントからの乱用」に弱くなりがちで、だからこそ Firebase AI Logic は **App Check導入を早期から強く推奨**してるよ。 ([Firebase][3])
さらに、AI Logic側には **“1ユーザーあたりRPMのレート制限”**があって、デフォルトは高め（100 RPM）だから、アプリに合わせて下げるのが推奨されてる。 ([Firebase][4])

## (B) 画像アップロード連打・巨大ファイルで地獄📷🔥

Cloud Storage は「アップロード」がある時点で狙われやすい😇
大量アップロードや巨大ファイルで、**通信・保存コスト・運用負荷**がズドン…💥

## (C) Firestoreが雑に読まれて・書かれて・燃える🗃️🔥

Cloud Firestore はクエリが便利＝悪用されると痛い😭
（もちろん、ここは **Security Rulesが主役**なんだけど、App Checkがあると “そもそも正規アプリ以外の入口” を狭められるイメージ）

---

## 3) App Checkは「Auth」や「Rules」と役割が違う🧩

![Auth vs Rules vs App Check](./picture/firebase_abuse_prevention_ts_study_001_04_role_separation.png)

ここ、超大事だからキャラ分けするね🙂✨

* Firebase Authentication：**ユーザーが誰か**（ログイン）👤
* Firebase Security Rules：**そのユーザーが何をできるか**（権限）🛡️ ([Firebase][5])
* App Check：**その通信が正規アプリからか**（アプリの身分証）🧿 ([Firebase][1])

つまり、App Checkは「Rulesの代わり」じゃなくて、**別レイヤーで入口を守る担当**って感じだよ〜🔒✨ ([Firebase][1])

---

## 4) 段階導入が基本：「まずは“測る” → それから“拒否る”】【超重要】📈🎛️

![Gradual Enforcement](./picture/firebase_abuse_prevention_ts_study_001_05_phased_rollout.png)

App Checkは、いきなり強制すると「正規ユーザーなのに弾かれる」事故が起きることがある😱
だから公式ははっきりこう言ってる：

1. **SDKを入れる（トークンが付くようにする）**
2. **強制する前に、メトリクスを見て“壊れないか”確認する** ([Firebase][6])
3. いけそうなら、サービスごとに **Enforce（強制）** をONにする（ONにしたら未検証リクエストは拒否） ([Firebase][2])

メトリクスでは、リクエストがこう分類されるよ👇 ([Firebase][6])

* Verified：✅ 正常（強制後も通る）
* Outdated client：🧓 古いSDKなどでトークン無し
* Unknown origin：👻 SDKっぽくない（盗まれたキー/偽造っぽい等）
* Invalid：💀 無効トークン

この画面を見て「今Enforceして平気？」を判断するのが王道！ ([Firebase][6])

---

## 5) （雰囲気だけ先見せ）App Checkは “Firebase触る前に初期化” が鉄則🧿⚛️

![Initialization Timing](./picture/firebase_abuse_prevention_ts_study_001_06_code_snippet.png)

Web（reCAPTCHA v3）の公式例はこんな感じ👇
「Firebaseサービスにアクセスする前に初期化しようね」って明記されてるよ。 ([Firebase][7])

```ts
import { initializeApp } from "firebase/app";
import { initializeAppCheck, ReCaptchaV3Provider } from "firebase/app-check";

const app = initializeApp({
  // firebaseConfig（これは“公開される前提”でOKなやつ）
});

initializeAppCheck(app, {
  provider: new ReCaptchaV3Provider("YOUR_RECAPTCHA_SITE_KEY"),
  isTokenAutoRefreshEnabled: true,
});
```

([Firebase][7])

※この章では「実装で詰まらない」ために、**“置き場所はFirebase初期化直後”**ってことだけ覚えればOK🙂✨
（実装は第5章でガッツリやるよ！）

---

## ここから本編：読む → 手を動かす → ミニ課題 → チェック 📚🔥

## ✅ 読む（この章で覚えるコアだけ）🧠🧿

* App Checkは **“正規アプリの証明（トークン）”**で、Firebaseや自前バックエンドへのアクセスを守る。 ([Firebase][1])
* 強制ONの前に **メトリクスで影響を確認**し、段階的に進める。 ([Firebase][6])
* Firebase AI Logic は **App Checkの早期導入を強く推奨**、AIはさらに **レート制限（デフォルト100 RPM）**も見直し推奨。 ([Firebase][3])

---

## ✅ 手を動かす：あなたのアプリで「守る対象」を棚卸し📝🧾

やることはシンプル！この章の成果物は **“守る対象リスト”** だよ✨

## 手順💡

1. ミニアプリの機能を紙（or メモ）に書く📝

   * メモ：Firestore
   * 画像：Storage
   * AI整形：AI Logic
   * 管理者だけ：Functions / 管理画面

2. 次に「入口」を書く🚪

   * ブラウザ画面から直接叩く？
   * ボタン1つで何回でも叩ける？
   * 失敗した時にリトライ連打しそう？😇

3. `docs/app-check-targets.md` を作って、下のテンプレを埋める🧱✨

テンプレ（コピペOK）👇

* 守る対象①：Firestore（メモ読み書き）

  * 乱用されたら：読み取り連打 / 書き込み荒らし / コスト増
  * まず守る手段：Rules（必須）＋ App Check（入口を狭める）
  * 強制ONの優先度：中（まずメトリクス見て判断）

* 守る対象②：Storage（画像アップロード）

  * 乱用されたら：巨大ファイル / 連打 / 不正画像
  * まず守る手段：Rules（必須）＋ App Check
  * 強制ONの優先度：高（狙われやすい）

* 守る対象③：AI Logic（AI整形ボタン）

  * 乱用されたら：連打で請求💸 / モデル枠圧迫
  * まず守る手段：App Check（推奨）＋ レート制限（見直す）
  * 強制ONの優先度：最優先（お財布を守る🫶）
  * レート制限メモ：デフォルト100 RPM → アプリに合わせて下げる検討 ([Firebase][4])

---

## ✅ ここでAI活用：棚卸しを爆速にする🚀🤖

「人間が全部読む」のはしんどいので、AIに下準備をやらせよう😆✨

## Google Antigravity でやる（おすすめ）🛰️

Antigravityは「ミッション管理＋自律エージェント」で、計画→実装→検証まで回しやすい思想だよ。 ([Google Codelabs][8])
ミッション例👇

* 「このリポジトリ内でFirebaseを使っている箇所を列挙して、Firestore/Storage/Functions/AIに分類して」
* 「ユーザー操作起点の“連打されやすいボタン”を特定して」

## Gemini CLI でやる（軽くて速い）⌨️⚡

Gemini CLIはターミナルに統合できるオープンソースAIエージェントで、コーディングだけじゃなく **詳細リサーチやタスク管理**にも使えるよ。 ([Google Cloud][9])
お願いの仕方例👇

* 「Firebase SDKのimportを探して、どの機能を使ってるか一覧にして」
* 「“守る対象の棚卸し”テンプレを埋めるのを手伝って」

（ついでに）Firebase Studio は `.idx/dev.nix` で環境を揃えられて、再現性が上がるのが強み！ ([Firebase][10])

---

## ✅ ミニ課題：攻撃者目線で「狙われそう」を3つ書く👿📝

棚卸しができたら、次は“狙われ方”を想像するよ！

次の型で3つ👇（短くてOK）

* 狙われ方①：AI整形ボタンの連打

  * 被害：請求💸 / モデル枠圧迫
  * 入口：UIのボタン（連打できる）
  * 対策：App Check＋レート制限＋UI側のクールダウン

* 狙われ方②：画像アップロード連打

  * 被害：容量・転送・運用負荷🔥
  * 入口：アップロードフォーム
  * 対策：Rules＋App Check＋サイズ制限（後の章でやる）

* 狙われ方③：メモ読み取り連打

  * 被害：読み取り課金 / データ覗き見リスク
  * 入口：一覧画面（自動更新）
  * 対策：Rules＋App Check＋取得設計見直し

---

## ✅ チェック（この章のゴール達成判定）✅🙂

![Chapter 1 Takeaways](./picture/firebase_abuse_prevention_ts_study_001_07_checklist.png)

次の3つ、口で説明できたら勝ち🎉

1. App Checkは「Rulesの代わり」ではなく、**“正規アプリの証明”のレイヤー**だと言える。 ([Firebase][1])
2. **メトリクス確認 → 段階的にEnforce** が基本だと言える。 ([Firebase][6])
3. AI機能は **App Check推奨＋レート制限（デフォルト100 RPM）を見直す**発想が出てくる。 ([Firebase][3])

---

## 次章予告👀✨

第2章では、App Checkの中身（トークン・TTL・自動更新・段階導入の考え方）を、もう一段だけ具体にして「どこで詰まりやすいか」まで潰すよ⌛🧠

必要なら、この第1章の成果物（`docs/app-check-targets.md`）を、あなたのミニアプリ仕様に合わせて「完成版テンプレ」に整形して渡すところまで一気にやるよ〜🧩🔥

[1]: https://firebase.google.com/docs/app-check "Firebase App Check"
[2]: https://firebase.google.com/docs/app-check/enable-enforcement "Enable App Check enforcement  |  Firebase App Check"
[3]: https://firebase.google.com/docs/ai-logic/app-check "Implement Firebase App Check to protect APIs from unauthorized clients  |  Firebase AI Logic"
[4]: https://firebase.google.com/docs/ai-logic/quotas "Rate limits and quotas  |  Firebase AI Logic"
[5]: https://firebase.google.com/docs/rules?utm_source=chatgpt.com "Firebase Security Rules - Google"
[6]: https://firebase.google.com/docs/app-check/monitor-metrics "Monitor App Check request metrics  |  Firebase App Check"
[7]: https://firebase.google.com/docs/app-check/web/recaptcha-provider "Get started using App Check with reCAPTCHA v3 in web apps  |  Firebase App Check"
[8]: https://codelabs.developers.google.com/getting-started-google-antigravity "Getting Started with Google Antigravity  |  Google Codelabs"
[9]: https://cloud.google.com/blog/ja/topics/developers-practitioners/introducing-gemini-cli "Gemini CLI : オープンソース AI エージェント | Google Cloud 公式ブログ"
[10]: https://firebase.google.com/docs/studio/get-started-workspace "About Firebase Studio workspaces"
