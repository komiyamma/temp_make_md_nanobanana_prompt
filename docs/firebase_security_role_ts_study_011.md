# 第11章：入力検証② 文字数・パターン（ユーザー入力の地雷💣）🔤

この章はひとことで言うと…
**「ユーザー入力が“爆弾💥”にならないように、Rulesでちゃんと止める」**です🙂🛡️

---

## 0) この章でできるようになること ✅✨

* **文字数**（短すぎ/長すぎ）をRulesで弾けるようになる🔢
* **パターン**（ユーザーIDっぽい文字だけ許す等）をRulesで弾けるようになる🔤
* 「表示名（日本語OK）」と「ハンドル（英数だけ）」みたいに、**用途別で検証を分ける**感覚が身につく🧠

---

## 1) なぜ文字数とパターンが“地雷”なの？💣😇

![firebase_security_role_ts_study_011_01_string_bomb.png](./picture/firebase_security_role_ts_study_011_01_string_bomb.png)

たとえば👇

![firebase_security_role_ts_study_011_02_risk_scenarios.png](./picture/firebase_security_role_ts_study_011_02_risk_scenarios.png)

* **超長文**を入れられて、画面が崩壊😱📱💥
* **空文字や空白だけ**で、ランキングや一覧が汚染🤢🧻
* **怪しい文字**（制御文字っぽいの、URL混ぜ、なりすましっぽいの）で運用トラブル🚨

しかもFirestoreはドキュメントサイズ上限もあるので（1MiBなど）、**最初から「保存していいサイズ」を絞る**のが安全です🧯📦 ([Firebase][1])

---

## 2) Rulesで使う“武器”🗡️（今日の主役）

![firebase_security_role_ts_study_011_03_rules_weapons.png](./picture/firebase_security_role_ts_study_011_03_rules_weapons.png)

Rulesの文字列チェックは、まずこの3つで戦えます🙂✨

* `size()`：**文字数**を返す（“文字”として数える） ([Firebase][2])
* `trim()`：前後のスペースを落とした文字列を返す（地味に超便利） ([Firebase][2])
* `matches()`：**正規表現で“文字列全体”が一致するか**を見る（RE2） ([Firebase][2])

> ポイント📝
> `matches()` は「部分一致」じゃなくて **文字列ぜんぶ** を判定します（= “全体一致”） ([Firebase][2])
> だから、基本は「許可したい文字だけのルール」を書けばOKです👍

---

## 3) 例題：プロフィール更新を安全にする🧑‍💻✨

![firebase_security_role_ts_study_011_04_profile_fields.png](./picture/firebase_security_role_ts_study_011_04_profile_fields.png)

ここでは、`users/{uid}` のプロフィールを想定します🙂
フィールド例👇

* `displayName`：表示名（日本語OK）😄
* `handle`：ユーザーIDっぽい短い英数（URLに載せやすい）🔗
* `bio`：自己紹介（長すぎ禁止）📝

---

## 4) 手を動かす🧑‍💻🔥：Rulesで「文字数・パターン」を実装する

## ステップA：検証用の関数を作る（読みやすさUP✨）

![firebase_security_role_ts_study_011_05_validation_logic.png](./picture/firebase_security_role_ts_study_011_05_validation_logic.png)

```rules
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    function isSignedIn() {
      return request.auth != null;
    }

    function isOwner(uid) {
      return isSignedIn() && request.auth.uid == uid;
    }

    // 表示名：前後空白NG、空白だけNG、1〜20文字
    function isValidDisplayName(name) {
      return (name is string)
        && (name == name.trim())              // 前後スペース禁止
        && (name.trim().size() >= 1)          // 空白だけ禁止
        && (name.size() <= 20);               // 長すぎ禁止
    }

    // handle：英小文字/数字/アンダースコアだけ、3〜20文字
    function isValidHandle(handle) {
      return (handle is string)
        && (handle.size() >= 3)
        && (handle.size() <= 20)
        && handle.matches('[a-z0-9_]+');      // “全体”が一致（RE2）
    }

    // bio：0〜160文字（空でもOK）
    function isValidBio(bio) {
      return (bio is string) && (bio.size() <= 160);
    }

    match /users/{uid} {
      allow read: if isOwner(uid);

      // create/update の両方で、同じ検証を通す例
      allow create, update: if isOwner(uid)
        && isValidDisplayName(request.resource.data.displayName)
        && isValidHandle(request.resource.data.handle)
        && isValidBio(request.resource.data.bio);
    }
  }
}
```

この中で大事なのは👇😎

* `name is string` を先に書く（型が違うと `.size()` で事故りやすい💥）
* **表示名**は「日本語OK」なので **正規表現を頑張りすぎない**（文字数とtrim中心）🙂
* **handle**は「英数だけ」にして **URLや検索で扱いやすく**する🔗✨
* `matches()` は“全体一致”なので、`[a-z0-9_]+` みたいに書けば「それ以外は全部NG」になる ([Firebase][2])

---

## ステップB：通る例✅ / 弾かれる例❌ をイメージする🧠

![firebase_security_role_ts_study_011_06_good_bad_examples.png](./picture/firebase_security_role_ts_study_011_06_good_bad_examples.png)

**displayName**

* ✅ `"こみやんま"`（OK）
* ✅ `"KOMIYAMMA"`（OK）
* ❌ `""`（空）
* ❌ `"   "`（空白だけ）
* ❌ `" たろう "`（前後スペースあり）
* ❌ `"A"` を21文字以上（長すぎ）

**handle**

* ✅ `"komiyamma"`
* ✅ `"user_123"`
* ❌ `"User_123"`（大文字NGにしてる）
* ❌ `"こみやんま"`（日本語NGにしてる）
* ❌ `"a"`（短すぎ）

---

## 5) ちょいコツ🍯：「表示名」と「ハンドル」を分けると幸せ

**表示名**は「人が読む」から、多少自由でOK🙂
**ハンドル**は「システムが扱う」から、厳しめが楽😆🔧

この分離だけで、

* URLに載せるのが簡単
* 検索やユニーク制約が作りやすい
* なりすましっぽい混乱が減る
  みたいなメリットが出やすいです✨

---

## 6) React側でも“先に”弾く（でもRulesが本番🛡️）

UIで先に弾くと、ユーザー体験が良くなります🙂💡
（ただし**最終防衛ラインはRules**です👮‍♂️）

例：`zod` でざっくり同じ制約をつける（イメージ）👇

```ts
import { z } from "zod";

export const profileSchema = z.object({
  displayName: z.string().trim().min(1).max(20),
  handle: z.string().min(3).max(20).regex(/^[a-z0-9_]+$/),
  bio: z.string().max(160),
});
```

* 画面側：すぐ赤文字で教える🟥🙂
* Rules側：改造クライアントでも必ず止める🛡️💥

---

## 7) AIを使って“速く作る”🤖⚡（でも最後は人間が責任👀）

## 7-1) Gemini CLI / Antigravity で叩き台を作る🧪

FirebaseのAI用プロンプトには、**Rules生成やテスト生成**のためのものが用意されています。たとえば `/firebase:generate_security_rules` がそれです🧰 ([Firebase][3])

さらに、Antigravity には Firebase MCP server を追加して、AIエージェントからFirebase操作や生成をしやすくする導線もあります🧩 ([Firebase][4])

## 7-2) そのままコピペ禁止🧯（AIレビュー観点）

AIに出させるのは「形」まで。**安全の責任は人間**です🙂‍↕️
最低チェック👇✅

* `matches()` が **許可リスト型**になってる？（禁止リスト型は漏れやすい😵） ([Firebase][2])
* `trim()` や `size()` の順番で事故らない？（型チェック先） ([Firebase][2])
* `create/update` どっちも守れてる？（片方だけ穴が空きがち😱）

---

## 8) Firebase AI Logic と組み合わせる（“追加の安全装置”）🧠🧯

![firebase_security_role_ts_study_011_07_defense_layers.png](./picture/firebase_security_role_ts_study_011_07_defense_layers.png)

Rulesは「門番🚪」として最高なんだけど、
**NGワード判定**とか **文脈での荒らし検知**みたいな“頭を使う判定”は苦手です🙂

そこで、たとえば👇

* クライアント：入力の形をチェック（zodなど）🙂
* Rules：文字数/形式を強制🛡️
* サーバー（Functions + Genkit / AI Logic）：投稿内容の判定や整形、モデレーション🤖

Firebase AI Logic は、クライアントSDKやプロキシなどで **生成AIモデルへ安全に接続するための仕組み**を提供しています。 ([Firebase][5])

> ここ大事📌
> AIは「便利な追加装置」であって、**Rulesの代わり**にはならないよ！🛡️🙂

---

## 9) ミニ課題🎯（10〜20分）

## 課題A：表示名を「1〜20文字」にする😄

* `displayName` を `trim()` して

  * 空白だけNG
  * 前後スペースNG
  * 1〜20文字
    にしよう✅

## 課題B：handle を「英小文字+数字+_」だけにする🔗

* `handle.matches('[a-z0-9_]+')` を使って
* 3〜20文字で制限✅ ([Firebase][2])

---

## 10) チェック✅（この章のゴール確認）

* [ ] `size()` で文字数制限できる（displayName / bio）🙂 ([Firebase][2])
* [ ] `trim()` で「空白だけ」「前後空白」を止められる😆 ([Firebase][2])
* [ ] `matches()` を「許可リスト」で書ける🔤 ([Firebase][2])
* [ ] 「表示名」と「ハンドル」を分ける理由を説明できる🧠✨

---

## おまけ：Functions側でも二重に検証するなら（バージョン目安）🧩

Rulesは必須として、サーバー側で追加検証するなら👇

* Functions（Node.js）：**Node.js 22 / 20**（18はdeprecated） ([Firebase][6])
* Functions（Python）：**Python 3.10〜3.13**（3.13がデフォルト） ([Firebase][7])
* Admin SDK（.NET）：**.NET 8 以上推奨** ([Firebase][8])

---

次の第12章では、いよいよ超重要🔥
**「書いていい項目だけ許す」＝権限昇格（role/isAdmin等）をRulesで叩き潰す🛡️💥** に進みます🙂✨

[1]: https://firebase.google.com/docs/firestore/quotas "Usage and limits  |  Firestore  |  Firebase"
[2]: https://firebase.google.com/docs/reference/rules/rules.String "Interface: String  |  Firebase"
[3]: https://firebase.google.com/docs/ai-assistance/prompt-catalog "AI prompt catalog for Firebase  |  Develop with AI assistance"
[4]: https://firebase.google.com/docs/ai-assistance/mcp-server?utm_source=chatgpt.com "Firebase MCP server | Develop with AI assistance - Google"
[5]: https://firebase.google.com/docs/ai-logic?utm_source=chatgpt.com "Gemini API using Firebase AI Logic - Google"
[6]: https://firebase.google.com/docs/functions/manage-functions?utm_source=chatgpt.com "Manage functions | Cloud Functions for Firebase - Google"
[7]: https://firebase.google.com/docs/functions/get-started?utm_source=chatgpt.com "Get started: write, test, and deploy your first functions - Firebase"
[8]: https://firebase.google.com/support/release-notes/admin/dotnet?utm_source=chatgpt.com "Firebase Admin .NET SDK Release Notes"
