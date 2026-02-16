# 第25章：Repository Port設計（最小メソッド主義）🗄️✨

## この章でやりたいこと 🎯

Repository Port（＝「保存・取得ができる能力」を表すインターフェース）を、**“必要最小限”のメソッドだけで**気持ちよく設計できるようになるよ😊💕

---

## 1) Repository Portって、そもそも何？🔌

![Repository as Collection](./picture/clean_ts_study_025_repository_collection.png)

RepositoryはDDDでよく「**メモリ上のコレクションみたいに扱える**（でも実体はDBなど）」って説明されるやつだよ〜📦✨
Eric Evansの定義もまさにそのニュアンスで、「ある種類のオブジェクト全部の集合を、コレクションっぽく扱えるようにする」って感じ💡 ([Hi!][1])

そして大事なのがここ👇
Repository（のインターフェース）を置くことで、**永続化の都合を“中心”から追い出せる**こと！
Microsoftのアーキテクチャガイドでも「Repositoryは永続化の関心をドメインの外へ保つための抽象」って説明されてるよ🧼✨ ([Microsoft Learn][2])

---

## 2) 最小メソッド主義ってなに？🍱✨

![Fat vs Lean Repository](./picture/clean_ts_study_025_fat_vs_lean.png)

一言でいうと…

**「UseCaseが本当に必要な操作だけを、最小限Portにする」** だよ😊👍

逆にダメなのはこれ👇😇💥

* なんでも入った巨大Repository（いわゆる “Fat Repository”）
* 便利そうだからとCRUD全部を生やす
* 「いつか使いそう」でメソッドを増やす

Portは**差し替え口**だから、太ると差し替えが地獄になるの〜😵‍💫🌀

---

## 3) 設計手順：UseCaseから逆算する 🧭✨

![Reverse Design from UseCase](./picture/clean_ts_study_025_reverse_design.png)

Repository Portは、**DBから逆算しない**で、**UseCaseから逆算**しよ〜💕

### Step A：UseCaseの“台本”を書く 🎬

例：CompleteTask（完了）なら…

1. idでTaskを取る
2. Entityの`complete()`を呼ぶ
3. 保存する
4. 結果を返す

### Step B：台本に必要な“能力”だけを抜き出す 🧲

* 取る：`findById`
* 保存：`save`
  （Listなら `list` も要る）

### Step C：命名は“内側の言葉”で ✨

* `selectTaskByPk` ❌（SQLっぽい）
* `findById` ✅（内側の言葉）

---

## 4) Taskアプリの最小TaskRepository案（まずは3つ）✅🗄️

![Repository Port visualization with minimum methods](./picture/clean_ts_study_025_repository_design.png)


Create / Complete / List に必要な分だけに絞ると、こうなりやすいよ👇😊

```ts
// usecases/ports/TaskRepository.ts
import { Task } from "../../entities/Task";
import { TaskId } from "../../entities/TaskId";

export interface TaskRepository {
  findById(id: TaskId): Promise<Task | null>;
  save(task: Task): Promise<void>;
  list(): Promise<readonly Task[]>;
}
```

### ポイント解説 💡✨

* `findById` は **見つからない可能性**があるから `null`（ここで例外にしないのが初心者に優しい🙂）
* `save` は **作成も更新もまとめて**OK（迷いが減る！）
* `list` は **一覧に必要**だから追加（ここも最小限）

---

## 5) よくある巨大化パターン 😵‍💫➡️🧼

ありがちな太り方👇

```ts
// ❌ 太りがちな例（やらなくてOK）
export interface TaskRepositoryBad {
  create(task: Task): Promise<void>;
  update(task: Task): Promise<void>;
  delete(id: TaskId): Promise<void>;
  findAll(): Promise<Task[]>;
  findCompleted(): Promise<Task[]>;
  findIncomplete(): Promise<Task[]>;
  findByTitleLike(keyword: string): Promise<Task[]>;
  findPage(page: number, size: number): Promise<Task[]>;
  // ...まだ増える
}
```

### 直し方は2つの方向性があるよ😊✨

#### 方向性①：本当に必要になったら“その時”足す 🌱

まずは3メソッドで運用して、UseCaseが増えたら追加。

#### 方向性②：読み書きを分ける（ミニCQRS）👀✍️

![CQRS Split](./picture/clean_ts_study_025_cqrs_split.png)

「一覧の都合」が強くなってきたら、Portを分けるとスッキリしやすいよ✨

```ts
export interface TaskWriteRepository {
  findById(id: TaskId): Promise<Task | null>;
  save(task: Task): Promise<void>;
}

export interface TaskReadRepository {
  list(): Promise<readonly Task[]>;
}
```

---

## 6) “UseCaseの責務”をRepositoryに入れないでね⚠️

![Logic Leak Warning](./picture/clean_ts_study_025_logic_leak.png)

たとえば…

* `completeTask(id)` をRepositoryに置くのは基本おすすめしない🙅‍♀️
  → **完了ルール**はEntity/UseCase側の責務だよ（Repositoryは保存と取得の担当）🧠✨

Repositoryは「永続化の都合を隠す」ためのもの、って感覚が大事だよ〜🫶
（Repositoryでドメインを動かし始めると、境界が溶ける😇🫠）

---

## 7) Fakeが一瞬で作れるか？を最終チェックにしよ 🧪🎭

![Easy Fake Check](./picture/clean_ts_study_025_easy_fake.png)

Port設計が良いと、テスト用のFakeが超簡単になるよ😊✨

```ts
// test/fakes/InMemoryTaskRepository.ts
import { TaskRepository } from "../../src/usecases/ports/TaskRepository";
import { Task } from "../../src/entities/Task";
import { TaskId } from "../../src/entities/TaskId";

export class InMemoryTaskRepository implements TaskRepository {
  private store = new Map<string, Task>();

  async findById(id: TaskId): Promise<Task | null> {
    return this.store.get(id.value) ?? null;
  }

  async save(task: Task): Promise<void> {
    this.store.set(task.id.value, task);
  }

  async list(): Promise<readonly Task[]> {
    return [...this.store.values()];
  }
}
```

✅ **Fakeがスルッと書けたら勝ち**🎉
逆に、Fakeが苦しいPortは、だいたい太ってる or 技術寄りになってるサインだよ🚨

---

## 8) ミニ演習（10分）✍️💕

### お題：ListTasksに「未完了だけ」が欲しくなった！

次のどっちが良いと思う？理由も考えてみてね😊

A. `listIncomplete(): Promise<readonly Task[]>` を増やす
B. `list(filter?: { completed?: boolean }): Promise<readonly Task[]>` にする

🌟ヒント：

* UseCaseが増える未来
* Portが“クエリ置き場”になって太る未来
* UI都合が入り込む未来

---

## 9) 理解チェック（サクッと）✅📝

1. Repository PortはDB都合から作る？UseCase都合から作る？🤔
2. `findById` が見つからない時、`null`にするメリットは？
3. `completeTask(id)` をRepositoryに置きたくなった時、まず疑うべきことは？
4. Portが太ってきた時の対処を2つ言える？
5. Fakeが作れないPortの典型的な匂いは？👃💥

---

## 10) AI相棒プロンプト（コピペ用）🤖✨

* 「このUseCaseの処理手順から、Repository Portの“必要最小メソッド”を提案して。増やしすぎを検知したら理由付きで止めて」
* 「このRepository interface、Fatになりそう？その理由と改善案（分割案）を出して」
* 「このPortを満たすInMemory Fakeを最小実装で書いて。ついでにテストの観点も3つ」
* 「命名が技術寄り（SQL/ORM寄り）になってないか診断して、内側の言葉に直して」

---

## ちょい最新事情（TypeScriptまわり）⚡🧠

最近のTypeScript界隈は、ネイティブ実装（Go）へ向けた動きが大きいよ〜🏃‍♀️💨

* TypeScript 7に向けて、コンパイラ/言語サービスのネイティブ化が進んでる（大幅な高速化が狙い） ([Microsoft for Developers][3])
* ネイティブ版のプレビューも配布されてる ([Microsoft for Developers][4])

こういう変化がある時ほど、**Portを最小に保つ設計**って「将来の差し替え耐性」が効いてくるよ😊🛡️

---

## まとめ 🎀✨

* Repository Portは「保存・取得の能力」を表す差し替え口🔌
* **UseCaseから逆算**して、メソッドは最小限に🗄️
* 太ったら「必要になってから追加」or「読み書き分割」👀✍️
* Fakeがすぐ作れるか？で設計をセルフ診断🧪🎭

次の章（26）では、Clock/Idみたいな“副作用Port”を最小抽象にして、テストしやすさをさらに上げていくよ〜⏰🆔✨

[1]: https://mnapoli.fr/repository-interface?utm_source=chatgpt.com "The Repository interface"
[2]: https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/infrastructure-persistence-layer-design?utm_source=chatgpt.com "Designing the infrastructure persistence layer - .NET"
[3]: https://devblogs.microsoft.com/typescript/progress-on-typescript-7-december-2025/?utm_source=chatgpt.com "Progress on TypeScript 7 - December 2025"
[4]: https://devblogs.microsoft.com/typescript/announcing-typescript-native-previews/?utm_source=chatgpt.com "Announcing TypeScript Native Previews"
