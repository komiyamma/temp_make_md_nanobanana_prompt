# 第01章：まずは困りごとを言語化しよう😵‍💫🔌

この章は「リバースプロキシの設定」をまだしません🙅‍♂️
その代わりに、**“何が辛いのか”と“どうなったら勝ちか”**をハッキリさせて、次章以降の作業がスムーズに進む状態を作ります🧠✨

---

## 1) いま起きがちな “地獄” を、ちゃんと名前で呼ぶ😇🔥

![Localhost Port Hell](./picture/docker_local_exposure_ts_study_001_01_hell.png)

ローカル開発って、気づくとこうなりません？👇

* フロント：`http://localhost:5173`
* API：`http://localhost:3000`
* 管理画面：`http://localhost:3001`
* 別プロジェクト：`http://localhost:5174`
* さらに別：`http://localhost:8787`
* もう何が何だか…🤯

しかもつらいのは「URLが多い」だけじゃないんです👇

* **ポート競合**：別アプリ起動したら `3000` が埋まってて死ぬ💥
* **ブックマークが地獄**：`localhost:5173` がどのプロジェクトか分からない📌😵
* **CORSが出る**：フロントとAPIの“出どころ”が違う扱いになって揉める🧨
* **Cookie/ログインがややこしい**：ドメインやSameSiteで詰みがち🍪💣
* **説明しづらい**：「ブラウザで5173開いて、次に3000で…」が面倒📣😮‍💨

---

## 2) ゴールはこれ：「URLが人間の脳にやさしい」🧠💕

![Meaningful URLs Goal](./picture/docker_local_exposure_ts_study_001_02_goal.png)

この教材のゴール（ローカル公開の整理）を、まず一言で言うと👇

✅ **入口を整理して、URLを“意味がわかる形”にすること**

イメージはこれです👇

![Before vs After Entry Points](./picture/docker_local_exposure_ts_study_001_03_before_after.png)

**Before（入口がバラバラ）**

* ブラウザ → `localhost:5173`（フロント）
* ブラウザ → `localhost:3000`（API）
* ブラウザ → `localhost:3001`（管理）

**After（入口が1つでスッキリ）**

* ブラウザ → `front.localhost`（フロント）
* ブラウザ → `api.localhost`（API）
* ブラウザ → `admin.localhost`（管理）

入口が整理できると、次が一気に楽になります🎉

* **ポートを覚えなくていい**🧠✨
* **同じPCで複数アプリ共存がラク**🏘️🏘️🏘️
* **本番っぽいURL設計に寄せられる**🚀
* **CORS/Cookie問題が減りやすい**🧹🍪

> 補足：WindowsのDocker環境は、Docker Desktop＋WSL2エンジンが基本ルートなので、ホスト側の“公開ポート”設計が散らかると事故りやすいです🪟🐳
> （だからこそ「入口の整理」が効きます）([Docker Documentation][1])

---

## 3) “リバースプロキシ” を超ざっくり一言で言うと🚪➡️🏠

![Reverse Proxy Traffic Cop](./picture/docker_local_exposure_ts_study_001_04_traffic_cop.png)

リバースプロキシは、こういう人です👇

> **「来たリクエストを受け取って、適切なアプリに振り分ける交通整理係」**🚥🙂

```text
ブラウザ
  │
  ▼
（共通の入口）リバースプロキシ 🚪🚥
  │          │          │
  ▼          ▼          ▼
フロント     API       管理画面
```

そして次章以降で、Compose（Compose Specificationベース）でこの“入口”を作っていく感じです🧩✨
([Docker Documentation][2])

---

## 4) まず作る成果物：「公開マップ」🗺️✨（これが設計の第一歩！）

![The Public Map Blueprint](./picture/docker_local_exposure_ts_study_001_05_public_map.png)

“設計が初めて”の人でも大丈夫🙆‍♂️
ここでは難しい言葉は捨てて、**表にして見える化**します📄✨

✅ これを埋めたら勝ちです👇

```md
| 種類 | 役割 | いまのURL | いまの起動方法 | いま困ってること | 理想のURL候補 |
|---|---|---|---|---|---|
| Front | 画面 | http://localhost:5173 | npm run dev | ポート覚えられない | front.localhost |
| API | データ | http://localhost:3000 | npm run dev | CORSが出る | api.localhost |
| Admin | 管理 | http://localhost:3001 | npm run dev | Cookieが… | admin.localhost |
```

ポイントはここ👇

* **「役割」**を1行で言えるようにする（例：画面 / API / 管理）🧠
* **「困ってること」**を“症状”で書く（例：CORSエラーが出る）🧯
* **「理想のURL候補」**はとりあえず案でOK（あとで変えられる）🧪

---

## 5) “勝ち”の定義を決める🏁✨（ふわっとした努力を卒業）

![Win Conditions](./picture/docker_local_exposure_ts_study_001_06_win_condition.png)

ここ、めちゃ大事です💡
ゴールが曖昧だと、設定をいじってるうちに迷子になります😵‍💫

この章では、次の3つを決めます👇

### ✅ (A) 何を減らしたい？（痛みの数値化）📉

例：

* 覚えるURLを **6個 → 3個** に減らしたい🙂
* 外に出すポートを **3個 → 1個** にしたい🔒

### ✅ (B) どう見えたら成功？（見た目の完成形）👀

例：

* ブラウザで `front.localhost` を開いたら画面が出る🎉
* `api.localhost/health` でAPIの生存確認ができる🫀

### ✅ (C) 何はやらない？（スコープ固定）🧱

例：

* この段階では「本番デプロイ」はやらない🙅‍♂️
* まずはHTTPでOK、HTTPSは後で🔐（必要になったらやる）

---

## 6) よくあるミス集😇（先に踏んでおくと強い）

![Common Pitfalls](./picture/docker_local_exposure_ts_study_001_07_pitfalls.png)

* **ミス①：いきなりツール選定しちゃう**（Nginx？Caddy？Traefik？）🧰💥
  → 先に「公開マップ」と「勝ちの定義」！それが先！🗺️🏁

* **ミス②：URL設計が“気分”になる**🎲
  → 命名ルールを1行で決めるだけで、未来が救われます🧱✨
  例：`front.localhost / api.localhost / admin.localhost`

* **ミス③：困りごとを“感想”で書く**（例：なんかダルい）😇
  → “症状”にする：`CORSが出る / ポートが被る / ブクマが混乱` みたいに🧯

---

## 7) AIに聞く例🤖✨（設計が初めてでも進められる魔法）

そのままコピペで使えるやつを置いときます📎😊

**公開マップ整理（棚卸し）**

```text
あなたはローカル開発環境の設計アシスタントです。
下の「サービス一覧」を、(1)役割の整理、(2)URL命名案、(3)入口を1つにする場合の最短ゴール
の3点で提案してください。

サービス一覧：
- Front: localhost:5173 (Vite)
- API: localhost:3000 (Node)
- Admin: localhost:3001
```

**“勝ちの定義”を作る**

```text
ローカル公開の整理をしたいです。
次の条件で「成功条件」を3つ、数値つきで提案してください：
- 覚えるURLを減らしたい
- ポート競合をなくしたい
- CORSやCookieの事故を減らしたい
```

**命名ルール案を複数出してもらう**

```text
front/api/admin の3サービスがあります。
人間が覚えやすく、将来サービスが増えても破綻しない命名ルール案を
(サブドメイン方式 / パス方式)でそれぞれ3案ずつください。
```

---

## 8) ミニ課題🧪✨（この章のゴール達成チェック✅）

次の3つをやってみてください🙂🎯

1. **公開マップ（表）を埋める**🗺️
2. **困りごとを3つ、症状として書く**🧯

   * 例：`ポート競合で起動できない` / `CORSエラーが出る` / `URL覚えられない`
3. **“勝ちの定義”を1文で書く**🏁

   * 例：**「入口は1個、URLは3つ、ポートは覚えない」**✨

---

## 9) ちょい最新メモ（2026-02時点）🧾🆕

この教材では“最近の標準”の上で進めます（ここは事実メモだけ）🙂

* Composeは **Compose Specification が最新かつ推奨**という整理です🧩([Docker Documentation][2])
* WindowsのDockerは **Docker Desktop＋WSL2** が基本ルートです🪟🐳([Docker Documentation][1])
* Nodeは **v24 がActive LTS、v25 がCurrent** の状態です🟢([Node.js][3])
* TypeScriptは **5.9系のリリースノート更新が継続**、そして **6.0 Betaの告知が出ています**🧠✨([typescriptlang.org][4])

---

次に進む準備はこれでOKです🎉
もしよければ、あなたの「公開マップ（表）」を貼ってください📄✨
それを材料にして、**第2章の“完成形イメージ図”**を一緒に作ります🗺️🚀

[1]: https://docs.docker.com/desktop/features/wsl/?utm_source=chatgpt.com "Docker Desktop WSL 2 backend on Windows"
[2]: https://docs.docker.com/reference/compose-file/?utm_source=chatgpt.com "Compose file reference"
[3]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[4]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html?utm_source=chatgpt.com "Documentation - TypeScript 5.9"
