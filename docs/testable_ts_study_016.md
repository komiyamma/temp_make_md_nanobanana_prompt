# 第16章：テストダブル入門（スタブ/モック/スパイ）🧸👀

![testable_ts_study_016_test_doubles.png](./picture/testable_ts_study_016_test_doubles.png)

この章は「I/O境界を分けたはいいけど、テストで差し替える道具がわからん…😵‍💫」を解決する回だよ〜！
テストダブル（代役）を覚えると、**外の世界（通知・HTTP・DB・時刻…）を“本物っぽく演じさせて”**、中心（ロジック）を気持ちよくテストできるようになるよ🎀

---

## 0. 今日のゴール🎯✨* **スタブ / スパイ / モック**の違いを、ふわっとじゃなく説明できる🙂


* 「このケースはどれ使う？」を迷わなくする🧭
* TypeScriptで**“通知送信”を送ったことにするテスト**を書ける📩😆

---

## 1. テストダブルってなに？（まず一言で）

🧸**テストダブル＝本物の代役**だよ🎭
外部I/O（通知、API、DB、ファイル…）は本物を呼ぶとテストが遅い・不安定・面倒になりがち💥
だからテストでは、代役を差し込んでコントロールするの✨

---

## 2. 3兄弟（スタブ / スパイ / モック）

👩‍👧‍👦✨覚え方はこれが一番ラク👇（超重要！）



### ✅ スタブ（Stub）

＝「返事を決めておく係」📮* 目的：**テスト対象が進むための結果を返す**


* 例：DB検索が「見つからない」を返す、APIが固定レスポンスを返す、など

### ✅ スパイ（Spy）

＝「見張り係（記録係）」👀📝* 目的：**呼ばれた回数・引数などを記録して後で見れる**


* 例：「通知が1回送られた？」「どんなメッセージ送った？」を確認

### ✅ モック（Mock）

＝「約束を確認する係（期待チェック）」📜✅* 目的：**“こう呼ばれるはず”をテストで検証する**


* 例：「この引数で呼ばれるべき」「この順で呼ばれるべき」を確認

> ちなみにJS系だと “mock function は spy としても使える” みたいに、道具としては同じ物体になりがち（`jest.fn()`や`vi.fn()`）だよ〜。Jest公式でも「モック関数はスパイとも呼ばれる」って説明してるよ👀 ([Jest][1])

---

## 3. どれ使う？秒で決める早見🧭✨* **分岐を通したい**（成功/失敗を作りたい）

→ **スタブ**💡


* **呼ばれたか知りたい** → **スパイ**👀
* **呼び方（契約）を守らせたい** → **モック**📜

そして迷ったらこの順が安全👇
**スタブ →（足りなければ）スパイ →（最後に）モック**😺✨
（モック多用はテストが折れやすい“あるある”🥺）

---

## 4. 今日の題材：通知送信を「送ったことにする」📩😆### 登場人物（境界）

🚪* `Notifier`：通知を送る（本物はメール/Slack/Pushとか）


* `registerUser`：ユーザー登録する中心ロジック（ユースケース）

「通知」はI/Oなので、**テストでは本物を呼ばない**のがポイントだよ🧊

---

## 5. 実装（中心）

🧠✨

```ts
// src/registerUser.ts
export type RegisterInput = {
  email: string;
  name: string;
};

export type RegisterResult =
  | { ok: true; userId: string }
  | { ok: false; reason: "already-exists" };

export interface UserRepo {
  findByEmail(email: string): Promise<{ id: string; email: string } | null>;
  save(user: { id: string; email: string; name: string }): Promise<void>;
}

export interface Notifier {
  sendWelcome(email: string, name: string): Promise<void>;
}

export async function registerUser(
  input: RegisterInput,
  deps: { repo: UserRepo; notifier: Notifier; idGen: () => string }
): Promise<RegisterResult> {
  const existing = await deps.repo.findByEmail(input.email);
  if (existing) return { ok: false, reason: "already-exists" };

  const user = { id: deps.idGen(), email: input.email, name: input.name };
  await deps.repo.save(user);

  await deps.notifier.sendWelcome(user.email, user.name);

  return { ok: true, userId: user.id };
}
```

---

## 6. テスト①：スタブで分岐を作る（既存ユーザーなら失敗）

📮🧪「DB検索で“見つかったことにする”」＝スタブの仕事だよ✨



```ts
// test/registerUser.stub.test.ts
import { describe, it, expect } from "vitest";
import { registerUser, type UserRepo, type Notifier } from "../src/registerUser";

describe("registerUser（スタブ編）", () => {
  it("既に同じemailがいたら登録できない", async () => {
    const repoStub: UserRepo = {
      findByEmail: async () => ({ id: "u-999", email: "a@example.com" }),
      save: async () => {
        throw new Error("save should not be called"); // 念のため
      },
    };

    const notifierStub: Notifier = {
      sendWelcome: async () => {
        throw new Error("notify should not be called");
      },
    };

    const result = await registerUser(
      { email: "a@example.com", name: "A" },
      { repo: repoStub, notifier: notifierStub, idGen: () => "u-1" }
    );

    expect(result).toEqual({ ok: false, reason: "already-exists" });
  });
});
```

ここでの気持ち🌸

* スタブは「返す値」で物語を作る📖✨
* まだ「通知が呼ばれたか」は見てない（それはスパイ/モックの領域）👀

---

## 7. テスト②：スパイで「呼ばれた？」を記録する👀📝

Vitestだと、関数の代役を `vi.fn()` で作って **呼び出し履歴を見れる**よ。
Vitest公式でも「観測したいなら `vi.spyOn`、引数として渡す関数を作るなら `vi.fn`」って整理されてるよ🧠 ([Vitest][2])

```ts
// test/registerUser.spy.test.ts
import { describe, it, expect, vi } from "vitest";
import { registerUser, type UserRepo, type Notifier } from "../src/registerUser";

describe("registerUser（スパイ編）", () => {
  it("新規登録できたら welcome通知が1回だけ送られる", async () => {
    const repoStub: UserRepo = {
      findByEmail: async () => null,
      save: async () => {},
    };

    const sendSpy = vi.fn(async (_email: string, _name: string) => {});
    const notifierSpy: Notifier = { sendWelcome: sendSpy };

    const result = await registerUser(
      { email: "a@example.com", name: "A" },
      { repo: repoStub, notifier: notifierSpy, idGen: () => "u-1" }
    );

    expect(result).toEqual({ ok: true, userId: "u-1" });

    // 👀 ここがスパイ！
    expect(sendSpy).toHaveBeenCalledTimes(1);
    expect(sendSpy).toHaveBeenCalledWith("a@example.com", "A");
  });
});
```

ここが大事💡

* **中心の戻り値（result）もテストする**（まずはここが主役🎀）
* それに加えて「通知が送られた」も確認（境界のやり取り）👀

---

## 8. テスト③：モックで「約束（期待）

」をガッチリ確認📜✅実務では「スパイ + 期待（expect）」で済ませることが多いけど、考え方としてはこれがモックの世界だよ✨
JestもVitestも「モック関数で呼び出しを検証」するのが基本🧪 ([Jest][1])

### 例：通知文面まで“契約”にする（ちょい固め）

ちょっとだけ設計を足してみるね👇（通知メッセージを中心で作る）



```ts
// src/welcomeMessage.ts
export function buildWelcomeMessage(name: string): string {
  return `ようこそ ${name} さん！`;
}
```

```ts
// test/welcomeMessage.mock.test.ts
import { describe, it, expect } from "vitest";
import { buildWelcomeMessage } from "../src/welcomeMessage";

describe("buildWelcomeMessage（中心ロジック）", () => {
  it("名前を入れた文面を作れる", () => {
    expect(buildWelcomeMessage("A")).toBe("ようこそ A さん！");
  });
});
```

☝️ここがポイント：
**“文面生成”は中心ロジックにして、戻り値テストで守る**と壊れにくいよ💎
通知そのものは「送ったか」くらいに留めるのが無難🙂（文面までモック契約にするとテストがすぐ折れがち🥺）

---

## 9. `vi.spyOn` も一回だけ触っておこ👀🧷すでに“本物っぽいオブジェクト”があって、**そのメソッドを監視したい**ときに便利なのが `vi.spyOn`。
VitestのモックAPIでも、`vi.fn` と `vi.spyOn` の違い（実装の扱い）が説明されてるよ🧠 ([Vitest][3])

```ts
import { describe, it, expect, vi } from "vitest";

describe("vi.spyOn（ちょい例）", () => {
  it("メソッド呼び出しを監視できる", async () => {
    const notifier = {
      async sendWelcome(email: string, name: string) {
        // 本物なら外部送信だけど、ここでは例なので空
      },
    };

    const spy = vi.spyOn(notifier, "sendWelcome").mockResolvedValue();

    await notifier.sendWelcome("a@example.com", "A");

    expect(spy).toHaveBeenCalledTimes(1);
    expect(spy).toHaveBeenCalledWith("a@example.com", "A");
  });
});
```

---

## 10. お片付け（超だいじ）

🧹✨モック/スパイは状態を持つから、テスト間で汚れが残ると事故るよ〜😱
Vitestのガイドでも「テストごとに clear/restore しようね」って注意があるよ🧼 ([Vitest][4])

```ts
// test/setup.ts （例）
import { afterEach, vi } from "vitest";

afterEach(() => {
  vi.clearAllMocks();
  vi.restoreAllMocks();
});
```

---

## 11. “やりすぎモック”を避けるコツ🙅‍♀️

🥺### ❌ よくある罠* 内部関数までモックして「何もテストしてない」状態😇


* 呼び出し回数・順番に縛りすぎて、リファクタで毎回崩壊💥

### ✅ おすすめルール* **中心は戻り値で守る**（純粋ロジックのテストが最強💪🍰）


* **境界だけを差し替える**（Notifier/Repo/HTTPなど）🚪
* Interaction（呼び出し確認）は最小限に👀✨

---

## 12. AI拡張（Copilot/Codex等）

で爆速にする🤖🎀AIに頼ると強いところ👇



* テストケースの洗い出し（境界値/異常系）🧠📌
* スタブ・スパイの雛形生成🧱
* AAA形式に整える✍️

### 使えるプロンプト例🪄* 「この `registerUser` に対して、成功/失敗のテストケースをAAAで列挙して。I/Oは `repo` と `notifier` だけをテストダブルにして」


* 「Vitestで `vi.fn()` を使った spy の例を書いて。`toHaveBeenCalledWith` まで含めて」

### そして注意⚠️* AIが**内部ロジックまでモック**し始めたら赤信号🚨
  → 「境界（I/O）以外はモックしないで」って言い直すと良いよ🙂

---

## 13. 章末ミニ課題🎓🌈### 課題A（スタブ）

📮* `findByEmail` がユーザーを返すとき、`save` と `sendWelcome` が呼ばれないテストを書いてね🧪



### 課題B（スパイ）

👀* 新規登録成功時に `repo.save` が **1回だけ** 呼ばれることを確認してね（`save` を `vi.fn()` にする）📝

### 課題C（モック寄り）

📜* `sendWelcome` に渡る引数（email/name）が入力と一致することを確認してね✅

---

## 14. この章のまとめ🎀✨* **スタブ＝返す**📮 / **スパイ＝記録**👀 / **モック＝期待を確認**📜


* 迷ったら **スタブ→スパイ→モック** の順が安全🙂
* モックを増やしすぎるとテストが折れやすいから、**中心は戻り値で守る**のが基本だよ🍰✨

---

次の第17章は **Clock（時刻）を分離して“時間を止める”** だよ⏰🧊
この章で覚えたテストダブルが、そのまま大活躍するよ〜！😆🧪

[1]: https://jestjs.io/docs/mock-function-api?utm_source=chatgpt.com "Mock Functions"
[2]: https://vitest.dev/guide/mocking/functions?utm_source=chatgpt.com "Mocking Functions"
[3]: https://vitest.dev/api/mock?utm_source=chatgpt.com "Mocks"
[4]: https://vitest.dev/guide/mocking?utm_source=chatgpt.com "Mocking | Guide"
