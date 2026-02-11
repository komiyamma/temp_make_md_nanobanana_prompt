# 第62章：DTO（Data Transfer Object）✨ 〜 画面に出すデータと、内部のデータを分ける理由 〜 📦🧠

![DTO（Data Transfer Object）](./picture/ddd_cs_study_062_dto_box.png)

### 今日のゴール 🎯

* DTOが「何のためにいるのか」をスッキリ理解する 😌✨
* 「ドメインのオブジェクトをそのまま返しちゃダメな理由」が腹落ちする 🙅‍♀️
* ASP.NET Coreでよくある形（Request/Response DTO）を作れるようになる 💪😊

---

## 1) DTOってなに？🤔📦

DTOはひとことで言うと、

> **「データの受け渡し専用の、軽い入れ物」** 🧺✨

* 画面（APIのレスポンス）に返す用
* 画面（APIのリクエスト）から受け取る用

つまり **“運ぶための箱”** です📦🚚
**ビジネスルール（正しさの判断）を持たせない** のが超大事ポイントです❗️

---

## 2) なんで分けるの？（超重要）🔥

「ドメインのクラスをそのまま画面に返せば早くない？」って思いがちですが…
分けないと、未来の自分が泣きます😭💥

### 理由A：画面に合わせると、ドメインが汚れる 😵‍💫🌀

画面は都合がコロコロ変わります📱🖥️

* 一覧では「名前だけ」
* 詳細では「住所も電話も」
* 管理画面では「内部フラグも」

この“画面都合”をドメインに混ぜると、
**ドメインが「画面の奴隷」**になります🥲⛓️

👉 DTOを使うと、**画面の形はDTOで自由に変えてOK** ✨
ドメインはビジネスに集中できます🧠💎

---

### 理由B：セキュリティ（勝手に更新される）事故を防ぐ 🛡️😱

「更新API」で、受け取ったJSONをそのままエンティティに当てると…

* ユーザーが送ってはいけない項目まで送れてしまう
  （例：`IsAdmin=true` とか…😱）

DTOにすると
✅ 受け取っていい項目だけを定義できる
→ **“危険な項目は存在しない”** 状態にできます🔒✨

---

### 理由C：外に出したくない情報を漏らさない 🙈💦

ドメインのエンティティには内部用の情報が混ざりがちです。

* 内部メモ
* 非公開フラグ
* 個人情報の元データ
* 監査用の値（CreatedBy とか）

DTOなら、**公開していい形だけ**を返せます✨

---

### 理由D：シリアライズ地獄（循環参照・巨大レスポンス）を避ける 🌀😇

ドメインやEFのエンティティをそのまま返すと
「関係が辿れて無限に膨らむ」みたいな事故が起きがちです😵‍💫
DTOは必要な形だけに固定できるので安心です👌✨

---

## 3) DTOはどこに置く？🏠📁

ざっくりおすすめはこの2種類です😊

* **Request DTO（入力）**：Web層（API）側に置くことが多い
* **Response DTO（出力）**：Application層に置くことが多い

  * 「このユースケースはこの形で返す！」が明確になるから✨

※プロジェクトの流儀で変えてOKです🙆‍♀️
大事なのは **ドメイン層にDTOを持ち込まない** ことが多いです（混ざりやすいから）⚠️

---

## 4) 例で理解しよ！「ユーザー登録」🧑‍💻✨

### ドメイン側（ルールの世界）🧠

* `Email` は値オブジェクトで「正しい形式じゃないと生まれない」
* `User` は「ビジネス的に意味のある存在」

```csharp
// Domain
public sealed record Email
{
    public string Value { get; }
    private Email(string value) => Value = value;

    public static Email Create(string value)
    {
        if (string.IsNullOrWhiteSpace(value)) throw new ArgumentException("Email is required.");
        if (!value.Contains("@")) throw new ArgumentException("Email format is invalid.");
        return new Email(value.Trim());
    }

    public override string ToString() => Value;
}

public sealed class User
{
    public Guid Id { get; }
    public string DisplayName { get; private set; }
    public Email Email { get; private set; }

    public User(Guid id, string displayName, Email email)
    {
        Id = id;
        DisplayName = displayName;
        Email = email;
    }
}
```

---

### Web側（入力の箱：Request DTO）📩

「APIで受け取る形」を固定します📦✨
ここには **バリデーション（必須チェック）**くらいは置いてもOKなことが多いです（でもビジネスルールは置かない）🙂

```csharp
// Web (Request DTO)
public sealed record RegisterUserRequest(
    string DisplayName,
    string Email
);
```

---

### Application側（出力の箱：Response DTO）📤

画面に返す形を“明確に”します✨
ドメインの `Email` みたいな型を外に出さず、**文字列にして返す**のが定番です😊

```csharp
// Application (Response DTO)
public sealed record UserDto(
    Guid Id,
    string DisplayName,
    string Email
);
```

---

## 5) DTOへのマッピング（変換）🔁✨

DTOは箱なので、中身（ドメイン）との変換が必要です📦➡️🧠

### まずは手動が最強（読みやすい＆事故りにくい）💪😊

AIにも作らせやすいです🤝✨

```csharp
// Application (Mapping)
public static class UserMapping
{
    public static UserDto ToDto(this User user) =>
        new(user.Id, user.DisplayName, user.Email.Value);
}
```

---

## 6) “DTOを使う流れ”のイメージ図 🌊✨

* 画面 → API → Application → Domain
* Domain → Application → API → 画面
 
 ```mermaid
 sequenceDiagram
    participant Screen as 画面/Frontend
    participant API as Web API
    participant App as Application Service
    participant Domain as Domain Model
    
    Note over Screen, API: Request DTO 📦
    Screen->>API: 登録リクエスト(RegisterUserRequest)
    API->>App: 渡す
    
    Note over App, Domain: 変換 (New Entity) 🔄
    App->>Domain: Userを作る
    Domain-->>App: 完成したUser
    
    Note over App, Domain: Response DTO 📦
    App-->>API: UserDtoに詰め替え
    API-->>Screen: レスポンス(UserDto)
 ```
 
 🧡ポイント：**画面はDTOだけ見てればOK**
 ドメインの都合に引きずられません😊

---

## 7) よくある事故パターン 😭⚠️（ここ超大事）

### ❌事故1：ドメインのエンティティをそのまま返す

* 内部情報漏れる🙈
* 画面都合でドメインが歪む😵‍💫
* シリアライズ地獄🌀

### ❌事故2：DTOにビジネスルールを書き始める

DTOは「箱」📦
ルールはドメイン🧠
これが混ざるとカオスになります😇

### ❌事故3：1個のDTOで全部やろうとする

* 更新用
* 参照用
* 一覧用
* 詳細用

これ、全部欲しい情報が違います😅
DTOは **用途ごとに分けてOK** 🙆‍♀️✨

---

## 8) AI（Copilot/Codex）で爆速にするコツ ⚡️🤖

DTOとマッピングは「定型作業」になりやすいのでAIが得意です🎉

### 便利プロンプト例（そのまま貼ってOK）📝✨

* 「`User` エンティティから `UserDto` を作って。外部公開は `Id, DisplayName, Email(string)` だけ」
* 「`RegisterUserRequest` を受けて `Email` 値オブジェクトを作る変換コードを書いて。例外が出る想定で」
* 「DTOとドメインの変換を Extension Method にして、null安全も考えて」

🧠コツ：**“公開していい項目”を必ず列挙して指示**すると事故りにくいです🔒✨

---

## 9) ミニ演習（サクッと）✍️🌸

### 演習A：一覧画面用DTOを作ろう 📃✨

**お題：注文（Order）の一覧画面**

* 一覧に必要：`OrderId`, `OrderedAt`, `TotalPrice`, `Status`

✅ やること

1. `OrderListItemDto` を作る
2. `Order` から `OrderListItemDto` への `ToDto()` を作る
3. 「詳細用DTO」は別にする（一覧と同じにしない）😆

### 演習B：更新用DTOを作ろう ✏️🔧

**お題：表示名の変更**

* 入力DTO：`ChangeDisplayNameRequest(string DisplayName)`
* 受け取った値で、ドメインのメソッド `ChangeDisplayName()` を呼ぶ（ここがドメインの仕事🧠✨）

---

## 10) まとめ 🌈✨

* DTOは **データ受け渡し専用の箱** 📦
* **画面の都合をドメインに入れない** のが最大の価値🧠💎
* セキュリティ・漏洩・シリアライズ事故も防げる🛡️✨
* DTOとマッピングはAIで爆速化しやすい⚡️🤖

---

次の章（AutoMapper vs 手動マッピング）につながる下準備としては完璧です😊✨
もし「DTO設計の命名ルール（Request/Response/Command/Query）」もセットでテンプレ化したいなら、その形でサンプル雛形も作れますよ📁💖
