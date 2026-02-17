# 第13章：最短ルート：Caddyで“入口1個”を作る🚀🍞

この章は **「とにかく最速で成功体験」** がゴールだよ〜！🎉
やることはシンプルで、**Caddy（入口）→ パスで2アプリに振り分け** を作ります✨

* `http://localhost:8080/app1/` → アプリ①
* `http://localhost:8080/api/` → アプリ②（APIっぽい）

---

## 0) 今日の完成図（超ざっくり）🗺️✨

![Architecture Diagram](./picture/docker_local_exposure_ts_study_013_01_architecture.png)

```
ブラウザ
  |
  |  http://localhost:8080/app1/  または  /api/
  v
[Caddy]  ← 入口はここ1個だけ🚪
  | \
  |  \---- /app1/* --> app1 (Node)
  |
   \------ /api/*  --> api  (Node)
```

---

## 1) まずは“動くダミーアプリ”を2つ作る🧪🍰

今回は **Nodeの標準機能だけ** でサクッとHTTPサーバを作るよ（依存なしで楽）😋
Node 24 は Active LTS 扱いで、いまの教材としても使いやすい立ち位置です。([Node.js][1])

## フォルダ構成📁

![Folder Structure](./picture/docker_local_exposure_ts_study_013_03_folder_structure.png)

```
chapter13-caddy/
  compose.yaml
  conf/
    Caddyfile
  app1/
    server.js
  api/
    server.js
```

## PowerShellでフォルダ作成🪟✨

```powershell
mkdir chapter13-caddy
cd chapter13-caddy
mkdir conf, app1, api
```

## app1/server.js（HTML返すだけ）🖥️

```javascript
// app1/server.js
const http = require("http");

const port = process.env.PORT || 3000;

http
  .createServer((req, res) => {
    res.statusCode = 200;
    res.setHeader("Content-Type", "text/html; charset=utf-8");
    res.end(`
      <h1>🐣 app1</h1>
      <p>path: <b>${req.url}</b></p>
      <p>👋 Caddy経由で来れてたら勝ち！</p>
    `);
  })
  .listen(port, () => console.log(`app1 listening on ${port}`));
```

## api/server.js（JSON返すだけ）🧃

```javascript
// api/server.js
const http = require("http");

const port = process.env.PORT || 4000;

http
  .createServer((req, res) => {
    res.statusCode = 200;
    res.setHeader("Content-Type", "application/json; charset=utf-8");
    res.end(
      JSON.stringify(
        {
          service: "api",
          path: req.url,
          message: "🍣 hello from api",
        },
        null,
        2
      )
    );
  })
  .listen(port, () => console.log(`api listening on ${port}`));
```

---

## 2) Caddyfileを書いて「パスで振り分け」する🔀🍞

![Handle Path Stripping](./picture/docker_local_exposure_ts_study_013_02_handle_path_strip.png)

ここが本章の主役！✨
Caddyの `handle_path` は **マッチしたプレフィックスを自動で取り除いて** 中のサービスへ流してくれる便利機能だよ（例：`/app1/hello` → アプリ側には `/hello` として届く）🧠✨ ([Caddy Web Server][2])

## conf/Caddyfile 🧾

```caddyfile
:80 {

	# ✅ /app1/* は app1 に流す（/app1 を自動で剥がす）
	handle_path /app1/* {
		reverse_proxy app1:3000
	}

	# ✅ /api/* は api に流す（/api を自動で剥がす）
	handle_path /api/* {
		reverse_proxy api:4000
	}

	# ✅ それ以外は案内を返す（迷子対策）
	handle {
		respond "Try: /app1/  or  /api/" 200
	}
}
```

> `reverse_proxy` は “指定先へ全部流す” の基本機能で、`/api/*` みたいにパス条件付きの例も公式に載ってるよ〜🧠 ([Caddy Web Server][3])

---

## 3) compose.yaml（Caddy＋2アプリを一気に起動）🐳🧩

![Caddy Volume Mounts](./picture/docker_local_exposure_ts_study_013_04_volume_mount.png)

Compose の推奨ファイル名は `compose.yaml`（または `compose.yml`）で、両方あれば `compose.yaml` を優先する仕様です。([Docker ドキュメント][4])

Caddy公式Dockerイメージは **`/data` と `/config` をボリュームで持てる**（特に `/data` は重要）という前提があるので、ここも素直に踏みます🧠🔒 ([Docker Hub][5])
さらに、設定は **`/etc/caddy` にフォルダごとマウント**するのが推奨されてる流れ（直マウントの注意もある）なので、その形にします👍 ([Docker Hub][5])

```yaml
## compose.yaml
services:
  caddy:
    image: caddy:2
    ports:
      # まずは 8080 を入口にする（80が他と競合しやすいので）
      - "8080:80"
    volumes:
      - ./conf:/etc/caddy
      - caddy_data:/data
      - caddy_config:/config
    depends_on:
      - app1
      - api

  app1:
    image: node:24-alpine
    working_dir: /app
    volumes:
      - ./app1:/app
    command: ["node", "server.js"]
    environment:
      - PORT=3000

  api:
    image: node:24-alpine
    working_dir: /app
    volumes:
      - ./api:/app
    command: ["node", "server.js"]
    environment:
      - PORT=4000

volumes:
  caddy_data:
  caddy_config:
```

> Caddy の安定版 Latest は v2.10.2（本日時点）なので、固定したい人は `image: caddy:2.10.2` みたいにしてもOK👌 ([GitHub][6])

---

## 4) 起動して動作チェック✅🎉

## 起動🚀

```powershell
docker compose up -d
```

## ブラウザでアクセス🌐

* `http://localhost:8080/app1/` → 🐣 app1 のHTML
* `http://localhost:8080/api/` → 🍣 api のJSON
* `http://localhost:8080/` → “Try: /app1/ or /api/”

---

## 5) “Caddyfile変更→即反映”を体験する🔁✨

Caddyは「再起動なしで設定をリロードできる」流れがあるので、教材的にここで一回気持ちよくなっとこ😆
Dockerでのリロードは `caddy reload` をコンテナ内で叩くのが推奨ルートだよ。([Docker Hub][5])

## 例：Caddyfileの `respond` 文言を変える✍️

`Try: ...` の文章をちょい変えて保存 → 次を実行：

```powershell
docker compose exec -w /etc/caddy caddy caddy reload
```

---

## 6) よくある詰まりポイント（最短で助かるやつ）🧯😇

## ① `/app1/` が 404 になる😵‍💫

* **Caddyfileのパスが `/app1/*` になってる？**（`/app1` だけだと微妙にハマることある）
* **ブラウザは `/app1/`（末尾スラッシュあり）で試す**のが無難✨

## ② 502（Bad Gateway）になる💥

![Troubleshoot 502](./picture/docker_local_exposure_ts_study_013_05_troubleshoot_502.png)

だいたいこれ👇

* app1/api が落ちてる
* ポート番号がズレてる（app1:3000 / api:4000）
* サービス名を間違えてる（Caddyfileの `app1` / `api` が compose と一致してない）

確認コマンド🔍

```powershell
docker compose ps
docker compose logs -f app1
docker compose logs -f api
docker compose logs -f caddy
```

## ③ “入口ポート”が開けない（起動はするけどアクセス不可）🚧

* 8080 が別アプリと競合してるときは、`compose.yaml` の `8080:80` を別番号に変更（例：`18080:80`）で回避できるよ🛠️

---

## 7) ミニ課題（達成感強め）🎮🏁

## 課題A：3つ目のアプリ `admin` を増やして `/admin/` に割り当てよう👑

* `admin/server.js` を作る（app1のコピペでOK）
* compose に `admin` サービス追加（PORT=5000とか）
* Caddyfile に `handle_path /admin/* { reverse_proxy admin:5000 }` 追加

## 課題B：`/api/hello` にアクセスしたら JSON の `path` がどうなるか観察👀

`handle_path` が **プレフィックスを剥がす**挙動、体で覚えると一気に強くなる💪 ([Caddy Web Server][2])

---

## 8) AIに投げる“勝ちテンプレ”🤖✨（コピペOK）

## 追加ルートを作らせる🧠

```text
Docker Compose（compose.yaml）とCaddyfileがあります。
/admin/* を新しい admin サービスに reverse proxy したいです。
- admin は node:24-alpine で server.js を起動
- 外部にポート公開はしない
必要な compose.yaml の追記と Caddyfile の追記を最小差分で出して
```

## 502の原因を絞り込ませる🧯

```text
Caddy経由で /api/ にアクセスすると 502 になります。
以下を前提に、原因候補を優先度順に3つに絞って、確認コマンドもセットでください：
- compose.yaml は caddy + app1 + api
- Caddyfile は handle_path /api/* { reverse_proxy api:4000 }
- api は node server.js
```

---

## この章のまとめ🎁✨

* **入口1個（Caddy）** を立てた！🚪
* **パスで2アプリ共存** できた！🎉
* `handle_path` の「プレフィックス剥がし」が超重要だと分かった！🧠 ([Caddy Web Server][2])
* CaddyのDocker運用は **`/data` をちゃんと永続化**が基本だと押さえた！🔒 ([Docker Hub][5])

---

次の章（第14章）に向けての一言だけ言うと…
ここまで来たら、もう **Caddyfileが怖くなくなるゾーン** 入ってます😺✨

[1]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[2]: https://caddyserver.com/docs/caddyfile/directives/handle_path "handle_path (Caddyfile directive) — Caddy Documentation"
[3]: https://caddyserver.com/docs/caddyfile/directives/reverse_proxy "reverse_proxy (Caddyfile directive) — Caddy Documentation"
[4]: https://docs.docker.jp/compose/compose-file/ "Compose Specification（仕様） — Docker-docs-ja 24.0 ドキュメント"
[5]: https://hub.docker.com/_/caddy "caddy - Official Image | Docker Hub"
[6]: https://github.com/caddyserver/caddy/releases "Releases · caddyserver/caddy · GitHub"
