# 第09章：Dockerネットワークの超復習🌐🐳

この章でやることはシンプルだよ👇
**「コンテナ同士は“同じネットワークにいると、名前で通信できる”」**を体に染み込ませます💪✨
これが分かると、リバースプロキシは **“名前に流すだけ”** の世界になる👍

（Compose のネットワークは、基本的に「プロジェクトごとにデフォルトネットワークが1個できて、サービス名で見つけられる」って挙動が土台だよ〜）([Docker Documentation][1])

---

## 1) まずは“3つの世界”を分けよう🌍🧠

![_01_three_localhosts](./picture/docker_local_exposure_ts_study_009_01_three_localhosts.png)

Dockerで混乱する最大の原因はこれ👇
**「localhost が誰の localhost なのか」**が毎回変わること😵‍💫

| あなたがいる場所     | `localhost` が指すもの | 例                              |
| ------------ | ----------------- | ------------------------------ |
| ブラウザ（ホスト側）🪟 | ホストPC自身           | `http://localhost:5173`        |
| コンテナAの中🐳    | コンテナA自身           | コンテナAで `curl http://localhost` |
| コンテナBの中🐳    | コンテナB自身           | コンテナBで `curl http://localhost` |

なので、**コンテナAからコンテナBへ行くときに `localhost` を使うのはだいたい事故**です💥
代わりに使うのが **“サービス名（＝名前）”** だよ✨([Docker Documentation][1])

---

## 2) “ネットワーク”は「同じ部屋」だと思おう🏠🧵

![_02_network_rooms](./picture/docker_local_exposure_ts_study_009_02_network_rooms.png)

Dockerネットワークは、ざっくり言うと👇

* 同じネットワーク＝同じ部屋にいる🧑‍🤝‍🧑
* 別ネットワーク＝部屋が違う（基本会えない）🚪🚫
* 同じ部屋だと、**名前で呼べる（サービスディスカバリ）**📛✨

特に大事なのがここ👇
**ユーザー定義ネットワークでは、コンテナは“コンテナ名/サービス名”で通信できる**（IP直打ちじゃなくてOK）([Docker Documentation][2])

---

## 3) Composeの“デフォルトネットワーク”超重要ポイント✅

![_03_compose_default](./picture/docker_local_exposure_ts_study_009_03_compose_default.png)

Compose は基本こう動きます👇

* プロジェクトを立ち上げると、**そのプロジェクト専用のネットワーク**が作られる
* そのネットワーク上で、各サービスは **サービス名で見つけられる**
* ネットワーク名は **プロジェクト名（ディレクトリ名等）**ベースになる（上書きもできる）([Docker Documentation][1])

ここ、後の章で「共通の入口（リバプロ）を別スタックに切り出す」時に効いてくるよ〜🚪✨

---

## 4) 手を動かす：名前でつながるのを体感しよう🧪🔗

## やること🎯

* `web` というサービス（nginx）を立てる
* `tester` から `http://web` にアクセスしてみる
* ついでに「`localhost` 事故」をわざと踏む😇

## `compose.yml` を作る📝

（ファイル名は `compose.yml` でも `docker-compose.yml` でもOK）

```yaml
services:
  web:
    image: nginx:alpine

  tester:
    image: curlimages/curl:8.6.0
    command: ["sleep", "infinity"]
```

## 起動🚀

```bash
docker compose up -d
```

## ✅ “名前でアクセス”してみる

![_04_name_resolution](./picture/docker_local_exposure_ts_study_009_04_name_resolution.png)

```bash
docker compose exec tester curl -I http://web
```

たぶん `HTTP/1.1 200 OK` みたいなのが返るはず🎉
これが **「同じネットワークにいるから、`web` って名前で解決できた」**ってこと！([Docker Documentation][1])

## 💥 わざと事故る：`localhost` を叩く

```bash
docker compose exec tester curl -I http://localhost
```

これはたいてい失敗するか、別の何かになる（= tester自身を見に行く）よね😇
**「コンテナ間通信に localhost は使わない」**が刺さったら勝ち✌️

---

## 5) “つながらないのが正しい”を作れると設計っぽくなる🧠🧱

![_05_isolation_arch](./picture/docker_local_exposure_ts_study_009_05_isolation_arch.png)

ネットワークを分ける＝**安全な壁を作る**ってことです🧱✨
Composeはネットワークを複数作って、サービスを分離できるよ([Docker Documentation][2])

たとえば概念として👇

* `front`：入口側（リバプロ、フロント）🌐
* `back`：内部側（DB、内部API）🔒
* `app` だけが両方に参加して橋渡し🌉

**同じネットワークを共有してないサービス同士は、基本的に会えない**
→ これが「事故の拡大」を止める最小の設計になるよ👍([Docker Documentation][2])

---

## 6) リバプロ視点での“合言葉”🚪➡️🏠

![_06_proxy_bridge](./picture/docker_local_exposure_ts_study_009_06_proxy_bridge.png)

リバプロがやることは、結局これ👇

* 外（ブラウザ）から来たリクエストを受ける🌐
* 中（Dockerネットワーク）にいるサービスへ流す🐳
* **流し先は `http://サービス名:ポート`** で書けると楽✨

つまり、リバプロが `web` に流したいなら
**同じネットワークに入って、`web` という名前が引ける状態**にしておけばOK👌

（Traefik系はラベルで設定を拾う文化が強いけど、どのみち「同じネットワーク上で名前/到達性がある」前提は変わらないよ）([Traefik Labs Documentation][3])

---

## 7) よくある詰まりポイント集📕🧯（超あるある）

## ❶ 502（Bad Gateway）が出る😇

だいたい原因はこれ👇

* 流し先が `localhost` になってる（= リバプロ自身を見に行ってる）💥
* リバプロが相手のいるネットワークに入ってない🚫
* ポートを間違えてる🔢

👉 まずは **同じネットワークにいるか**を確認！

---

## ❷ 「サービス名で引けない」＝ネットワークが違う説が濃厚🕵️

Composeの基本挙動（同一ネットワーク＆サービス名で発見可能）を思い出そう！([Docker Documentation][1])
サービスが複数ネットワークに属する場合もあるので、どこに繋がってるかを見るのが早いよ👀

```bash
docker network ls
docker compose ps
docker network inspect <ネットワーク名>
```

---

## ❸ “別プロジェクト”と共通ネットワークを作ったら名前衝突した😵‍💫

外部ネットワーク（複数Composeで共有）をやると、
**同じサービス名が同じネットワークに存在**しうる⚠️

この時に使うのが **network alias（別名）** なんだけど、注意点があるよ👇

* alias はネットワーク単位
* **同じaliasを複数が共有すると、どれに解決されるか保証されない**（ランダムっぽくなる）([Docker Documentation][4])

👉 なので現場のコツはこれ：

* 共有ネットワークに出すサービス名は **プロジェクト接頭辞付きでユニークに**（例：`shop_api`）
* どうしても共通名が欲しい時だけ alias を慎重に使う🧠

---

## ❹ 急にDNSが死んだっぽい（名前解決が不安定）🌀

まれに **Docker Engine の特定バージョンで embedded DNS 周りの不具合報告**が出ることがあります。
例として、あるバージョン更新で `127.0.0.11` のDNSが壊れたという報告が上がってたよ。([GitHub][5])

👉 対処の“勝ち筋”はだいたいこのへん👇

* Docker Desktop を再起動🔁
* Engine/ Desktop を更新（または問題バージョンを避ける）⬆️
* ネットワーク作り直し（`docker compose down` → `up`）🧹

---

## 8) ここだけ覚えれば勝てる✅✨（ミニ暗記カード）

* コンテナ間通信は **`localhost` じゃない**🧨
* 同じネットワークなら **サービス名で届く**📛([Docker Documentation][1])
* “分離”したいなら **ネットワークを分ける**🧱([Docker Documentation][2])
* リバプロは **同じネットワークに参加して、名前へ流す**🚪➡️🏠

---

## 9) ミニ課題🎒✍️（10〜20分）

## 課題A：`web2` を増やして、名前で叩き分けよう🎯

1. `web2`（nginx）を追加
2. `tester` から `http://web2` にもアクセスしてみる

## 課題B：ネットワーク分離を“わざと”作ってみよう🧱

1. `web` と `tester` を別ネットワークにして起動
2. `http://web` が失敗するのを確認
3. 同じネットワークに戻して復旧！

---

## 10) AIに投げると爆速になる“質問テンプレ”🤖⚡

コピペして使ってOKだよ👇

* 「この compose.yml で `tester` から `web` に繋がらない。**ネットワーク観点**で疑うポイントを順にチェックリスト化して」
* 「リバプロ（Traefik/Caddy/Nginx）が `api` に 502 を出す。**`localhost`事故**を含めて原因候補を優先度順に」
* 「複数Composeで external network を共有したい。**サービス名衝突を避ける命名ルール**を提案して」([Docker Documentation][4])

---

次の章（第10章）では、この“ネットワーク感覚”をそのまま使って、**Composeでのサービス間通信を設計っぽく整理**していくよ🧩🔗
「入口（外）と内部（中）を分けて考える」やつね🚪✨

[1]: https://docs.docker.com/compose/how-tos/networking/?utm_source=chatgpt.com "Networking in Compose"
[2]: https://docs.docker.com/engine/network/?utm_source=chatgpt.com "Networking | Docker Docs"
[3]: https://doc.traefik.io/traefik/providers/docker/?utm_source=chatgpt.com "Traefik Docker Documentation"
[4]: https://docs.docker.com/reference/compose-file/services/?utm_source=chatgpt.com "Define services in Docker Compose"
[5]: https://github.com/moby/moby/issues/51614?utm_source=chatgpt.com "29.1.0 breaks the embedded DNS resolver · Issue #51614"
