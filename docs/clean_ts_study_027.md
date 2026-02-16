# 第27章：Portの入出力モデル（内側基準で決める）📦

この章はね、「Port（差し替え口）」に流れる**データの形**をちゃんと決めて、
**DB都合やHTTP都合が“内側”に侵入しないようにする回**だよ〜！🧼🧠💕

---

## 0. 2026年の“今”ちょいメモ（最新情報）📰🆕

* 現時点の安定版は **TypeScript 5.9 系（GitHubのLatestタグは 5.9.3）**だよ 📌 ([GitHub][1])
* そして TypeScript は **6.0 が 7.0 への橋渡し（最後のJSベース）**、7.0 はネイティブ化（Go移植）の大きな流れに向かってるみたい 🏎️💨 ([Microsoft for Developers][2])
* Node.js 側も **v24 が Active LTS** など、周辺もけっこう動いてるよ 🔧 ([Node.js][3])

（この章の内容は、こういう変化があっても崩れにくい“芯の作り方”って感じ！🧸✨）

---

## 1. まず結論：Portの入出力は「内側の言葉」で固定する🧡🔒

![Port Data Model Filter](./picture/clean_ts_study_027_port_filter.png)

Portの型は、こういう方針が正解だよ👇

✅ **内側の都合（業務の言葉）で決める**
❌ **外側の都合（SQLのRow、ORM型、HTTPのRequest/Response）で決めない**

つまり…

* Portに `TaskRow`（snake_caseなDB行）を入れない🙅‍♀️
* Portに `Request` や `Response`（Webの型）を入れない🙅‍♀️
* Portは「内側が欲しい形」だけを話す🗣️✨

---

## 2. 事故りがちな例（わざと悪い例）💥😇

![DB Leakage into UseCase](./picture/clean_ts_study_027_db_leak.png)

たとえば、DB都合が混ざるとこうなる👇

```ts
// ❌ DBの都合がそのまま入ってきてる例（よくある…）
type TaskRow = {
  task_id: number;          // DB都合の型
  title_text: string;       // DB都合の命名
  is_done: 0 | 1;           // DB都合の表現
  created_at: string;       // DB都合（ISO文字列）
};

interface BadTaskRepository {
  insert(row: TaskRow): Promise<void>;
  findById(task_id: number): Promise<TaskRow | null>;
}
```

これ、何がイヤかというと…😵‍💫💦

* UseCase が `0|1` を `boolean` に直す羽目になる
* `created_at` を `Date` に直す処理が内側に散らばる
* そのうち「SQLの列が増えた」だけで内側が壊れる

**＝ “差し替え口”のはずが、内側をDBに縛りつける鎖になる** 🔗😭

---

## 3. じゃあどう決める？3ステップでいこ！🧭✨

![3 Steps to Decide Model](./picture/clean_ts_study_027_model_steps.png)

### Step 1：境界をまたぐ“意味”を言葉にする🗣️

このミニTaskアプリなら、Portが扱うのはだいたいこれ👇

* 保存したい：Task（の情報）💾
* 取りたい：Task（の情報）🔍
* 一覧が欲しい：Taskの並び📋

### Step 2：内側の型（Value Object / DTO）を作る🧱

ここが本章のキモ！💖
「内側が扱いやすい型」を用意するよ。

* `TaskId`（ただのstringじゃなく、意味を持たせる）🆔
* `TaskSnapshot`（Portを通る“データだけ”の表現）📸

### Step 3：Portのメソッドは“UseCaseから逆算”で最小にする✂️

Portは増やすほど複雑になるから、**今のUseCaseに必要な分だけ**ね😊✨

---

## 4. Entityで返す？DTOで返す？どっちがいいの？🤔💭

![Port Input/Output Models (Snapshot vs Entity)](./picture/clean_ts_study_027_port_io.png)


ここ、迷いポイントだから、判断基準を置いとくね👇

### A案：Portの入出力＝Entity（Taskそのもの）🧡

✅ 良いところ

* UseCaseがそのまま使える（変換少ない）
* “ルールの塊”をそのまま扱える

⚠️ 気になるところ

* 永続化Adapterが Entity を組み立てる必要がある
* 「DBの形とズレる」ほどMapperが増える（でも本来それはOK！）

### B案：Portの入出力＝専用DTO（TaskSnapshot）📸

✅ 良いところ

* Portを通るものが「データだけ」になる（分かりやすい）
* 永続化・JSON化・テストがラク

⚠️ 気になるところ

* UseCase側で Entity 化（rehydrate）する手間がある

👉 この教材では **B案（TaskSnapshot）**を推すよ！
「Portの境界で“データの形”を守る」感覚が、いちばん身につきやすいから🧸✨

---

## 5. 実装してみよ！：Portの入出力モデル設計（完成形）🛠️💕

### 5-1. `TaskId`（意味付きID）を作る🆔✨

![TaskId Branding](./picture/clean_ts_study_027_taskid_brand.png)

```ts
declare const taskIdBrand: unique symbol;

export type TaskId = string & { readonly [taskIdBrand]: "TaskId" };

export function toTaskId(value: string): TaskId {
  // ここで形式チェックしたければしてOK（最小なら省略でもOK）
  return value as TaskId;
}
```

ポイント💡

* `TaskId` をただの `string` にしないことで、取り違え事故が減るよ〜！🧯✨

---

### 5-2. Portを通るDTO：`TaskSnapshot` 📸

```ts
export type TaskSnapshot = Readonly<{
  id: TaskId;
  title: string;
  completed: boolean;
  createdAt: Date;
  completedAt: Date | null;
}>;
```

ポイント💡

* `Readonly` にして「境界を超えたデータは勝手に書き換えない」ルールを強制📌✨
* `Date` を使うのは内側都合（DB側は文字列でも数値でも、外側で変換すればOK）⏰

---

### 5-3. Entityは“ルール担当”、Snapshotは“持ち運び担当”🎒

![Entity Rehydrate Cycle](./picture/clean_ts_study_027_rehydrate_cycle.png)

```ts
import { TaskId, TaskSnapshot } from "./task-types";

export class Task {
  private constructor(
    private readonly _id: TaskId,
    private _title: string,
    private _completed: boolean,
    private readonly _createdAt: Date,
    private _completedAt: Date | null,
  ) {}

  static create(args: { id: TaskId; title: string; now: Date }): Task {
    const title = args.title.trim();
    if (title.length === 0) throw new Error("InvalidTitle"); // ここは後の章でドメインエラー化してね⚠️
    return new Task(args.id, title, false, args.now, null);
  }

  static rehydrate(snapshot: TaskSnapshot): Task {
    return new Task(
      snapshot.id,
      snapshot.title,
      snapshot.completed,
      snapshot.createdAt,
      snapshot.completedAt,
    );
  }

  complete(now: Date): void {
    if (this._completed) return; // 二重完了は無視（方針は自由）
    this._completed = true;
    this._completedAt = now;
  }

  toSnapshot(): TaskSnapshot {
    return {
      id: this._id,
      title: this._title,
      completed: this._completed,
      createdAt: this._createdAt,
      completedAt: this._completedAt,
    } as const;
  }
}
```

ここが気持ちいいポイント😍✨

* **Entityがルールを守る**（タイトル空は禁止、とか）
* **PortはSnapshotだけを運ぶ**（DBの都合は持ち込まない）

---

### 5-4. Port（Repository）の入出力をSnapshotで固定する🔌📦

![Port Fixed with Snapshot](./picture/clean_ts_study_027_snapshot_fixed.png)

```ts
import { TaskId, TaskSnapshot } from "../entities/task-types";

export interface TaskRepository {
  save(task: TaskSnapshot): Promise<void>;
  findById(id: TaskId): Promise<TaskSnapshot | null>;
  listAll(): Promise<readonly TaskSnapshot[]>;
}
```

✅ これで「UseCase ↔ Repository」の会話は **内側語彙だけ**になるよ✨
（DBがSQLiteでも、別の何かでも関係なし👍）

---

### 5-5. `satisfies` で「実装がPortを満たす」保証をつける🛡️

`satisfies` は「形を満たしてるか検査しつつ、型推論をなるべく壊さない」用途で便利だよ🧡 ([TypeScript][4])

```ts
import { TaskRepository } from "../ports/task-repository";
import { TaskId, TaskSnapshot } from "../entities/task-types";

export const InMemoryTaskRepository = class {
  private store = new Map<TaskId, TaskSnapshot>();

  async save(task: TaskSnapshot): Promise<void> {
    this.store.set(task.id, task);
  }

  async findById(id: TaskId): Promise<TaskSnapshot | null> {
    return this.store.get(id) ?? null;
  }

  async listAll(): Promise<readonly TaskSnapshot[]> {
    return Array.from(this.store.values());
  }
} satisfies new () => TaskRepository;
```

ポイント💡

* 「implements」でも良いけど、`satisfies` を混ぜるとチェックが気持ちよく効くことがあるよ🧁✨
* ここは好みでOK！

---

## 6. 仕上げ：Portの入出力が“外側都合”になってないかチェック✅🧼

チェックリスト置いとくね！📝💕

* [ ] Portの型に `Row` / `Model` / ORM生成型が混ざってない？
* [ ] `snake_case` なプロパティ名が混ざってない？
* [ ] `0|1` みたいなDB表現が混ざってない？
* [ ] HTTPの `Request/Response` が混ざってない？
* [ ] 日付・IDが「外側の表現」のまま入ってない？（変換は外側で！）

---

## 7. ミニ理解チェック問題🎓💖

1. `TaskRepository` が `TaskRow`（DB行）を返す設計の、いちばんの問題は何？😵‍💫
2. `TaskSnapshot` を `Readonly` にするメリットは？🔒
3. Entity と Snapshot を分けると、どこに「変換」が集まって嬉しい？🧹✨

---

## 8. 提出物（この章のゴール）📦🎁

* `TaskId`（意味付きID）🆔
* `TaskSnapshot`（Portを通る内側DTO）📸
* `TaskRepository` の型（入出力がSnapshot）🔌
* InMemoryの実装（Portを満たす）🧺✅

---

## 9. AI相棒に投げるプロンプト（コピペOK）🤖✨

* 「この `TaskRepository` の入出力に、外側都合（DB/HTTP/ORM）が混ざってないか指摘して。混ざってたら“内側語彙”に直して提案して」
* 「`TaskSnapshot` の項目、最小化できる？（UseCaseから逆算して不要なら削って）」
* 「EntityとSnapshotを分けた時の、変換責務（どこに置くべきか）をこの構成で整理して」

---

次の章（第28章）は、今作ったPortが「技術用語っぽく汚れてないか」を命名・責務で磨く回だよ🧼✨
続けていこ〜！💪💖

[1]: https://github.com/microsoft/typescript/releases "Releases · microsoft/TypeScript · GitHub"
[2]: https://devblogs.microsoft.com/typescript/progress-on-typescript-7-december-2025/ "Progress on TypeScript 7 - December 2025 - TypeScript"
[3]: https://nodejs.org/en/about/previous-releases "Node.js — Node.js Releases"
[4]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-9.html?utm_source=chatgpt.com "Documentation - TypeScript 4.9"
