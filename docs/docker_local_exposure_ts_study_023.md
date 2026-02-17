# 第23章：複数プロジェクトを同居させるためのネットワーク設計🧵🧠

この章は「AプロジェクトとBプロジェクトを同時に立ち上げても、ネットワーク周りで喧嘩しない🥊🚫」を作る回だよ〜！
結論から言うと、**“入口（リバプロ）用の共有ネットワーク” を1本だけ外出し（external）して、各プロジェクトはそこに必要なサービスだけ参加させる**のが、いちばん事故りにくいです💡✨ ([Docker Documentation][1])

---

## 23.1 まずは「ネットワーク」を1枚の絵で理解する🖼️🐳

Dockerネットワークは超ざっくり言うと「**コンテナ用のLAN（スイッチ）**」です🔌
同じネットワークに繋いだコンテナ同士は、**サービス名で通信できる**（= 名前解決が効く）から、リバプロが楽になります😊 ([Docker Documentation][1])

イメージ👇

* `internal(A)`：Aプロジェクトの中だけで完結するLAN
* `internal(B)`：Bプロジェクトの中だけで完結するLAN
* `edge(shared)`：入口（リバプロ）と、外に見せたいサービスだけが繋がる共有LAN

![Network Topology (Edge vs Internal)](./picture/docker_local_exposure_ts_study_023_01_network_topology.png)

```text
          (ブラウザ) 🧑‍💻🌐
                |
             localhost:80/443
                |
         [ Reverse Proxy ] 🚪✨
                |
         edge(shared) 🧵  ← 共有ネットワーク（external）
          /        \
   (Aのweb/api)   (Bのweb/api)
      |              |
 internal(A)      internal(B)
  /   |   \         /   |   \
db  redis  etc    db  redis  etc
(外から触らせない)   (外から触らせない)
```

---

## 23.2 「何が喧嘩の原因？」を先に潰す😵‍💫🧯

複数プロジェクト同居でよくある地雷はこの3つ💣

1. **ネットワーク名が衝突**する

* Composeはデフォルトでプロジェクトごとにネットワークを作るけど、その名前は “プロジェクト名” に依存します📛
* プロジェクト名はディレクトリ名ベースだったり、`-p` / `COMPOSE_PROJECT_NAME` / さらにトップレベル `name:` でも変えられます🧩 ([Docker Documentation][2])

![Network Name Conflict](./picture/docker_local_exposure_ts_study_023_02_network_conflict.png)

2. **externalにするべき共有ネットワークを、各プロジェクトが作ろうとして揉める**

* 「共有したいのに、それぞれ別物を作ってる」状態になりがち😇
* 共有したいネットワークは **`external: true`** を使って “既存のネットワークに参加” させるのが安全です✅ ([docs.docker.jp][3])

3. **何でもかんでも共有ネットワークに繋いで、境界が消える**

* DBやRedisまで `edge(shared)` に繋ぐと「別プロジェクトから触れちゃう」事故が起きます🥶
* 共有は **入口に必要なサービスだけ** に絞るのが鉄則👍✨

---

## 23.3 ベストプラクティス：共有ネットワークは「1本だけ」外出しする🧵🚪

ここから実践！
やることはシンプルで、こう👇

1. 共有ネットワーク（例：`dev-edge`）を **先に作る**
2. リバプロ側はそのネットワークに繋ぐ
3. 各プロジェクトは “公開したいサービスだけ” をそのネットワークに繋ぐ
4. プロジェクト内部は `internal` で閉じる

ポイント：Composeの `networks:` には **`name:`** があって、これを使うと「プロジェクト名でスコープされない固定名」にできます📌

![Setup Process Flowchart](./picture/docker_local_exposure_ts_study_023_03_setup_process.png)

しかも `external` と一緒に使うのが定番！✨ ([Docker Documentation][1])

---

## 23.4 ハンズオン：共有ネットワーク `dev-edge` を作って、A/Bを同居させる🛠️🎮

## STEP0：共有ネットワークを作る（最初に1回だけ）🧵✨

PowerShell（またはVS Codeのターミナル）でOK！

```bash
docker network create dev-edge
docker network ls
```

`dev-edge` が見えたら成功🎉

> ✅ `external: true` を使う場合、このネットワークが存在しないと Compose はエラーになります（「既存のやつ探して繋ぐ」動作だから） ([docs.docker.jp][3])

---

## STEP1：入口（proxy）スタックの compose.yaml 🧯🚪

例として、ここでは “proxy専用プロジェクト” を想定（第22章の続きのノリ）📦
**大事なのは networks の書き方だけ**だから、リバプロはTraefikでもCaddyでもOKだよ👍

`proxy/compose.yaml`（例）

```yaml
name: proxy

services:
  proxy:
    image: traefik:v3.6
    command:
      - --api.dashboard=true
      - --providers.docker=true
      - --providers.docker.exposedbydefault=false
      - --entrypoints.web.address=:80
    ports:
      - "80:80"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    networks:
      - edge

networks:
  edge:
    name: dev-edge
    external: true
```

* `name: proxy` は “プロジェクト名” を明示するためのやつ（複数同居で効く）🧷 ([Docker Documentation][4])
* `networks.edge.name: dev-edge` は **固定名**（プロジェクト名で変化しない）📌 ([Docker Documentation][1])
* `external: true` で **既存 dev-edge を使う**🧵 ([docs.docker.jp][3])

![Proxy Connection to Edge](./picture/docker_local_exposure_ts_study_023_04_proxy_edge.png)

起動：

```bash
cd proxy
docker compose up -d
```

---

## STEP2：プロジェクトAの compose.yaml（internal + edge）🅰️🧩

`project-a/compose.yaml`（例：front + api + db）

```yaml
name: project-a

services:
  front:
    image: node:24
    working_dir: /app
    volumes:
      - ./:/app
    command: bash -lc "npm ci && npm run dev -- --host 0.0.0.0 --port 5173"
    networks:
      - internal
      - edge
    labels:
      - traefik.enable=true
      - traefik.http.routers.a-front.rule=Host(`a.localhost`)
      - traefik.http.services.a-front.loadbalancer.server.port=5173

  api:
    image: node:24
    working_dir: /app
    volumes:
      - ./api:/app
    command: bash -lc "npm ci && npm run dev -- --host 0.0.0.0 --port 3000"
    networks:
      - internal
      - edge
    labels:
      - traefik.enable=true
      - traefik.http.routers.a-api.rule=Host(`api-a.localhost`)
      - traefik.http.services.a-api.loadbalancer.server.port=3000

  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: postgres
    networks:
      - internal

networks:
  internal: {}
  edge:
    name: dev-edge
    external: true
```

ここでの設計意図💡

* `db` は **internalだけ**（外から見せない）🧊
* `front/api` は **internal + edge**（内部連携もしつつ、入口にも出す）🚪✨

  ![App Service Isolation](./picture/docker_local_exposure_ts_study_023_05_app_isolation.png)

* “同じネットワーク上だとサービス名で見つけられる” のがComposeの基本感覚です👍 ([Docker Documentation][1])

起動：

```bash
cd project-a
docker compose up -d
```

---

## STEP3：プロジェクトBも同じ作法で🅱️🌈

`project-b/compose.yaml` も同様に `internal` と `edge(external)` を持たせて、公開したいサービスだけ `edge` に参加させます✨
（ホスト名は `b.localhost` とかに変えるだけ！）

---

## 23.5 動作チェック：今、誰が dev-edge に繋がってる？🕵️‍♂️🔍

「ほんとに共有できてる？」を確認しよう！

```bash
docker network inspect dev-edge
```

`Containers` のところに

* proxyの `proxy`
* Aの `front/api`
* Bの `front/api`

みたいに並んでたら勝ちです🏆✨

![Network Inspect Visualization](./picture/docker_local_exposure_ts_study_023_06_network_inspect.png)

---

## 23.6 よくあるミス集（ここ超大事）📕🧯

## ミス1：`external: true` を書いたのにネットワークが無い😇

症状：`network dev-edge declared as external, but could not be found` 的なエラー
対処：先に作る！

```bash
docker network create dev-edge
```

（これは仕様どおりだよ〜） ([docs.docker.jp][3])

---

## ミス2：`name: dev-edge` を書かず、プロジェクトごとに別ネットワークになってた😵‍💫

症状：Aとproxyが同じ “edge” って書いてるのに通信できない
原因：内部的には `project-a_edge` と `proxy_edge` みたいに別物になってるパターン
対処：共有したい方は **`name:` で固定名** にする📌 ([Docker Documentation][1])

![Network Name Scoping](./picture/docker_local_exposure_ts_study_023_07_name_scope.png)

---

## ミス3：DBまで `edge` に繋いでしまった🥶

症状：BからAのDBに繋げられちゃう（やろうと思えば）
対処：`db` は **internalだけ** に戻す🍵✨

---

## ミス4：プロジェクト名が意図せず変わって、ネットワーク名やボリューム名がブレる📛

原因：ディレクトリ名ベースでスコープされるから、場所を変えると変わることがある
対処：トップレベル `name:` / `-p` / `COMPOSE_PROJECT_NAME` を使って安定化🧷 ([Docker Documentation][4])

---

## 23.7 ミニ課題🎯🧪（手を動かすと一気に定着する）

## 課題A：A/B/Cを同居させてみよう🧩🧩🧩

* `dev-edge` に参加するのは `front` だけにして、`api` は internal のみにする
* その代わり `front` → `api` は **internal上でサービス名**（例：`http://api:3000`）で叩く

狙い：**公開境界を “最小” にする感覚** を作る✨

---

## 課題B：2つの “入口” を作ってみよう🚪🚪（上級の入口）

* `dev-edge-a` と `dev-edge-b` を作る
* proxyを2つ立てるか、entrypointを分けるか、好きな方で

狙い：**チーム開発や複数案件の現場っぽい分離** を体験🔥

---

## 23.8 AIに聞くと爆速になる「質問テンプレ」🤖⚡

コピペで使ってOK！

* 「ComposeでA/Bプロジェクトを同居させたい。共有external network `dev-edge` を使う構成で、**dbはinternalのみ**にして、Traefikラベルも含めた `compose.yaml` を作って」
* 「`docker network inspect dev-edge` の結果を貼るから、**どこが繋がってないか** 推理して」
* 「`name:` / `COMPOSE_PROJECT_NAME` / `-p` の優先順位を、今回の構成に当てはめて説明して」 ([Docker Documentation][5])

---

## 23.9 章末チェックリスト✅✨

* [ ] 共有ネットワーク `dev-edge` を先に作った🧵
* [ ] proxy は `dev-edge (external)` に繋がってる🚪
* [ ] 各プロジェクトは `internal` を持ってる🏠
* [ ] `edge` に繋ぐのは “公開したいサービスだけ” に絞った🧊
* [ ] `name:` でネットワーク名が固定されてる📌 ([Docker Documentation][1])

---

次の章（第24章）は、この設計と相性抜群の **「ポート競合を永久に起こさないコツ📛🔒」** に行けるよ〜！
今の構成ができてると、24章がめちゃ気持ちよく進みます😄🚀

[1]: https://docs.docker.com/reference/compose-file/networks/?utm_source=chatgpt.com "Networks"
[2]: https://docs.docker.com/compose/how-tos/networking/?utm_source=chatgpt.com "Networking in Compose"
[3]: https://docs.docker.jp/compose/networking.html?utm_source=chatgpt.com "Compose の ネットワーク機能(networking) — Docker-docs-ja ..."
[4]: https://docs.docker.com/reference/compose-file/version-and-name/?utm_source=chatgpt.com "Version and name top-level elements"
[5]: https://docs.docker.com/reference/cli/docker/compose/?utm_source=chatgpt.com "docker compose"
