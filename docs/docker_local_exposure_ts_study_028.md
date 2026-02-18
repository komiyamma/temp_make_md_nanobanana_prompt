# 第28章：ありがちトラブル辞典：404/502/つながらない📕🧯

エラーって、見た目は怖いけど…😱
**「どこまで届いて、どこで落ちた？」** を順番に見れば、だいたい勝てます💪🐳✨

---

## まず最初にやる“3分トリアージ”🕒🕵️‍♀️

ポイントは **「外（ブラウザ）→入口（リバプロ）→中（アプリ）」** の順で追うことだよ〜🚪➡️🏠

1. **コンテナ生きてる？**（落ちてたら話が終わる🥲）

* `docker compose ps` で STATUS を見る👀
  ([Docker Documentation][1])

2. **入口（リバプロ）にリクエスト来てる？**

* `docker compose logs -f proxy` でアクセスが来てるか確認👂
  ([Docker Documentation][2])

3. **入口が“どこへ流すべきか”分かってる？（= 404系）**

* Traefikなら Router の rule / entrypoints を疑う🧠
  ([Traefik Docs][3])

4. **中（アプリ）に“そもそも繋がる？”（= 502系）**

* proxyコンテナの中から `curl http://api:3000` みたいに直叩きする🎯

5. **名前解決（DNS/hosts）で死んでない？（= つながらない系）**

* `app1.localhost` が引けてるかを確認🧩

この順番、ほんと強いよ🧠✨

![3-Minute Triage Workflow](./picture/docker_local_exposure_ts_study_028_triage_flow.png)

---

## 1) 404 の正体：だいたい「ルールが合ってない」🪧❌

404 は大きく2種類あるよ👇

![Two Types of 404](./picture/docker_local_exposure_ts_study_028_404_types.png)

## A. リバプロが返してる 404（入口で迷子）🚥😵

**特徴**：

* 入口のログに「ルーティングできない」っぽさが出る
* Traefikだと **Routerにマッチしない** と 404 になりがち🐯
  ([Traefik Docs][3])
* 「HTTPで来たのにHTTPS側しか受けてない」みたいな **entrypoint違い** でも 404 に見えることがある👻
  ([GitHub][4])

**ありがち原因トップ5 🥇**

* Host ルールが違う（`app1.localhost` のつもりが `app.localhost` 書いてた）🏷️
* Path ルールが違う（`/api` のつもりが `/api/` だった等）🍰
* 入口のポート/entrypointsが違う（web / websecure）🔐
* ルータ優先度（priority）で別ルールに吸われてる🌀
  ([Traefik Docs][3])
* dashboard系は **URL末尾の `/` 必要** みたいな地味罠もある（特に Traefik ダッシュボードで遭遇しやすい）📊
  ([Stack Overflow][5])

**確認のしかた（最短）⚡**

* リバプロログをフォローして、アクセスが来た瞬間に何が起きてるか見る👂
  ([Docker Documentation][2])
* Traefikなら、labels の router rule を一回 “超シンプル” にする（Hostだけ、Pathだけ）→当たるかチェック🎯
  ([Traefik Docs][6])

---

## B. アプリが返してる 404（中には届いてるけど、そのURLが無い）🏠🤷

**特徴**：

* リバプロのログには upstream に流した形跡がある
* API のエンドポイントが違う / SPAルーティングが崩れてる など

**よくある例🍰**

* SPAを `/app1/` 配下に置いたのに、アプリ側が `/` 前提でリンクを吐く（base path 問題）🔁
* APIの prefix が変わったのにフロントが古いURLを叩いてる📦

![SPA Base Path Mismatch](./picture/docker_local_exposure_ts_study_028_spa_base_path.png)

**確認のしかた（気持ちいい）😆**

* proxyコンテナ内から upstream を直叩き：

  * `curl -i http://front:5173/`
  * `curl -i http://api:3000/health`
    → ここで 200 が返れば「中は生きてる」確定✨

---

## 2) 502 の正体：だいたい「中のサービスに繋げてない」🔌💥

502（Bad Gateway）は、入口が「中に繋ごうとしたけど無理だった😭」の合図。

![502 Connection Failure](./picture/docker_local_exposure_ts_study_028_502_connection.png)

## Caddyの 502 は“接続エラー起点”が多い🧯

Caddy の `reverse_proxy` は upstream へ繋げない状況などで 502 を返すことがあるよ。([Caddy Web Server][7])
（そして、こういう 502 は “上流が 502 を返した” とは限らないのが罠😇）

---

## 502 の“あるある原因”ベスト7 🥇🥈🥉

1. **ポートの勘違い（いちばん多い）** 🔢

* 入口が見るのは **「コンテナ内ポート」** が基本
* `ports: "8080:80"` の `8080` は **ホスト側**、`80` が **コンテナ側** 🧠

2. **`localhost` 罠（コンテナ内の localhost は自分自身）** 🪤

* proxyコンテナから見た `localhost:3000` は「proxy自身」だよ😇
* だいたい `api:3000` みたいに **サービス名** を使うのが正解✅

![The Localhost Trap in Containers](./picture/docker_local_exposure_ts_study_028_localhost_trap.png)

3. **同じネットワークにいない** 🧵

* プロジェクト分割（proxyスタックを別compose）した時に起きやすい
* external network がズレてると繋がらない🧨

4. **サービスが落ちてる / 起動に失敗してる** 🪦

* `docker compose ps` で `exited` とかになってる
  ([Docker Documentation][1])

5. **起動はしてるけど“準備できてない”（DB待ち等）** ⏳

* 入口が先に投げて死ぬ
* logs で起動順・依存を読む👂
  ([Docker Documentation][2])

6. **TLS/HTTPS の向き先を間違えた** 🔐

* upstream が HTTP なのに `https://` で繋ぎに行って死亡…など

7. **keepalive / タイムアウト系で切断** 🧵✂️

* upstreamのkeepalive設定次第で “connection reset” が出て 502 になることもある（Caddy docsでも注意されてる）([Caddy Web Server][7])

---

## 502 の切り分け“必殺技”⚔️：入口から中を直叩きする🎯

「ブラウザ→入口」じゃなくて、**「入口→中」** を直接テストするのが最強！

* proxyコンテナの中に入って確認
* そこで `curl` が通らないなら、ルーティング以前に“接続”が死んでる💀

![Direct Hit Troubleshooting](./picture/docker_local_exposure_ts_study_028_direct_hit.png)

---

## 3) 「つながらない」の正体：入口まで届いてない🚪🙅‍♀️

これはブラウザ側で👇みたいになるやつ：

* 画面が真っ白 / タイムアウト⌛
* `ERR_NAME_NOT_RESOLVED`（名前解決できない）🧩
* `ERR_CONNECTION_REFUSED`（ポートが閉じてる）🔒

![Connection Refused](./picture/docker_local_exposure_ts_study_028_connection_refused.png)

## つながらない原因あるある🧊

1. **DNS/hosts が違う** 📝

* `app1.localhost` を打ってるのに、そもそもその名前が 127.0.0.1 に向いてない
* まずは PowerShell で名前解決チェック👀

2. **80/443 が開いてない** 🔌

* proxy が落ちてる / ports が書かれてない / 別アプリが先に使ってる（ポート競合）💥

3. **Docker Desktop / WSL2 周りが不調** 🪟🐧

* Windows は Docker Desktop + WSL2 が基本ルートなので、WSL統合や状態が崩れると全体が変な挙動になりがち😵‍💫
  ([Docker Documentation][8])

---

## 4) すぐ使える“コマンド辞典”📚💨

## A. まず生存確認🫀

```bash
docker compose ps
```

（STATUS と PORTS を見る）([Docker Documentation][1])

## B. ログを見る👂

```bash
## 入口（proxy）だけ追うのがコツ！
docker compose logs -f proxy

## APIだけ、フロントだけ、みたいに絞るのもOK
docker compose logs -f api
```

([Docker Documentation][2])

## C. Windows（PowerShell）で疎通の基本チェック🪟🔍

```powershell
## 名前解決（DNS）
Resolve-DnsName app1.localhost

## 80番が空いてる/繋がるか（入口確認）
Test-NetConnection -ComputerName 127.0.0.1 -Port 80
Test-NetConnection -ComputerName 127.0.0.1 -Port 443
```

## D. “入口→中”を直叩き（超重要）🎯

```bash
## 例：proxyコンテナに入る（シェルは環境により sh / bash）
docker compose exec proxy sh

## 中で upstream を直叩き（例）
curl -i http://api:3000/health
curl -i http://front:5173/
```

## E. Traefikのルール確認（labels の考え方）🧠

Traefikは **Dockerラベルで router / service を作る** のが基本だよ〜🧷
([Traefik Docs][6])
Docker公式にも “TraefikでHTTPルーティングする” ガイドがあるので、迷ったらそこに戻るのもアリ📘✨ ([Docker Documentation][9])

## F. Caddyの“デバッグ強化”🧯

Caddyは Caddyfile の先頭に **global options** を置けて、トラブル時は `debug` が頼れるよ🧠
([Caddy Web Server][10])

---

## 5) 症状別：最短の直し方まとめ🧩✨

## ✅ 404 が出たら（入口で迷子疑い）🚥

* Host / Path を **一旦シンプルに**（Hostだけにする等）
* Traefikなら router rule / entrypoints を見直す([Traefik Docs][3])
* dashboard系は **`/dashboard/` の末尾 `/`** を疑う📊 ([Stack Overflow][5])

## ✅ 502 が出たら（中に繋げてない疑い）🔌

* `localhost` を使ってたらほぼそれ🪤（サービス名に直す）
* upstream のポートが **コンテナ内ポート** になってるか確認🔢
* proxyコンテナ内から `curl http://api:PORT` が通るまで粘る🔥
* Caddyの 502 は接続失敗起点のことがある（上流が502返したとは限らない）([GitHub][11])

## ✅ つながらない（入口まで届いてない疑い）🚪

* まず `docker compose ps` で ports が出てるか確認([Docker Documentation][1])
* `Test-NetConnection` で 80/443 に繋がるか見る🪟
* Docker Desktop/WSL2の状態も疑う（WSL統合設定など）([Docker Documentation][8])

---

## 6) AIに投げるときの“勝ちプロンプト”例🤖✨

「状況 → 期待 → 現実 → ログ → 変えたこと」をセットにすると強いよ📦

```text
目的：app1.localhost で front に到達したい
現象：ブラウザで 404（Traefikの404っぽい）
やったこと：router rule を Host(`app1.localhost`) に設定
貼るもの：
1) docker compose ps の結果
2) docker compose logs -f proxy の該当部分（アクセス時の数十行）
3) 該当サービスの labels（router rule / entrypoints / service / port）
質問：
- 404が入口由来かを判定して
- 直すなら labels をどう変えるべき？
```

---

## 7) 再発防止のチェックリスト✅🧷

* [ ] 入口（proxy）ログを常に見れるようにしてる👂
* [ ] “入口→中を直叩き curl” を習慣にしてる🎯
* [ ] `localhost` を proxy設定に書かない（サービス名で統一）🪤🚫
* [ ] Host/Path ルールはまずシンプル→徐々に足す🧠
* [ ] `docker compose ps` で PORTS/STATUS を毎回チラ見する👀 ([Docker Documentation][1])

---

## ミニ課題（実戦）🧪🔥

## 課題1：404 をわざと作って直す😈➡️😇

1. router rule の Host をわざと間違える（`app2.localhost` とか）
2. 404 を確認
3. logs を見て「入口で迷子」を確定
4. Host を正しく戻して復旧🎉

## 課題2：502 をわざと作って直す💥➡️🛠️

1. proxy設定の upstream を `localhost:3000` に変える
2. 502 を確認
3. proxyコンテナ内で `curl http://api:3000` は通るのに、`curl http://localhost:3000` は死ぬのを確認
4. upstream を `api:3000` に戻して復旧🎉

## 課題3：つながらない を“入口手前”で直す🚪

1. proxyの ports を一時的に外して up
2. ブラウザが繋がらないのを確認
3. `docker compose ps` で PORTS が消えてるのを確認
4. ports を戻して復旧🎉

---

この章のゴールはね…✨
**「404/502/つながらない」を見た瞬間に、次に打つコマンドが自動で出る状態」** になることだよ🧠💪🐳

次の章（ログと観測）に繋がるように、もしよければあなたの想定スタック（Caddy派？Traefik派？）に合わせて、**“第28章専用：トラブル→コマンド→見る場所”早見表**も作るよ📄✨

[1]: https://docs.docker.com/reference/cli/docker/compose/ps/?utm_source=chatgpt.com "docker compose ps"
[2]: https://docs.docker.com/reference/cli/docker/compose/logs/?utm_source=chatgpt.com "docker compose logs"
[3]: https://doc.traefik.io/traefik/reference/routing-configuration/http/routing/router/?utm_source=chatgpt.com "Traefik HTTP Routers Documentation"
[4]: https://github.com/traefik/traefik/issues/8141?utm_source=chatgpt.com "Traefik always returns a 404 HTTP code even if no ..."
[5]: https://stackoverflow.com/questions/63116661/404-when-trying-to-access-traefik-dashboard?utm_source=chatgpt.com "404 when trying to access traefik dashboard - docker"
[6]: https://doc.traefik.io/traefik/routing/providers/docker/?utm_source=chatgpt.com "Traefik Docker Routing Documentation"
[7]: https://caddyserver.com/docs/caddyfile/directives/reverse_proxy?utm_source=chatgpt.com "reverse_proxy (Caddyfile directive) — Caddy Documentation"
[8]: https://docs.docker.com/desktop/features/wsl/?utm_source=chatgpt.com "Docker Desktop WSL 2 backend on Windows"
[9]: https://docs.docker.com/guides/traefik/?utm_source=chatgpt.com "HTTP routing with Traefik"
[10]: https://caddyserver.com/docs/caddyfile/options?utm_source=chatgpt.com "Global options (Caddyfile) — Caddy Documentation"
[11]: https://github.com/caddyserver/caddy/issues/7283?utm_source=chatgpt.com "Handling connection error (502) on `reverse_proxy` or ` ..."
