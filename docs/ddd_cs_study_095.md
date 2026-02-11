# 第95章：1人開発者のキャリア 🧑‍💻✨

## 設計ができると、AIを部下にした「チームリーダー」になれる 🤖🫶👑

![1人開発者のキャリア](./picture/ddd_cs_study_095_ai_leader.png)

---

## 0. この章で「できるようになること」🎯🌸

この章が終わるころには、こんな状態になってるのがゴールだよ〜！😊✨

* **AIにコードを書かせつつ、自分は“設計と判断”に集中**できる🧠💡
* AIに振り回されず、**「このアプリの正解（境界線・ルール）」を握れる**✋🧱
* **ポートフォリオや仕事で“設計できる人”として伝える方法**がわかる📁✨
* 「1人開発」なのに、**AIを使って“チーム開発みたいな生産性”を出す**流れが作れる🚀🤝

---

## 1. いまの現実：もう「AIを使える」だけでは足りないよ😵‍💫💦

最近の開発環境って、AIがどんどん“標準装備”になってきてるんだよね。

* Visual Studio だと **GitHub Copilot / Copilot Chat が統合拡張として入る流れ**になってて、一定バージョン以降はセットで扱えるよ📌✨ ([Visual Studio][1])
* しかも **Copilot Free** みたいに、無料枠で IDE 内の補完・編集・チャットに触れられる導線も用意されてる🌱 ([Microsoft Learn][2])
* OpenAI 側も **Codex の IDE 拡張（VS Code）**で「コードを読んで、編集して、実行まで」みたいな“作業者っぽい動き”ができる方向に寄ってる🤖🔧 ([OpenAI Developers][3])

つまりね……

**「AIで書けます！」は、もう“普通”になっていく**の🥺💦
じゃあ差がつくのはどこ？っていうと……

👉 **AIに何をやらせて、何をやらせないか決められる人（＝設計できる人）**
ここがキャリアの強みになるよ💪✨

---

## 2. 「AIを部下にする」ってどういうこと？👩‍🏫🤖

![ddd_cs_study_095_ai_newbie](./picture/ddd_cs_study_095_ai_newbie.png)

 
 ここ、超大事だからイメージでいくね🍀
 
 ```mermaid
 block-beta
   block:Leader["👑 Leader (Human)"]
     Decision["判断・責任"]
     Boundary["境界線定義"]
   end
   
   space
   
   block:Staff["🤖 Staff (AI)"]
     Code["Coding"]
     Review["Review"]
     Test["Test Gen"]
   end
   
   Boundary -- "Rules" --> Staff
   Staff -- "Proposal" --> Decision
   
   style Leader fill:#ffdfba,stroke:#f80
   style Staff fill:#bae1ff,stroke:#00a
 ```
 
 ### ✅ AIは「優秀だけど、空気が読めない新人」👶⚡

* 速い！でも全体像は知らない😳
* それっぽいコードは出す！でも方針は守らないことがある😵
* 仕様の穴があっても埋めたつもりで突っ走る🏃💨

### ✅ あなたは「チームリーダー」👑

リーダーの仕事って、コードを書くことより **“判断と境界線づくり”** なのね。

* 目的を決める（何を作る？何を捨てる？）🎯
* ルールを決める（ドメインの正解はどれ？）📚
* 範囲を切る（この機能はどのコンテキスト？）🧱
* 品質を守る（テスト、レビュー、セキュリティ）🛡️

で、ここでDDDが効くの✨
DDDって「難しい理論」ってより、**“境界線を決める技術”**だからね💡

---

## 3. 2025〜のC#開発は「設計 + AI運用」がセットになっていくよ🧠🤖

C#側も普通に進化してて、.NET 10 では **C# 14** が前提になってるよ〜📈✨ ([Microsoft][4])
（例：プロパティまわりの改善など、書き味がちょいちょい良くなる系🥰）

そして .NET 10 を Visual Studio で本気で使うなら、**対応バージョンの Visual Studio が必要**っていう現実もあるよね（.NET 10 のダウンロードページに “Visual Studio support” が明記されてる）📌 ([Microsoft][4])

ここで言いたいのは一個だけ👇
**ツールが進化しても、迷わない人（＝設計できる人）が一番強い**ってこと😊✨

---

## 4. 1人開発者のキャリアが伸びる「設計スキル」って何？🌷

「設計できます」って言うと、いきなりUMLとか言い出しそうだけど…違うよ😂💦
このロードマップの前提だと、まずはこれでOK！

### 設計スキル = “迷いを減らす決め方” 🧭✨

![ddd_cs_study_095_design_compass](./picture/ddd_cs_study_095_design_compass.png)


* 変更が起きた時に、**どこを直すべきか迷わない**
* AIが暴走しそうな時に、**止める線（境界）を引ける**
* コードが増えても、**言葉と構造が崩れない**

DDDで言うなら、特に効くのはこの3つだよ👇

1. **ユビキタス言語（単語帳）**📒
2. **境界づけられたコンテキスト（独立国）**🏰
3. **集約（ルールを守る“チーム”）**👥

これがあると、AIに指示するときも「ブレない」✨
ブレない＝修正コストが激減する💰🔥

---

## 5. AIチームリーダーの「基本オペレーション」6点セット📦🤖✨

![ddd_cs_study_095_six_steps](./picture/ddd_cs_study_095_six_steps.png)


1人開発でも、これやるだけで急に“チーム感”が出るよ！

### ① まず「設計メモ」を先に作る📝✨

* ドメイン用語（ユビキタス言語）
* ルール（例：注文はキャンセル可能？期限は？）
* 境界（例：販売と決済は分ける？）

ここがあると、AIは“指示書付きの部下”になるよ😊

### ② AIに「タスク分解」させる🔪📋

「実装して」じゃなくて、まず分解！

### ③ AIに「実装」させる🧱🤖

ただし、**境界線を渡さない**（後述の安全運用）

### ④ AIに「テスト案」を出させる🧪✨

“仕様”からテストを作らせると強い！

### ⑤ AIに「レビュー」させる🔍👀

意地悪レビュー役をやらせると最高😂

### ⑥ 人間（あなた）が「採用判断」する✅👑

最終決裁はあなた。ここがキャリアの格になる✨

---

## 6. そのまま使える！AIへの指示テンプレ（DDD初心者向け）💌🤖

![ddd_cs_study_095_prompt_structure](./picture/ddd_cs_study_095_prompt_structure.png)


下の文章を、Copilot Chat や Codex などに投げるだけでOKだよ〜😊✨
（中身はあなたのアプリに合わせて変えてね！）

```text
あなたはこのプロジェクトの「実装担当」です。
私は「設計担当（最終決裁者）」です。

# 目的
〜〜を実装したい。

# ドメイン用語（ユビキタス言語）
- 会員(User)：〜〜
- 注文(Order)：〜〜
- 注文確定(Confirm)：〜〜

# ルール（超重要）
- 注文は「確定」後は明細を変更できない
- 金額は Money 値オブジェクトで扱う（decimal直書き禁止）
- ドメイン層にEF Coreの型や属性を入れない

# 境界（やっていいこと / ダメなこと）
- やっていい：Domain / Application のコード追加
- ダメ：仕様の追加提案で勝手にルールを変えること（提案はOK、勝手に変更はNG）

# 依頼
「注文確定」ユースケースを Application 層に追加し、
必要な Domain の変更があれば差分で提案してください。
テスト観点も箇条書きで出してください。
```

ポイントは、AIにこう言ってること👇

* **あなたは実装担当**（部下）
* **私は設計担当**（リーダー）
* **ルールと境界線は破るな**（DDD）

これだけで、AIの暴走率がかなり下がるよ😊🧱✨

---

## 7. キャリアに効く「見せ方」：設計できる人のポートフォリオはここが違う📁🌟

![ddd_cs_study_095_portfolio_kit](./picture/ddd_cs_study_095_portfolio_kit.png)


企業でもフリーでも、評価されやすいのはここだよ〜！

### ✅ “動くアプリ”より刺さる3点セット💘

1. **README に「境界」と「用語」が書いてある**📘
2. **ドメインモデル（Entity / VO / 集約）が破綻してない**🧱
3. **変更に強い証拠（テスト、ADR、コミットの意図）がある**🧪📝

AI時代って「コード量」自体は増やせちゃうから、
**“設計で迷ってない痕跡”が強い実力証明**になるの✨

---

## 8. でも注意！AIチーム開発には「新しい危険」もあるよ🛡️😨

最近は **AI入りIDEや開発支援ツールに、データ漏えい・RCE（リモートコード実行）につながりうる脆弱性が多数**…みたいな話も出てるのね。 ([The Hacker News][5])

さらに、**プロンプトインジェクション**（ファイルや文書に紛れた命令でAIをだます攻撃）は、OWASPでも重要リスクとして扱われてるよ。 ([OWASP Gen AI Security Project][6])
そして英国NCSCも「完全には防ぎきれない可能性」を指摘してる系の話がある。 ([TechRadar][7])

だからリーダーとしては、これだけは守ろう🥺✨

### 🔒 AI部下の安全運用：7つの約束💍🛡️

![ddd_cs_study_095_safety_shield](./picture/ddd_cs_study_095_safety_shield.png)


* ✅ **.env / secrets / 個人情報はAIに渡さない**
* ✅ **AIに“自動でコマンド実行”させない設定を基本に**（必要時だけ手動承認）
* ✅ **外部から取ってきたコード/設定/JSONは疑う**
* ✅ **「この変更の意図は？」を毎回書かせる**（説明できない変更は戻す）
* ✅ **テストが通ってから採用**（ここ超大事）
* ✅ **依存ライブラリ追加は要相談**
* ✅ **“境界線を越える変更”は必ずPR単位で分ける**

これ、まさに「AIを部下にするリーダーの仕事」だよ👑✨

---

## 9. 【ワーク】今日から“チームリーダー運用”を始めよう💪💕

DDD初心者でもできる、めちゃ効く課題いくね！

### ✅ ワークA：リポジトリに「AI運用ルール」を追加しよう📄🤖

`/docs/ai/working-agreement.md` を作って、次を箇条書きで書く✍️✨

* ドメイン用語リンク（単語帳どこ？）
* 触っていい層 / ダメな層（Domainは慎重、とか）
* 変更は「意図」「影響範囲」「テスト」をセットで出すこと
* secrets禁止
* コマンドは手動承認

これをAIに作らせて、あなたが直せばOK😊🫶

### ✅ ワークB：AIに「タスク分解だけ」させる練習🔪📋

次のプロンプトで、実装させないのがコツ！

```text
次の機能を実装したいです：
「注文確定」

実装はまだしません。
DDDの観点で、必要な作業をタスク分解してください。
- 追加/変更が必要なドメインオブジェクト候補
- アプリケーションサービスの流れ
- 例外/エラーパターン
- テスト観点
を箇条書きで出してください。
```

### ✅ ワークC：レビュー役AIを置く👀✨

```text
あなたは超意地悪なレビュアーです😈
次の観点でレビューしてください：
- 境界（Domain/Application/Infrastructure）が守られてる？
- 不変条件（集約のルール）が壊れてない？
- 例外設計とResult設計は妥当？
- テスト不足はどこ？
改善案もください。
```

---

## 10. まとめ：キャリアが伸びる人は「AIを使う人」じゃないよ🌸

最後に一言でまとめるね😊✨

**AI時代に強いのは、AIにコードを書かせる人じゃなくて、
AIが迷わない“地図（設計）”を描ける人**🗺️👑

DDDはその地図づくりの道具🧱
あなたがリーダーで、AIは部下🤖🤝
この関係が作れると、1人開発でもスピードも品質も両取りできるよ🚀💕

---

次の章（第96章）では、さらに一段やさしいテーマで
「未来の自分への思いやりとしての設計」って話に入っていくよ〜😊💖

[1]: https://visualstudio.microsoft.com/github-copilot/ "
	Visual Studio With GitHub Copilot - AI Pair Programming"
[2]: https://learn.microsoft.com/en-us/visualstudio/ide/copilot-free-plan?view=visualstudio "GitHub Copilot Free in Visual Studio - Visual Studio (Windows) | Microsoft Learn"
[3]: https://developers.openai.com/codex/ide/ "Codex IDE extension"
[4]: https://dotnet.microsoft.com/en-US/download/dotnet/10.0 "Download .NET 10.0 (Linux, macOS, and Windows) | .NET"
[5]: https://thehackernews.com/2025/12/researchers-uncover-30-flaws-in-ai.html?utm_source=chatgpt.com "Researcher Uncovers 30+ Flaws in AI Coding Tools ..."
[6]: https://genai.owasp.org/llmrisk/llm01-prompt-injection/?utm_source=chatgpt.com "LLM01:2025 Prompt Injection - OWASP Gen AI Security Project"
[7]: https://www.techradar.com/pro/security/prompt-injection-attacks-might-never-be-properly-mitigated-uk-ncsc-warns?utm_source=chatgpt.com "Prompt injection attacks might 'never be properly mitigated' UK NCSC warns"
