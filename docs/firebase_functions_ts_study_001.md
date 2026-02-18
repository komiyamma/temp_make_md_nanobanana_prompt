# 第01章：Functionsって何？「裏側」を置く場所の全体像🗺️

この章は「**フロント（React）だけじゃ無理な処理**を、どこに置くのが正解か？」の地図を作ります🙂✨
ここが腹落ちすると、以降のHTTP / イベント / スケジュールが全部スッと入ります！

---

## 1) Functionsって一言でいうと？🧠

**Functions = アプリの“裏側（サーバー側）”に置く小さなプログラム**です🧩
ブラウザ（フロント）からは見えない場所で動いて、必要な時だけ呼び出されます。

しかも、いわゆる **サーバレス**なので「自分でサーバーを立てて管理する」感じじゃありません。
コードを置いたら、あとはGoogle側が動かしてくれるイメージです☁️✨ ([Firebase][1])

---

## 2) フロントだけで頑張ると、どこで詰む？😵‍💫🧱

ここが超大事！フロントは便利だけど、**向いてない仕事**が明確にあります👇

### ✅ フロントに置いちゃダメ（または危険）な代表例

1. **秘密情報（APIキー、Webhook URL、署名鍵など）**🔑
   → ブラウザに入れた瞬間、「見ようと思えば見れる」世界です😇
2. **信頼できない入力の処理（検証、制限、スパム対策）**🛡️
   → フロントのチェックは“優しさ”であって、セキュリティじゃないです💦
3. **重い処理（画像変換、集計、外部API連打、AI推論など）**🏋️
   → ブラウザが固まる、通信が切れる、端末差が出る…地獄🥶
4. **自動で動いてほしい処理（通知、定期バッチ）**⏰
   → ユーザーが画面を開いてないと何も起きません😢

だから「裏側に置く場所」としてFunctionsが必要になります🙂

---

## 3) Functionsの“3つの起動ボタン”🎛️✨

Functionsは「いつ動くか？」が超シンプルです。基本はこの3つだけ！

### A. HTTPトリガー（APIの入口）🌐

**URLを叩いたら動く**やつです。
「自分のAPIを作る」＝まずこれ！✨

* 例：`GET /health`、`POST /echo`、`/api/report` など

### B. イベントトリガー（自動で反応）⚡

Firestoreの更新など、**何かが起きたら勝手に動く**やつです。

* 例：`messages/{id}` が作られたら通知する📨
  Firestoreには `onDocumentCreated` / `onDocumentWritten` みたいなイベントがあります ([Firebase][2])

### C. スケジュール（定期実行）⏰

**毎日9時**とか、**毎時**とか、Cronで動くやつです。
`onSchedule` を使うと、Cloud Scheduler経由で起動されます☁️ ([Firebase][3])

---

## 4) ここでミニ演習✍️「どこに置く？」仕分けゲーム🎮

次の処理を、直感で **A:フロント / B:Functions / C:Firebaseの別機能（ルール等）** に仕分けてみてください🙂✨
（この章の“手を動かす”はコレです！）

1. ユーザーが入力した文章をFirestoreに保存📝
2. 保存された文章にNGワードがあったら弾く🚫
3. Firestoreに新規投稿が来たらSlackに通知📨
4. 「今日の人気投稿ランキング」を毎朝作り直す🌅
5. 画像をアップロードしたらサムネを作る🖼️
6. ログインしてない人は「投稿ボタン」を押せないようにする🔒
7. 外部API（天気など）を叩いて結果を保存する🌦️
8. 課金状態（サブスク）を確認して機能を解放する💳
9. 「AIで文章を要約して保存」する🤖
10. だれでも読める公開ページを表示する📄

---

## 5) 仕分けの答え合わせ✅（理由つき）

**1. フロント（A）**
→ Firestoreに保存自体はフロントでも普通にできます（もちろんRules前提）🙂

**2. Functions（B）**
→ NGワード判定は「攻撃される前提」で裏側でやるのが強いです🛡️
（フロントだけだと改造されて素通りできます）

**3. Functions（B）**
→ 通知は裏側の仕事！Firestoreイベントで自動化が王道⚡ ([Firebase][2])

**4. Functions（B）**
→ 定期実行はスケジュール関数の得意分野⏰ ([Firebase][3])

**5. Functions（B）**
→ 画像変換は重い＆セキュリティ的にも裏側が安全🖼️

**6. Firebaseの別機能（C） + フロント（A）**
→ UIで押せなくするのはフロント（親切）🙂
→ “本当に守る”のはRulesや認証（Firebase側）です🔒
（この教材シリーズでも何度も出てくる鉄板）

**7. Functions（B）**
→ 外部APIキーを隠す＆失敗時にリトライ設計しやすい🏗️

**8. Functions（B）**
→ 課金判定は「改造される前提」なので裏側でチェックが安全💳

**9. Functions（B）**
→ AIは重い/コスト/失敗があるので、裏側でガードしやすい🤖
（後半でGenkitも絡めて強くします🔥）

**10. フロント（A）**
→ 表示はフロントの仕事！公開ページは得意分野📄

---

## 6) AI時代のFunctionsは“ガードレール役”がめちゃ重要🤖🛡️

AIをアプリに入れるとき、ありがちな事故はこれ👇

* 無制限に呼ばれて **請求が爆発**💸
* ユーザー入力で **危ないプロンプト**が入る😇
* 失敗や遅延で **UXが崩壊**😵

そこでFunctionsが活きます！

### 例：AI要約を安全に動かす流れ（ざっくり）

* フロント：要約してほしい文章を送る📤
* Functions：

  * 入力サイズ制限📏
  * ログイン必須・回数制限🧯
  * 必要なら危ないワードをフィルタ🚫
  * AIを呼ぶ🤖
  * 結果をFirestoreに保存🗃️

Firebaseには **Firebase AI Logic** があり、Gemini/Imagen系のモデルをアプリから扱えるようにする仕組みがあります ([Firebase][4])
さらに、Functions側では **GenkitフローをCallableとして呼べる `onCallGenkit`** みたいな入口も用意されています ([Firebase][5])

（この教材の後半で、ここを“実務の形”にします🔥）

---

## 7) AIで学習・設計を爆速にするコツ🛸💻✨

このシリーズでは「AI導入済み」が前提なので、最初から“良い使い方”で行きましょう🙂

### ✅ まずはAIに「仕分け」を手伝わせる（超おすすめ）

たとえば👇みたいに聞くと強いです✨

* 「この処理、フロント/Functions/Rulesのどこが適切？理由もセットで」
* 「秘密情報が絡む点を指摘して」
* 「イベント駆動にした方が良い部分ある？」

### ✅ Firebaseまわりは“Firebase用のAI支援”を使うと精度が上がる🎯

* **Gemini CLIにFirebase拡張**を入れると、Firebase向けの能力が増えます ([Firebase][6])
* **Firebase MCP server** を入れると、AIツールがFirebaseプロジェクトやコードベースに触れるための導線ができます ([Firebase][7])
* **Prompt catalog** には、Firebase向けの定番プロンプトがまとまっていて、`/firebase:init` みたいなスラッシュコマンドとして使える例も載ってます ([Firebase][8])

### ⚠️ 小さな安全ルール（これは守る🙏）

AIがターミナル操作できる時は、**削除・上書き・移動系**は必ず人間が最終確認！🧯
（便利さと危険はセットです😇）

---

## 8) ちょいメモ：ランタイムの空気感だけ👀

この教材はTypeScript中心ですが、現時点でのNodeランタイムは **20 / 22 がフルサポート**で、**18は2025年初頭にdeprecate**された扱いです ([Firebase][9])
（ここは3章でちゃんと整理します🙂）

---

## 9) 章末チェック✅（言えたら勝ち🏆）

次を“自分の言葉で”一言で言えたらOK！

1. Functionsは何をする場所？⚙️
2. HTTP / イベント / スケジュールの違いは？🎛️
3. 「秘密情報」をフロントに置くとダメな理由は？🔑
4. 「通知」「集計」「重い処理」がフロントNGな理由は？📣📊
5. AI機能を入れるとき、Functionsが役立つポイントは？🤖🛡️

---

## 次章予告👀🚀

次は **「2nd genを選ぶ理由」**！
“なんで今は2nd gen推しなの？”を、難しい話を抜きにして腹落ちさせます🙂✨

[1]: https://firebase.google.com/docs/functions?utm_source=chatgpt.com "Cloud Functions for Firebase - Google"
[2]: https://firebase.google.com/docs/functions/firestore-events?utm_source=chatgpt.com "Cloud Firestore triggers | Cloud Functions for Firebase - Google"
[3]: https://firebase.google.com/docs/functions/schedule-functions?utm_source=chatgpt.com "Schedule functions | Cloud Functions for Firebase - Google"
[4]: https://firebase.google.com/docs/ai-logic?utm_source=chatgpt.com "Gemini API using Firebase AI Logic - Google"
[5]: https://firebase.google.com/docs/functions/oncallgenkit?utm_source=chatgpt.com "Invoke Genkit flows from your App | Cloud Functions for Firebase"
[6]: https://firebase.google.com/docs/ai-assistance/gcli-extension?utm_source=chatgpt.com "Firebase extension for the Gemini CLI"
[7]: https://firebase.google.com/docs/ai-assistance/mcp-server?utm_source=chatgpt.com "Firebase MCP server | Develop with AI assistance - Google"
[8]: https://firebase.google.com/docs/ai-assistance/prompt-catalog?utm_source=chatgpt.com "AI prompt catalog for Firebase | Develop with AI assistance"
[9]: https://firebase.google.com/docs/functions/get-started?utm_source=chatgpt.com "Get started: write, test, and deploy your first functions - Firebase"
