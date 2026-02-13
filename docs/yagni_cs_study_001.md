# 第01章：YAGNIってなに？「作らない勇気」の入門 🌱🙂

## 0. この章でできるようになること（ゴール）🎯✨

* **YAGNIを“誤解なく”1文で説明**できるようになる🗣️💡
* 「それ今いる？」を**自分で判断する基準**を持てるようになる🧭👀
* ありがちな“作り込みの罠”を**回避する最初の一歩**を踏めるようになる🧯🚧
* 最後に、**自分専用のYAGNIルール1文**を完成させる📦✍️

---

## 1. まず結論：YAGNIの一言定義 🧩

![Build only what you need now](./picture/yagni_cs_study_001_definition.png)


**YAGNI = 「今、必要なものだけ作る」**✨
もっと丁寧に言うと👇

* 「将来たぶん要るかも…」で機能を足さない
* “必要になった瞬間”に、ちゃんと作る

YAGNIはXP（エクストリーム・プログラミング）で語られてきた考え方で、ロン・ジェフリーズの有名な説明が軸になってます。 ([ronjeffries.com][1])

---

## 2. なんでYAGNIが大事なの？（超リアルな理由）😅💥

![yagni_cs_study_001_maintenance_cost.png](./picture/yagni_cs_study_001_maintenance_cost.png)

「未来のために作っとこ！」って、優しさに見えるんだけど…実際はこうなりがち👇

* **未来が当たらない**🎯💦（当たったとしても“別の形で必要”になりがち）
* **作った瞬間から保守コスト発生**🧹🧾（テスト・例外・ドキュメント・理解コスト）
* **複雑さで速度が落ちる**🐢（「変更したいのに怖い」になる）
* **DDD初心者ほど“立派な箱”を先に作りがち**📦📦📦（でも中身がまだ薄い…）

つまりYAGNIは、**開発の体力を温存して、変化に強くする**ための作戦なんだよね💪🌸 ([martinfowler.com][2])

---

## 3. よくある誤解をぜんぶ潰す（ここ超大事）🧯✨

### 誤解①：YAGNI = 手抜き？😵‍💫

![yagni_cs_study_001_misconception.png](./picture/yagni_cs_study_001_misconception.png)

**違うよ〜！🙅‍♀️**
YAGNIは「雑に作る」じゃなくて、**価値が出るところに集中する**ってこと✨

### 誤解②：設計しないってこと？🫣

**それも違う！🙅‍♀️**
“後で育てられる”くらいの最低限の設計はするよ🌱
ただし、**未来のための立派すぎる仕組み**は今は作らない✂️

### 誤解③：リファクタしないならYAGNIでOK？😇

これが一番危険⚠️
YAGNIは、XPの文脈だと「シンプルに作って、必要になったら整える（リファクタ）」とセットで語られがち。
「今だけ動けばOK」で放置すると、ただの負債になる😇💣 ([ウィキペディア][3])

---

## 4. KISS / DRY とどう関係するの？（ざっくりおいしく）🧁✨

![yagni_cs_study_001_principles_trio.png](./picture/yagni_cs_study_001_principles_trio.png)

### KISS（シンプルにしよう）🍭

* YAGNIは**シンプルに保つためのブレーキ**🚦
* 「将来の拡張性のために…」で構造が複雑になるのを止める✋

### DRY（同じことを繰り返さない）🍩

* DRYは大事だけど、**早すぎる共通化は罠**🎣
* まずは少し重複しててもOK。
  重複が“痛み”になってから共通化すると、ちょうどいいことが多い🩹✨

（この「痛みが出たら直す」って感覚、YAGNIと相性よすぎる🤝💖）

---

## 5. ミニ演習📝：「今必要」だけに絞る練習✂️✨

![Cutting the Scope](./picture/yagni_cs_study_001_mvp_cut.png)


### お題：学内イベントの「参加登録」アプリ🎪📱

あなたは学園祭の運営。やりたいこと候補はこれ👇

**候補機能リスト**

1. 参加登録（名前・学籍番号・メール）📝
2. 登録済み一覧を見る📋
3. キャンセル🗑️
4. 管理者ログイン🔐
5. QRコード受付📷
6. 参加者へ一斉メール📧
7. 支払い（チケット）💳
8. 参加者の属性分析📊
9. 多言語対応🌍
10. 将来の他イベントにも使える汎用化♾️

---

### ステップA：MVPを決めよう（3つまで）🍰

**ルール**：

* 「初日の運営が成立する」だけ考える
* “気が利く未来”は一旦スキップ🙈

例（答えの一例）👇

* 1. 参加登録
* 2. 登録済み一覧
* 3. キャンセル

---

### ステップB：「今は作らない」リストを作ろう🧊

* 4. 管理者ログイン（最初は運営PC限定で運用で回す）
* 5. QR受付（紙の名簿 or 検索で当面OK）
* 6. 一斉メール（手動メールで当面OK）
* 7. 支払い（無料イベントなら不要）
* 8. 分析（まずは開催できることが優先）
* 9. 多言語（来年要望が出たら）
* 10. 汎用化（2回目が来てからでも遅くない）

---

### ステップC：受け入れ条件を1〜2個だけ書く✅

例👇

* 「登録したら一覧に出る」
* 「キャンセルしたら一覧から消える」

---

## 6. “C#あるある”で見る：YAGNIの空気感 🧠🧯

![yagni_cs_study_001_over_engineering.png](./picture/yagni_cs_study_001_over_engineering.png)

### ありがち：最初から全部「差し替え可能」にしたくなる😇

* まだ差し替えないのに `IService` / `IRepository` を量産
* DIコンテナも早めに導入
* 抽象が増えて読むのがしんどい😵‍💫

でも、YAGNI的にはこう👇

* **差し替えの痛みが出たら切る**✂️
* テストが辛くなったら、そこから“必要な分だけ”抽象化する🧪

#### 例：最初は素直に書く（必要になったら整える）🌱

```csharp
public sealed class RegistrationService
{
    private readonly List<Participant> _participants = new();

    public void Register(string name, string studentId, string email)
    {
        _participants.Add(new Participant(name, studentId, email));
    }

    public IReadOnlyList<Participant> List() => _participants;
}

public sealed record Participant(string Name, string StudentId, string Email);
```

> まずはこのくらいでOK🙆‍♀️✨
> 本当にDBが必要になったら、その時点でリポジトリを導入しても間に合うよ🌸

---

## 7. AI活用🤖：MVP範囲をAIに箇条書きさせる（盛らせないコツ付き）🧯✨

![yagni_cs_study_001_ai_prompting.png](./picture/yagni_cs_study_001_ai_prompting.png)

### 7-1. “盛らせない”プロンプト（コピペOK）📝

Copilot/Codexにこう投げる👇

```text
あなたは厳しめのPMです。
以下の要件から「初回リリース(MVP)で必須な機能」を最大3つに絞ってください。
制約:
- 拡張性・将来対応・汎用化は考えない
- 例外的なケースや管理機能は後回し
- 受け入れ条件も各1つだけ添える
出力は箇条書きのみ。
要件: （ここに要件を貼る）
```

### 7-2. AIが盛ってきた時の“返し”テンプレ😇✂️

```text
その提案のうち「将来のため」「便利そうだから」だけで入っている項目を列挙して削って。
MVPに残す理由を、受け入れ条件ベースで説明して。
```

---

## 8. 成果物📦：自分用YAGNIルール1文（これがゴール！）✍️✨

### 書き方テンプレ🧾

* 「◯◯の“痛み”が出るまで、△△は作らない」

例👇

* 「**差し替えが本当に必要**になって困るまで、`interface` は増やさない」🪓
* 「**要件にない汎用化**は、2回目の類似案件が来るまで作らない」♾️✋
* 「**運用で回せる**なら、管理画面は後回しにする」🧑‍💻🗂️

---

## 9. 1分チェッククイズ✅🎓

1. YAGNIは「設計しない」ことである。→ ✅/❌
2. 「将来要るかも」だけで機能を追加するのはYAGNI的。→ ✅/❌
3. まず小さく作って、必要になったら整えるのがYAGNIの感覚。→ ✅/❌

（答え：1❌ 2❌ 3✅）🎉

---

## おまけ：いまの“最新”メモ（さらっと）🆕✨

* **.NET 10 はLTS**で、サポートは **2028年11月ごろまで**の案内になってるよ📌 ([Microsoft for Developers][4])
* **C# 14** の新機能は Microsoft Learn にまとまってる🧠 ([Microsoft Learn][5])
* Visual Studio 2022 は **17.14 系**が現行の流れ（リリース履歴あり）🛠️ ([Microsoft Learn][6])

---

次は第2章で、「作り込みすぎのサイン👀🚨」を“見抜く目”を作っていこうね〜！✨💪

[1]: https://ronjeffries.com/xprog/articles/practices/pracnotneed/?utm_source=chatgpt.com "You're NOT gonna need it!"
[2]: https://martinfowler.com/bliki/Yagni.html?utm_source=chatgpt.com "Yagni"
[3]: https://en.wikipedia.org/wiki/You_aren%27t_gonna_need_it?utm_source=chatgpt.com "You aren't gonna need it"
[4]: https://devblogs.microsoft.com/dotnet/announcing-dotnet-10/?utm_source=chatgpt.com "Announcing .NET 10"
[5]: https://learn.microsoft.com/ja-jp/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "C# 14 の新機能"
[6]: https://learn.microsoft.com/en-us/visualstudio/releases/2022/release-history?utm_source=chatgpt.com "Visual Studio 2022 Release History"
