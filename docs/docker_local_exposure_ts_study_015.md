# 第15章：フロント（Vite等）をリバプロ越しに見る🌬️🖥️

## 15.0 いまの“最新版”ざっくりメモ🗓️✨

* Vite の最新安定は **7.3.1**（npm の “Latest” 表示）だよ📦✨ ([npm][1])
* Node は **v24 が Active LTS / v25 が Current** という並び（2026-02 更新）🟢 ([Node.js][2])

---

## 15.1 この章のゴール🎯😺

**ブラウザは `http://front.localhost` だけ**を見ればOKにする🌈
そして…

* 画面が表示される👀✨
* TS/React を保存したら **勝手に画面が差分更新（HMR）**される🔥
* 「`localhost:5173` どれだっけ地獄」から解放😇🎉

---

## 15.2 なんで詰まりやすいの？（devサーバーの正体）🧠🔍

Vite の dev サーバーは、ただの静的配信じゃなくて…

* ブラウザにモジュールを配る（変換したりもする）📦
* 変更を検知して、**WebSocket で HMR 通知**を飛ばす⚡🕸️

つまり **リバプロが WebSocket を通せないと HMR が死ぬ**ことがあるよ👻
Vite 公式も「Vite の前にいるリバプロは WebSocket をプロキシできる前提」と書いてる📝
失敗すると「プロキシを迂回して直接 WebSocket 接続」にフォールバックする（＝変なエラーが出たり、環境によっては繋がらなくなる）って挙動も明記されてるよ🧯 ([vitejs][3])

一方で **Caddy の `reverse_proxy` は WebSocket 対応が標準**なので、基本はうまくいく方向💪🍞 ([Caddy Web Server][4])

---

## 15.3 まずは図で理解🗺️✨

![WebSocket Flow](./picture/docker_local_exposure_ts_study_015_01_websocket_flow.png)

イメージはこれ👇（“入口”は Caddy だけ）

* ブラウザ → `front.localhost:80`
* Caddy → `front` コンテナの `5173` に中継
* HMR の WebSocket も **同じ入口（80）**を通って中継される

```
Browser
  ├─ http://front.localhost/        (HTTP)
  └─ ws://front.localhost/          (HMR WebSocket)
            │
            ▼
        [Caddy :80]
            │ reverse_proxy
            ▼
      [Vite dev :5173]
```

---

## 15.4 “一番ラクに動く”構成（サブドメイン方式）🚀🏷️

![Subdomain vs Path for Vite](./picture/docker_local_exposure_ts_study_015_05_subdomain_vs_path.png)

dev サーバー（Vite）を **パス配下**（例：`/app`）に押し込むと、HTML/アセット/WS のパスが絡んで難しくなりがち😵‍💫
ここはまず **サブドメイン方式（`front.localhost`）**で勝ちにいくよ🎯✨

### 15.4.1 フォルダ構成（例）📁

```
reverse-proxy-lab/
  ├─ compose.yml
  ├─ Caddyfile
  └─ front/
      ├─ package.json
      ├─ vite.config.ts
      └─ src/...
```

### 15.4.2 `compose.yml`（Caddy + Vite）🐳🧩

![Vite Host Binding](./picture/docker_local_exposure_ts_study_015_02_vite_bind.png)

ポイントはこれ👇

* Vite は **コンテナ外にポート公開しない**（公開は Caddy だけ）🔒
* Vite は **`--host 0.0.0.0`**（コンテナ外＝別コンテナから見えるように）📡

  * Vite の `server.host` は `0.0.0.0`/`true` で全アドレス待受できるよ、って公式にある📝 ([vitejs][3])

```yaml
services:
  caddy:
    image: caddy:2
    ports:
      - "80:80"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
    depends_on:
      - front

  front:
    image: node:24
    working_dir: /app
    volumes:
      - ./front:/app
    command: sh -c "npm ci && npm run dev -- --host 0.0.0.0 --port 5173 --strictPort"
```

### 15.4.3 `Caddyfile`（`front.localhost` → Vite）🍞🚪

```caddyfile
front.localhost {
  reverse_proxy front:5173
}
```

これで **`http://front.localhost`** にアクセスすると Vite が見えるはず👀✨

---

## 15.5 Vite 側の“最低限のつぼ”🧠🔧

### ✅ (1) `front.localhost` は基本セーフ

Vite は **`localhost` と `.localhost` 配下ドメインはデフォルト許可**って仕様になってる👍
つまり `front.localhost` / `app1.localhost` は、基本そのままで通る可能性が高いよ✨ ([vitejs][3])

### ✅ (2) それ以外のドメインを使うときは `server.allowedHosts`

もし `dev.myapp.test` とか独自ドメイン風にしたら、**Host がブロック**されることがある😇
そのときは `server.allowedHosts` に追加する（むやみに `true` は危険寄り）⚠️ ([vitejs][3])

例（独自ホストを許可したい）👇

```ts
// front/vite.config.ts
import { defineConfig } from "vite";

export default defineConfig({
  server: {
    allowedHosts: ["dev.myapp.test"],
  },
});
```

### ✅ (3) “保存しても反映されない”は WebSocket じゃなくて監視の問題かも👀

Windows + Docker Desktop（WSL2 backend）系だと、**ファイル監視が効かない/鈍い**ことがある（編集が Windows 側プロセスだと特に）って Vite 公式に注意があるよ📝 ([vitejs][3])

対策の方向性は2つ👇

* できれば **プロジェクトを WSL 側のファイルシステムに置く**（安定＆速い）🚀
* どうしても無理なら **polling**（ただし CPU は上がりやすい）🔥 ([vitejs][3])

polling 例👇（必要なときだけ！）

```ts
import { defineConfig } from "vite";

export default defineConfig({
  server: {
    watch: {
      usePolling: true,
    },
  },
});
```

---

## 15.6 よくある詰まり辞典📕🧯（症状→原因→直し方）

![HMR Fallback Warning](./picture/docker_local_exposure_ts_study_015_03_hmr_fallback.png)

### ① 画面は出るけど、HMR が効かない（更新されない）😿

* 原因候補A：**WebSocket がプロキシされてない**

  * Vite は「リバプロが WebSocket を通す前提」📝 ([vitejs][3])
  * Caddy は基本 WebSocket OK 🍞🕸️ ([Caddy Web Server][4])
  * もし別リバプロ（Traefik/Nginx等）なら WS 設定不足の可能性あり

    * Traefik は WebSocket を “out of the box” でサポート🧰 ([doc.traefik.io][5])
* 原因候補B：**ファイル監視が死んでる（WSL2 系）**

  * 対策：WSL 側に置く or polling ([vitejs][3])

### ② ブラウザ Console に「Direct websocket connection fallback…」っぽいのが出る👻

* 意味：HMR の WS がリバプロ経由で繋がらず、**迂回して直結しにいった**合図
* 直し方：

  1. リバプロで WebSocket を通す（まずこれ）
  2. それでも環境的にムリなら、Vite の `server.hmr` を調整（次の③） ([vitejs][3])

### ③ HTTPS 絡みで HMR だけ死ぬ（wss/port がズレる）🔐🫠

たとえば入口が `https://front.localhost` になったり、443 を使う構成になると、HMR の接続先を明示したくなることがあるよ。

Vite の `server.hmr` は `protocol/host/port/clientPort` などを持ってる（公式の型定義も明記）📝 ([vitejs][3])

例：入口が 443 のときに “クライアント側の接続先ポート” を揃える感じ👇

```ts
import { defineConfig } from "vite";

export default defineConfig({
  server: {
    strictPort: true,
    hmr: {
      protocol: "wss",
      clientPort: 443,
    },
  },
});
```

---

## 15.7 デバッグ最短ルート🕵️‍♂️⚡

![WebSocket Debugging](./picture/docker_local_exposure_ts_study_015_04_ws_debug.png)

### ブラウザで確認（いちばん早い）🧠

1. DevTools → Network → **WS**
2. `ws://front.localhost/...` が

   * **Status 101 Switching Protocols** なら勝ち🎉
   * 失敗してたら、そこにエラー理由が出ること多い👀

### Docker 側で確認（入口→中を順番に潰す）🐳

* Caddy コンテナから Vite が見えてる？

  * 「名前解決」と「ポート」が正しいかを確認する感じ

（例：`front:5173` に到達できるか）

```bash
docker compose exec caddy wget -qO- http://front:5173 | head
```

---

## 15.8 ミニ課題🎒✨

1. `front.localhost` で Vite を開いて、`src/App.tsx` を編集→保存→**即反映**を確認🔥
2. わざと Caddyfile のポートを `5174` にして **502** を出し、原因をログと構成で特定🧯
3. `dev.myapp.test` みたいなホスト名を “あえて” 使って Host ブロックを踏み、`server.allowedHosts` で直す🍪（仕組み理解用）

---

## 15.9 Copilot/Codex に投げると速い“勝ちプロンプト”🤖💨

* 「Caddy で `front.localhost` を Vite(5173) に reverse_proxy して、HMR(WebSocket)も通る最小 Caddyfile を書いて」🍞
* 「Docker Compose で “Caddyだけ80公開、Viteは内部のみ” の構成にして。Vite は `--host 0.0.0.0` 前提」🐳
* 「ブラウザで WS が 101 にならない。想定原因を3つに絞って、確認手順を順番に出して」🕵️‍♂️

---

## 15.10 まとめ✅🎉

* Vite の HMR は **WebSocket**。ここがリバプロ越しで詰まりポイント👻 ([vitejs][3])
* Caddy は `reverse_proxy` が **WebSocket 対応**で基本ラク🍞 ([Caddy Web Server][4])
* Docker で Vite を動かすなら **`--host 0.0.0.0`** が超重要📡 ([vitejs][3])
* Windows + WSL2 系で「更新されない」は **ファイル監視**の問題も疑う👀 ([vitejs][3])

---

次の章（第16章）で「API を同じドメイン配下に寄せて CORS を減らす🧹✨」に進むと、**“フロントとAPIが同じ入口”**になって気持ちよさが一段上がるよ〜😺🚀

[1]: https://www.npmjs.com/package/vite?utm_source=chatgpt.com "vite"
[2]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[3]: https://vite.dev/config/server-options "Server Options | Vite"
[4]: https://caddyserver.com/docs/caddyfile/directives/reverse_proxy?utm_source=chatgpt.com "reverse_proxy (Caddyfile directive) — Caddy Documentation"
[5]: https://doc.traefik.io/traefik/master/user-guides/websocket/?utm_source=chatgpt.com "Traefik WebSocket Documentation"
