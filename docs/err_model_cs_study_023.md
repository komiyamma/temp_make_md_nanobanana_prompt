# 第23章：UIエラー設計（ユーザーにやさしく）🫶🎀

この章のゴールはこれ👇😊
✅ **「見せる情報」と「隠す情報」**を分けられる
✅ **入力エラー**は“直せる形”で案内できる✍️
✅ **インフラ障害**は“再試行できる形”で導ける🔁
✅ **想定外（バグ）**は“ユーザーに優しく、運用に強く”できる🧯🔎

---

## 1) UIエラー設計って、なにを設計するの？🤔💡

![Scope of UI Error Design](./picture/err_model_cs_study_023_design_scope.png)

UIのエラーって「赤い文字を出す」だけじゃなくて、

* **どこに**出す？（項目の下？画面上？ダイアログ？）🧭
* **何を**書く？（専門用語なし、原因と次の行動）📝
* **何を**書かない？（スタックトレース、内部ID、機密）🙈
* **どうやって**復帰させる？（修正/再試行/戻る）🛟

…まで含めた“体験設計”だよ☺️
ユーザーはエラーで混乱しやすいから、**責めない＆次の一手が分かる**が超大事✨ ([Microsoft Learn][1])

---

## 2) 3分類（ドメイン/インフラ/バグ）をUIに落とす🧩🎯

![Error Category to UI Strategy](./picture/err_model_cs_study_023_category_ui_map.png)

「第6章の3分類」を、UIではこう扱うのが基本だよ👇

* **ドメインエラー（業務ルール違反）💗**
  → ユーザーが直せることが多い：**具体的に、項目単位で**案内する
* **インフラエラー（通信/DB/外部API）🌩️**
  → ユーザーが直せないことが多い：**再試行/時間を置く/状態確認**を案内する
* **バグ（不変条件違反）⚡**
  → ユーザーに責任なし：**やさしく謝る＋問い合わせ用の手がかり**（相関IDなど）で運用につなげる

特に「何が起きた？」「結果どうなる？」「次どうすれば？」の3点セットは鉄板🧱✨ ([Microsoft Learn][2])

---

## 3) “出し方”は4パターンでだいたい勝てる🏆🎨

![UI Patterns](./picture/err_model_cs_study_023_ui_patterns.png)

### A. 項目のすぐ下（フィールドエラー）🧷

* **入力ミス**は基本これ
* 「どこがダメ？」が一瞬で分かる
* 例：メール形式、必須、範囲外、桁数など

Fluentのガイドでも、バリデーション文は**短く、次にどうすればいいか**が大事って言ってるよ📎 ([Fluent 2 Design System][3])

### B. フォーム上部（エラー要約）📌

* エラーが複数あるときに便利
* 「まずここ直してね」が一覧で見える
* アクセシビリティ的にも相性よし（見落とし防止）🧑‍🦯 ([W3C][4])

### C. 画面上のバナー/トースト（全体通知）📣

* **通信失敗**や**保存失敗**など、画面全体に関わるとき
* トーストは消えるので、重要ならバナー寄りが安全🙂

### D. ダイアログ（モーダル）🛑

* “今すぐ判断が必要”だけに絞る（削除、支払い確定、データ破壊など）
* エラーで頻繁に出すと、ユーザーが疲れる😵‍💫

---

## 4) 文言づくりのコツ：やさしくて強い文章テンプレ💬🎀

![UI Feedback Types](./picture/err_model_cs_study_023_ui_feedback.png)

### まずはテンプレ（超おすすめ）🧰

**①何が起きた** → **②結果** → **③次の行動**

Microsoftのエラーメッセージ指針でも、この3点を入れるのが良いってされてるよ✅ ([Microsoft Learn][2])

### NG例🙅‍♀️💥 → OK例🙆‍♀️✨

* NG：「エラー 500」
  OK：「保存に失敗しました。通信が不安定かもしれません。もう一度お試しください。」🔁

* NG：「不正な入力です」
  OK：「メールアドレスの形式が合っていません。例：[name@example.com](mailto:name@example.com) を参考に入力してください」✍️ ([W3C][4])

* NG：「あなたの操作が間違っています！」
  OK：「うまく処理できませんでした。もう一度やり直すか、しばらくしてからお試しください」🫶
  ※責めない・怒らない・大文字やビックリマーク多用しないのも定番だよ😌 ([Microsoft Learn][2])

---

## 5) アクセシビリティ：最低限これだけは守る🧑‍🦯✨

![Accessibility Rules](./picture/err_model_cs_study_023_a11y_rules.png)

フォーム系はここが超重要👇

* **エラーは“テキストで”説明する**（色だけに頼らない）🎨❌
* **どの項目がエラーか特定できる**（「どこ？」が分かる）📍
* **直し方のヒント**があると親切（例の形式、範囲、桁数）💡

WCAGでも「エラーが起きたこと・何が間違いかをテキストで示す」が求められてるよ📚 ([W3C][4])

---

## 6) Result型からUI表示へ： “画面用メッセージ”を別で持つ🎁➡️🪞

![Result to UI Transformation](./picture/err_model_cs_study_023_result_to_ui.png)

ポイントはこれ👇
**同じエラーでも**

* 画面：短く・やさしく・次の行動つき🫶
* ログ：調査できる情報（分類・例外・相関ID・外部依存など）🔎

つまり、UIに渡すのは「画面表示用のDTO（ViewModel）」が安心だよ😊

### 例：UIに渡す形（イメージ）🧾

```csharp
public sealed record UiError(
    string Title,          // 例: "入力を確認してください"
    string Message,        // 例: "予算は0以上で入力してください"
    string? Field = null,  // 例: "Budget"
    string? ActionLabel = null, // 例: "もう一度試す"
    bool CanRetry = false,
    string? SupportId = null    // 例: 相関ID（バグ/障害のとき）
);
```

### Result → UiError 変換（ざっくり例）🔁

```csharp
public static UiError ToUiError(AppError error, string? correlationId = null)
{
    return error switch
    {
        DomainError d => new UiError(
            Title: "入力を確認してください",
            Message: d.UserMessage,          // 画面向け
            Field: d.FieldName               // 項目が分かる
        ),

        InfraError i => new UiError(
            Title: "通信に失敗しました",
            Message: "通信が不安定かもしれません。もう一度お試しください。",
            ActionLabel: "再試行",
            CanRetry: i.Retryable
        ),

        BugError b => new UiError(
            Title: "予期しないエラーが起きました",
            Message: "お手数ですが、もう一度お試しください。解決しない場合はサポートに連絡してください。",
            SupportId: correlationId
        ),

        _ => new UiError(
            Title: "エラーが起きました",
            Message: "もう一度お試しください。",
            SupportId: correlationId
        )
    };
}
```

> ✅ **“UserMessageは画面用”としてエラーカタログで管理**すると、UIが安定するよ📚🏷️
> ✅ “ログ用の詳細”はUIに出さない（出すなら「詳細」ボタンなどで慎重に）([Microsoft Learn][2])

---

## 7) ミニ演習（同じエラーを「画面用」と「ログ用」に書き分ける）📝🎓

![Exercise Scenarios](./picture/err_model_cs_study_023_exercise_scenarios.png)

題材：推し活グッズ購入🛍️💖（購入フォームがある想定）

### お題① ドメイン（入力エラー）💗

* 予算がマイナス
* 数量が0
* 期限切れ（購入期限を過ぎた）

**やること**

1. それぞれ **フィールドエラー文**を作る（短く・具体的に）
2. 画面上部の **要約文**も1つ作る（複数エラー時用）

### お題② インフラ（通信/外部API）🌩️

* 決済APIがタイムアウト
* DB接続失敗（再試行できる/できない を分ける）

**やること**

1. バナー文（短い）
2. 「再試行」ボタンの文言（短い動詞）
3. “ユーザーが次にできること”を1つ添える

「ユーザーが今すぐ解決できない」系は、**復帰導線（Retry/時間を置く）**を必ず付けるのがコツだよ🔁 ([Microsoft Learn][2])

### お題③ バグ（想定外）⚡

* Null参照とか、不変条件違反が起きた（=想定外）

**やること**

1. 画面の文言（責めない、短い、次の行動）
2. 問い合わせ用に **SupportId（相関ID）**を表示する場所を決める（例：文末に小さく）
3. ログに残す内容（例外、相関ID、操作、ユーザー入力は必要最低限）

---

## 8) AI活用（案出し→人が選ぶ）🤖✨

![AI Copywriter](./picture/err_model_cs_study_023_ai_writer.png)

UI文言づくりはAIがめっちゃ得意だよ🎀
おすすめプロンプト例👇

```text
次のエラーに対して、ユーザー向けの短いメッセージ案を5つ作って。
条件：
- 専門用語なし
- 責めない
- 次に何をすればいいか入れる
- 20〜45文字くらい
エラー：予算が上限を超えた（上限 10,000円）
```

```text
次のエラーを「項目の下に出す文」「画面上部の要約文」に分けて作って。
エラー：メール形式が不正
```

```text
インフラ障害（タイムアウト）のメッセージを
1) バナー用（短い）
2) 詳細説明（1〜2文）
3) ボタン文言（短い動詞）
で出して。
```

MicrosoftのUI文言ガイドでも「分かりやすく・短く・タスク達成を助ける」が軸だよ📎 ([Microsoft Learn][5])

---

## 9) ありがち落とし穴（先に潰そ😉）🕳️💦

![Bad UI Pitfalls](./picture/err_model_cs_study_023_bad_ui_examples.png)

* ❌ 画面に例外メッセージそのまま表示（専門用語＆情報漏れ）
* ❌ エラーコードだけ表示（ユーザーが動けない）
* ❌ 毎回ダイアログ（操作が止まりまくる）
* ❌ 入力中に毎キーで警告（支援技術的にも騒がしくなりがち）
  → “確定時”や“フォーカスが外れた時”中心が無難🧑‍🦯 ([dequeuniversity.com][6])
* ❌ エラーが直ったのに表示が残る（不安になる）😵

---

## まとめ🎀✨（この章の持ち帰り）

* UIは **表示場所（4パターン）**を持つと迷わない🧭
* 文言は **「何が起きた/結果/次どうする」**で強い🧱 ([Microsoft Learn][2])
* **責めない・専門用語を避ける・短く具体的に**🫶 ([Microsoft Learn][1])
* アクセシビリティ的に **テキストで説明＆どの項目か特定**が大事🧑‍🦯 ([W3C][4])
* ResultからUIへは **画面用モデルに変換**して、安全に扱う🎁🪞

次の章（第24章）は、このUI体験を“運用で勝てる形”にするための **ログ設計（構造化ログ）**に進むよ🔎🧾✨

[1]: https://learn.microsoft.com/en-us/windows/apps/design/style/writing-style "Writing style - Windows apps | Microsoft Learn"
[2]: https://learn.microsoft.com/en-us/windows/win32/debug/error-message-guidelines "Error Message Guidelines - Win32 apps | Microsoft Learn"
[3]: https://fluent2.microsoft.design/components/web/react/core/field/usage "React Field - Fluent 2 Design System"
[4]: https://www.w3.org/WAI/WCAG22/Understanding/error-identification.html "Understanding Success Criterion 3.3.1: Error Identification | WAI | W3C"
[5]: https://learn.microsoft.com/en-us/power-platform/well-architected/experience-optimization/user-interface-content "Recommendations for writing user interface content - Power Platform | Microsoft Learn"
[6]: https://dequeuniversity.com/checklists/web/form-validation-feedback "Form Validation and Feedback | Web Accessibility Checklist"
