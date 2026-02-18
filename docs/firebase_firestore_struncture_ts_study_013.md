# 第13章：ランキング設計（Top Nを気持ちよく出す）🥇✨

ランキングって、見た目は「並べるだけ」なんだけど…裏ではけっこう“設計力”が出ます😇
この章のゴールは **「Top N を速く・安定して・ズルされにくく」出せる形**を作ることです💪🔥

---

## 読む：ランキングの基本ルールはこれだけ🧠✨

### ✅ ルール1：Firestoreでランキングするなら「並べ替えできる数値フィールド」が必要

Firestoreは **保存されているフィールドを `orderBy()` で並べる**のが基本です📜
つまりランキングには、たとえばこんな “並べ替えキー” が必要👇

* `likesCount`（いいね数）👍
* `commentsCount`（コメント数）💬
* `score`（あなたが決めた総合スコア）⭐
* `hotScore`（時間減衰込みのトレンドスコア）🔥

「（いいね数 ÷ 経過時間）みたいなのをその場で計算して並べる」は苦手なので、**計算結果をフィールドとして持つ**のがコツです😄

### ✅ ルール2：同点が出るので“タイブレーク（第2キー）”を必ず用意する

ランキングで **同じスコアが出る**のは日常茶飯事です🍵
同点のときの並びを固定しないと、ページングやUIが不安定になります😵‍💫

なので基本形はこれ👇

* 第1キー：`score`（desc）
* 第2キー：`createdAt`（desc）
* （必要なら）第3キー：`postId` 相当（固定）🆔

### ✅ ルール3：`orderBy()` したいフィールドが無いドキュメントは “結果から消える”

「score を入れ忘れた投稿」が混ざると、**ランキングに出ない**ことが起きます⚠️
なので **作成時に `score: 0` みたいに必ず入れる**のが安全です。([Firebase][1])

### ✅ ルール4：`where + orderBy` は “複合インデックス” が必要になりがち

日次ランキングみたいに

* `where("dayKey", "==", "2026-02-16")`
* `orderBy("score", "desc")`

みたいな形は、**複合インデックス**が必要になることが多いです🛠️
（エラーが出たら、そのリンクから作る流れが定番）([Firebase][2])

---

## 手を動かす：まずは「3種類のランキング」を決めよう🎮📝

今回の題材（記事 `posts`）で、まずはこれを作るのがおすすめです👇✨

1. **全期間ランキング（All-time Top 10）** 🏆
2. **日次ランキング（Daily Top 10）** 📅
3. **トレンド（Hot Top 10）** 🔥（時間でスコアが落ちるやつ）

---

## 1) データ設計：最初に入れるフィールドを決める🧱

まず `posts` に “ランキングの材料” を揃えます👇

* `likesCount: number` 👍（0スタート）
* `commentsCount: number` 💬（0スタート）
* `score: number` ⭐（例：`likesCount*3 + commentsCount*5`）
* `hotScore: number` 🔥（後でサーバー側で更新してもOK）
* `createdAt`（作成時刻）⏰
* `dayKey: string`（例：`"2026-02-16"`）📅
* `weekKey: string`（例：`"2026-W07"`）🗓️

> ポイント：**作成時に全部入れる（0でOK）**
> フィールドが欠けると `orderBy()` の挙動で事故りやすいです⚠️([Firebase][1])

---

## 2) 3つのランキング実装パターン（どれを選ぶ？）🤔

## A. いちばんシンプル：`posts` をそのまま `orderBy`（まずはこれでOK）🥰

**読み取りが少なくて速い**（Top10なら投稿10件読むだけ）👍
ただし、`score/hotScore` を更新する設計が必要になります。

* 👍 UI実装がラク
* ⚠️ スコア更新が多いと書き込み増える

## B. “ランキング専用コレクション”を作る（運用が気持ちいい）😎

例：`rankingsDaily/{dayKey}/items/{postId}` に

* `postId`
* `score`
* `createdAt`

を保存して、**ランキングはここを読む**方式📚

* 👍 投稿本文を汚さず運用できる
* ⚠️ Top10表示で「ランキング10件＋投稿10件」みたいに読み取りが増える（でも許容なことが多い）

## C. “Top N を1ドキュメントに固める”（超高速だけど更新が繊細）⚡

例：`rankingsDaily/{dayKey}` 1つのドキュメントに
`top: [{postId, score}, ...]` を配列で持つ方式。

* 👍 読み取りは1回で最速
* ⚠️ 更新が競合しやすい（同時更新が多いと大変）
* ⚠️ ドキュメントサイズ上限（1 MiB）に注意([Firebase][3])

最初は **A →（伸びたら）B** が王道です🏰✨

---

## 3) クエリ設計：Top N を“安定して”出す📜✅

## 3-1) 全期間 Top 10（All-time）🏆

```ts
import { collection, query, orderBy, limit, getDocs } from "firebase/firestore";

const q = query(
  collection(db, "posts"),
  orderBy("score", "desc"),
  orderBy("createdAt", "desc"),
  limit(10)
);

const snap = await getDocs(q);
const posts = snap.docs.map(d => ({ id: d.id, ...d.data() }));
```

## 3-2) 日次 Top 10（Daily）📅

```ts
import { collection, query, where, orderBy, limit, getDocs } from "firebase/firestore";

const dayKey = "2026-02-16"; // 例：UI側で選択

const q = query(
  collection(db, "posts"),
  where("dayKey", "==", dayKey),
  orderBy("score", "desc"),
  orderBy("createdAt", "desc"),
  limit(10)
);

const snap = await getDocs(q);
```

この形は **複合インデックスが必要**になりがちです🛠️([Firebase][2])
エラーが出たら、メッセージのリンクから作るのが最短ルートです😄

## 3-3) ページングもやるなら「カーソル」を使う📜➡️

Top 10 の次（11〜20件）を取りたいときは `startAfter()` を使います👇
（カーソルは **並び順が安定していること** が超重要！）([Firebase][4])

---

## 4) スコア更新：どこで計算する？🤔⚙️

ランキングで一番ハマるのはここです💥
「クライアントが score を勝手に書ける」だと、ズルし放題になります😇

## おすすめ方針（初心者でも事故りにくい）✅

* いいね/コメントは **イベント**（追加）として保存（例：likesドキュメント）👍
* カウンタ更新（`likesCount` など）とスコア更新（`score/hotScore`）は

  * まずは **トランザクション/サーバー側**でやる
  * 伸びたら **分散カウンタ**や **バッチ更新**へ

Firestoreは書き込みが集中すると詰まることがあるので、**“集中しそう”なら分散の発想**が大事です🔥([Firebase][5])

---

## 5) 伸びた時の強化：分散カウンタ（シャーディング）🧱🔥

「人気投稿にいいねが集中」すると、1ドキュメント更新の連打が辛くなることがあります😵
そこで **分散カウンタ**が定番です✨([Firebase][6])

* `posts/{postId}/likeShards/{shardId}` に `count` を持つ
* いいね時にランダム shard を `+1`

さらに今は **Aggregation Queries** で `sum()` もできるので、shardsを全部読まずに合計を取れる設計も作れます📊([Firebase][7])
（ただ、ランキング用途だと「投稿ごとに集計」が必要になるので、最終的には `likesCount` を別で持つのがラクです😄）

---

## 6) トレンド（hotScore）設計：時間減衰を入れる🔥⏳

トレンドの定番はこれ👇

* 新しい投稿が有利
* でも「一瞬だけバズった」だけじゃなく、盛り上がりが続く投稿も評価したい

例の考え方（式は自由！）

* `raw = likes*3 + comments*5`
* `ageHours = 今 - createdAt`
* `hotScore = raw / (ageHours + 2)` みたいに “時間が経つと落ちる”🔥

Firestoreはこの割り算をクエリ内で作りにくいので、**計算結果（hotScore）を保存**するのが王道です😄

---

## 7) サーバー側で更新するなら：Functions / Cloud Run の選び方⚙️🤖

## Cloud Functions for Firebase（手軽）⚡

* Node.js は **20 / 22** がサポートされています([Firebase][8])
* Python は **3.10〜3.13（3.13がデフォルト）** と説明されています([Firebase][9])
  一方で、設定例として `firebase.json` の runtime に `python310 / python311` が載っているページもあります（ドキュメント内で表現が揺れることがあるので、CLIのエラー表示を最優先に合わせるのが安全です）([Firebase][8])

## Cloud Run functions（より自由、.NETも視野）🚀

Cloud Run functions はランタイムの選択肢が広く、**.NET** なども含めて整理しやすいです([Google Cloud Documentation][10])
（ランキングの再計算バッチや、AI評価の重い処理を載せる先として相性◎）

---

## 8) AIを絡める：ランキングを“賢く”する🤖✨

ランキングって、数字だけだとこうなりがち👇

* 炎上・釣りが上位に来る😇
* 低品質でも短期バズで勝つ😇

そこで AI を「補助スコア」として使うと強いです💪

## 例：AIで `qualityScore`（0〜1）を付ける⭐

* 投稿作成時に AI で「読みやすさ」「有益度」「危険度」などを判定
* `finalScore = hotScore * qualityScore` のように反映
* 判定結果は `aiLogs` に保存して、**モデル名/時刻/プロンプトハッシュ**も一緒に残す🧾

Firebase AI Logic はクライアントから Gemini API を使う入口として提供され、App Check などと一緒に “安全側” に寄せやすい思想です🛡️([Firebase][11])
（AIは更新が速いので、ログに「モデル名」を残すのは本当におすすめ！）

---

## 9) Antigravity / Gemini CLI で爆速に作る（コピペ用）🤖⚡

## Antigravity（エージェントに「設計→実装→検証」まで振る）🛰️

「日次ランキング＋トレンドランキングを、posts直読み(A案)とランキング専用(B案)で比較して。必要なインデックス、更新戦略、ズル対策まで含めて提案して。最後にTypeScriptコード雛形も出して」

Antigravityの導入・考え方は公式の導線（Codelab）を踏むと早いです([Google Codelabs][12])

## Gemini CLI（ターミナルでレビュー＆生成）⌨️✨

「この `firestore.indexes.json` を見て、Daily Top10/Hot Top10 のクエリに必要な複合インデックスが足りてるかチェックして。不足分を追記案として出して」

Gemini CLIの概要は公式ドキュメントを参照できます([Google for Developers][13])

---

## ミニ課題：日次ランキングを“安定＆事故なし”で出す📅🥇

## やること（30〜60分）⏱️

1. `posts` に `score/dayKey/createdAt` を **作成時に必ず入れる**（0でOK）✅
2. 日次ランキングのクエリを書いて、コンソールで動かす🔎
3. インデックスエラーが出たら作成して再実行🛠️
4. 同点があるデータを作って、並びが安定しているか確認👀

## 提出物（自分用メモでOK）📝

* あなたのランキングは **A/B/C どの方式**にした？その理由は？🤔
* `score` の定義（式）を書けた？⭐
* タイブレーク（第2キー）は何にした？🧷

## チェック✅

* [ ] 同点でも並びがガタつかない
* [ ] `score` が無い投稿が混ざっても事故らない（作成時0で回避）([Firebase][1])
* [ ] `where + orderBy` に必要なインデックスを用意できた([Firebase][2])
* [ ] “ズル更新”をクライアント任せにしない方針が立った😇

---

* [The Verge](https://www.theverge.com/news/822833/google-antigravity-ide-coding-agent-gemini-3-pro?utm_source=chatgpt.com)
* [TechRadar](https://www.techradar.com/pro/google-gemini-and-github-are-teaming-up-for-ai-powered-coding?utm_source=chatgpt.com)
* [Indiatimes](https://indiatimes.com/trending/googles-gemini-cli-is-here-everything-you-need-to-know-about-the-free-ai-tool-for-developers-662205.html?utm_source=chatgpt.com)
* [windowscentral.com](https://www.windowscentral.com/artificial-intelligence/microsoft-adds-googles-gemini-2-5-pro-to-github-copilot-but-only-if-you-pay?utm_source=chatgpt.com)

[1]: https://firebase.google.com/docs/firestore/query-data/order-limit-data?utm_source=chatgpt.com "Order and limit data with Cloud Firestore - Firebase - Google"
[2]: https://firebase.google.com/docs/firestore/query-data/index-overview?utm_source=chatgpt.com "Index types in Cloud Firestore - Firebase - Google"
[3]: https://firebase.google.com/docs/firestore/quotas?utm_source=chatgpt.com "Usage and limits | Firestore | Firebase - Google"
[4]: https://firebase.google.com/docs/firestore/query-data/query-cursors?utm_source=chatgpt.com "Paginate data with query cursors | Firestore | Firebase"
[5]: https://firebase.google.com/docs/firestore/understand-reads-writes-scale?utm_source=chatgpt.com "Understand reads and writes at scale | Firestore - Firebase"
[6]: https://firebase.google.com/docs/firestore/solutions/counters?utm_source=chatgpt.com "Distributed counters | Firestore - Firebase - Google"
[7]: https://firebase.google.com/docs/firestore/query-data/aggregation-queries?hl=ja&utm_source=chatgpt.com "集計クエリでデータを要約する | Firestore - Firebase - Google"
[8]: https://firebase.google.com/docs/functions/manage-functions "Manage functions  |  Cloud Functions for Firebase"
[9]: https://firebase.google.com/docs/functions/get-started "Get started: write, test, and deploy your first functions  |  Cloud Functions for Firebase"
[10]: https://docs.cloud.google.com/run/docs/runtimes/function-runtimes?hl=ja "Cloud Run functions ランタイム  |  Google Cloud Documentation"
[11]: https://firebase.google.com/docs/ai-logic/quotas?utm_source=chatgpt.com "Rate limits and quotas | Firebase AI Logic - Google"
[12]: https://codelabs.developers.google.com/getting-started-google-antigravity?utm_source=chatgpt.com "Getting Started with Google Antigravity"
[13]: https://developers.google.com/gemini-code-assist/docs/gemini-cli?utm_source=chatgpt.com "Gemini CLI | Gemini Code Assist"
