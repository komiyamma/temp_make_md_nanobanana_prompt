# 第16章：段階的に強制ON（守りと改善の両立⚖️）🎛️📈

この章は「App Checkを“強制ON”にしても炎上しない」ための、**実戦的な切り替え手順書**を作ります🔥
ポイントはこれ👇

* いきなり強制しない（まず“見える化”）👀
* **メトリクスを見てから**強制ONする📈 ([Firebase][1])
* 何かあったら**すぐ戻せる手順**（ロールバック）を用意しておく🧯
* AI（Firebase AI Logic）はコスト爆発しやすいので、**App Check + レート制限**も一緒に設計する🤖💸 ([Firebase][2])

---

## 読む📚：強制ONって、何が起きるの？😳

## 1) 「強制ON」するとどうなる？

Firebase コンソールの App Check で、対象サービス（Firestore/Storage/AI Logic など）を **Enforce（強制）** にすると、**App Checkトークンが正しく付いてないリクエストは拒否**されます🧿🚫 ([Firebase][3])
そして、反映には最大15分かかることがあります⏱️ ([Firebase][3])

## 2) 強制ONの前に見るべき「メトリクス4分類」📊

App Checkのメトリクスは大きく4つに分かれます👇 ([Firebase][1])

* ✅ Verified：OK（強制ON後も通る）
* 🧓 Outdated client：古いSDK/古いアプリでトークンが付いてない可能性（強制ONすると壊れやすい）
* 👻 Unknown origin：SDKっぽくない（盗まれたキー/直叩き等の可能性）
* ❌ Invalid：トークン不正（偽装やエミュレータ等の可能性）

判断のコツも公式が言ってます👇 ([Firebase][1])

* Verifiedがほとんど → 強制ONして守り始めてOKかも
* Outdatedが多い → まだ待つ（ユーザーの更新待ち）
* 未リリースなら → 最初から強制ONでOK（古いクライアントがいない）

---

## 手を動かす🛠️：段階的に強制ONする“事故らない手順”🧯

ここからは **「Firestore → Storage → AI Logic →（必要なら）Functions」** の順で、段階的に強制していく想定でいきます🎛️

## Step 0：強制ONの“前に”用意するもの（超重要）🧰

強制ONはスイッチ1つで全ユーザーに効くので、準備が命です😇

* 🧪 ローカル開発が止まらない：Debug Provider を使える状態（第13章の成果）
* 🧾 失敗時UXがある：通らない時に「再読み込み / アプデ依頼 / サポート導線」が出る（第15章の成果）
* 🧯 ロールバック手順が紙に書いてある：誰が、どこを、どう戻すか（後でテンプレ作るよ）

---

## Step 1：まずは“観測モード”（強制しない）でメトリクスを見る👀📈

App Check を組み込んだら、強制ONの前にメトリクスで現状把握します。
公式も「強制前に、既存ユーザーを壊さないことを確認してね」と言ってます🫶 ([Firebase][1])

見る場所：Firebase Console → App Check → 対象サービスのメトリクス

ここでのゴール🎯

* Verified が主流になってる ✅
* Outdated client が減ってきてる ✅

---

## Step 2：Firestore を強制ON（1つ目の本番スイッチ）🗃️🧿

やることはシンプル👇（公式の手順そのまま）

1. Firebase Console の App Check を開く
2. Firestore のメトリクスを開く
3. Enforce を押す（確認して確定） ([Firebase][3])

反映は最大15分かかることがあるので、**“押した直後に全部を決めつけない”**のがコツです⏱️ ([Firebase][3])

✅ 強制ON直後にチェックするもの（5分チェック）

* 新しいブラウザでアプリが普通に動く？🧑‍💻
* ログイン済みユーザーがメモを読める？📝
* エラーが出たらUXが出る？🙂
* メトリクスで Verified が増えてる？📈
* Unknown/Invalid が増えてるなら「攻撃が見えてきた」かも👿

---

## Step 3：Storage を強制ON（アップロードは狙われやすい📷😱）

Firestoreで問題がなければ、次はStorage。
画像アップロード連打や巨大ファイルで燃えやすいので、守りの価値が高い🔥

手順は同じ：Storage のメトリクス → Enforce ([Firebase][3])

✅ Storage強制ONで追加チェック

* 画像アップロードが通る？📤
* 画像表示（ダウンロード）が通る？🖼️
* 「通らなかった時」の画面が優しい？🥹（無言で失敗は最悪）

---

## Step 4：Firebase AI Logic を強制ON（コスト防衛ライン🤖💸）

AIは「呼ばれる＝課金や負荷が増える」ので、App Checkで守るのがかなり大事🧿
Firebase AI Logic は **App Checkと連携するプロキシ（ゲートウェイ）**として動き、**強制ONすると未検証は拒否**されます🚪🧱 ([Firebase][2])

さらにAIは **レート制限（per user）**もセットで考えると安心です👍

* デフォルトは **1ユーザーあたり 100 RPM**（プロジェクト全体に適用） ([Firebase][4])
* 個別ユーザーだけ制限、みたいなのは基本できません（現状） ([Firebase][4])

✅ AI強制ONで追加チェック

* 「AI整形ボタン」だけが落ちた時、他の機能は生きてる？🫀
* AIが落ちた時に「時間をおいてね」「再試行」みたいな導線ある？🙂
* レート制限を最初は控えめにして、様子見できてる？🎛️ ([Firebase][4])

---

## Step 5：（おまけ）reCAPTCHA Enterprise のしきい値調整は“危険なつまみ”🎚️😇

Enterprise側で「リスク許容度（しきい値）」を上げ下げする時、公式がこう注意してます👇
**いったん強制を外してから調整して、メトリクスで無事を確認してから再開**が安全🧯 ([Firebase][5])

これは「段階的運用」の超重要テクです👍

---

## ここが本題🧾：リリース手順書テンプレ（短くて強い）💪

そのままコピペして使える形にするとこう👇

1. **観測期間**（例：2〜7日）

* App Check メトリクスで Verified/Outdated/Unknown/Invalid を確認 ([Firebase][1])

2. **切替順**

* Day1：Firestore Enforce
* Day2：Storage Enforce
* Day3：AI Logic Enforce（+ レート制限を保守的に） ([Firebase][4])

3. **切替直後の確認（15分〜）**

* 主要導線テスト（読む/書く/アップロード/AI）
* エラー時UX確認
* メトリクス確認 ([Firebase][1])

4. **緊急ロールバック**🧯

* 影響が大きい場合は **一時的に unenforce**（強制を外す）→ 落ち着かせる
  ※ Enterprise の公式手順でも「一時的に unenforce を検討」と明記されています ([Firebase][5])
* 原因調査 → 再度段階導入

---

## AI活用🤖：Antigravity / Gemini CLI で“手順書作り”を爆速にする🚀

ここ、2026年はかなり熱いです🔥
Firebaseは **Gemini CLI拡張（Firebase extension）**を公式で用意していて、入れると **Firebase MCP server が自動で設定**され、Firebase用の事前プロンプトや「Firebaseプロジェクトを操作するツール」まで使えるようになります🧠🧰 ([Firebase][6])

さらに **Firebase MCP server は Antigravity でも使える**って公式に書かれてます✨ ([Firebase][7])
プロンプトのカタログも公式で提供されています📚 ([Firebase][8])

## Gemini CLI（Windows）で Firebase拡張を入れる🧩

PowerShellでこれ👇（公式） ([Firebase][6])

```text
gemini extensions install https://github.com/gemini-cli-extensions/firebase/
```

アップデートもこれ👇 ([Firebase][6])

```text
gemini extensions update firebase
```

## 何に使うと美味しい？🍣（第16章向け）

* 「強制ONのチェックリスト」をAIに作らせる🧾
* リポジトリを読ませて「App Check初期化漏れっぽい場所」を洗い出す🔎
* “ロールバック手順”を文章で整える（人間レビュー前提）🧯
* Firebase MCP の事前プロンプト（カタログ）を叩いて、運用タスクの抜けを減らす📚 ([Firebase][8])

Antigravity 側も、Firebase MCP server を追加してプロジェクト初期化やデプロイまで支援できる流れが紹介されています🚀 ([The Firebase Blog][9])

---

## ミニ課題📝：あなた専用の「強制ON手順書」を完成させよう🏁

次の3つを1枚にまとめてください（短くてOK）✨

1. 強制ONの順番（Firestore→Storage→AI Logic）🎛️
2. 各ステップの「5分チェック項目」👀
3. 緊急ロールバック手順（誰が・どこで・何を戻す）🧯

---

## チェック✅：ここまでできたら勝ち🎉

* メトリクス4分類の意味を説明できる📊 ([Firebase][1])
* Verifiedが十分になるまで“待つ判断”ができる🧘 ([Firebase][1])
* Enforceの手順と、反映に最大15分あり得るのを知ってる⏱️ ([Firebase][3])
* AIは App Check + レート制限で“破産回避”の絵が描ける🤖💸 ([Firebase][2])
* Enterpriseのしきい値調整は「一時unenforce→確認→再強制」が安全って言える🎚️🧯 ([Firebase][5])

---

必要なら次の返答で、**あなたのミニアプリ用に「強制ON手順書（完成版）」をそのまま貼れる形**で作るよ🧾✨
「Firestore/Storage/AI の画面導線（どこを開くか）」も、迷子にならないようにスクショなしでも説明できる形に整えます📌

[1]: https://firebase.google.com/docs/app-check/monitor-metrics "Monitor App Check request metrics  |  Firebase App Check"
[2]: https://firebase.google.com/docs/ai-logic/app-check "Implement Firebase App Check to protect APIs from unauthorized clients  |  Firebase AI Logic"
[3]: https://firebase.google.com/docs/app-check/enable-enforcement "Enable App Check enforcement  |  Firebase App Check"
[4]: https://firebase.google.com/docs/ai-logic/quotas "Rate limits and quotas  |  Firebase AI Logic"
[5]: https://firebase.google.com/docs/app-check/web/recaptcha-enterprise-provider "Get started using App Check with reCAPTCHA Enterprise in web apps  |  Firebase App Check"
[6]: https://firebase.google.com/docs/ai-assistance/gcli-extension "Firebase extension for the Gemini CLI  |  Develop with AI assistance"
[7]: https://firebase.google.com/docs/ai-assistance/mcp-server "Firebase MCP server  |  Develop with AI assistance"
[8]: https://firebase.google.com/docs/ai-assistance/prompt-catalog?hl=ja "Firebase の AI プロンプト カタログ  |  Develop with AI assistance"
[9]: https://firebase.blog/posts/2025/11/firebase-mcp-and-antigravity/ "Antigravity and Firebase MCP accelerate app development"
