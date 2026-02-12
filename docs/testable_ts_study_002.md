# 第02章：I/Oと副作用ってなに？⚡🚪

![testable_ts_study_002_io_chaos.png](./picture/testable_ts_study_002_io_chaos.png)

## ねらい 🎯この章で「I/O＝外の世界」をちゃんと言葉にできるようになるよ😊✨
そして、コードを見たときに「ここが副作用っぽい！」ってマーキングできるのがゴール🖍️💡

---

## 1) まず結論：I/Oってなに？🌍📦I/O（Input / Output）

は、ざっくり言うと **「プログラムの外の世界とやり取りすること」** だよ🚪✨



* **Input**：外から情報をもらう（例：APIの結果、DB、ファイル、時刻、環境変数…）📥
* **Output**：外へ影響を与える（例：DB更新、ファイル保存、ログ出力、通知送信…）📤

つまり **“外の世界が絡んだらI/O寄り”** って覚え方がいちばんラク😊🧠

---

## 2) 「副作用」ってなに？💥😵‍💫副作用（side effect）

は、もっとざっくり言うとこう👇

> **関数が「値を返す」以外のことをして、外の世界を変えたり、外の世界に左右されたりすること**⚡

たとえば…👇

* `Date.now()` を読む（実行した瞬間で結果が変わる）⏰
* `Math.random()`（毎回結果が変わる）🎲
* `fetch()`（ネットワーク次第で変わる・遅い・失敗する）🌐
* `console.log()`（出力という外への影響）📝
* `process.env`（環境によって変わる）⚙️

副作用が混ざると、**テストが不安定**になりやすいのがポイントだよ🧪💦

---

## 3) I/Oっぽいものカタログ 🗂️

👀（ここ超大事！）「これ見たらI/O！」っていう定番リストを作っちゃおう😊✨



## 3.1 ネットワーク系 🌐* HTTP/API：`fetch()` / axios など
  Node.js だと `fetch` はグローバルで使えて、最近のNodeでは“experimental外れた”扱いになってるよ📌 ([nodejs.org][1])

## 3.2 永続化系 🗄️* DBアクセス（SELECT/INSERT/UPDATE）


* Redis / KVストア
* セッション保存

## 3.3 ファイル系 📁* `fs.readFile` / `fs.writeFile`


* 画像アップロード、ログファイル出力

## 3.4 “見落としがちI/O” 🌀（地雷ゾーン）* 時刻：`Date`, `Date.now()` ⏰


* 乱数：`Math.random()` 🎲
* 環境変数：`process.env` ⚙️
* ログ：`console.log`, logger 📝
* UUID生成、暗号乱数（ライブラリ次第）🔑
* タイムゾーン・ロケール依存（表示・日付計算）🌏

---

## 4) なぜI/Oと副作用が“悪者扱い”されるの？😈➡️

😇I/Oそのものが悪いわけじゃないよ！必要だからね😊
ただし **「ロジックの中心に混ぜる」と困る** の💦

## 困りごとあるある 😵‍💫* ✅ テストが遅い（ネット・DB・ファイル…）

🐢


* ✅ テストが不安定（時刻・乱数・通信エラー…）🎲🌧️
* ✅ “準備が大変”になりがち（DB用意、環境変数、モック地獄…）🧟‍♀️
* ✅ 変更に弱い（API変更、DBスキーマ変更で中心ロジックまで巻き添え）💣

だから次章以降でやるのは、
**「I/Oを外に押し出して、中心（ロジック）を安定させる」** って作戦だよ🏠✨

---

## 5) ミニ実例：I/Oとロジックを“仕分け”してみよ🧺🧠## 例：一見ふつうの処理（でもI/Oまみれ）

😇➡️😱

```ts
export async function placeOrder(userId: string, amount: number) {
  const now = new Date();                 // 👈 時刻I/O寄り ⏰
  const coupon = Math.random() < 0.2;     // 👈 乱数I/O寄り 🎲

  console.log("placing order...", userId);// 👈 ログ出力（外への影響）📝

  const res = await fetch("https://api.example.com/users/" + userId); // 👈 ネットI/O 🌐
  const user = await res.json();

  const total = coupon ? amount * 0.9 : amount; // 👈 ここはロジック寄り 💡
  return { user, total, orderedAt: now.toISOString() };
}
```

## 仕分け結果（まずは分けられればOK！

）✅* **I/O寄り**：`new Date()` / `Math.random()` / `console.log()` / `fetch()`


* **ロジック寄り**：`coupon ? amount * 0.9 : amount`

この“分類できる力”が、I/O境界の分離のスタート地点だよ😊✨

---

## 6) ハンズオン：あなたのコードで分ける📝

✨## Step A：最近書いた処理を1つ選ぶ 🔍「API叩く」「ファイル読む」「ログ出す」みたいなやつがおすすめ🌟



## Step B：2色でマーキング 🖍️

🖍️* ピンク：I/O（外の世界）💗


* 水色：ロジック（計算・判断）🩵

## Step C：2つのリストを書く 📋* I/O一覧（何に依存してる？何を変更してる？）


* ロジック一覧（入力→出力の計算ルールは何？）

### コツ🍀

「それ、テストで固定できる？」って自分に聞くと見抜きやすいよ🧪👀



* 固定できない / 環境で変わる → I/O寄り
* 入力が同じなら出力も同じ → ロジック寄り

---

## 7) ちょい豆知識：最近のTypeScript/Nodeだと“副作用の扱い”も話題だよ🤏✨* TypeScript 5.9 では `import defer` みたいに **モジュールの評価（＝副作用の発生タイミング）

を遅らせる** 話も出てるよ📦⏳ ([TypeScript][2])


* npm上の最新安定版は 5.9.3（現時点）だよ📌 ([NPM][3])

（この章の本筋は“設計の考え方”だけど、こういう「副作用コントロールの流れ」が来てるのも面白いよね😊🎀）

---

## 8) AI（Copilot/Codex）

に手伝ってもらうプロンプト例 🤖🧁そのまま貼ってOK系だよ✨



* 「この関数の中のI/O（副作用）になってる行を全部列挙して、理由も一言ずつ書いて」
* 「I/Oとロジックを分けたい。まず分類だけして（リファクタ案は次）」

AIが迷ってたら、人間側でルールを追加してあげるのがコツ🧠✨
「時刻・乱数・環境変数・ログもI/O扱いでね」みたいに言うと精度上がるよ😊

---

## まとめ 🎉この章の勝ち筋はこれ👇✨



* ✅ I/O＝外の世界とのやり取りって説明できる🌍
* ✅ 副作用＝外の世界を変える/外に左右されるって言える⚡
* ✅ コードを見て「I/O寄り」「ロジック寄り」を仕分けできる🧺

次の第3章では、「じゃあ“テストしやすい”ってどんな状態？」をハッキリさせていくよ🧪✨

---

## おまけ：今日の最新メモ🗒️

Node.jsのリリース状況は公式の一覧やスケジュールで追えるよ（LTSの流れが見える）📅 ([nodejs.org][4])

[1]: https://nodejs.org/api/globals.html "Global objects | Node.js v25.3.0 Documentation"
[2]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html?utm_source=chatgpt.com "Documentation - TypeScript 5.9"
[3]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "TypeScript"
[4]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
