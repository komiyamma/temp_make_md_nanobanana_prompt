# 乱用対策：App Check＋ボット耐性で守りを完成：20章アウトライン

（2026年2月時点の公式ドキュメント内容を踏まえて構成しています✅）([Firebase][1])

---

## この教材で作るミニアプリ（題材）🧩✨

「メモ＋画像＋AI整形」アプリを題材にします📝📷🤖

* メモ：Firestore
* 画像：Storage
* AI整形ボタン：Firebase AI Logic（Gemini呼び出し）
* 管理者だけ使える機能：Functions / 管理画面
* そして全部に **App Check を段階的に効かせる**🧿

---

## 全体アウトライン（章の流れ）🗺️

* **Phase A（1〜6章）**：App Checkの基本とWeb導入（reCAPTCHA v3 / Enterprise）🧿
* **Phase B（7〜12章）**：守る対象を増やす（Firestore / Storage / Functions / AI）🛡️
* **Phase C（13〜16章）**：開発・運用の現実（デバッグ、CI、UX、計測）🧪📈
* **Phase D（17〜20章）**：ボット耐性の仕上げ（再生攻撃、カスタムバックエンド、AI活用）🔒🤖

---

## 20章カリキュラム（読む→手を動かす→ミニ課題→チェック）📚🔥

## 第1章：なぜApp Checkが必要？“正規アプリ以外から叩かれる”を体感😱🧿

* **読む**：App Checkが「不正クライアント対策」で、まずは“トークンを付ける→後から強制”が基本、という流れを掴む([Firebase][2])
* **手を動かす**：自分のアプリで「守りたいAPI（Firestore/Storage/Functions/AI）」を洗い出してメモ📝
* **ミニ課題**：攻撃者目線で「何が狙われそう？」を3つ書く👿
* **チェック✅**：App Checkは「Rulesの代わり」じゃなく「正規クライアント証明」側だと説明できる🙂

---

## 第2章：App Checkの仕組み（トークン・TTL・段階導入）⌛🧠

* **読む**：トークンTTLは調整でき、短いほど安全だが負荷/遅延が増える感覚を掴む([Firebase][2])
* **手を動かす**：TTLを「まずはデフォルト→後で見直す」方針で決める✍️
* **ミニ課題**：自分のアプリで「トークンが漏れたら何が起きる？」を一言で🙂
* **チェック✅**：TTLのトレードオフを説明できる🗣️

---

## 第3章：reCAPTCHA v3 入門（スコアとしきい値）🤖📊

* **読む**：v3は0.0〜1.0のスコアで、App Check側に“しきい値”がある([Firebase][2])
* **手を動かす**：しきい値の初期値（例：0.5推奨）を採用して、後でメトリクス見て調整する方針にする🎛️([Firebase][2])
* **ミニ課題**：しきい値を上げすぎたときのUX事故を想像して1行で🙂
* **チェック✅**：「ボット排除＝ユーザー排除」になり得ると理解できた👍

---

## 第4章：reCAPTCHA Enterprise って何？いつ使う？🏢🔐

* **読む**：Enterpriseは“リスク許容度”をより運用前提で調整しやすい（しきい値、課金/設定の注意など）([Firebase][3])
* **手を動かす**：v3で開始→必要ならEnterpriseに移行、の判断基準を作る🧭
* **ミニ課題**：自分のアプリは v3 / Enterprise どっち寄り？理由つきで🙂
* **チェック✅**：Enterpriseは「本気運用寄り」だと説明できる🛡️

---

## 第5章：ReactにApp Checkを入れる（v3版）⚛️🧿

* **読む**：Webは `initializeAppCheck` で provider を入れて、**auto refreshは明示的にON** が基本([Firebase][2])
* **手を動かす**：アプリ起動時（Firebase初期化直後）にApp Check初期化を入れる
* **ミニ課題**：初期化の置き場所を「1箇所」にまとめる（services/firebase.ts など）📦
* **チェック✅**：Firestore/Storageを触る前に初期化が必要と言える🙂

---

## 第6章：Enterprise版に差し替える（移行できる設計にする）🔁🏢

* **読む**：Enterpriseも同じく `initializeAppCheck` で provider差し替え、auto refresh明示ON([Firebase][3])
* **手を動かす**：provider生成を関数化して、v3/Enterpriseを切替可能にする🎛️
* **ミニ課題**：切替の方針（環境変数/Remote Config/ビルドフラグ）を決める
* **チェック✅**：providerが“差し替え可能な部品”になっている✅

---

## 第7章：まずはメトリクス監視だけ（いきなり強制しない）👀📈

* **読む**：トークンは送るが、**強制（enforcement）しない限り**多くのFirebaseサービスは拒否しない流れ([Firebase][2])
* **手を動かす**：App Checkのメトリクス画面で「通ってる/弾かれてる」を見る習慣を作る👀
* **ミニ課題**：「強制ONにする前のチェック項目」5つ作る🧾
* **チェック✅**：段階導入の意味が腹落ちした😌

---

## 第8章：Firestoreを守る（RulesとApp Checkの役割分担）🗃️🛡️

* **読む**：守る対象としてCloud Firestoreが明確に含まれる([Firebase][2])
* **手を動かす**：Firestoreアクセスを1画面に集約して、ON/OFFで挙動差が見えるようにする🧪
* **ミニ課題**：「Rulesは“誰が何できる”」「App Checkは“正規アプリか”」を例で書く✍️
* **チェック✅**：守りのレイヤーが2段あると説明できる🙂

---

## 第9章：Storageを守る（アップロードが狙われる😱）📷🛡️

* **読む**：Cloud Storageもメトリクス/強制対象に入っている([Firebase][2])
* **手を動かす**：プロフィール画像アップロードでON/OFF差を観察👀
* **ミニ課題**：不正アップロード（巨大ファイル/連打）を想定して対策案を3つ
* **チェック✅**：「Storageは特に狙われやすい」が言える🙂

---

## 第10章：Functionsを守る（CallableでenforceAppCheck）☎️🔒

* **読む**：Callable Functionsは `enforceAppCheck` で missing/invalid を拒否できる([Firebase][4])
* **手を動かす**：管理者用Callableを1つ作り、enforceをONにして挙動確認🧑‍💼
* **ミニ課題**：管理者機能を「Callableに寄せる」設計を1つ考える🧠
* **チェック✅**：「守りたい処理はCallableに寄せる」が言える👍

---

## 第11章：再生攻撃（リプレイ）対策：トークン使い回しを防ぐ♻️🚫

* **読む**：App Checkトークンを“消費（consume）”して一回限りにする仕組みがある（β）([Firebase][4])
* **手を動かす**：特に重要なCallableだけ replay protection を検討する（全部ONにしない）🧠
* **ミニ課題**：「絶対に使い回しされたくないAPI」を2つ選ぶ
* **チェック✅**：性能コスト（追加往復）も含めて判断できる🙂([Firebase][4])

---

## 第12章：AIを守る（Firebase AI Logic × App Check）🤖🧿

* **読む**：AI Logic は **App Check導入が推奨**され、**ユーザーごとのレート制限も設定可能**([Firebase][1])
* **手を動かす**：メモ整形ボタン（要約/言い換え）を作り、App Check ON/OFFで比較👀
* **ミニ課題**：「AIはコストが読みにくい」→“最初は控えめに解放”の案を作る🎛️
* **チェック✅**：AIは“守り（App Check）＋回数制御（Rate limit）”で考える🙂([Firebase][1])

---

## 第13章：ローカル開発：Debug Provider（ローカルでも詰まらない）🧪🧿

* **読む**：WebのDebug Providerは、コンソールに出るデバッグトークンを登録して使う流れ([Firebase][5])
* **手を動かす**：ローカル起動→デバッグトークン確認→Firebase Consoleに登録✅
* **ミニ課題**：デバッグトークンを漏らさない運用ルールを作る🔐
* **チェック✅**：「ローカルはDebug Provider」が自然に選べる🙂

---

## 第14章：CIでもApp Check（GitHub Actionsなど）🏗️🔒

* **読む**：CI用にデバッグトークンを作って、秘密情報として扱う流れが公式にある([Firebase][5])
* **手を動かす**：CI環境変数にデバッグトークンを置く設計にする（コードに直書きしない）
* **ミニ課題**：PRで「App Checkが効いてる最低限のE2E」1本作る🧪
* **チェック✅**：CIで詰まらない筋道ができた✅

---

## 第15章：失敗時UX（通らない時の表示）🙂🧯

* **読む**：強制後は「未検証リクエストは拒否」が基本なので、UIが無言で死ぬと最悪😇([Firebase][4])
* **手を動かす**：典型エラー時に「再読み込み」「時間を置く」「サポート導線」を出す
* **ミニ課題**：エラー文を“人間の日本語”で3パターン作る📝
* **チェック✅**：「守りの強化＝UX設計が必須」が言える🙂

---

## 第16章：段階的に強制ON（守りと改善の両立⚖️）🎛️📈

* **読む**：強制前にメトリクス監視、必要なら一時的にunenforceして影響を抑える考え方がある([Firebase][2])
* **手を動かす**：Firestore→Storage→AI→Functions の順で“段階強制”の計画を作る
* **ミニ課題**：リリース手順書（いつ誰が何をONにする）を短く書く🧾
* **チェック✅**：“怖くない強制ON”の手順ができた✅

---

## 第17章：Functionsの言語とバージョン感（Node/Python/.NET）🧰🔢

* **読む**：Cloud Functions for Firebase は Node.js / Python を選べ、Nodeは 22/20/18、Pythonは 3.10/3.11 が明示されている([Firebase][6])
* **手を動かす**：App Check強制が絡むCallableを Node/TS でまず固める（王道）([Firebase][4])
* **＋発展（.NET）**：.NETで書きたい場合は **Cloud Run functions** 側のランタイム選択肢（例：.NET 8 / .NET 10 preview など）を理解して、Firebaseとは“連携”として組む方針にする([Google Cloud Documentation][7])
* **ミニ課題**：「Firebase Functionsでやる」「Cloud Runでやる」の線引きを自分なりに書く
* **チェック✅**：言語選択で迷わない軸ができた🙂

---

## 第18章：自前バックエンドを守る（X-Firebase-AppCheck を検証）🧱🛡️

* **読む**：カスタムバックエンドは `X-Firebase-AppCheck` を受け取り、Admin SDKで verify する流れが公式([Firebase][8])
* **手を動かす**：Node（Express）で1エンドポイント作って verifyToken する([Firebase][8])
* **＋発展（.NET想定）**：他言語はJWTライブラリ＋JWKSエンドポイントで検証、という公式手順がある（= .NETでも可能）([Firebase][8])
* **ミニ課題**：.NETなら「JWT検証→issuer確認→期限確認」までのチェックリストを作る✅
* **チェック✅**：App CheckはFirebase外のAPIも守れると説明できる🙂

---

## 第19章：AIで“守りの実装”を加速（Antigravity / Gemini CLI / Studio）🚀🤖

* **読む**：

  * Antigravityは“Mission Controlでエージェントが計画・実装・Web調査もできる”思想([Google Codelabs][9])
  * Gemini CLI はターミナル統合のオープンソースAIエージェントとして紹介されている([Google Cloud][10])
  * Firebase Studio は Nixで環境再現しやすい([Firebase][11])
* **手を動かす**：

  * Antigravity：App Check導入タスクを“ミッション化”（チェックリスト→実装→動作確認）
  * Gemini CLI：リポジトリを見せて「App Check初期化漏れ」「危険な直アクセス箇所」を指摘させる🔎
  * Studio：`.idx/dev.nix` に必要ツールを揃えて再現性UP🧰
* **ミニ課題**：AIに作らせた差分を“人間レビュー”して、落とし穴を1つ見つける👀
* **チェック✅**：AIは“爆速化”、最終判断は自分、ができてる🙂

---

## 第20章：総合演習：ON/OFFで挙動差を観察して、運用手順まで完成🏁👀

* **読む**：強制ONは影響が出るので、メトリクス監視しつつ進めるのが基本([Firebase][2])
* **手を動かす**：

  * App Check **OFF** → 動く
  * App Check **ON（強制）** → 正規以外が落ちる
  * Debug Provider → ローカルでも動く
* **ミニ課題**：運用チェックリスト（10項目）を作って完成✨
* **チェック✅**：「守り」＋「UX」＋「運用」まで一通りできた🎉

---

## おまけ：この教材の“完成状態”の目安🏆

* Firestore/Storage/AI/Functions で **App Checkが段階的に強制**されている🧿
* ローカル/CIは **Debug Providerで詰まらない**🧪([Firebase][5])
* AI機能は **App Check＋（必要なら）ユーザー単位レート制限**で破産しない🤖💸([Firebase][1])
* “しきい値”はメトリクス見ながら調整できる🎛️([Firebase][2])

---

次は、この20章のうち **第1章〜第5章を「本文つきの教材（図解っぽく）」**にして一気に作るのが気持ちいいです😆🔥
（もしくは「第10章 Functions」「第12章 AI」を先にやって、守りの効果が一番見える順に進めるのもアリ👍）

[1]: https://firebase.google.com/docs/ai-logic "Gemini API using Firebase AI Logic  |  Firebase AI Logic"
[2]: https://firebase.google.com/docs/app-check/web/recaptcha-provider "Get started using App Check with reCAPTCHA v3 in web apps  |  Firebase App Check"
[3]: https://firebase.google.com/docs/app-check/web/recaptcha-enterprise-provider "Get started using App Check with reCAPTCHA Enterprise in web apps  |  Firebase App Check"
[4]: https://firebase.google.com/docs/app-check/cloud-functions "Enable App Check enforcement for Cloud Functions  |  Firebase App Check"
[5]: https://firebase.google.com/docs/app-check/web/debug-provider "Use App Check with the debug provider in web apps  |  Firebase App Check"
[6]: https://firebase.google.com/docs/functions/manage-functions "Manage functions  |  Cloud Functions for Firebase"
[7]: https://docs.cloud.google.com/run/docs/runtimes/function-runtimes?hl=ja "Cloud Run functions ランタイム  |  Google Cloud Documentation"
[8]: https://firebase.google.com/docs/app-check/custom-resource-backend "Verify App Check tokens from a custom backend  |  Firebase App Check"
[9]: https://codelabs.developers.google.com/getting-started-google-antigravity?utm_source=chatgpt.com "Getting Started with Google Antigravity"
[10]: https://cloud.google.com/blog/ja/topics/developers-practitioners/introducing-gemini-cli "Gemini CLI : オープンソース AI エージェント | Google Cloud 公式ブログ"
[11]: https://firebase.google.com/docs/studio/get-started-workspace?utm_source=chatgpt.com "About Firebase Studio workspaces - Google"
