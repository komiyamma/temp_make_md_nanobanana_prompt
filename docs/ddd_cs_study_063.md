# 第63章：AutoMapper vs 手動マッピング 〜AI時代ならどっちが迷わない？🤖✨

![AutoMapper vs 手動マッピング](./picture/ddd_cs_study_063_mapper_choice.png)

DTO（画面やAPIのためのデータ）と、ドメイン（本当に守りたいルールの世界）って、**そのまま同じ形にしない**のがDDDの基本でしたよね🙂
でもそこで必ず出てくるのがこの作業👇

* **DTO → ドメイン**（入力をルールに通して “正しい形” にする）
* **ドメイン → DTO**（画面に出すために “見せる形” にする）

この「変換（マッピング）」を、**AutoMapper**で自動化するか、**手で書く**か。今日はここをスッキリ決めます💡✨

---

## 今日のゴール🎯

読み終わったらこうなります👇

* AutoMapperの「得意・苦手」がわかる😊
* 手動マッピングが「遅い」どころか、むしろ速い場面がわかる🚀
* **AI（Copilot/Codex）で手動マッピングを爆速化するコツ**がわかる🤝🤖
* 1人開発で迷わない「結論パターン」を持って帰れる🎁

---

## そもそも、なんでマッピングが必要？🧩

![063_mapping_necessity](./picture/ddd_cs_study_063_mapping_necessity.png)

DTOとドメインは目的が違うからです🙂

* DTO：画面やAPIの都合（表示したい・受け取りたい形）
* ドメイン：ビジネスルールの都合（不正な状態を作らせない形）

たとえば「Email」はDTOだと `string` で届くけど、ドメインでは「メールとして正しい形式」しか生まれないようにしたい、みたいな感じです📧✨
 
 ```mermaid
 flowchart LR
    subgraph Dirty["DTOの世界 (緩い)"]
      D_Email[string Email]
    end
    
    subgraph Filter["変換の門番 👮‍♀️"]
      M_Map[Mapping / Factory]
      Check{形式OK?}
    end
    
    subgraph Clean["ドメインの世界 (堅牢)"]
      V_Email[Email ValueObject]
    end
    
    D_Email --> M_Map
    M_Map --> Check
    Check -- Yes --> V_Email
    Check -- No --> Error[エラーで弾く🚫]
 ```
 
 ---

## 選択肢① AutoMapper（自動変換）🪄

![063_automapper_magic](./picture/ddd_cs_study_063_automapper_magic.png)

### いいところ😊

* 同じようなDTOが大量にあると **書く量が減る** ✍️➡️🧠
* 変換が単純（プロパティ名が一致しまくり）なら爆速💨
* 一括でルールを設定できる（Profile）📦

### しんどいところ😵‍💫

* **「どこで何が起きてるか見えにくい」**（魔法の箱になりがち）
* 設定ミスが **実行時に爆発** しやすい💥
* ドメインの値オブジェクトや生成ルールが増えるほど、結局カスタム地獄になりやすい🌀

---

## 選択肢② 手動マッピング（自分で書く）✍️

![063_manual_craft](./picture/ddd_cs_study_063_manual_craft.png)

### いいところ😌

* 変換の意図が **コードにそのまま残る**（未来の自分に優しい）💖
* デバッグが超楽（ステップ実行できる）🪜
* ドメインのルール（値オブジェクト生成、Resultパターン等）と相性がいい🤝

### しんどいところ😫

* 量が多いと面倒（昔は…）
  → **でも今はAIでほぼ解決**🤖✨

---

## AI時代の結論💡：1人開発なら「手動＋AI」が最強になりがち👑🤖

![063_ai_manual](./picture/ddd_cs_study_063_ai_manual.png)

昔：手動マッピングは「作業が多い」
今：手動マッピングは「AIに書かせて、人間は意図だけ見る」✅

つまり👇

* **手動マッピングの弱点（作業量）をAIが消す**
* **AutoMapperの弱点（見えにくさ・実行時爆発）は残る**

だから1人開発だと、かなりの確率でこうなります👇

> **基本は手動（AI生成）**
> AutoMapperは「単純な変換が大量にある時だけ」採用🎯

---

## 具体例で体感しよう📦（DTO ⇄ ドメイン）

ここは最小例でいきます😊

### ドメイン側（Value Objectあり）

```csharp
public sealed record Email
{
    public string Value { get; }

    private Email(string value) => Value = value;

    public static bool TryCreate(string value, out Email? email)
    {
        email = null;
        if (string.IsNullOrWhiteSpace(value)) return false;
        if (!value.Contains('@')) return false;

        email = new Email(value.Trim());
        return true;
    }
}

public sealed class User
{
    public Guid Id { get; }
    public string Name { get; }
    public Email Email { get; }

    private User(Guid id, string name, Email email)
    {
        Id = id;
        Name = name;
        Email = email;
    }

    public static bool TryCreate(Guid id, string name, Email email, out User? user)
    {
        user = null;
        if (id == Guid.Empty) return false;
        if (string.IsNullOrWhiteSpace(name)) return false;

        user = new User(id, name.Trim(), email);
        return true;
    }
}
```

### DTO側

```csharp
public sealed class UserDto
{
    public Guid Id { get; set; }
    public string? Name { get; set; }
    public string? Email { get; set; }
}
```

---

## 手動マッピング（おすすめ）✨

![063_try_pattern](./picture/ddd_cs_study_063_try_pattern.png)

DTO→ドメインは「検証しながら」作れるのが強いです💪

```csharp
public static class UserMapping
{
    public static bool TryToDomain(UserDto dto, out User? user, out string? error)
    {
        user = null;
        error = null;

        if (dto is null) { error = "dto is null"; return false; }

        if (!Email.TryCreate(dto.Email ?? "", out var email))
        {
            error = "Emailが不正です";
            return false;
        }

        if (!User.TryCreate(dto.Id, dto.Name ?? "", email!, out user))
        {
            error = "Userが不正です";
            return false;
        }

        return true;
    }

    public static UserDto ToDto(User domain)
        => new()
        {
            Id = domain.Id,
            Name = domain.Name,
            Email = domain.Email.Value
        };
}
```

**ポイント💡**

* 「失敗する可能性」がある変換は、**Try形式**が相性良いです🙂
* 例外で飛ばすより、UIでメッセージを出しやすい🎀

---

## AutoMapper版（やるならこう）🪄

「ドメイン生成にルールがある」時点で、結局カスタムが増えます😵‍💫

```csharp
using AutoMapper;

public sealed class UserProfile : Profile
{
    public UserProfile()
    {
        CreateMap<User, UserDto>()
            .ForMember(d => d.Email, opt => opt.MapFrom(s => s.Email.Value));

        // DTO -> Domain は “newできない/検証がある” ので一筋縄ではいかない例
        CreateMap<UserDto, User>()
            .ConvertUsing((src, _, ctx) =>
            {
                if (!Email.TryCreate(src.Email ?? "", out var email))
                    throw new AutoMapperMappingException("Emailが不正です");

                if (!User.TryCreate(src.Id, src.Name ?? "", email!, out var user))
                    throw new AutoMapperMappingException("Userが不正です");

                return user!;
            });
    }
}
```

**これ、どう感じました？🙂**

* 変換ロジックがProfileの中に隠れていく
* 失敗時は例外中心になりがち
* “見通し” が落ちやすい

AutoMapperが悪いというより、**DDDのドメイン側がちゃんとしてくるほど相性が難しくなる**ってイメージです🧠✨

---

## 迷わないための判断基準チェックリスト✅

![063_decision_checklist](./picture/ddd_cs_study_063_decision_checklist.png)

### 手動（AI生成）を選ぶべきとき👑

* 値オブジェクトや生成ルールがある（TryCreate / Resultなど）🧱
* デバッグしやすさが大事（1人開発は超大事）🔎
* 変換に「意図」がある（見せ方・丸め・結合・条件分岐）🎨
* “どこで何してるか” を常に見える化したい👀

### AutoMapperが向くとき🪄

* ほぼ全部が **同名プロパティのコピー** 📋
* DTOの数が多くて、手動だと本当にダルい（ただし単純）😇
* チーム開発でAutoMapper文化があり、全員が慣れてる👥

---

## AIで手動マッピングを爆速にする指示テンプレ🤖📝

Copilot/Codexにこう投げると強いです👇（そのまま使ってOK）

```text
UserDto と User(ドメイン) のマッピングを手動で作りたい。
条件:
- DTO->Domain は Try形式で、失敗理由(string)も返す
- Email は Email.TryCreate を使う
- User は User.TryCreate を使う
- Domain->DTO は単純変換でOK
- クラス名は UserMapping、static メソッドで
テストしやすい形にして
```

**さらに強くする一言🔥**

* 「想定される失敗ケースも3つ書いて」
* 「ユニットテストも一緒に作って」

これで “作業” はAIに任せて、あなたは **意図のチェック係** になれます👩‍💻✨

---

## よくある事故と対策💥🛡️

### 事故①：DTOをドメインにそのまま流し込みたくなる😵

👉 対策：**DTO→ドメインは必ず “生成メソッド” 経由**（TryCreate/Factory）

### 事故②：AutoMapperの設定が増えて迷子🌀

👉 対策：AutoMapperを使うなら

* “Domain→DTOだけ” に絞る（片道）🚶‍♀️
  が現実的な落とし所になりがちです🙂

### 事故③：変換が散らばって探せない🔍

👉 対策：Mappingは置き場所を固定📁

* `Application/Mapping/`
* `Web/Mapping/`
  みたいに “ここ見ればある” 状態にする✨

---

## ミニ演習（第63章）🧪✨

1. `OrderDto`（Id, TotalAmount, Currency, Items…）を作る🛒
2. ドメイン側に `Money` 値オブジェクトを作る💰
3. **手動マッピングをAIに生成させる**🤖
4. 自分は「境界（どこで検証されるか）」だけチェックする👀✅
5. 余裕があれば「AutoMapper版」も作って、デバッグ体験を比べる🎮

---

## まとめ🍀

* **1人開発×DDD**だと、マッピングは「見えること」が正義👀✨
* 手動マッピングはAIで一気に軽くなる🤖💨
* AutoMapperは「単純な変換が大量」なら強いけど、ドメインが育つほど難しくなりがち🧱

次の章（第64章）は **Entity Framework Core と DDDの折り合い**！
ここで「DBとドメインをどう仲良くさせるか」へ進みますよ〜😊✨
