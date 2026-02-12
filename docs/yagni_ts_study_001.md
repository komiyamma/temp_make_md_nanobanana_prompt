# 第01章：YAGNIってなに？「作らない勇気」の入門 🌱🙂

**ねらい🎯**：YAGNIを“誤解なく”説明できるようになる（＝作り込み地獄から抜け出す第一歩！✨）

---

## 0. はじめに：あるあるストーリー📦😇

個人開発でよくある流れ👇

* 「よし！推し活メモ作ろ〜💖」
* なのに…

  * 先に“完璧なAPI設計”を作り
  * “将来のため”の汎用Repositoryを作り
  * “いつか差し替え”のinterfaceを増やし
  * 気づいたら **画面が1つもない**…😇😇😇

ここで効くのが **YAGNI** です✊✨

---

## 1. YAGNIの一言まとめ🧩

![YAGNIの一言まとめ](./picture/yagni_ts_study_001_now_vs_future.png)

**YAGNI = “今必要なものだけ作る”**
つまり…

* ✅「必要になってから作る」
* ❌「必要になりそうだから作る（未来予想の作り込み）」はしない

YAGNIは、Extreme Programming（XP）由来の考え方として広く知られています。([martinfowler.com][1])

---

## 2. まず誤解をぶっ壊す🧯（超大事！）

YAGNIって言うと、たまにこう誤解されます👇

### ❌ よくある誤解

* 「手抜きでしょ？」🙅‍♀️
* 「設計しないってこと？」🙅‍♀️
* 「何も考えずに書き散らかすやつ？」🙅‍♀️

### ✅ 正しいニュアンス

* **“未来の仮説”にコストを払わない**
* そのかわり、**必要になったら足せるように**

  * 小さく保つ
  * 直せる形にしておく（リファクタ前提）
  * テストがあるとさらに安心🧪✨

※YAGNIは、継続的リファクタや自動テストなどの実践とセットで語られることが多いです。([ウィキペディア][2])

---

## 3. 「作らない」って、どこまで？ライン引きのコツ🧠🧵

YAGNIで大事なのは、これ👇

### ✅ “作らない”の対象

* 将来のための機能（例：ログイン、課金、通知…「いつか」系）
* 将来のための仕組み（例：汎用化、差し替え可能設計、拡張ポイント大量）

### ✅ “作る”の対象

* **今の受け入れ条件に必要**なもの
* **今この瞬間、動く価値が出る**もの
* **次の変更が来たら本当に困るところ**だけの最小の備え（最小限ね！）

---

## 4. KISS / DRY との関係（ふんわり🧁）

![KISS / DRY との関係](./picture/yagni_ts_study_001_premature_dry.png)

ここ、気持ちよく整理しよ〜☺️✨

### KISS（Keep it simple）🧁

* 「できるだけシンプルに作ろう」っていう考え方。([ウィキペディア][3])
* **YAGNIはKISSの“行動ルール版”**みたいな感じで、

  * “今いらない複雑さ”を増やさない方向に背中を押してくれます💪

### DRY（Don’t repeat yourself）🧬

* 「同じ“知識”をあちこちに散らさない」っていう考え方。([ウィキペディア][4])
* でも初心者あるあるとして…

  * DRYを早くやりすぎて
  * **まだ共通じゃないものまで無理やり共通化**しがち😵‍💫

👉 **YAGNIは“早すぎるDRY”にブレーキ**をかけるのに超便利です🚦✨
（重複が“痛み”になってから共通化でOK！）

---

## 5. TypeScript開発でYAGNIが効く場面（個人開発あるある）📦

「未来用の罠」が出やすいポイントを、TypeScriptあるあるで紹介するね👇

### 5.1 API設計：先に完璧なAPIを作りがち🛰️

* ❌ 画面がないのに、エンドポイントを10個設計
* ✅ まずは **“今の画面に必要な1〜2個”**だけでOK

### 5.2 型設計：型を盛りすぎる🧨

* ❌ Union爆発、Generics芸、謎の抽象型
* ✅ **最初は素直な型**（薄め）でOK

  * “困ってから強くする”が勝ち🏆

### 5.3 共通化：utils地獄🍭

* ❌ `utils/` に便利関数が増殖して、誰も把握できない😇
* ✅ “同じ処理が3回出て、ほんとに同じだ…”ってなってからでOK

### 5.4 フォルダ構成：最初から大規模アーキにしがち📁

* ❌ layers/ domain/ infrastructure/ adapters/ …（まだ機能2個なのに！）
* ✅ **まずは小さく**：機能が増えてから整える

---

## 6. ちいさなコード例で体感しよ🧪✨（早すぎる抽象化）

### ❌ “未来のため”に頑張りすぎ例

```ts
// 「いつかStorageを差し替えるかも…」で始まるやつ（今は不要かも）
interface StorageLike {
  getItem(key: string): string | null;
  setItem(key: string, value: string): void;
}

class MemoRepository {
  constructor(private storage: StorageLike) {}

  save(text: string) {
    this.storage.setItem("memo", text);
  }

  load(): string {
    return this.storage.getItem("memo") ?? "";
  }
}
```

### ✅ まず“今いる最小”でOK例

```ts
export function saveMemo(text: string) {
  localStorage.setItem("memo", text);
}

export function loadMemo(): string {
  return localStorage.getItem("memo") ?? "";
}
```

ポイント💡

* “差し替え”が**本当に必要になった瞬間**に、はじめてinterfaceを切ればいい
* そのときには、要件が具体化してるから「どんな差し替え？」も判断しやすいよ🙂✨

---

## 7. ミニ演習📝：「いつか作りたい機能」10個 → “今必要”を2個に絞る✂️

### ステップ1：まず10個、ノンストップで書く🖊️💨

例（推し活メモ系でも何でもOK）

* ログイン
* タグ
* 検索
* 並び替え
* 共有リンク
* 画像添付
* クラウド同期
* 通知
* ダークモード
* エクスポート

### ステップ2：次の質問で“今必要？”をチェック👀✅

各機能に対して、これを当ててみて👇

* それがないと、**今日の利用者が困る？**
* それは、**受け入れ条件に書ける？**
* それがないと、**価値が伝わらない？**
* それを作ると、**画面が1つでも完成に近づく？**

### ステップ3：いったん“今は2個だけ”にする✂️✨

* ✅ 今作る：2個
* 🧊 今は作らない：残り8個（ただし消さない！「未来箱📦」に入れる）

> コツ：**「作らない」＝「忘れる」じゃないよ🙂**
> “将来候補リスト”として見える場所に置くのが上手なYAGNI✨

---

## 8. AI活用🤖：「今作る範囲」を盛らせずに出してもらう

Copilot ChatはVS Code内のチャットとして使えます。([Visual Studio Code][5])
（アイコンから開いて、自然文で質問できるやつね🙂）

### 8.1 まず投げるプロンプト（超おすすめ）🧾✨

コピペして使ってOK👇

```text
このアプリ要件から「今作る範囲(MVP)」を箇条書きにしてください。
条件：
- “今の価値に直結するもの”だけ
- 未来のための汎用化・拡張ポイント・設定項目は入れない
- 「今は作らない候補」も別枠で出して（理由つきで）
```

### 8.2 AIが盛り始めたら止める呪文🚦😅

```text
提案が過剰設計っぽいです。
「受け入れ条件にないもの」「将来の仮説だけのもの」を赤信号として指摘して、
最小案に削ってください。
```

---

## 9. 成果物📦：自分用YAGNIルールを“1文”で作る

最後に、自分だけのルールを1つ作ろう🙂✨
（迷ったときの“お守り”になるよ！）

### テンプレ（好きなの選んでOK）🎀

* 「受け入れ条件にないものは実装しない。TODOに置く。」✅
* 「迷ったら作らない。まず動く最小を完成させる。」✅
* 「共通化は3回出てから。Genericsは痛みが出てから。」✅
* 「将来のためのinterfaceは、差し替え要求が来てから切る。」✅

---

## 10. 理解チェック（ゆるクイズ🎓✨）

**Q1**：YAGNIは「設計しない」の意味？

* A. はい
* B. いいえ

**Q2**：「将来のための汎用化」を今やるべき判断は？

* A. なんとなく必要そうならやる
* B. 具体的な変更要求・痛みが出てからやる

**Q3**：DRYを早くやりすぎると起きがちなことは？

* A. コードが簡単になる
* B. まだ共通じゃないものを無理やりまとめて複雑になる

**答え✅**：Q1=B / Q2=B / Q3=B 🙆‍♀️✨

---

## 11. まとめ🌱🙂

* YAGNIは **「今必要なものだけ作る」**（未来予想の作り込みをしない）([martinfowler.com][1])
* KISSと相性よし、DRYは“早すぎ注意”([ウィキペディア][3])
* TypeScriptでは「型盛り」「utils地獄」「先アーキ」が罠になりがち📦😇
* AIは便利だけど盛りやすいので、**“削らせる指示”**が大事🤖✂️([Visual Studio Code][5])

---

## （おまけ）2026っぽい“最新寄り”メモ🗞️✨

* TypeScriptは **5.9系**のリリースノートが公開されていて、`import defer` や `--module node20` などが話題になっています。([Microsoft for Developers][6])
* npm上の `typescript` は **5.9.3** が “Latest” として表示されています（2025-09-30公開）。([npm][7])
* AIコーディング支援は「チャット＋エージェント」方向に進化が速いので、**“盛らせないYAGNIプロンプト”**の価値が上がってます🙂🧯([The Verge][8])

---

* [The Verge](https://www.theverge.com/news/808032/github-ai-agent-hq-coding-openai-anthropic?utm_source=chatgpt.com)
* [The Verge](https://www.theverge.com/news/669339/github-ai-coding-agent-fix-bugs?utm_source=chatgpt.com)
* [Business Insider](https://www.businessinsider.com/microsoft-github-reshuffle-ai-coding-agents-2026-1?utm_source=chatgpt.com)
* [The Verge](https://www.theverge.com/news/753984/microsoft-copilot-gpt-5-model-update?utm_source=chatgpt.com)
* [The Verge](https://www.theverge.com/news/618839/google-gemini-ai-code-assist-free-individuals-availability?utm_source=chatgpt.com)

[1]: https://martinfowler.com/bliki/Yagni.html?utm_source=chatgpt.com "Yagni"
[2]: https://en.wikipedia.org/wiki/You_aren%27t_gonna_need_it?utm_source=chatgpt.com "You aren't gonna need it"
[3]: https://en.wikipedia.org/wiki/KISS_principle?utm_source=chatgpt.com "KISS principle"
[4]: https://en.wikipedia.org/wiki/Don%27t_repeat_yourself?utm_source=chatgpt.com "Don't repeat yourself"
[5]: https://code.visualstudio.com/docs/copilot/chat/copilot-chat?utm_source=chatgpt.com "Get started with chat in VS Code"
[6]: https://devblogs.microsoft.com/typescript/announcing-typescript-5-9/?utm_source=chatgpt.com "Announcing TypeScript 5.9"
[7]: https://www.npmjs.com/package//typescript?activeTab=versions&utm_source=chatgpt.com "typescript"
[8]: https://www.theverge.com/news/669339/github-ai-coding-agent-fix-bugs?utm_source=chatgpt.com "GitHub's new AI coding agent can fix bugs for you"
