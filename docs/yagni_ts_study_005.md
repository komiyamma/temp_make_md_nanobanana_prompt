# 第05章：TypeScriptでやりがちな“未来用設計”を安全に先送りする 🧯🧠

（ねらい🎯：型・共通化・レイヤーの“作り込み”を、**後で困らない形で**回避できるようになる！）

---

## 1) まず最初に：未来用設計って、なにが「悪い」の？😵‍💫

未来を考えるのは悪じゃないよ〜！🙆‍♀️✨
でも、**まだ起きてない困りごと**に対して、先に仕組みを盛ると…👇

* 仕様が変わった時に「立派な仕組み」が逆に邪魔になる🧱💥
* “使われない拡張点”が増えて、読むコストが爆増📚😇
* TypeScriptだと「型パズル」が始まって進捗が止まる🧩🫠
* AI（Copilot等）も盛りがちで、さらに巨大化しやすい🎈🤖

この章は、**未来の可能性をゼロにせず**、でも**今は作らない**ための「安全な先送り」のやり方を作るよ〜🧯🌿

---

## 2) “安全に先送り”の合言葉はこれ👇✨

![Safety Exit](./picture/yagni_ts_study_005_safety_exit.png)

### ✅ 「変える場所を決める」→ ✅「今は素直に書く」→ ✅「痛みが出たら強くする」💪🙂

ポイントは「将来の変更に備える」じゃなくて、
**“変更が来た時に逃げられる出口”だけ作っておく**って感じ！🚪✨

---

## 3) 先送りを安全にする「3つの最小装備」🧰🛡️

### 装備①：境界（boundary）を1枚だけ置く 🧱✨

![Boundary Wall](./picture/yagni_ts_study_005_boundary_wall.png)

たとえば「API」「保存（localStorage等）」「日時」みたいな、変わりがちな所にだけ薄い壁を作るよ🙂

* ❌ いきなりRepository/Service/UseCase全部作る
* ✅ まずは **“呼び出し口1つ”** だけ作る

例：保存の境界（最小）📝

```ts
export type Memo = {
  id: string
  text: string
  createdAt: number
}

const STORAGE_KEY = "oshi-memos"

export function loadMemos(): Memo[] {
  const raw = localStorage.getItem(STORAGE_KEY)
  if (!raw) return []
  return JSON.parse(raw) as Memo[]
}

export function saveMemos(memos: Memo[]): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(memos))
}
```

これで「保存方式をDBに変える」みたいな未来が来ても、まずここだけ触ればOKになりやすいよ〜🧯✨

---

### 装備②：変換（mapping）で“雑な世界”と“きれいな世界”を分ける 🧼✨

![Data Mapping](./picture/yagni_ts_study_005_data_mapping.png)

APIレスポンスとかって、いつ変わるかわからないよね😇
だから **“外”は雑でもOK**、中に入れる時に整える！

```ts
// 外（API由来）はゆるい型でもOK（まず動かす）
type MemoDto = {
  id: string
  text: string
  created_at: number
}

// 中（アプリ内）は自分が使いやすい型に統一
export type Memo = {
  id: string
  text: string
  createdAt: number
}

export function toMemo(dto: MemoDto): Memo {
  return {
    id: dto.id,
    text: dto.text,
    createdAt: dto.created_at,
  }
}
```

ここを分けておくと、未来の変更が来ても**変換関数だけ直す**で済みやすいよ🧯✨

```mermaid
flowchart LR
    API[外部API<br>型がゆるい/変わるかも] -->|DTO| Mapper(変換関数<br>toMemo)
    Mapper -->|Memo| Domain[アプリ内<br>自分が使いやすい型]
    
    style API fill:#f9f,stroke:#333
    style Domain fill:#ccf,stroke:#333
```


---

### 装備③：ちょこっとテスト（またはチェック関数）で守る 🧪🩷

未来のための大設計じゃなくて、**壊れたら困る所だけ**守る！

* 例：`toMemo()` の変換だけは守る🛡️
* 例：メモ追加ロジックだけ守る🛡️

---

## 4) 【型】盛りすぎ問題を止めるコツ🧩🧯

### 4-1) “浅い型”から始めていい理由🙂

![“浅い型”から始めていい理由](./picture/yagni_ts_study_005_shallow_types.png)

最初から「完璧なUnion」「完璧なGenerics」にすると、だいたいこうなる👇

* 実装が遅い🐢
* 読めない🫠
* 仕様変更で全部崩れる🧨

だから基本はこれでOK👇✨
**「まず浅く → 使い方が固まったら強く」**💪

---

### 4-2) `as`（型アサーション）で黙らせすぎない🙅‍♀️💦

`as` は便利だけど、**間違いも通しちゃう**から、YAGNI的には“最後の手段”くらいにしてね😇

代わりに役立つのが `satisfies` 🎀
`as` と違って「型チェックはするけど、推論は壊しにくい」用途で使えるよ〜（パターンによるけど、やりたいことに合う場面が多い！）([Better Stack][1])

例：設定オブジェクトを“いい感じに”チェック✅

```ts
type SortKey = "createdAt" | "text"

type UiConfig = {
  defaultSort: SortKey
  pageSize: number
}

export const config = {
  defaultSort: "createdAt",
  pageSize: 20,
} satisfies UiConfig
```

* ✅ `defaultSort` のタイプミスは弾く
* ✅ でも “変に型を固定しすぎる”ことを避けやすい

---

### 4-3) 「型を強くする」タイミングの合図🚥

次のどれかが来たら、強くしてOK！

* 同じ形のデータが3箇所以上に散ってる📌
* バグが型の弱さ由来で2回以上出た🐛🐛
* 「この形は絶対守りたい」が言語化できる✍️✨

---

## 5) 【Generics】は“痛みが出てから”🧬😇

Genericsってカッコいいけど、早いとだいたい事故る😂

### よくある事故例（未来用）😵‍💫

* “なんでも対応できる”汎用関数を作る
* 使う側が読み解けない
* 未来が来ない（＝誰も使わない）

だからルールはこれでOK👇✨

* ✅ まず具体型で書く
* ✅ コピペが増えてきたら共通化を検討
* ✅ 「型引数が2つ超えたら黄色信号」🚧（目安ね！）

---

## 6) 【utils/helpers】作りすぎを止めるルール🚫🧰

### 合言葉：**“共通化は、重複が増えてから”**🙂✨

おすすめのミニルール👇

* **同じロジックが3回出たら**、はじめて共通化を検討🧠
* 共通化したら、**利用箇所を2つ以上**にする（1つなら早かったかも）👀
* utilsは「目的が言える名前」だけ残す（例：`formatDateForUi`）📝

---

## 7) 【フォルダ】最初から大規模にしない📁😌

![Simple Feature Folder](./picture/yagni_ts_study_005_simple_folder.png)

最初からこういうの作ると、だいたい燃える🔥

* `domain/` `application/` `infrastructure/` …（立派すぎるやつ）🏰😇

まずはこれくらいで全然OK👇✨

```txt
src/
  features/
    memo/
      memoTypes.ts
      memoStore.ts
      memoUsecases.ts
      MemoView.tsx
```

「1機能=1フォルダ」くらいが、YAGNIと相性よいよ〜🌿🙂

---

## 8) ミニ演習📝：「盛りすぎコード」をYAGNIで削る✂️✨

### お題：メモ保存を“立派にしすぎた”例😇

**Before（盛りすぎ）**

```ts
export interface Entity<TId> {
  id: TId
}

export interface Repository<TEntity extends Entity<TId>, TId> {
  findAll(): Promise<TEntity[]>
  save(entity: TEntity): Promise<void>
  delete(id: TId): Promise<void>
}

export class MemoEntity implements Entity<string> {
  constructor(
    public id: string,
    public text: string,
    public createdAt: Date,
  ) {}
}

export class MemoRepository implements Repository<MemoEntity, string> {
  async findAll(): Promise<MemoEntity[]> { /* ... */ throw new Error("TODO") }
  async save(entity: MemoEntity): Promise<void> { /* ... */ throw new Error("TODO") }
  async delete(id: string): Promise<void> { /* ... */ throw new Error("TODO") }
}
```

### やること✅

1. **“今必要な操作だけ”** に絞って書き直す（例：一覧・追加だけ）🧩
2. `Entity` / `Repository` / `class` を消してOK（必要になったら復活）🧯
3. 型は浅めでOK（まず動く）🏃‍♀️💨

**ヒント（Afterの方向性）**

```ts
export type Memo = {
  id: string
  text: string
  createdAt: number
}

export function addMemo(memos: Memo[], text: string): Memo[] {
  const memo: Memo = { id: crypto.randomUUID(), text, createdAt: Date.now() }
  return [memo, ...memos]
}
```

---

## 9) AI活用🤖：盛らせない“指示テンプレ”🧯✨

![AI Blueprint Control](./picture/yagni_ts_study_005_ai_blueprint.png)

Copilotは **Agent mode** みたいに自律で編集してくれる機能もあるけど、油断すると“立派なアーキ”に走りやすいの〜😂
（Agent modeは、タスクに応じて複数ファイル編集やコマンド提案まで自律で進めるモードだよ）([GitHub Docs][2])

だから指示はこうする👇✨

### ✅ 盛らせないプロンプト（コピペ用）🧾💖

* 「**今の要件だけ**で実装して。拡張性の仕込みは禁止」🚫
* 「Genericsは使わない（必要になったら後で）」🧬🙅‍♀️
* 「新規ファイルは最大3つまで」📄📄📄
* 「Repository/Service層は作らない」🧱✋
* 「型は最小、`as`で黙らせない」🧩

### ✅ “削るレビュー”をAIにやらせる🕵️‍♀️✨

* 「このコード、YAGNI的に削れる抽象化を5つ挙げて」
* 「今の要件に不要な型の複雑さを指摘して、簡略案を出して」
* 「utils化が早すぎる箇所があれば、インライン案も出して」

---

## 10) おまけ：tsconfigも“未来用”に盛りすぎ注意⚙️😇

TypeScriptは最近のバージョンで、Node向けの安定オプションが増えてるよ〜。たとえば TypeScript 5.9 では `--module node20` が「将来挙動がブレにくい安定オプション」として説明されてるよ🧯✨([TypeScript][3])
（最新タグとしては TypeScript 5.9.3 が “Latest” 表示になってるよ）([GitHub][4])

YAGNI的には、`tsconfig` も「必要な分だけ」からでOK🙂
オプション盛りすぎると、あとで自分が泣く🥲

---

## 11) 成果物📦：TypeScript版YAGNI判断ルール集（テンプレ）📝✨

最後に、あなた専用ルールを1枚にまとめよ〜💖

* 型は「浅く開始 → 痛みが出たら強化」🧩
* Genericsは「必要になってから」🧬
* 共通化は「3回出たら検討」✂️
* 境界は「1枚だけ」🧱
* フォルダは「1機能=1フォルダ」📁
* AIには「今の要件だけ」「拡張仕込み禁止」を毎回言う🤖🧯

---

* [The Verge](https://www.theverge.com/news/808032/github-ai-agent-hq-coding-openai-anthropic?utm_source=chatgpt.com)
* [itpro.com](https://www.itpro.com/software/development/github-just-launched-a-new-mission-control-center-for-developers-to-delegate-tasks-to-ai-coding-agents?utm_source=chatgpt.com)
* [businessinsider.com](https://www.businessinsider.com/microsoft-github-reshuffle-ai-coding-agents-2026-1?utm_source=chatgpt.com)
* [The Verge](https://www.theverge.com/news/821948/microsoft-windows-11-ai-agents-taskbar-integration?utm_source=chatgpt.com)
* [The Verge](https://www.theverge.com/news/787076/microsoft-office-agent-mode-office-agent-anthropic-models?utm_source=chatgpt.com)

[1]: https://betterstack.com/community/guides/scaling-nodejs/typescript-as-satisfies-type/?utm_source=chatgpt.com "TypeScript as vs satisfies vs Type Annotations"
[2]: https://docs.github.com/en/copilot/get-started/features "GitHub Copilot features - GitHub Docs"
[3]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html "TypeScript: Documentation - TypeScript 5.9"
[4]: https://github.com/microsoft/typescript/releases "Releases · microsoft/TypeScript · GitHub"
