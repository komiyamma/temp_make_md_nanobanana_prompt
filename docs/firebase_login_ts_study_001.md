# 第01章：ゴール確認：このカテゴリで作る“認証の骨格”🔩

この章は「コードをガッツリ書く」より先に、**この20章で作る“認証の背骨”がどんな形か**を、頭の中にくっきり描く回だよ🙂🦴✨
背骨が描けると、次章以降の実装が一気にラクになる！💪🔥

---

![Authentication Concept](./picture/firebase_login_ts_study_001_01_concept.png)

## 1) まず“認証”で何ができる？（全体像）🔐🌈

Firebase Authentication は、ざっくり言うと **「ユーザーにログインしてもらって、アプリ側で“この人は誰か”を確定する仕組み」**だよ👤✅
代表的には **メール/パスワード**、そして **Googleログイン**みたいな外部プロバイダのログインが使える（このカテゴリはここを固める！）✨ ([Firebase][1])

さらにこの先、ログイン状態ができると👇みたいなことが可能になるよ🧠

* ログインしてる人だけが見られるページ（マイページ等）🚧
* “誰のデータか”をユーザーID（uid）でひも付けて管理📦
* 失敗時のエラーを「人間の言葉」で出して迷子を減らす😇

---

![Three Auth States](./picture/firebase_login_ts_study_001_02_three_states.png)

## 2) “認証の骨格”＝この3つの状態をUIで扱えること🦴🔁

認証まわりで大事なのは、画面が **常にこの3状態のどれか**になることだよ🙂

1. **読み込み中（loading）**：
   アプリ起動直後など、ログイン済みか確認してる最中⏳
2. **未ログイン（guest）**：
   ログイン画面にいる、保護ページに行けない🚪
3. **ログイン済み（user）**：
   マイページ表示OK、ログアウトもできる✅

この3つをハンドリングできたら、もう“背骨”は通ったも同然！💪✨

---

![Chapter Goal Checklist](./picture/firebase_login_ts_study_001_03_goal.png)

## 3) このカテゴリ（20章）で最終的にできるようになること🎯✨

最終ゴールはこう👇

* メール/パスワードで **登録・ログイン・ログアウト**🔑
* Googleログインも通す🌈
* リロードしてもログイン状態が復元される（保持）💾
* 未ログインで保護ページに行っても弾ける（ガード）🚧
* エラーがやさしくて、次の行動が分かる（UX設計）😇
* さらに **Firebase AI Logic（Gemini）** を混ぜて、説明文やエラーメッセージを賢くできる🤖📝 ([Firebase][2])

---

![Screen Flow Diagram](./picture/firebase_login_ts_study_001_04_screen_flow.png)

## 4) 手を動かす：まず“3画面”を決めよう🧱🖊️

この章の実作業は **たった1つ**！

## ✅ 作る（決める）画面はこの3つでOK

* **ログイン画面**（Login）🚪
* **サインアップ画面**（Sign up）✍️
* **マイページ**（My page / Account）👤

そして「どう行き来するか」も決めちゃう👇

* 未ログイン → ログイン画面
* ログイン画面 →（初めてなら）サインアップ
* ログイン成功 → マイページ
* マイページ → ログアウト → ログイン画面

---

![Skeleton Blueprint](./picture/firebase_login_ts_study_001_05_skeleton.png)

## 5) “画面設計メモ”を1枚だけ作る📄✨（超重要）

プロジェクトに `docs/auth-skeleton.md` を作って、これを書いてね✍️
（書けたら次章以降、実装が迷子にならない🧭）

```md
## 認証の骨格メモ（第1章）

## 画面
- /login   : ログイン画面
- /signup  : サインアップ画面
- /me      : マイページ（ログイン必須）

## 画面ごとの要素（最低限）
## ログイン
- 入力：email / password
- ボタン：ログイン、Googleでログイン
- リンク：アカウント作成へ（/signup）
- 表示：エラー欄、loading表示

## サインアップ
- 入力：email / password
- ボタン：登録
- リンク：ログインへ（/login）
- 表示：エラー欄、loading表示

## マイページ
- 表示：displayName / email（出せれば）
- ボタン：ログアウト

## 状態（UIの切替ルール）
- loading中：スピナー（ページを出さない）
- userがnull：/me へ行こうとしたら /login に飛ばす
- userが存在：/login や /signup にいるなら /me に飛ばす（好みで）
```

---

![AI Error Fixing](./picture/firebase_login_ts_study_001_06_ai_error.png)

## 6) AIを“最初から”混ぜるコツ（この章から使ってOK）🤖✨

## 6-1) Firebase AI Logic って何がうれしいの？💡

アプリ（Web/モバイル）から **Gemini（やImagen）を呼ぶ**とき、**クライアント向けSDK**として用意されてて、Firebaseサービスと組み合わせやすいよ、という立ち位置だよ🧩✨ ([Firebase][2])
このカテゴリでは「エラー文をやさしくする」「注意書きを自動生成する」みたいな **UX改善**に使うよ😇📝

## 6-2) いま作れる“小ワザ案”（まだ実装しなくてOK）

* ログイン画面の説明文をAIで生成：
  「パスワードは12文字以上が安心だよ🙂」みたいな補足を出す🧠
* エラーの言い換え：
  “invalid-email” を「メールの形が変かも！もう一回見てね🙂」にする😇

## Geminiに投げるプロンプト例（コピペOK）🧠💬

```txt
あなたはやさしいUIライターです。
Firebase認証エラーを、初心者向けに日本語で短く言い換えてください。
条件：
- 1文で
- 次に何をすればいいかが分かる
- 責めない口調
エラーコード: auth/invalid-email
```

---

![AI Tools Collaboration](./picture/firebase_login_ts_study_001_07_ai_tools.png)

## 7) Antigravity / Gemini CLI の使いどころ（第1章のおすすめ）🚀🔎

## Antigravity：この章は“設計メモ作り”を任せると強い🛰️

Antigravityは、エージェントに「ミッション」を渡して、計画→実装→調査まで進めやすい開発体験を狙ったものだよ🧑‍✈️✨ ([Google Codelabs][3])
**第1章の使い方**はシンプル👇

* ミッション：「認証の骨格メモを作って。3画面と遷移と状態を整理して」
* 出力を自分が読んで、違和感がないかだけチェック🙂

## Gemini CLI：リポジトリ全体の“抜け”探しが得意🔍

Gemini CLI はターミナルから使えるAIエージェントで、コード理解や支援に寄せた説明が公式にあるよ🧰✨ ([Google Cloud Documentation][4])
**第1章の使い方**は👇

* 「認証の状態が3つ（loading/guest/user）になってる？」
* 「画面遷移がメモと一致してる？」
  みたいな **設計の自己レビュー**に使うのが気持ちいい😎

---

## 8) ミニ課題 🎮✅（5分で終わる）

1. `docs/auth-skeleton.md` を作る📄
2. 3画面（Login/Signup/Me）と遷移を書ききる🧱
3. “状態ルール”に **loading** を必ず入れる⏳（ここ忘れがち！）

---

## 9) チェック✅（できたら次章へGO🔥）

* [ ] 「未ログイン / ログイン済み / 読み込み中」の3状態が言える🙂
* [ ] 3画面（login/signup/me）の役割がブレてない🧭
* [ ] `/me` が“ログイン必須”だと明記できた🚧
* [ ] AIで改善したいUX（例：エラー言い換え）を1つ決めた🤖✨

---

次の第2章では、Firebase Consoleで **Authプロバイダ（メール＋Google）をON**にして、最短で「ログインが動く土台」を作るよ🔧🔥

[1]: https://firebase.google.com/docs/auth/web/start?utm_source=chatgpt.com "Get Started with Firebase Authentication on Websites"
[2]: https://firebase.google.com/docs/ai-logic?utm_source=chatgpt.com "Gemini API using Firebase AI Logic - Google"
[3]: https://codelabs.developers.google.com/getting-started-google-antigravity?utm_source=chatgpt.com "Getting Started with Google Antigravity"
[4]: https://docs.cloud.google.com/gemini/docs/codeassist/gemini-cli?utm_source=chatgpt.com "Gemini CLI | Gemini for Google Cloud"
