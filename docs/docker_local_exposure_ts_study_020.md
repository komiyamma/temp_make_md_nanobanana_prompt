# 第20章：ここから自動化ルート：Traefik入門🚦🤖

この章は「**リバプロ設定を“手書き”から“自動増殖”へ**」切り替える回だよ〜✨
Caddy/Nginxみたいに「入口の設定ファイルを毎回いじる」より、Traefikは **“各アプリ側にラベルを貼る”だけで、入口が勝手に増える**のが強み👍
（Dockerイベント監視もデフォでONだよ）([doc.traefik.io][1])

---

## 1) 今日のゴール🎯✨

* `http://whoami.localhost` と `http://app.localhost` を **ポート増やさず**に同居させる🚪🏠🏠
* 「ルーティングはTraefik、ルールは各サービスのlabels」って感覚を掴む🏷️🧠
* **“502になったらポート指定”**が自然に出てくるようにする🔥([doc.traefik.io][2])

---

## 2) まず“Traefik脳”を作る🧠🔧（この3語だけでOK）

Traefikは基本、これだけ覚えれば回り始めるよ👇

* **Entrypoint**：入口のポート（例：`:80`）🚪
* **Router**：どのURLをどこへ流す？（例：`Host(\`app.localhost`)`）🪧
* **Service**：実際の転送先（＝コンテナの内部ポート）📦
* **Middleware**：途中でちょい加工（後で使う：/apiを剥がす等）🧴

![Traefik Core Concepts](./picture/docker_local_exposure_ts_study_020_01_traefik_core_concepts.png)

Traefikはコンテナを見つけると、**containerごとにrouter/serviceを自動で作ったり**できる（labelsで上書きする）ってイメージね🙂([doc.traefik.io][2])

---

## 3) 最小構成を作る📦🐳（Traefik + 2アプリ）

### フォルダ構成🗂️

![Project Directory Structure](./picture/docker_local_exposure_ts_study_020_02_folder_structure.png)

こんな感じで作るよ〜👇

```text
ch20-traefik-intro/
  compose.yaml
  app/
    index.html
```

### `app/index.html`（超テキトーでOK）📝✨

```html
<!doctype html>
<html>
  <head><meta charset="utf-8" /><title>app</title></head>
  <body>
    <h1>app.localhost で見えてたら勝ち🎉</h1>
    <p>Traefik でホスト名ルーティングできてるよ〜🚦</p>
  </body>
</html>
```

### `compose.yaml`（この章のメイン！）🔥

ポイントは3つ👇

* Traefikは **80/8080だけ外に出す**（アプリ側のportsは基本いらない）
* `exposedByDefault=false` にして、**見せたいコンテナだけ `traefik.enable=true`**
* 同じネットワークに置いて、Traefikが中へ流せるようにする🧵

```yaml
name: ch20-traefik-intro

services:
  traefik:
    image: traefik:v3.6.8
    command:
      - --api.insecure=true
      - --providers.docker=true
      - --providers.docker.exposedbydefault=false
      - --providers.docker.network=proxy
      - --entrypoints.web.address=:80
    ports:
      - "80:80"
      - "8080:8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    networks:
      - proxy

  whoami:
    image: traefik/whoami:v1.11.0
    labels:
      - traefik.enable=true
      - traefik.http.routers.whoami.rule=Host(`whoami.localhost`)
      - traefik.http.routers.whoami.entrypoints=web
    networks:
      - proxy

  app:
    image: nginx:alpine
    volumes:
      - ./app:/usr/share/nginx/html:ro
    labels:
      - traefik.enable=true
      - traefik.http.routers.app.rule=Host(`app.localhost`)
      - traefik.http.routers.app.entrypoints=web
    networks:
      - proxy

networks:
  proxy:
    name: proxy
```

* Traefikの「Docker provider有効化」「80と8080」「`--api.insecure=true`」の超基本は公式のQuick Startの流れそのまま👌（8080はダッシュボード用。後章で安全に扱うよ）([doc.traefik.io][3])
* `providers.docker.exposedByDefault` は「デフォで公開するか」の設定。**trueがデフォ**だから、学習段階からfalseにしとくと事故りにくい✨([doc.traefik.io][1])

  ![Exposed By Default Logic](./picture/docker_local_exposure_ts_study_020_03_exposed_by_default.png)

* この章の時点（2026-02-12）でTraefikは **v3.6.8** が出てるよ🆕([GitHub][4])
* `whoami` のタグは `v1.11.x` がまとまって使われてるやつ（Docker Hubにtag一覧ある）([hub.docker.com][5])

---

## 4) 起動して見てみよう👀🚀

PowerShellで👇

```powershell
cd ch20-traefik-intro
docker compose up -d
docker compose ps
```

ブラウザで開く👇

* `http://whoami.localhost` ✅
* `http://app.localhost` ✅
* `http://localhost:8080/dashboard/` ✅（Traefikダッシュボード）([doc.traefik.io][3])

![Access Verification](./picture/docker_local_exposure_ts_study_020_04_access_verification.png)

💡補足：`*.localhost` は環境によっては追加設定なしでローカル解決してくれる（特にChromium系でそういう挙動が案内されてる）よ〜🧠✨
もし開けなかったら、前章のhosts設定（`whoami.localhost` / `app.localhost` を 127.0.0.1 に向ける）を入れるとOK🙆‍♂️([Docker Documentation][6])

---

## 5) “ラベルで増える”を体験する💥（サービス追加＝labels追加）

ここからが本番😺
**Traefik側の設定はいじらず**、サービスを追加してlabels書くだけで入口が増えるのが気持ちいいやつ✨

![Plug and Play Service Addition](./picture/docker_local_exposure_ts_study_020_05_plug_and_play.png)

### 例：ポートが80じゃないサービスを追加（= 502対策も覚える）🧯

`hashicorp/http-echo` はデフォで **5678** を使うよ([hub.docker.com][7])
Traefikは「コンテナの最初のexposed port」を使うのが基本なので、**明示しておくと安定**👍（間違うと502の代表例）([doc.traefik.io][2])

`compose.yaml` にこれを追記👇

```yaml
  echo:
    image: hashicorp/http-echo:latest
    command: ["-text=echo.localhost で見えてたらOK🎉"]
    labels:
      - traefik.enable=true
      - traefik.http.routers.echo.rule=Host(`echo.localhost`)
      - traefik.http.routers.echo.entrypoints=web
      - traefik.http.services.echo.loadbalancer.server.port=5678
    networks:
      - proxy
```

反映👇

```powershell
docker compose up -d
```

開く👇

* `http://echo.localhost` ✅

> ✅ここが今日いちばん大事：
> **「ルールはアプリ（labels）に持たせる」＝“追加が怖くない”**🎉

---

## 6) labelsの“読み方”チートシート🏷️📌

![Traefik Label Anatomy](./picture/docker_local_exposure_ts_study_020_06_label_anatomy.png)

labelsは長いけど、分解すると一瞬で読めるよ😇

* `traefik.http.routers.<名前>.rule=Host(\`xxx`)`
  → 「このHostなら、このrouterに入れる」🪧
* `traefik.http.routers.<名前>.entrypoints=web`
  → 「入口は80番にする」🚪
* `traefik.http.services.<名前>.loadbalancer.server.port=5678`
  → 「転送先の**内部ポート**は5678」📦
  （Traefikが間違ったポートを見に行くと **502** になりがち。ここで上書きする）([doc.traefik.io][2])
* `traefik.enable=true`
  → 「このコンテナはTraefik管理対象に入れて〜」🙋‍♂️
  しかもこれは `exposedByDefault` を上書きするよ([doc.traefik.io][2])

---

## 7) ⚠️地雷：labelsに秘密を書くな💣🔑

Traefik公式でも「**labelsは秘密情報を入れる場所じゃない**」って注意されてるよ〜😵‍💫
（dockerのinspectやUIから見えることがあるからね）([doc.traefik.io][2])

➡️ パスワードやAPIキーは、後で出てくる「環境変数」「secrets」「外部設定ファイル」側に寄せよう🙆‍♂️

---

## 8) よくある詰まりポイント辞典📕🧯（この章だけで直せるやつ）

### A) 404が出る😇

だいたいこれ👇

* `Host(\`app.localhost`)` のスペルミス
* ブラウザが別Hostでアクセスしてる（`localhost`で開いちゃってる等）
* ルータが作られてない（`traefik.enable=true` 忘れ）([doc.traefik.io][2])

✅確認

```powershell
docker compose logs traefik --tail 100
```

ダッシュボードで **Routers** を見るのが早い👀📊（次章で安全運用する）

### B) 502が出る😵‍💫

これが王道👇

* Traefikが **違うポートへ転送**してる

  ![502 Error due to Wrong Port](./picture/docker_local_exposure_ts_study_020_07_502_error_port.png)

  → `traefik.http.services.<name>.loadbalancer.server.port=XXXX` を正しく書く！([doc.traefik.io][2])

### C) 80番がすでに埋まってる🚧

別のWebサーバ（IIS/他のリバプロ）が80を使ってるとTraefikが起動できない💥
→ その場合はこの章だけ **一時的に** `8081:80` みたいに逃がしてOK（本筋は「入口1個」なので後で戻す）

---

## 9) Copilot / Codex に投げる“勝ちプロンプト”例🤖✨

### 例1：labelsを自動生成してもらう🏷️

```text
docker compose の service に付ける Traefik v3 の labels を作って。
要件:
- host は admin.localhost
- entrypoint は web(:80)
- 転送先のコンテナ内部ポートは 3000
- exposedByDefault=false 前提なので traefik.enable=true も付ける
出力は labels の配列だけでOK
```

### 例2：502の切り分け手順を作ってもらう🧯

```text
Traefik v3 + Docker Compose で 502 が出る。
原因を「ポート」「ネットワーク」「ルール不一致」に分けて、
確認コマンド（docker compose logs/ps 等）込みで手順を書いて。
```

---

## 10) ミニ課題🎮（やると“自動化”が体に入る）

### 課題A：3つ目のアプリを増やす🎉

* `admin.localhost` を増やす
* 中身は `traefik/whoami` でも `nginx` でもOK
* **「Traefik側はいじらない」**を守るのが勝ち🏆

### 課題B：わざと502を起こして直す😈➡️😇

* `echo` の `server.port` を `9999` にして 502 を出す
* 正しい `5678` に戻して復旧
  「502＝ポート疑え」が脳に刻まれる🔥([doc.traefik.io][2])

### 課題C：Middlewareを“1個だけ”入れてみる🧴

（Middlewareは次の章以降で本格的にやるけど、触ると楽しい✨）

たとえば `/admin` で来たら `app` に流す（PathPrefix）＋prefix剥がす（StripPrefix）みたいなのは、labelsで宣言できるよ〜（仕組みだけチラ見）([doc.traefik.io][2])

---

## 11) この章の“卒業チェック”✅🎓

* [ ] `docker compose up -d` でTraefik + 複数サービスが立つ
* [ ] `app.localhost` / `whoami.localhost` がポート増やさず開く
* [ ] サービス追加は「labels追加」でいける感覚がある
* [ ] 502が出たら `loadbalancer.server.port` を思い出せる([doc.traefik.io][2])
* [ ] labelsに秘密を書いちゃダメがわかる([doc.traefik.io][2])

---

次の第21章は、**便利すぎるTraefikダッシュボードを“安全にローカル運用する”**回だよ🧯📊
今のままだと `--api.insecure=true` で便利だけど、扱いを間違えると危ないので、ちゃんと“安全な見える化”にしていこう〜✨([doc.traefik.io][3])

[1]: https://doc.traefik.io/traefik/reference/install-configuration/providers/docker/ "Traefik Docker Documentation - Traefik"
[2]: https://doc.traefik.io/traefik/reference/routing-configuration/other-providers/docker/ "Traefik Docker Routing Documentation - Traefik"
[3]: https://doc.traefik.io/traefik/getting-started/docker/?utm_source=chatgpt.com "Docker and Traefik Quick Start"
[4]: https://github.com/traefik/traefik/releases "Releases · traefik/traefik · GitHub"
[5]: https://hub.docker.com/r/traefik/whoami/tags?ordering=last_updated&page=1&utm_source=chatgpt.com "traefik/whoami - Docker Image"
[6]: https://docs.docker.com/guides/traefik/?utm_source=chatgpt.com "HTTP routing with Traefik"
[7]: https://hub.docker.com/r/hashicorp/http-echo?utm_source=chatgpt.com "hashicorp/http-echo - Docker Image"
