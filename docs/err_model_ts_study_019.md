# 第19章：AsyncResult（Promise<Result>）の扱い方⚡🎁

（asyncでもResult設計を崩さないコツだよ〜😊🧡）

---

## 0. この章でできるようになること🎯✨

* async関数でも「成功/失敗」を Result で返して、読みやすさをキープできる🙂📦
* 「どこで await する？」「どこで catch する？」を迷わなくなる🧠🧭
* “Unhandled Rejection 地獄😱”を避ける設計の型が作れる🛡️✨

※ちなみに今のTypeScriptは 5.8 系が安定版として並び、5.9 は Beta 扱いのリリースが出てるよ（2026/01時点の公開情報）📌 ([GitHub][1])

---

## 1. まず結論：AsyncResultってなに？🎁⚡

AsyncResult はひとことで言うとこれ👇

* Result：同期の「成功/失敗の箱」🎁
* AsyncResult：非同期版で「Promiseで包まれたResult」🎁⚡

![AsyncResult：Promiseで包まれたResult[(./picture/err_model_ts_study_019_promise_wrapper.png)

つまり…

* 成功：Promiseが「成功（resolve）」して、中身が Ok
* 失敗：Promiseが「成功（resolve）」して、中身が Err
* 例外：Promiseが「失敗（reject）」しちゃう（＝事故りやすい）😱

ここが超重要ポイントだよ‼️

---

## 2. “reject”が増えると何がつらいの？😵‍💫💥

Promiseが reject されたのに拾われないと、環境によってはグローバルに “未処理” として扱われるよ⚠️

* ブラウザ：unhandledrejection イベントが飛ぶ🌐⚡ ([MDN Web Docs][2])
* Node：process の unhandledRejection が飛ぶ🧨 ([Node.js][3])

つまり「設計として想定してた失敗」なのに、**実装ミスで未処理になった瞬間、運用事故に化ける**ことがある…😇🧯

だからこの章の方針はこれ👇
✅ 想定内の失敗（ドメイン/インフラ）は Err に寄せる
✅ 想定外（バグ/不変条件違反）は例外として落とす（境界でまとめて処理）

---

## 3. まず最小セットの型を作ろう🧩✨

```ts
export type Result<T, E> =
  | { ok: true; value: T }
  | { ok: false; error: E };

export const ok = <T>(value: T): Result<T, never> => ({ ok: true, value });
export const err = <E>(error: E): Result<never, E> => ({ ok: false, error });

export type AsyncResult<T, E> = Promise<Result<T, E>>;
```

この形にしておくと、条件分岐が超わかりやすい🙂🌈

---

## 4. AsyncResultの「事故らないルール」5つ🧸🛡️

### ルール①：async関数は “原則 throw しない” 🙅‍♀️💥

* 想定内の失敗：Errで返す
* バグだけ throw（＝Fail Fast）⚡🧱

### ルール②：境界（入口/出口）だけは try/catch を置く🚪🧯

中で撒き散らさない。最後にまとめる✨

### ルール③：awaitは「責任を持って拾う場所」でやる🧭

awaitしたら、その場で Result にして返す（または上に返す）🙂

### ルール④：非同期合成は “ヘルパー” で読みやすくする🪄📚

if地獄を避ける🫠

### ルール⑤：未処理rejectionの監視は保険として入れる👮‍♀️

ゼロにする設計を目指しつつ、最後の最後にログで気づけるようにする🧾✨
（Node/ブラウザの仕組みは公式が解説してるよ） ([Node.js][3])

---

## 5. “tryCatchAsync” を作ると世界が平和になる🕊️✨

「Promiseがrejectする可能性がある処理」を、強制的に AsyncResult に変換しちゃう道具だよ🎁⚡

```ts
export const tryCatchAsync = async <T, E>(
  f: () => Promise<T>,
  onError: (e: unknown) => E
): AsyncResult<T, E> => {
  try {
    const v = await f();
    return ok(v);
  } catch (e: unknown) {
    return err(onError(e));
  }
};
```

これで、reject しがちなAPI（fetchとか外部SDKとか）を “Errに正規化” できる🙂🧼

---

## 6. 合成ヘルパー：andThenAsync（超よく使う）⛓️✨

「前の処理がOkなら次へ、Errならそのまま返す」やつ！

```ts
export const andThenAsync = async <T, E, U>(
  ar: AsyncResult<T, E>,
  f: (v: T) => AsyncResult<U, E>
): AsyncResult<U, E> => {
  const r = await ar;
  return r.ok ? f(r.value) : r;
};
```

これがあると、非同期3ステップでも読みやすい📖💗

---

## 7. ミニ実装：asyncな3ステップを Promise<Result> で成立させる🎓🧪

### お題🎀

「ユーザーIDを受け取る → ユーザー取得 → 保存」みたいな流れを作るよ🙂

#### エラー型（例）

```ts
type DomainError =
  | { kind: "UserNotFound"; userId: string }
  | { kind: "InvalidUserId"; userId: string };

type InfraError =
  | { kind: "Network"; message: string }
  | { kind: "Db"; message: string; cause?: unknown };
```

#### ① 入力チェック（同期だけど Result で返す）

```ts
const validateUserId = (userId: string): Result<string, DomainError> => {
  if (!userId || userId.trim().length < 3) {
    return err({ kind: "InvalidUserId", userId });
  }
  return ok(userId.trim());
};
```

#### ② ユーザー取得（AsyncResult）

```ts
type User = { id: string; name: string };

const fetchUser = (userId: string): AsyncResult<User, DomainError | InfraError> =>
  tryCatchAsync(
    async () => {
      // 例：外部I/Oは失敗しうる
      const res = await fetch(`https://example.test/users/${userId}`);
      if (res.status === 404) throw new Error("notfound");
      if (!res.ok) throw new Error(`http ${res.status}`);
      return (await res.json()) as User;
    },
    (e) => {
      // ここは「正規化」する場所✨
      const msg = e instanceof Error ? e.message : "unknown";
      if (msg === "notfound") return { kind: "UserNotFound", userId } as const;
      return { kind: "Network", message: msg } as const;
    }
  );
```

#### ③ 保存（AsyncResult）

```ts
const saveUser = (user: User): AsyncResult<void, InfraError> =>
  tryCatchAsync(
    async () => {
      // 例：DB保存のつもり
      // await db.save(user)
    },
    (e) => {
      const msg = e instanceof Error ? e.message : "unknown";
      return { kind: "Db", message: msg, cause: e };
    }
  );
```

#### ④ 3ステップ合成（読みやすい！）

```ts
export const registerFlow = async (
  userId: string
): AsyncResult<void, DomainError | InfraError> => {
  const v = validateUserId(userId);
  if (!v.ok) return v; // 早期return✨（これ大事）

  return andThenAsync(fetchUser(v.value), (user) => saveUser(user));
};
```

ポイントはここ👇😊

* 「入力ミス」は Result（同期）で返す
* 「外部I/O」は tryCatchAsync で Err にする
* “想定内の失敗” は reject じゃなく Err で運ぶ🎁

---

## 8. 例外との住み分け（ここ超テストに出る📌😆）

### Resultで返すべきもの✅

* ユーザー入力ミス（ドメイン）📝
* 在庫なし/期限切れ（ドメイン）🛒
* ネットワーク/DB一時障害（インフラ）🌩️

### 例外で落としていいもの✅（＝バグ）

* nullのはずがないのにnull（不変条件違反）🧱
* switchのdefaultに来た（設計漏れ）😇
* 型的にありえない値が来た（内部破壊）💥

---

## 9. “原因を失わない”小ワザ：causeチェーン🎁🧵

エラーを包むとき、原因を持たせるとデバッグが楽になるよ🙂
JavaScriptには Error.cause がある✨ ([MDN Web Docs][4])

（Result設計でも「InfraErrorにcauseを載せる」だけで十分効くよ🧡）

---

## 10. ミニ演習📝✨（やると一気に身につくよ！）

### 演習A：tryCatchAsyncを自分の言葉で説明してみよう🧠💬

* 「rejectをErrに変える」ってどういうこと？
* どこに置くのが良い？（境界？ユースケース層？）

### 演習B：andThenAsyncをもう1個作る🪄

* mapAsync（Okのvalueだけ加工する）を実装してみてね🙂

### 演習C：落ち方パターンを網羅✅

「この処理が壊れるパターン」を10個書いて、

* Domain / Infra / Bug に分類
* AsyncResultで返す？throwする？ を決める📋✨

---

## 11. AI活用🤖💖（Copilot/Codex向けプロンプト例）

* 「AsyncResult（Promise<Result>）用に mapAsync / mapErrAsync / andThenAsync を型安全に実装して」
* 「この関数が reject しうる箇所を列挙して、AsyncResultに正規化する案を出して」
* 「DomainError/InfraErrorの境界が混ざってないかレビューして」👀
* 「未処理rejectionになりうる呼び出し方の事故例を3つ作って」😱

---

## 12. 章のまとめ🎀✨

* AsyncResult = Promise<Result> で **“想定内の失敗” を reject から守る**🛡️
* tryCatchAsync があると「外部I/Oの失敗」を綺麗にErrへ寄せられる🧼
* 例外は “バグだけ” にして、境界でまとめて処理するのが気持ちいい🙂🚪

次の章（入力チェックは実行時だよ🧪🫥）に行くと、AsyncResult設計がさらに安定するよ〜！✨

[1]: https://github.com/microsoft/typescript/releases "Releases · microsoft/TypeScript · GitHub"
[2]: https://developer.mozilla.org/en-US/docs/Web/API/Window/unhandledrejection_event?utm_source=chatgpt.com "Window: unhandledrejection event - Web APIs | MDN"
[3]: https://nodejs.org/api/process.html?utm_source=chatgpt.com "Process | Node.js v25.3.0 Documentation"
[4]: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Error/cause?utm_source=chatgpt.com "Error: cause - JavaScript - MDN Web Docs"
