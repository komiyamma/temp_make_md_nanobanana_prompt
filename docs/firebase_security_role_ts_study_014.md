# 第14章：ロール設計の基本（管理者/一般ユーザーをどう分ける？）👮‍♂️👩‍💻

この章のゴールはこれだけ！👇
**「誰が・何を・どこまでできるか」を、あとからブレない形で決める**ことです🧠🔐
RulesやCustom Claimsは“実装”の話だけど、**設計（言葉の定義）**がグラつくと全部崩れます😱💥

---

## 0) まず超重要な用語を1分で🧩✨

* **ロール（role）**：人の種類（例：admin / editor / user）👤
* **権限（permission）**：できる操作（例：記事を公開できる、削除できる）🛠️
* **リソース（resource）**：守りたいデータ（例：posts、users、adminLogs）📦
* **境界（boundary）**：どこで守るか（例：Firestore Security Rulesが門番🚪）🛡️

ポイントはこれ👇
ロールを増やすより、**「権限」をちゃんと名前で固定**するほうが事故らないです✅🙂

![Visual definition of RBAC terms.](./picture/firebase_security_role_ts_study_014_01_rbac_terms.png)

---

## 1) ロール設計は「6ステップ」で迷子にならない🗺️😺

## ステップ1：操作を全部“動詞”で書き出す✍️

例（ブログ＋管理画面）📰⚙️

* 記事：作成 / 編集 / 公開 / 非公開 / 削除
* コメント：投稿 / 非表示 / 削除
* ユーザー：停止 / 復活
* ログ：閲覧のみ

👉 ここで「画面」じゃなく「操作」にするのがコツ！画面は変わるけど操作は変わりにくい🙂✨

---

## ステップ2：守る対象（コレクション）に紐づける📦🔗

* posts（公開記事・下書き）
* comments
* users（プロフィール）
* adminLogs（管理者しか見ない）

---

## ステップ3：危険度で“3段階”に分ける🔥🧯

* **低**：読むだけ（ただし一覧は危険😇）
* **中**：自分のデータを書き換える
* **高**：他人のデータ変更 / 公開・削除 / 権限変更
![Risk levels in operation.](./picture/firebase_security_role_ts_study_014_02_risk_levels.png)

👉 高リスク操作は、**ロールを分ける価値が高い**です👮‍♂️✨

---

## ステップ4：ロールはまず「3つ」で十分にする🍡

最初はこれでOKです👇

* user（一般）🙂
* editor（運用担当）✍️
* admin（管理者）👑
![The three primary roles.](./picture/firebase_security_role_ts_study_014_03_three_roles.png)

「moderator」「staff」「support」…って増やしたくなるけど、**増やすほどRulesが複雑化**してバグります😵‍💫

---

## ステップ5：ロールごとに“できること表”を作る📋✨

例（最小構成）👇

| 操作 / ロール     | user 🙂 | editor ✍️ | admin 👑 |
| ------------ | ------: | --------: | -------: |
| 公開記事を読む      |       ✅ |         ✅ |        ✅ |
| 下書きを読む       |       ❌ |    ✅（担当分） |        ✅ |
| 記事を作成        | ✅（自分名義） |         ✅ |        ✅ |
| 記事を公開        |       ❌ |         ✅ |        ✅ |
| 記事を削除        |       ❌ |         ❌ |        ✅ |
| adminLogsを見る |       ❌ |         ❌ |        ✅ |

![Access Control Matrix.](./picture/firebase_security_role_ts_study_014_04_role_matrix.png)

👉 「✅の理由」を1行で書いておくと、未来の自分が助かります🥹📝

---

## ステップ6：ルールは“意味を固定”する（ここが本題）🧱🔒

ロール名って、**一度広まると変えるのが超つらい**です😇
だから最初にこう決めちゃう👇

* admin：**権限の付与・削除ができる唯一の存在**👑
* editor：**公開/非公開など運用はできるが、権限は触れない**✍️
* user：**自分の範囲だけ**🙂

この「意味の固定」ができたら、Rulesに落とすのが楽になります✅
![Fixing the meaning of roles.](./picture/firebase_security_role_ts_study_014_05_role_meaning_anchor.png)

---

## 2) Firebaseで“ロール”を扱う場所は2つだけ（覚えやすい）🧠🚪

## A. 認証トークン側（Custom Claims）🎫🔐

ロールをトークンに入れて、Rulesが参照する王道パターンです。
Firebaseは **Admin SDKでカスタム属性（custom claims）をユーザーに付与できて、Security Rulesでそれを使ってアクセス制御**できます。 ([Firebase][1])

## B. Security Rules側（auth.token を見る）👀🛡️

Rulesでは、認証情報（カスタムクレーム含む）を **auth.token** から参照できます。 ([Firebase][2])

> なので、第14章は「ロールの意味を決める章」
> 次の第15〜16章で「実際にトークンへ入れてRulesで分岐する章」になります🎫➡️🛡️
![Location of role data vs enforcement.](./picture/firebase_security_role_ts_study_014_06_token_vs_rules.png)

---

## 3) ここで事故りがちな“ロール設計あるある”😱💥（先に潰す）

## 事故①：ロールを増やしすぎて、誰も説明できない🧟‍♂️

* 「この人はstaff？support？moderator？」みたいになる
* その結果、Rulesがコピペ地獄🌀

✅ 対策：まず3ロール固定。増やす時は「新しい権限」が本当に必要か確認🙂

---

## 事故②：ロールの“意味”が日替わりになる🍱

* 今日はeditorが削除できる
* 明日はできない
* 1ヶ月後にまたできる

✅ 対策：ロールは**契約**。変えるなら“別ロール”を作る（または権限の切り替え設計を別にする）🧾🔒

---

## 事故③：Firestore内に role フィールドを置いて、ユーザーが書ける😱

これは最悪パターン…！
クライアント改造されたら「role=admin」って送られて終わります💀

✅ 対策：ロールは **Admin SDKで付与→トークンで判定**が王道です。 ([Firebase][1])

---

## 4) 手を動かす🧑‍💻✨：あなたのアプリ用「ロール設計表」を作ろう📋

## やること（10分）⏱️

1. あなたのアプリの“操作”を **最低10個**書く✍️
2. それを「低/中/高」に分類🔥
3. user/editor/admin の表に ✅/❌ を埋める
4. 各行に「理由」を1行メモ📝

## テンプレ（コピペ用）👇

| 操作（動詞） | 対象（コレクション） | 危険度 | user | editor | admin | 理由メモ      |
| ------ | ---------- | --- | ---: | -----: | ----: | --------- |
| 例：公開する | posts      | 高   |    ❌ |      ✅ |     ✅ | 公開は影響が大きい |

---

## 5) AI活用（Antigravity / Gemini CLI）🤖💨：ロール表づくりを爆速にする

FirebaseのAI支援には「プロンプトカタログ」があり、Antigravity や Gemini CLI などの“エージェント系”ツールから使う想定の案内があります。 ([Firebase][3])
さらに、Firebase MCP server を使うと、AIツールがFirebaseプロジェクトやコードベースを理解しながら支援できる、という位置づけです。 ([Firebase][4])

## AIに頼むと強いこと💪🙂

* 操作の棚卸し（抜け漏れ発見）🔍
* 「最小権限」のロール表のたたき台生成📋
* 「この操作は高リスク？」みたいな相談相手🧠

## ただし注意⚠️

AI支援は便利だけど、生成結果は必ず人間レビュー前提です。Firebaseのプロンプトカタログ側でも注意が明記されています。 ([Firebase][5])

## AIに投げる指示例（そのまま使える）👇

```text
あなたはセキュリティ設計者です。
次のアプリ機能から「最小権限」を満たすロール設計表を作ってください。
ロールは user / editor / admin の3つ。
出力は「操作」「対象」「危険度（低/中/高）」「各ロールの可否」「理由メモ」。

機能:
- （ここに自分の操作一覧を貼る）
```

## AIレビュー観点チェック（これだけは見る）✅🧑‍⚖️

* 「高リスク操作」が user に✅になってない？😇
* “role変更” “削除” “公開” が editor に混ざってない？🔥
* 「一覧（list）」相当の操作が雑に✅になってない？📖💥
* 理由メモが言語化できてる？（説明できない権限は危ない）🗣️

---

## 6) ミニ課題🎯（5分）＋チェック✅

## ミニ課題🎯

あなたのアプリで、管理画面の操作を **3分類**してみてください👇

1. だれでも見てOK🙂
2. 運用担当ならOK✍️
3. 管理者だけOK👑

そして、各カテゴリに「代表操作」を2つずつ書く📝✨

## チェック✅

* ロールが3つで説明できた？🍡
* adminが“権限を触れる唯一の存在”になってる？👑
* 表の各行に「理由メモ」がある？📝
* AIの出力をそのまま信じず、ツッコミ入れられた？🤖✅

---

## まとめ🎉

ロール設計は「実装の前の、言葉を決める作業」です🧠✨
ここが固まると、次章で **Custom Claimsにロールを入れて、Rulesで auth.token を見て分岐**がスッと入ります🎫➡️🛡️ ([Firebase][1])

次（第15章）は、いよいよロールをトークンへ入れる入口に進みますよ〜！🔥😊

[1]: https://firebase.google.com/docs/auth/admin/custom-claims?utm_source=chatgpt.com "Control Access with Custom Claims and Security Rules"
[2]: https://firebase.google.com/docs/rules/rules-and-auth?utm_source=chatgpt.com "Security Rules and Firebase Authentication"
[3]: https://firebase.google.com/docs/ai-assistance/prompt-catalog?utm_source=chatgpt.com "AI prompt catalog for Firebase | Develop with AI assistance"
[4]: https://firebase.google.com/docs/ai-assistance/mcp-server?utm_source=chatgpt.com "Firebase MCP server | Develop with AI assistance - Google"
[5]: https://firebase.google.com/docs/ai-assistance/prompt-catalog?hl=ja&utm_source=chatgpt.com "Firebase の AI プロンプト カタログ | Develop with AI assistance"
