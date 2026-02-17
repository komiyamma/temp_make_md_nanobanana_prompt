# 第22章：“共通の入口”を別スタックとして切り出す📦🚪

ここから先は一気に“現実の開発っぽさ”が増えるよ〜😎✨
ポイントは **「入口（80/443）だけを担当する“交通整理係”を、アプリ群から独立させる」** こと！

---

## 1) なんで切り出すの？🤔💡

アプリが増えると、毎回こんなことが起きがち👇😵‍💫

* プロジェクトごとにリバプロ設定をコピペ → **微妙にズレる**
* ポートが競合 → **どれかが起動しない**
* “入口”の設定が散らばる → **直す場所が分からない**

![Monolith vs Separated Architecture](./picture/docker_local_exposure_ts_study_022_01_chaos_vs_hub.png)

そこで…✅
**入口だけを1つのCompose（=別スタック）にして固定化**すると、

* アプリ側は「接続するだけ」になる🔌✨
* 入口の設定が1箇所で済む🧠
* 新アプリ追加が“ラベル足すだけ”みたいな感じで楽になる🎉

---

## 2) 完成イメージ図🗺️🚦

別スタック化すると、こうなるよ👇

![External Network Architecture](./picture/docker_local_exposure_ts_study_022_02_architecture_diagram.png)

```text
(ブラウザ)
  │  http://app1.localhost
  ▼
[ proxyスタック（入口） ]  ← ここだけが 80/443 を公開🚪
  │
  ├──> [ app1スタック ]（Vite/Next等）
  ├──> [ apiスタック ]（Express/Fastify等）
  └──> [ adminスタック ]（管理画面）
     ↑ 全部「同じ共有ネットワーク」に参加してるだけ
```

この「同じ共有ネットワーク」が今回の主役！🧩✨
Composeは普通、プロジェクトごとに**別ネットワーク**を作るから、そのままだと別スタック同士は繋がりにくいんだよね。([Docker Documentation][1])

---

## 3) 仕組みのキモ：external network（共有ネットワーク）🧠🧵

やることは超シンプル👇

* 共有ネットワーク（例：`rp`）を **一回だけ作る**
* proxyスタックも、各アプリスタックも、**そのネットワークに参加する**
* すると proxy から各アプリへ通信できる🎯

Composeには **external: true** って仕組みがあって、
「そのネットワークは“このComposeの外”で管理されてるよ（だから勝手に作らないよ）」って指定できるよ。([Docker Documentation][1])
（ネットワークが存在しないとエラーになるのも大事ポイント！）([Docker Documentation][1])

![External Network Logic](./picture/docker_local_exposure_ts_study_022_03_external_network.png)

---

## 4) ハンズオン：proxyスタックを切り出して、appスタックを接続する🚀🐳

ここでは **Traefik** で作る例にするね（ラベル運用が気持ちいいやつ😺）
Traefikは「Dockerのネットワークをどれ使う？」も設定できるよ。([doc.traefik.io][2])

---

## Step A：共有ネットワークを作る🧵✨

まずは1回だけ！

```powershell
docker network create rp
docker network ls
```

✅ これで `rp` という共有ネットワークが“土台”として存在する状態！

![Creating Shared Network](./picture/docker_local_exposure_ts_study_022_04_create_network.png)

---

## Step B：proxyスタック（入口専用Compose）を作る🚪📦

フォルダ例（雰囲気でOK）👇

```text
repo/
  infra/
    proxy/
      compose.yaml
```

`infra/proxy/compose.yaml`（最低限の入口）👇

```yaml
services:
  traefik:
    image: traefik:v3.6
    command:
      - --providers.docker=true
      - --providers.docker.exposedByDefault=false
      - --providers.docker.network=rp
      - --entrypoints.web.address=:80
      - --log.level=INFO
    ports:
      - "80:80"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    networks:
      - rp

networks:
  rp:
    external: true
    name: rp
```

* `providers.docker.network=rp` → 「基本はrpネットワークで繋ぎに行く」指定だよ。([doc.traefik.io][2])
* `docker.sock` をマウント → TraefikがDockerのコンテナ情報（ラベル）を読めるようにするやつ。([doc.traefik.io][2])
* `external: true` + `name: rp` → さっき作った共有ネットワークに参加。([Docker Documentation][1])

![Proxy Stack Connection](./picture/docker_local_exposure_ts_study_022_05_proxy_connection.png)

起動！

```powershell
cd infra/proxy
docker compose up -d
docker compose ps
```

---

## Step C：アプリ側スタックを「rp に参加」させる🔌✨

フォルダ例👇

```text
repo/
  apps/
    app1/
      compose.yaml
```

`apps/app1/compose.yaml`（例：Vite devサーバーを proxy 経由で見せる）👇

```yaml
services:
  app1:
    image: node:24
    working_dir: /app
    volumes:
      - .:/app
    command: bash -lc "npm ci && npm run dev -- --host 0.0.0.0 --port 5173"
    expose:
      - "5173"
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.app1.rule=Host(`app1.localhost`)"
      - "traefik.http.routers.app1.entrypoints=web"
      - "traefik.http.services.app1.loadbalancer.server.port=5173"
      - "traefik.docker.network=rp"
    networks:
      - rp
      - app1_internal

networks:
  rp:
    external: true
    name: rp

  app1_internal:
    name: app1_internal
```

ここ、気持ちいいポイントだけ覚えてね😺✨

* `ports:` は付けない（入口はproxyだけにしたい！）🚫
* `expose:` は「コンテナ内では開ける」って宣言（rpネットワークから見える）🔓
* アプリは **rp と internal** の2つに参加

  * internal：アプリ内のDBとかRedisとか用（あとで活きる）🧊
  * rp：入口（proxy）から到達させるため🚪
* `traefik.docker.network=rp` を書くと「どのネットワークのIPに向かう？」が安定するよ。([doc.traefik.io][2])

![Dual Network Interfaces](./picture/docker_local_exposure_ts_study_022_06_dual_network.png)

起動！

```powershell
cd apps/app1
docker compose up -d
docker compose ps
```

ブラウザで `http://app1.localhost` を開けたら勝ち🏆🎉
（hostsは前の章で作った前提の流れでOK👌）

---

## 5) よくある事故と直し方🧯📕😇

## 事故①：`network rp not found` って怒られる😵

👉 共有ネットワークを作り忘れ！
→ Step A を実行（`docker network create rp`）
external network は「存在してないとダメ」って仕様だよ。([Docker Documentation][1])

![Network Not Found Error](./picture/docker_local_exposure_ts_study_022_07_network_missing_error.png)

---

## 事故②：proxyは起きてるのに 404 / 502 になる😇

切り分けはこれ👇

* 404：ルールが合ってない（Host名ミス・router名ミス）📝
* 502：中が見つからない（ポート違い・ネットワーク未接続・コンテナ落ちてる）🧱

チェック手順（超効くやつ）🕵️‍♂️✨

```powershell
docker ps
docker logs <proxyのコンテナ名>
docker logs <appのコンテナ名>
docker network inspect rp
```

`rp` に proxy と app が両方いるか確認！

---

## 事故③：別スタックなのに「同じ名前のネットワーク」になってない😵‍💫

👉 ここで効くのが `name: rp` ！
Composeは通常、プロジェクト名スコープでネットワーク名が変わりやすいけど、`name` はそのままの名前で使えるよ。だから共有が安定する！([Docker Documentation][1])

---

## 6) AIに頼むと爆速になるところ🤖⚡

## 🧠 “新しいアプリを追加したい” とき

AIにこう投げると早い👇

* 「今の構成（proxyスタック＋external network rp）に app2 を追加したい。`app2.localhost` でVite(5174)を見せる compose.yaml を作って」
* 「Traefikのlabelsだけ増やす形で、既存のテンプレから事故りにくい差分にして」

## 🧯 404/502 で詰まったとき

* 「今の compose.yaml と logs を貼るから、404/502の原因候補を優先度順に出して。まず“rpネットワーク未接続”と“port違い”を疑って」

---

## 7) ミニ課題（15〜25分）🎒✨

## 課題A：app2 を追加して共存させよう🧩

* app2スタックを作って `app2.localhost` にルーティング
* app1とapp2で **ports競合ゼロ** を維持できたら成功🎉

## 課題B：internalネットワークの意味を体感🧊

* app1側に簡単なDB（例：postgres）を足して、**app1_internal だけ**に繋げる
* proxyからDBが見えない状態を作れたら勝ち🏆

---

## まとめ🎯✨

この章でやったのは、実質これだけ👇

* **入口（proxy）を別スタック化**して固定化📦🚪
* **external network（rp）で全スタックをゆるく接続**🧵
* アプリ追加を「接続＋ラベル」で増やせる状態にした🎉

次（第23章）はこの設計をさらに整理して、**プロジェクトが増えても喧嘩しないネットワーク設計**に入っていくよ〜🥊🚫✨

[1]: https://docs.docker.com/reference/compose-file/networks/ "Networks | Docker Docs"
[2]: https://doc.traefik.io/traefik/reference/install-configuration/providers/docker/ "Traefik Docker Documentation - Traefik"
