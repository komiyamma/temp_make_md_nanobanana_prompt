# 第2章 エンティティ分解 User Report Post Comment 🧩🧠✨

この章のゴールはこれ👇
「どの単位が **Firestoreのドキュメント** になるべきか？」を、**更新頻度（＝後で非正規化判断に使う）**まで含めて決められる状態にすることだよ😄📝

---

## 1 まず大前提 ドキュメントは小さく育てる感覚 🌱📄

Firestoreは「**大量の小さめドキュメント**を、コレクションにいっぱい並べる」のが得意な設計だよ📚✨ ([Firebase][1])
しかもドキュメントは **最大 1 MiB** まで（意外とすぐ効いてくる！）([Firebase][2])

さらに大事ポイント👇
1回の書き込みは、そのドキュメント本体だけじゃなく **関連するインデックスも更新**するから、**更新が集中するドキュメント**はしんどくなりやすい😵‍💫（後の章でインデックス最適化をやる理由！）([Firebase][3])

---

## 2 エンティティ分解ってなに 🧩

エンティティ分解＝ざっくり言うと👇
「アプリに出てくる“登場人物”を、データのかたまりとして切り出す」ことだよ😄

今回の題材（3階層）だと登場人物はこう👇

* **User**：ユーザー（投稿者）👤
* **Report**：日報🗓️
* **Post**：記事📝
* **Comment**：コメント💬

ここでやるのは「コレクション配置（サブコレにするか等）」じゃなくて、まず **かたまりの切り方（＝ドキュメント単位）** を決める作業だよ🧠✨

---

## 3 ドキュメント単位を決める 3つの質問 🧠🔍

次の質問に YES が多いものほど「同じドキュメントにまとめやすい」よ👇

## 質問A 一緒に表示する 📺

* 画面でいつもセットで表示する？

## 質問B 一緒に更新する 🔁

* 更新タイミングがほぼ同じ？（片方だけ頻繁に書き換わる、は危険信号⚠️）

## 質問C 寿命が同じ 🕯️

* 削除や非公開のタイミングが同じ？

そして逆に👇
**「更新が多いもの」「増え続けるもの（コメント等）」「大勢が触るもの」**は、**1つのドキュメントに寄せすぎない**のがコツ😄
（ドキュメントIDが偏って連番になるのもホットスポットの原因になるので避けよう、という話もあるよ🧯）([Firebase][4])

---

## 4 手を動かす フィールド分解シートを作る 🧱📝

ここから作業だよ〜！💪✨
「必須フィールド」と「編集頻度」をセットで書くのがポイント🔥

## 編集頻度のタグを決めよう 🏷️

* 🧊 ほぼ不変（作成後ほぼ変わらない）
* 🌤️ たまに変わる（プロフィール等）
* 🔥 よく変わる（カウント、最後の更新時刻、最新コメントなど）
* 🌪️ 超集中しそう（みんなが連打する：いいね数、閲覧数…）

---

## 5 例 User の必須フィールド案 👤🧾

「User」は **認証IDの持ち主**で、画面で出したい情報が中心だよ😄

| フィールド       | 型イメージ            | 編集頻度 | メモ                    |
| ----------- | ---------------- | ---: | --------------------- |
| uid         | string           |   🧊 | 参照用（Authのuidと合わせるとラク） |
| displayName | string           |  🌤️ | 画面表示でほぼ必須             |
| photoURL    | string           |  🌤️ | アイコン                  |
| createdAt   | timestamp        |   🧊 | 作成時                   |
| updatedAt   | timestamp        |  🌤️ | プロフ更新時                |
| role        | "user" | "admin" |  🌤️ | ルール設計の材料🛡️           |

💡コツ：Userに「投稿数」「いいね数」みたいな **🔥系の頻繁更新**を詰めると、将来しんどくなりやすいよ（集計章で回避策やる！）([Firebase][3])

---

## 6 例 Report 日報の必須フィールド案 🗓️📝

日報は「1日1枚」みたいに **粒度が分かりやすい**からドキュメント向き😄

| フィールド      | 型イメージ                | 編集頻度 | メモ           |
| ---------- | -------------------- | ---: | ------------ |
| reportId   | string               |   🧊 | 参照用          |
| authorId   | string               |   🧊 | 投稿者          |
| date       | "2026-02-16"         |   🧊 | 日付キー（検索にも便利） |
| title      | string               |  🌤️ | あってもなくても     |
| body       | string               |   🔥 | 書き足し・修正が多い想定 |
| visibility | "private" | "public" |  🌤️ | 公開/非公開       |
| createdAt  | timestamp            |   🧊 |              |
| updatedAt  | timestamp            |   🔥 | 編集があると更新     |

---

## 7 例 Post 記事の必須フィールド案 📰✨

記事は「一覧に出す」ことが多いので、一覧に必要なフィールドを意識しよう📜✨

| フィールド     | 型イメージ                 | 編集頻度 | メモ        |
| --------- | --------------------- | ---: | --------- |
| postId    | string                |   🧊 |           |
| authorId  | string                |   🧊 |           |
| title     | string                |  🌤️ |           |
| body      | string                |   🔥 |           |
| tags      | string[]              |  🌤️ | 後で検索に使うかも |
| status    | "draft" | "published" |  🌤️ |           |
| createdAt | timestamp             |   🧊 |           |
| updatedAt | timestamp             |   🔥 |           |

⚠️注意：本文 `body` が長文になりがちなら、ドキュメントサイズ上限（1 MiB）を意識してね📦([Firebase][2])
（画像や巨大データを直接入れない、などの方針が効いてくる👍）

---

## 8 例 Comment コメントの必須フィールド案 💬🚀

コメントは「増え続ける」代表選手！🥇
だから **記事ドキュメントに配列で全部突っ込む**みたいな形は、サイズ面でも更新集中でも厳しくなりやすいよ😇（この章では“気づければ勝ち”）([Firebase][2])

| フィールド     | 型イメージ     | 編集頻度 | メモ               |
| --------- | --------- | ---: | ---------------- |
| commentId | string    |   🧊 |                  |
| postId    | string    |   🧊 | どの記事？            |
| authorId  | string    |   🧊 | 誰が？              |
| body      | string    |   🔥 | 修正や削除対応も想定       |
| createdAt | timestamp |   🧊 |                  |
| updatedAt | timestamp |  🌤️ | 編集したら            |
| deleted   | boolean   |  🌤️ | 論理削除の入口（後の章で深掘り） |

---

## 9 ミニ課題 編集頻度メモを入れて設計を守る 💪📝🔥

次をやってみて！超効くよ😄✨

## ミニ課題A

上の4エンティティそれぞれで、フィールドの横に
**🧊 / 🌤️ / 🔥 / 🌪️** を全部付ける！

## ミニ課題B

🔁「同じドキュメントに入りそうなフィールド」ごとに、色分けするつもりでグルーピングしてみて🎨

* **🧊〜🌤️が中心のまとまり**：同居しやすい
* **🔥が混ざりすぎる**：分割候補
* **🌪️がいる**：ほぼ確実に別設計が必要（分散・別コレクション・サーバー側管理など）([Google Cloud Documentation][5])

---

## 10 チェック 1つでもYESなら分割を疑おう 👀✅

最後にセルフチェックだよ〜😄

* [ ] 🔥（よく変わる）が、1つのドキュメントに集まりすぎてない？
* [ ] コメント・ログ・履歴みたいに「増え続ける」ものを、1ドキュメントに抱えてない？（サイズ上限もある）([Firebase][2])
* [ ] みんなが同時に触る数字（いいね数等）を、1ドキュメントで直更新しようとしてない？（将来のホットスポット候補）([Google Cloud Documentation][5])
* [ ] ドキュメントIDを連番っぽく作ろうとしてない？（偏りでホットスポットになりやすい）([Firebase][4])

---

## 11 AIで爆速に終わらせる コピペ用プロンプト集 🤖⚡📎

ここからは「手で考える＋AIでレビュー」の黄金ムーブだよ✨
（Antigravityは“エージェントが計画して動く”開発スタイルの説明があるよ🛰️）([Google Codelabs][6])
Gemini CLIはCloud Shellで追加セットアップなしで使える案内があり、Code Assistの枠とも絡むよ🧰([Google for Developers][7])

## 依頼1 エンティティと必須フィールドを列挙して

* 「日報/記事/コメントのアプリをFirestoreで設計したい。User/Report/Post/Commentの必須フィールドを提案して。各フィールドに“編集頻度”を 🧊🌤️🔥🌪️ で付けて。」

## 依頼2 🔥が集まりすぎてないかレビューして

* 「このフィールド案で、頻繁更新が1ドキュメントに集中しないかレビューして。将来ホットスポットになりそうな箇所を指摘して。」

## 依頼3 1画面1クエリを意識して見直して

* 「一覧/詳細/コメント欄の3画面を想定して、必要フィールドが不足してないか確認して。余計なフィールドも削って。」

## 依頼4 AI機能を後で入れる前提の設計レビュー

* 「将来、生成AIの要約やコメント返信案を作りたい。保存すべきフィールド（例：model名、生成日時、元テキスト参照）を最小で提案して。」

（FirebaseのAIまわりは更新が速いので、モデルの扱いなどは最新情報が重要だよ📌 例：Firebase JS SDKのリリースノートは 2026-02-05 更新で、12.9.0/12.8.0 の内容が載ってる）([Firebase][8])

---

## 12 次章につながるひとこと 🧠➡️🆔

この章でできた「エンティティ＋必須フィールド＋編集頻度メモ」が、次の👇にそのまま効くよ✨

* 第3章 ID設計（自動ID vs 意味ID）🆔
* 第4章 サブコレの使いどころ🧩
* 第6章 正規化 vs 非正規化⚖️（頻度メモが主役になる！）

---

必要なら、この第2章の成果物として「**フィールド分解シート（完成版テンプレ）**」を、あなたのToDo/メモアプリじゃなくて今回の **日報/記事/コメント**用に、最初から埋めた版も作るよ😄📝✨

[1]: https://firebase.google.com/docs/firestore/data-model "Cloud Firestore Data model  |  Firebase"
[2]: https://firebase.google.com/docs/firestore/quotas?utm_source=chatgpt.com "Usage and limits | Firestore | Firebase - Google"
[3]: https://firebase.google.com/docs/firestore/understand-reads-writes-scale?utm_source=chatgpt.com "Understand reads and writes at scale | Firestore - Firebase"
[4]: https://firebase.google.com/docs/firestore/best-practices "Best practices for Cloud Firestore  |  Firebase"
[5]: https://docs.cloud.google.com/firestore/native/docs/resolve-latency?utm_source=chatgpt.com "Resolve latency issues | Firestore in Native mode"
[6]: https://codelabs.developers.google.com/getting-started-google-antigravity?utm_source=chatgpt.com "Getting Started with Google Antigravity"
[7]: https://developers.google.com/gemini-code-assist/docs/gemini-cli?utm_source=chatgpt.com "Gemini CLI | Gemini Code Assist"
[8]: https://firebase.google.com/support/release-notes/js "Firebase JavaScript SDK Release Notes"
