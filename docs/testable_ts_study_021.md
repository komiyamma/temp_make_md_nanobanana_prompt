# 第21章：DB/永続化を外に押し出す🗄️🧩

![testable_ts_study_021_repository_librarian.png](./picture/testable_ts_study_021_repository_librarian.png)

この章はね、「**DBの都合でロジックがベタベタ汚れる問題**」をスパッと解決する回だよ〜！😆✨
キーワードは **Repository（リポジトリ）** 🌟

---

## 1) 今日できるようになること🎯✨* DBアクセス（SQL/ORM）

を **中心（ロジック）から追い出す** 🚪💨


* 中心は **DBの存在を知らない** まま動くようにする🙈✨
* テストは **爆速**（DBなしユニットテスト中心）にする⚡🧪
* DBは **差し替え可能**（SQLite→Postgresでも中心は無傷）🔁🧩

---

## 2) なんでDBが中心にいるとツラいの？😵‍💫🌀中心コードの中に…



* SQLが混ざる🧂
* ORMの型が混ざる🧱
* トランザクションや接続管理が混ざる🔌
* DBの都合（null/型/命名）が混ざる🧟‍♀️

こうなると、**テストが遅い・壊れやすい・変更が怖い** が一気に来るよね😭

だから方針はこれ👇

* **中心**：ビジネスルール（純粋ロジック）🍰
* **外側**：DBやSQL、接続、永続化の事情🗄️
* **境界**：Repository interface（最小の約束）📜✨

---

## 3) Repositoryは「永続化の窓口」🚪

📌Repositoryは、ざっくり言うと

> 「保存・取得の“操作だけ”を約束するインターフェース」

だよ😊✨
**中心はRepository“だけ”を知って、DBのことは一切知らない**のがポイント！

---

## 4) ハンズオン題材：Todoを保存したい📝

💖やることはシンプル！



* Todoを追加する➕
* Todoを取得する🔎
* Todo一覧を見る📚

**中心はルールだけ**にしたいので、DBの話は外側へ🗄️➡️🚪

---

## 5) ファイル構成イメージ📁✨

こんな感じに分けると迷子になりにくいよ〜😊



* `src/domain/`：ドメイン（型・ルール）🍰
* `src/usecases/`：ユースケース（やりたいこと）🎮
* `src/ports/`：境界（interface）📜
* `src/adapters/`：外側（DB実装・インメモリ実装）🧩
* `src/main.ts`：組み立て場所（Composition Root）🏗️

---

## 6) 中心：ドメインを作る🍰✨

まず中心は「DBなんて知らない世界」を作ろう😆



```ts
// src/domain/todo.ts
export type TodoId = string;

export type Todo = Readonly<{
  id: TodoId;
  title: string;
  done: boolean;
}>;

export function createTodo(id: TodoId, title: string): Todo {
  const t = title.trim();
  if (t.length === 0) throw new Error("タイトルは必須だよ🥺");
  if (t.length > 40) throw new Error("タイトル長すぎ！40文字までね✂️");

  return { id, title: t, done: false };
}
```

---

## 7) 境界：Repository interfaceを作る📜🧩

「必要な操作だけ」ね！✨（ここ超大事）



```ts
// src/ports/todoRepository.ts
import type { Todo, TodoId } from "../domain/todo.js";

export interface TodoRepository {
  save(todo: Todo): Promise<void>;
  findById(id: TodoId): Promise<Todo | null>;
  list(): Promise<Todo[]>;
}
```

✅ **ここにSQLの匂いを入れない**（where とか join とか言い出すと危険👃💨）

---

## 8) 中心：ユースケースを書く🎮✨

ユースケースはRepositoryを使うだけ！DBの話ゼロ！😆



```ts
// src/usecases/addTodo.ts
import { createTodo } from "../domain/todo.js";
import type { TodoRepository } from "../ports/todoRepository.js";

export async function addTodo(
  repo: TodoRepository,
  id: string,
  title: string,
): Promise<void> {
  const todo = createTodo(id, title);
  await repo.save(todo);
}
```

---

## 9) テスト用：インメモリRepositoryを作る🧸⚡ここが気持ちいいポイント！
DBなしでテストできるから **速い・安定・ラク** 😇✨

```ts
// src/adapters/inMemoryTodoRepository.ts
import type { Todo, TodoId } from "../domain/todo.js";
import type { TodoRepository } from "../ports/todoRepository.js";

export class InMemoryTodoRepository implements TodoRepository {
  private map = new Map<TodoId, Todo>();

  async save(todo: Todo): Promise<void> {
    this.map.set(todo.id, todo);
  }

  async findById(id: TodoId): Promise<Todo | null> {
    return this.map.get(id) ?? null;
  }

  async list(): Promise<Todo[]> {
    return [...this.map.values()];
  }
}
```

---

## 10) ユースケースのユニットテスト🧪🎉Vitestは最近 **Vitest 4** が出てるよ〜（2025-10-22）

📣✨ ([Vitest][1])



```ts
// test/addTodo.test.ts
import { describe, it, expect } from "vitest";
import { InMemoryTodoRepository } from "../src/adapters/inMemoryTodoRepository.js";
import { addTodo } from "../src/usecases/addTodo.js";

describe("addTodo", () => {
  it("タイトルが保存される🎀", async () => {
    const repo = new InMemoryTodoRepository();

    await addTodo(repo, "t1", "牛乳を買う");

    const saved = await repo.findById("t1");
    expect(saved?.title).toBe("牛乳を買う");
    expect(saved?.done).toBe(false);
  });

  it("空タイトルはエラー🥺", async () => {
    const repo = new InMemoryTodoRepository();

    await expect(addTodo(repo, "t2", "   ")).rejects.toThrow();
  });
});
```

ここまでで、**中心はDBなしで完全に守れる** よ！最強〜⚡🧪

---

## 11) 外側：SQLiteで永続化するAdapterを書く🗄️

🧩ここからDBの話！でも **外側だけ** だよ😊✨



### Nodeの `node:sqlite` ってどうなの？🧠Nodeには `node:sqlite` が入っていて、SQLiteを扱えるよ〜！
ただし **まだ experimental（開発中）** 扱いだよ📌 ([Node.js][2])

* Node v22系のドキュメントでは `--experimental-sqlite` が必要って書いてある版もあるよ ([Node.js][3])
* 新しめのNodeドキュメントでは「フラグ不要になったけど experimental」は継続、って流れだよ ([Node.js][2])

（この章の学習にはちょうどいい✨ 依存追加いらないのが楽だしね😆）

---

## 12) SQLite Repository実装例🧩

🗄️

```ts
// src/adapters/sqliteTodoRepository.ts
import { DatabaseSync } from "node:sqlite";
import type { Todo, TodoId } from "../domain/todo.js";
import type { TodoRepository } from "../ports/todoRepository.js";

function toRow(todo: Todo) {
  return {
    id: todo.id,
    title: todo.title,
    done: todo.done ? 1 : 0,
  };
}

function toDomain(row: any): Todo {
  return {
    id: row.id as TodoId,
    title: row.title as string,
    done: row.done === 1,
  };
}

export class SqliteTodoRepository implements TodoRepository {
  private db: DatabaseSync;

  constructor(dbFile: string) {
    this.db = new DatabaseSync(dbFile);
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS todos (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        done INTEGER NOT NULL
      );
    `);
  }

  async save(todo: Todo): Promise<void> {
    const r = toRow(todo);
    const stmt = this.db.prepare(`
      INSERT INTO todos (id, title, done)
      VALUES (?, ?, ?)
      ON CONFLICT(id) DO UPDATE SET title=excluded.title, done=excluded.done
    `);
    stmt.run(r.id, r.title, r.done);
  }

  async findById(id: TodoId): Promise<Todo | null> {
    const stmt = this.db.prepare(`SELECT id, title, done FROM todos WHERE id = ?`);
    const row = stmt.get(id);
    return row ? toDomain(row) : null;
  }

  async list(): Promise<Todo[]> {
    const stmt = this.db.prepare(`SELECT id, title, done FROM todos ORDER BY id`);
    const rows = stmt.all();
    return rows.map(toDomain);
  }
}
```

🌟ポイント

* SQL・テーブル構造・数値/boolean変換は **全部ここ（外側）** 🧩
* 中心は `TodoRepository` だけ知ってればOK💖

---

## 13) 組み立て場所で接続する🏗️

🔌中心と外側を“結婚”させるのは **mainだけ** 👰‍♀️🤵‍♂️✨



```ts
// src/main.ts
import { SqliteTodoRepository } from "./adapters/sqliteTodoRepository.js";
import { addTodo } from "./usecases/addTodo.js";

async function main() {
  const repo = new SqliteTodoRepository("app.db");

  await addTodo(repo, "t1", "レポート提出📄");
  await addTodo(repo, "t2", "お昼ごはん🍙");

  console.log(await repo.list());
}

main();
```

---

## 14) 外側のテストは「最小限」がおすすめ🔌🧪中心はユニットでガチガチに守ったから、外側は



* SQLが正しいか
* 変換（row↔domain）が合ってるか

だけを **少数の結合テスト** で確認すればOK😊✨

```ts
// test/sqliteRepo.test.ts
import { describe, it, expect } from "vitest";
import { SqliteTodoRepository } from "../src/adapters/sqliteTodoRepository.js";

describe("SqliteTodoRepository", () => {
  it("保存して取得できる🗄️✨", async () => {
    const repo = new SqliteTodoRepository(":memory:");

    await repo.save({ id: "t1", title: "ねこにごはん🐱", done: false });

    const got = await repo.findById("t1");
    expect(got?.title).toBe("ねこにごはん🐱");
    expect(got?.done).toBe(false);
  });
});
```

`:memory:` で一瞬で終わるの気持ちいい〜⚡😆

---

## 15) よくあるミス集👃

💨 → 直し方🛠️✨### ❌ ユースケース内にSQLを書く➡️ ✅ Repositoryへ追い出す🧩



### ❌ Repositoryが「なんでも屋」になる（where/join渡し始める）

➡️ ✅ **ユースケースが必要な操作だけ**に絞る✂️✨

### ❌ ORM/DBの型を中心へ持ち込む（Row型が漏れる）

➡️ ✅ 変換はAdapter内で完結させる🔁💎



### ❌ テストが全部DB結合テスト➡️ ✅ 中心はインメモリ差し替えでユニット中心に⚡🧪

---

## 16) AI拡張の使いどころ🤖🎀### 使うと速い✨* Repository interface案を出させる📜


* インメモリ実装の雛形を作らせる🧸
* テストケースの洗い出しをさせる🧪

### 使うと危険⚠️* 「DBの都合」を中心へ混ぜた設計を平気で出す😇（それっぽいけど地雷💣）



#### おすすめプロンプト例💬✨* 「`TodoRepository` をユースケース（追加/取得/一覧）

に必要最小限の操作だけで設計して。SQLやORM型は漏らさないで」


* 「インメモリ実装をMapで。ユニットテストしやすい形にして」

---

## 17) 演習🎓🌈### 演習1：完了にするユースケース✅* `completeTodo(repo, id)` を作る


* すでに `done=true` ならエラーにする😤
* ユニットテストはインメモリで🧪✨

### 演習2：Repositoryを増やさずに対応する🧠* `list()` を使って「未完了だけ表示」を中心でやってみよう（小規模ならOK）

🙂


* 大規模なら「検索操作」追加もありだけど、**必要になってから**でOK（YAGNIっぽくね😉）

---

## 18) まとめ✅🎀* DBはI/Oだから **外側へ** 🗄️

➡️🚪


* 中心は **Repository interfaceだけ**を知る📜✨
* テストは **インメモリ差し替え**で爆速⚡🧪
* 外側は **最小限の結合テスト**でOK🔌🙂

おつかれさま〜！第21章で、いよいよ「DBの変更が怖くない」世界が見えてきたよ😆🌟

---

### ちょいメモ：最新版の根拠（さらっと）

📌✨* TypeScript 5.9 は公式でアナウンス済み（2025-08-01公開） ([Microsoft for Developers][4])


* Nodeは 2026年1月時点で v24 がActive LTS、v22がMaintenance LTS（公式のリリース一覧） ([Node.js][5])
* `node:sqlite` は experimental（ただし最近のドキュメントでフラグ周りが更新されてる流れ） ([Node.js][2])

[1]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
[2]: https://nodejs.org/api/sqlite.html?utm_source=chatgpt.com "SQLite | Node.js v25.3.0 Documentation"
[3]: https://nodejs.org/download/release/v22.9.0/docs/api/sqlite.html?utm_source=chatgpt.com "SQLite | Node.js v22.9.0 Documentation"
[4]: https://devblogs.microsoft.com/typescript/announcing-typescript-5-9/?utm_source=chatgpt.com "Announcing TypeScript 5.9"
[5]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
