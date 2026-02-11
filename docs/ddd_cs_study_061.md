# 第61章：アプリケーションサービス（ユースケースを実現する層）🧩✨

![アプリケーションサービス（ユースケースを実現する層）](./picture/ddd_cs_study_061_app_service.png)

DDDって聞くと「値オブジェクト！集約！リポジトリ！」ってパーツに目が行きがちなんだけど…
実はそれらを **“ちゃんと動くアプリ” にまとめ上げる司令塔** が必要なんだよね🙂‍↕️🚦

それが **アプリケーションサービス**（Application Service）だよ〜！🎉

---

## 1. アプリケーションサービスって何する人？👩‍💼🧠

![061_commander](./picture/ddd_cs_study_061_commander.png)

一言でいうと、

**「ユーザーがやりたいこと（ユースケース）」を、ドメインの部品を使って実現する係** ✅

たとえばユースケースってこういうやつ👇

* 会員登録する 📝
* 商品を注文する 🛒
* タスクを追加する ✅
* 予約をキャンセルする 📅❌

アプリケーションサービスは **“手順を組み立てる人”** で、
**ビジネスルールそのものは、できるだけドメイン（Entity/VO/Aggregate）に持たせる** のがコツだよ🙂✨

---

## 2. どこまでが担当？（超重要）🧭

![061_responsibility](./picture/ddd_cs_study_061_responsibility.png)

アプリケーションサービスの担当はだいたいこれ👇

* 入力（Command/DTO）を受け取る 📩
* 必要な集約をリポジトリから取ってくる 🔍
* 集約に「命令」する（メソッド呼ぶ）📣
* 保存する 💾
* 必要なら通知する（ドメインイベント発火後の処理など）📢
* 結果（DTO/Result）を返す 🎁

逆に、**やりすぎ注意**なのはこれ👇⚠️

* `if` だらけでビジネスルールを書き始める（ドメインが空っぽになる）😵‍💫
* DBのSQLやEFの細かい都合が漏れる（アプリ層がインフラに汚染される）🧪
* “神クラス” 化して巨大になる（何でも屋になる）🧟‍♂️

---

## 3. ありがちな混乱ポイント（ここで整理）🧹✨

![061_confusion_points](./picture/ddd_cs_study_061_confusion_points.png)

### ✅ Controller（画面・APIの入り口）

* HTTPとか画面の都合を扱う係 🌐
* できれば薄くする（受付→サービス呼ぶだけ）🍃

### ✅ Application Service（今回の主役）

* ユースケースを実現する係 🎮
* “手順” を書く（オーケストレーション）🎻

### ✅ Domain（Entity/VO/Aggregate/Domain Service）

* ルールを守らせる係 🧠
* “正しさ” の中心 ❤️

### ✅ Infrastructure（DBや外部API）

* 現実の道具を扱う係 🛠️
* 交換可能にしておきたい 🔁

---

## 4. ミニ例で体感しよう：タスクを追加する ✅📝

![061_task_add_flow](./picture/ddd_cs_study_061_task_add_flow.png)

「タスク管理アプリ」で、ユーザーがやりたいことは

> 「タスクを追加したい！」

だよね🙂
これをDDDっぽく分けるとこうなるよ👇

* Domain：`TodoList` 集約が「タスク追加」を正しく処理する ✅
* Application：`AddTask` の手順（取得→命令→保存）を書く 🧭
* Infrastructure：保存先（DBとか）💾
* Web：APIや画面 🌐
 
 ```mermaid
 sequenceDiagram
    participant User
    participant App as Application<br/>(司令塔)
    participant Repo as Repository
    participant Dom as Domain<br/>(TodoList)
    
    User->>App: 「タスク追加して！」(Command)
    
    App->>Repo: 1. 取得 (GetById)
    Repo-->>App: TodoList
    
    App->>Dom: 2. 命令 (AddTask)
    Dom-->>Dom: ルール確認✅<br/>(文字数など)
    
    App->>Repo: 3. 保存 (Save)
    
    App-->>User: 完了報告🎁
 ```
 
 ---

## 5. コード例：薄いアプリケーションサービスの正解形🌸

![061_thin_service](./picture/ddd_cs_study_061_thin_service.png)

### Domain（集約）側：ルールはこっちに寄せる🧠

```csharp
public sealed class TodoList
{
    private readonly List<TodoItem> _items = new();

    public Guid Id { get; }
    public IReadOnlyList<TodoItem> Items => _items;

    public TodoList(Guid id) => Id = id;

    public Result AddTask(string title)
    {
        if (string.IsNullOrWhiteSpace(title))
            return Result.Fail("タイトルは必須だよ🥺");

        if (title.Length > 50)
            return Result.Fail("タイトルは50文字までだよ✂️");

        _items.Add(new TodoItem(Guid.NewGuid(), title.Trim(), isDone: false));
        return Result.Ok();
    }
}

public sealed record TodoItem(Guid Id, string Title, bool IsDone);
```

> 注目ポイント👀✨
> 「タイトル必須」とか「50文字まで」は **ドメインの責任** にしてるよ！

---

### Application（アプリケーションサービス）側：手順を書く🚦

```csharp
public sealed class TodoApplicationService
{
    private readonly ITodoListRepository _repo;

    public TodoApplicationService(ITodoListRepository repo)
        => _repo = repo;

    public async Task<Result> AddTaskAsync(AddTaskCommand command, CancellationToken ct)
    {
        // 1) 対象の集約を取得する
        var list = await _repo.GetByIdAsync(command.TodoListId, ct);
        if (list is null)
            return Result.Fail("対象のリストが見つからないよ😢");

        // 2) 集約に命令する（ルール判断はドメイン側）
        var result = list.AddTask(command.Title);
        if (!result.IsSuccess)
            return result;

        // 3) 保存する
        await _repo.SaveAsync(list, ct);

        // 4) 結果を返す
        return Result.Ok();
    }
}

public sealed record AddTaskCommand(Guid TodoListId, string Title);
```

> ここが超大事💡
> アプリケーションサービスは **薄い**！
> `list.AddTask(...)` に命令して、結果見て、保存してるだけ🙂‍↕️✨

---

### Repository（インターフェイスだけ）🧱

```csharp
public interface ITodoListRepository
{
    Task<TodoList?> GetByIdAsync(Guid id, CancellationToken ct);
    Task SaveAsync(TodoList list, CancellationToken ct);
}
```

---

### Result（超ミニ版）🎁

```csharp
public sealed class Result
{
    public bool IsSuccess { get; }
    public string? Error { get; }

    private Result(bool isSuccess, string? error)
        => (IsSuccess, Error) = (isSuccess, error);

    public static Result Ok() => new(true, null);
    public static Result Fail(string error) => new(false, error);
}
```

---

## 6. 「薄さ」を守るためのチェックリスト✅✨

![061_checklist](./picture/ddd_cs_study_061_checklist.png)

アプリケーションサービスを書いたら、これ見てね🙂

* [ ] ルールの`if`が大量にない？（ドメインに寄せられるかも）🧠
* [ ] “取得→命令→保存” になってる？🚦
* [ ] DB都合（EFのEntity直触り等）が漏れてない？🧪
* [ ] メソッド名がユースケースになってる？（例：`AddTask`）📝
* [ ] 1メソッドが長編小説になってない？📚💥

---

## 7. AIに手伝ってもらうコツ（めちゃ相性いい）🤖💕

アプリケーションサービスは「手順」が中心だから、AIがかなり得意だよ！

こんな感じで頼むと気持ちよく出る🙂✨

* 「**アプリケーションサービスは薄く**、取得→命令→保存で」
* 「**ビジネスルールはドメイン側**に寄せて」
* 「失敗は `Result` で返して、例外乱発しないで」
* 「Command/DTOを作って」

プロンプト例👇

```text
TodoList集約に AddTask(title) がある前提で、
アプリケーションサービス AddTaskAsync を作って。
責務は「取得→命令→保存」で薄く。
失敗は Result で返して。
```

---

## 8. ミニ演習🎯✅（すぐできる！）

次のユースケースを、同じ形で作ってみてね😊💕

### お題A：タスク完了にする ✅

* `TodoList` に `CompleteTask(taskId)` を追加
* Application Service に `CompleteTaskAsync(command)` を追加

### お題B：タスク名を変更する ✏️

* `RenameTask(taskId, newTitle)`
* 文字数チェックなどのルールはドメイン側へ🧠

---

## まとめ🌟

* アプリケーションサービスは **ユースケースの司令塔** 🚦
* 仕事はだいたい **取得→命令→保存** 🧭
* **ルールはドメインに寄せる**（アプリ層は薄く！）🧠✨
* AIに頼むなら「薄く！ルールはドメイン！」って言うのが勝ち🤖🏆

---

次の第62章（DTO）に行くと、
「画面に返す形」と「ドメインの形」をもっとキレイに分けられて、気持ちよさが倍増するよ〜🥰📦
