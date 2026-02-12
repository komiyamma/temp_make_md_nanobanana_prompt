# 第10章：「テストしにくい臭い」カタログ👃💨

![testable_ts_study_010_code_smell.png](./picture/testable_ts_study_010_code_smell.png)

この章はね、「テストがつらい…😵‍💫」って感じたときに、**どこが“臭い”の原因か**をサクッと見つけて、**どこにI/O境界（＝外の世界との境目🚪）を引けばいいか**を言葉にできるようになる章だよ〜✨

---

## この章でできるようになること🎯✨* 「あ、これ臭い！

」を**パターンで発見**できる👀💡


* 臭いに赤ペン🖍️して「境界候補」を**言語化**できる🗣️✨
* いきなり大改造じゃなくて、**最短の1手**で改善できる🔧🌱

---

## まずは超ざっくり！

臭い判定の3問👃💨コードを見た瞬間、これ聞いてみて〜😊

1. **毎回同じ入力なら、毎回同じ結果？**（揺れてたら臭い🎲⏰）
2. **外の世界に触ってない？**（HTTP/DB/ファイル/環境変数/ログ…🌍）
3. **依存を差し替えられる？**（直書きだと詰む😱）

YESが増えるほど、テストはつらくなるよ〜🧪💦

---

## “赤ペン入れ”の手順🖍️

🧠（超おすすめ）コードを見たら、次の順でマークすると迷子になりにくいよ✨



* ① **外界ワード**を囲む🌍（例：HTTP、ファイル、日時、乱数、環境変数、ログ）
* ② **判断（ルール）**を囲む🧠（割引、判定、計算、整形…）
* ③ ②を中心に残して、①を外に押し出すイメージで
  **「ここが境界！」**を一文で書く✍️
  例：「時刻取得はClockにする」「HTTPはApiClientにする」など✨

---

## 臭いカタログ（よく出る順）

👃💨📚以下は「見つけ方 → なぜつらい → 最短の直し方」のセットだよ〜😊🎀
（コード例はミニサイズでいくね！）

---

## 1) 関数の奥でnewしてる🧱

😱（依存を自作臭）### 見つけ方👀* 関数の中に new がいる（しかもDB/HTTP/Logger系）



### なぜつらい？😵‍💫* テストで差し替えできない＝本物が動いちゃう（遅い・壊れる）

⚡💥

### 最短の直し方🔧* まずは **引数で受け取る**（注入🎁

）


* new は「組み立て係（外側）」へお引っ越し🏗️

```ts
// ❌ くさい例：中でnewしちゃう
export async function getUserName(userId: string) {
  const client = new ApiClient(); // ← ここが臭い
  const user = await client.fetchUser(userId);
  return user.name.toUpperCase();
}
```

```ts
// ✅ まずは引数で注入する（最短の1手）
export interface UserApi {
  fetchUser(id: string): Promise<{ name: string }>;
}

export async function getUserName(userId: string, api: UserApi) {
  const user = await api.fetchUser(userId);
  return user.name.toUpperCase();
}
```

---

## 2) 直Date（現在時刻ベタ書き）

⏰🧊### 見つけ方👀* Date / Date.now がロジックの中にいる



### なぜつらい？😵‍💫* テストの結果が「実行した瞬間」に依存してブレる😇💥

### 最短の直し方🔧* now() だけの **Clock** を注入🎁

（Nodeではfetch等も標準化が進んでるけど、時刻/乱数は分離したほうがテストが安定するよ〜✨）([Node.js][1])

```ts
export interface Clock { now(): Date; }

export function isExpired(expireAt: Date, clock: Clock) {
  return clock.now().getTime() > expireAt.getTime();
}
```

---

## 3) 直fetch（HTTP直叩き）

🌐😱### 見つけ方👀* fetch が中心っぽい処理の中にいる



### なぜつらい？😵‍💫* ネットワークは遅い・落ちる・仕様変更する…でテストが不安定🌩️


* Nodeではfetchが使えるようになって便利だけど、**便利＝テストしやすい**ではないのが罠😇
  （Node 18でfetchが有効、Node 21で安定扱いの流れ）([Node.js][1])

### 最短の直し方🔧* ApiClient interface を作って、中心はそれだけ知る✨



```ts
export interface WeatherApi {
  getTemp(city: string): Promise<number>;
}

export async function needCoat(city: string, api: WeatherApi) {
  const temp = await api.getTemp(city);
  return temp < 12;
}
```

---

## 4) 直process.env（環境変数べったり）

⚙️😱### 見つけ方👀* process.env がいろんな所で参照されてる



### なぜつらい？😵‍💫* テストで環境をいじると、**他のテストに伝染**しやすい🦠💥


* そもそもESLintにも「process.envやめよ」ルールがあるくらい“グローバル依存”扱いなんだよね🧯 ([ESLint][2])

### 最短の直し方🔧* Configを1回読み取って、中心へ渡す📦🎁



```ts
export type Config = { mode: "dev" | "prod" };

export function shouldShowDebugPanel(config: Config) {
  return config.mode === "dev";
}
```

---

## 5) 巨大関数（なんでも屋）

🧟‍♀️📦### 見つけ方👀* 1つの関数で「取得→変換→判断→保存→ログ」ぜんぶやってる



### なぜつらい？😵‍💫* テストケースが爆発💣（分岐×外部依存×例外…）


* どこが悪いかも分からなくなる迷宮🌀

### 最短の直し方🔧* 「判断（中心🧠）

」だけを抽出して、まず純粋にする🍰✨


* 次にI/Oを外へ🚪

コツ👉 **“動詞”が多いほど臭い**（fetch/parse/validate/save/log…全部入ってたら危険⚠️）

---

## 6) console.logだらけ（ログが中心に侵入）

📝😵### 見つけ方👀* console.log / console.error がロジックの中にいる



### なぜつらい？😵‍💫* テスト出力が汚れる＋「ログしたか」を検証しづらい


* ログもI/Oだからね〜📣🌍

### 最短の直し方🔧* Loggerを注入して、テストではスパイにする🕵️

‍♀️



```ts
export interface Logger { info(msg: string): void; }

export function greet(name: string, logger: Logger) {
  logger.info(`hello ${name}`);
  return `Hi, ${name}!`;
}
```

---

## 7) 直Math.random（乱数で揺れる）

🎲😇### 見つけ方👀* Math.random がロジックの中にいる



### なぜつらい？😵‍💫* テストが**たまに落ちる**（いちばん嫌なやつ😇💥）

### 最短の直し方🔧* Random interface を注入して固定値にする🎯

---

## 8) グローバル可変（モジュール変数に状態）

🧨🌀### 見つけ方👀* ファイル先頭に let があって、いろんな関数から書き換えてる



### なぜつらい？😵‍💫* テスト間で状態が共有されて、順番で壊れる👻

### 最短の直し方🔧* 状態を「箱」に閉じ込めて、生成して渡す📦🎁

---

## 9) 例外が“そのまま”飛び回る🚨😱### 見つけ方👀* throw があちこち、どの失敗が仕様なのか不明



### なぜつらい？😵‍💫* テストが「例外の当てっこゲーム」になりやすい🎮💥

### 最短の直し方🔧* 中心は「扱いやすい結果（成功/失敗）

」に寄せる


* 例外→結果の変換は境界でやる（第26章で本格的にやるよ🔁🧯）

---

## 10) タイマー/リトライ直書き⏳🔁😵### 見つけ方👀* setTimeout / setInterval / sleep 的な待ちが混ざる



### なぜつらい？😵‍💫* テストが遅い＆時間に依存して不安定🧊

### 最短の直し方🔧* Scheduler（待ち）

を注入して、テストでは即時実行にする⚡

---

## 臭い→境界の“変換表”🗺

️✨（覚えやすいやつ）* 時刻 ⏰ → Clock（nowだけ）


* 乱数 🎲 → Random（nextだけ）
* HTTP 🌐 → ApiClient（必要な取得だけ）
* DB 🗄️ → Repository（必要な保存/取得だけ）
* ファイル 📁 → FileGateway（読み書き）＋中心は解析だけ
* 設定 ⚙️ → Config（起動時にまとめて注入）
* ログ 📝 → Logger（必要なinfo/errorだけ）

---

## ハンズオン🖍️

🔥：赤ペンで臭い探し（答え付き）## お題コード（臭いだらけ版）

😈「どこが臭いか」を5個以上見つけて、境界候補を言ってみて〜！



```ts
export async function decideCoupon(userId: string) {
  const mode = process.env.APP_MODE;            // (A)
  const now = new Date();                       // (B)

  console.log("start", userId);                 // (C)

  const res = await fetch(`https://api.example.com/users/${userId}`); // (D)
  const user = await res.json();

  if (mode === "prod" && Math.random() < 0.2) { // (E)
    return { type: "SPECIAL", at: now.toISOString(), userName: user.name };
  }

  return { type: "NORMAL", at: now.toISOString(), userName: user.name };
}
```

## 例：答え（赤ペンの入れ方）

🖍️✨* (A) 設定（Config）⚙️


* (B) 時刻（Clock）⏰
* (C) ログ（Logger）📝
* (D) HTTP（ApiClient）🌐
* (E) 乱数（Random）🎲

境界の一文例✍️

* 「中心は“ユーザー情報と条件からクーポン種別を決める”だけにして、Config/Clock/Random/Apiは外から渡す」✨

---

## VS Codeで臭いを速攻で見つける小技🔍⚡* 検索で拾う（Ctrl+Shift+F）

🕵️‍♀️



  * new
  * Date / Date.now
  * fetch
  * process.env
  * Math.random
  * console.
  * setTimeout / setInterval

さらに、ESLintのFlat Configがデフォルトになってきてる流れなので、ルールで機械的に炙り出すのも強いよ〜🧯✨([ESLint][3])
（例：no-process-env みたいに「グローバル依存やめてね」ってルールが公式にある）([ESLint][2])

---

## AI（Copilot/Codex）

で臭い検出をブースト🤖🎀### そのままコピペで使えるプロンプト例✨* 「次のコードの“テストしにくい臭い”を最大10個列挙して、各臭いに対してI/O境界（interface候補）

を提案して」


* 「この関数を“中心（純粋ロジック）”と“外側（I/O）”に分離する最小手順を、変更が小さい順に3案出して」
* 「Vitestでテストする前提で、差し替え用のスタブ/スパイ案を作って」
  ※VitestはJestっぽいAPI（vi.fn/vi.mock等）で移行しやすい設計になってるよ〜([Vitest][4])

### AIの回答で気をつける点⚠️

😇* なんでもモックする提案が来たら要注意💥
  → 目的は「境界を作る」ことで、**中心を純粋にする**のが先だよ〜🍰✨

---

## まとめ🎀✨

（この章のゴール感）* 臭い＝「ここ境界にできるよ！」っていう地図🗺️👃


* いきなり大改造じゃなくて、**注入（引数で渡す）**が最短の一手🎁
* 次の章以降で「じゃあ境界どう引く？」をもっと上手にするよ✂️🧠

---

次はこの章の続きとして、あなたの実コード（短めでOK😊）を貼ってくれたら、いっしょに赤ペン入れて「境界候補」を具体化していけるよ〜🖍️✨

[1]: https://nodejs.org/en/blog/announcements/v18-release-announce?utm_source=chatgpt.com "Node.js 18 is now available!"
[2]: https://eslint.org/docs/latest/rules/no-process-env?utm_source=chatgpt.com "no-process-env - ESLint - Pluggable JavaScript Linter"
[3]: https://eslint.org/blog/2025/03/flat-config-extends-define-config-global-ignores/?utm_source=chatgpt.com "Evolving flat config with extends"
[4]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
