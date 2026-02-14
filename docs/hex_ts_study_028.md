# 第28章：Adapterが薄いかチェック（太ったら負け）🥗⚠️

![hex_ts_study_028[(./picture/hex_ts_study_028_thin_adapter_principle.png)

（テーマ：**「Adapterは翻訳係。ルールを抱えたら負け」**😇🔌🧩）

---

### 0. まず結論：Adapterの仕事はコレだけ！🧩✨

Adapterは **「外の世界 ↔ 中心（Port）」の翻訳**をする係だよ〜📮🔁

* 外部の形式（JSON/HTTP/ファイル/DB/CLI引数…）を **中心が欲しい形に変換**
* 中心の返した結果を **外部が欲しい形に変換**
* 外部I/Oの失敗（ファイル読めない等）を **中心に渡せる失敗に整形**

この「変換器」の説明は、提唱者のCockburnの説明そのものだよ（Adapterは外部の信号とPortのAPIを相互変換する係）([アリステア・コックバーン][1])

---

## 1. なぜ「太ったAdapter」は危険なの？😵‍💫💥

ヘキサゴナルの大事な狙いは **中心（ドメイン/ユースケース）を外部から隔離**して、差し替え＆テストを楽にすること。([アリステア・コックバーン][1])
依存の向きも「UI → domain ← data source」みたいに、外側が中心に寄るのがポイントだよね🧭([martinfowler.com][2])

でもAdapterが太ると…👇😱

* ルールが外に漏れる → **中心がスカスカ**になる🥲
* 入口（CLI→HTTP）を変えたら壊れる → **差し替えが地獄**🔥
* テストがAdapter都合になる → **遅い/不安定/書きにくい**🧪💦

Cockburnも「内側のコードが外に漏れる」ことが根本原因だって指摘してるよ🛡️([アリステア・コックバーン][1])

---

## 2. 「太ったAdapter」判定：3秒チェック⏱️👀

Adapterの中に、こんなのが出てきたら黄色信号〜⚠️

### NGワード（＝ルール臭）🚫

* 「タイトル空はダメ」
* 「完了は二重適用禁止」
* 「この状態のときだけ〜」
* 「○○ならポイント加算」
* 「期限切れなら失敗」

👉 それ **中心（ドメイン/ユースケース）の仕事**！🧠❤️

### NG構造（＝太りやすい形）🍔🐘

* 巨大if / switchが増殖
* 「保存するだけ」のはずが、いつの間にか**状態遷移**してる
* DTO変換のついでに**業務チェック**してる
* “便利だから”でユースケース相当の処理が入ってる

---

## 3. Adapterに置いていいもの / ダメなもの ✅🚫

迷ったらこの仕分けでOKだよ〜🥳

### ✅ 置いていい（Adapterの本業）🧩

* 形式変換：CLI引数 → 入力DTO、Domain → JSONなど🔁
* プロトコル変換：HTTP/ファイル/DBの読み書き🌐💾
* 例外の整形：fsの例外 → 「外部I/O失敗」みたいに包む🎁
* ログ：I/Oの開始・成功・失敗を記録🪪📊（中心は静かに）
* リトライやタイムアウト（外部都合の制御）⏳🔁

### 🚫 置いちゃダメ（中心の仕事）🛡️

* 業務ルール（不変条件、状態遷移、仕様判断）
* ユースケースの手順（AしてBしてCして…）
* 「この仕様ならこう」みたいな判断の塊

---

## 4. 実例：太ったFileRepository（やりがち！）📄💾😇

「FileTodoRepositoryAdapter（JSON保存）」で、ついこうなりがち👇

```ts
// adapters/outbound/FileTodoRepositoryAdapter.ts（悪い例💥）
import { promises as fs } from "node:fs";
import path from "node:path";

type PersistedTodo = { id: string; title: string; completed: boolean };

export class FileTodoRepositoryAdapter {
  constructor(private readonly filePath = path.join(process.cwd(), "todos.json")) {}

  async add(title: string) {
    // ❌ ルールが混入：タイトル空禁止（本当は中心）
    if (!title || title.trim() === "") {
      throw new Error("title must not be empty");
    }

    const todos = await this.load();

    // ❌ ルールが混入：重複タイトル禁止（本当は中心）
    if (todos.some(t => t.title === title.trim())) {
      throw new Error("duplicated title");
    }

    const todo: PersistedTodo = {
      id: crypto.randomUUID(),
      title: title.trim(),
      completed: false,
    };

    todos.push(todo);
    await this.save(todos);
    return todo;
  }

  async complete(id: string) {
    const todos = await this.load();
    const t = todos.find(x => x.id === id);
    if (!t) throw new Error("not found");

    // ❌ ルールが混入：完了二重適用禁止（本当は中心）
    if (t.completed) throw new Error("already completed");

    t.completed = true; // ❌ 状態遷移をAdapterでやってる
    await this.save(todos);
    return t;
  }

  async list() {
    return this.load();
  }

  private async load(): Promise<PersistedTodo[]> {
    try {
      const txt = await fs.readFile(this.filePath, "utf-8");
      return JSON.parse(txt);
    } catch (e: any) {
      if (e?.code === "ENOENT") return [];
      throw e;
    }
  }

  private async save(todos: PersistedTodo[]) {
    await fs.writeFile(this.filePath, JSON.stringify(todos, null, 2), "utf-8");
  }
}
```

これ、動くけど…
**AddTodo/CompleteTodo/ListTodos** が存在するのに、Repositoryがユースケース化してるよね🍔😵‍💫
結果：中心が弱くなって、入口差し替え（CLI→HTTP）でつらくなるやつ💦

---

## 5. 正しい分離：ルールは中心へ、Adapterは翻訳へ🛡️✨

ここから「ダイエット」するよ〜🥗💪

### 5-1. ルールはドメイン（Todo）へ🧠❤️

```ts
// domain/Todo.ts
export class DomainError extends Error {}

export class Todo {
  private constructor(
    public readonly id: string,
    public readonly title: string,
    public readonly completed: boolean,
  ) {}

  static createNew(id: string, title: string): Todo {
    const t = title.trim();
    if (t.length === 0) throw new DomainError("タイトルは空にできません");
    return new Todo(id, t, false);
  }

  // 永続化から復元（基本は同じ不変条件を守る）
  static rehydrate(id: string, title: string, completed: boolean): Todo {
    const t = title.trim();
    if (t.length === 0) throw new DomainError("保存データが壊れてます（title空）");
    return new Todo(id, t, completed);
  }

  complete(): Todo {
    if (this.completed) throw new DomainError("完了の二重適用はできません");
    return new Todo(this.id, this.title, true);
  }
}
```

### 5-2. 手順はユースケースへ🎮➡️🧠

```ts
// app/ports/TodoRepositoryPort.ts
import { Todo } from "../../domain/Todo";

export interface TodoRepositoryPort {
  list(): Promise<Todo[]>;
  saveAll(todos: Todo[]): Promise<void>;
}
```

```ts
// app/usecases/AddTodo.ts
import { Todo } from "../../domain/Todo";
import type { TodoRepositoryPort } from "../ports/TodoRepositoryPort";

export class AddTodo {
  constructor(
    private readonly repo: TodoRepositoryPort,
    private readonly makeId: () => string, // UUIDなどは外へ🔌
  ) {}

  async execute(title: string): Promise<Todo> {
    const todos = await this.repo.list();
    const todo = Todo.createNew(this.makeId(), title);

    // （もし「重複タイトル禁止」が仕様なら、ここで判断するのが自然✨）
    // if (todos.some(t => t.title === todo.title)) throw new DomainError("重複タイトル");

    await this.repo.saveAll([...todos, todo]);
    return todo;
  }
}
```

```ts
// app/usecases/CompleteTodo.ts
import { DomainError } from "../../domain/Todo";
import type { TodoRepositoryPort } from "../ports/TodoRepositoryPort";

export class CompleteTodo {
  constructor(private readonly repo: TodoRepositoryPort) {}

  async execute(id: string) {
    const todos = await this.repo.list();
    const idx = todos.findIndex(t => t.id === id);
    if (idx < 0) throw new DomainError("対象のTodoがありません");

    const updated = todos[idx].complete();
    const next = [...todos];
    next[idx] = updated;

    await this.repo.saveAll(next);
    return updated;
  }
}
```

### 5-3. Adapterは「読み書き＋変換＋例外整形」だけ📄🧩

```ts
// adapters/outbound/FileTodoRepositoryAdapter.ts（良い例✨）
import { promises as fs } from "node:fs";
import path from "node:path";
import { Todo } from "../../domain/Todo";
import type { TodoRepositoryPort } from "../../app/ports/TodoRepositoryPort";

type PersistedTodo = { id: string; title: string; completed: boolean };

export class InfrastructureError extends Error {}

export class FileTodoRepositoryAdapter implements TodoRepositoryPort {
  constructor(private readonly filePath = path.join(process.cwd(), "todos.json")) {}

  async list(): Promise<Todo[]> {
    const raw = await this.loadPersisted();
    // ✅ 変換はOK（永続形式 → ドメイン）
    return raw.map(r => Todo.rehydrate(r.id, r.title, r.completed));
  }

  async saveAll(todos: Todo[]): Promise<void> {
    const raw: PersistedTodo[] = todos.map(t => ({
      id: t.id,
      title: t.title,
      completed: t.completed,
    }));
    await this.savePersisted(raw);
  }

  private async loadPersisted(): Promise<PersistedTodo[]> {
    try {
      const txt = await fs.readFile(this.filePath, "utf-8");
      const data = JSON.parse(txt);
      if (!Array.isArray(data)) throw new InfrastructureError("保存形式が不正です");
      return data as PersistedTodo[];
    } catch (e: any) {
      if (e?.code === "ENOENT") return []; // ✅ これはI/O都合の扱い（OK）
      throw new InfrastructureError(`ファイル読み込み失敗: ${String(e?.message ?? e)}`);
    }
  }

  private async savePersisted(raw: PersistedTodo[]): Promise<void> {
    try {
      await fs.writeFile(this.filePath, JSON.stringify(raw, null, 2), "utf-8");
    } catch (e: any) {
      throw new InfrastructureError(`ファイル書き込み失敗: ${String(e?.message ?? e)}`);
    }
  }
}
```

💡ここが気持ちいいポイント😊💕

* ルールは全部「中心」に集まる🧠
* Adapterは薄いまま（変換＋I/Oだけ）🥗
* 入口をHTTPに変えても、中心は無傷でいける🌐✨

---

## 6. 「薄さ」を守るためのチェックリスト🥗✅

開発中に、Adapterを見たらこれチェックしてね〜👀✨

### ✅ Adapterが薄いサイン

* 関数名が「load/save/parse/serialize/map」っぽい🔁
* if文が「I/O都合（ENOENT、timeout、HTTP 500）」中心⛔🌐
* ドメイン用語（完了/二重適用/割引/上限…）がほぼ出ない🙆‍♀️
* 1メソッドが短い（呼んで返すだけ）📦

### ⚠️ 太り始めサイン

* 「仕様の文章」がコードに見える（例：完了は二重適用禁止）📜😱
* adapterにテストを書いてるのに、仕様テストになってる🧪💥
* adapterの修正でユースケースが壊れる🔁💔

---

## 7. どうやって「ダイエット」する？手順書🔧📌

太ってても大丈夫！この順で痩せるよ〜🥳

1. Adapterのif文を全部ハイライト🖍️
2. 「I/O都合」か「仕様判断」かに仕分け📦
3. 仕様判断は、まずユースケースへ移動🎮
4. “状態遷移”はドメインメソッドへ移動🧠
5. Adapterに残るのは「変換・呼び出し・例外ラップ」だけ🧩
6. 中心のユースケース単体テストで守る🧪🛡️

---

## 8. AI拡張に頼るならここ🤖✨（そのままコピペOK）

### 8-1. Adapter肥満チェック用プロンプト🍔➡️🥗

```text
この TypeScript ファイルは Ports & Adapters の Adapter です。
「業務ルール（不変条件・状態遷移・仕様判断）」が紛れ込んでいないかレビューしてください。

- “変換・呼び出し・例外ラップ” 以外の責務があれば指摘
- 指摘ごとに「どこへ移すべきか」（domain / usecase / adapter のどれか）も提案
- 最後に「薄くするための最小リファクタ手順」を箇条書きで
```

### 8-2. 移動先迷子用プロンプト🧭✨

```text
以下の処理は「domain」「usecase」「adapter」のどこに置くべき？
理由も一言で。

処理: （ここに該当コードを貼る）
判断基準:
- 仕様判断/状態遷移 → domain or usecase
- 外部I/O都合 → adapter
- 変換だけ → adapter（ただし仕様判断は含めない）
```

---

## 9. 2026ミニ最新メモ（チラ見でOK）🗞️✨

* Node.js は v24 が Active LTS、v25 が Current になってるよ〜🟢([nodejs.org][3])
* TypeScript は GitHub上で 5.9.3 が Latest として表示されてるよ📌([GitHub][4])
* TypeScript 5.9 は「tsc --init の内容見直し」や「--module node20 の安定オプション」など、設定まわりもアップデートされてるよ🛠️([Microsoft for Developers][5])

（ここは章の主役じゃないけど、「今の空気感」として置いとくね😊）

---

## 10. まとめ：今日の合言葉🥗🔌🧩

* Adapterは **翻訳だけ**🧩✨
* ルールは **中心へ集める**🧠❤️
* 太ったら、**if文の仕分け → 移動** で痩せる🥗💪

次の章でHTTP入口を足すとき、ここができてると「中心そのまま」でスッ…と差し替えできて超気持ちいいよ〜🌐😊💕

[1]: https://alistair.cockburn.us/hexagonal-architecture "hexagonal-architecture"
[2]: https://martinfowler.com/articles/badri-hexagonal/ "Badri on Hexagonal Rails"
[3]: https://nodejs.org/en/about/previous-releases "Node.js — Node.js Releases"
[4]: https://github.com/microsoft/typescript/releases "Releases · microsoft/TypeScript · GitHub"
[5]: https://devblogs.microsoft.com/typescript/announcing-typescript-5-9/ "Announcing TypeScript 5.9 - TypeScript"
