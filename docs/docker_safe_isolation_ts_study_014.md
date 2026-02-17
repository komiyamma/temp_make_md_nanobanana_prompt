# 第14章：Linux capabilitiesを減らす：できることを最小化🧤✂️

この章は「**privilegedに逃げないで**、コンテナの“できること”を必要最小限にする」回です😎🔒
ポイントは **cap_drop / cap_add** を “設計の道具” として使うこと✨

---

## 1) capabilitiesって何？ざっくり理解🧠💡

![Root vs Capabilities](./picture/docker_safe_isolation_ts_study_014_01_remote_control.png)

Linuxの `root権限` って、実は「超強い権限の寄せ集め」なんです。
その“権限のボタン”を小分けにしたのが **capabilities**（ケーパビリティ）🎛️

* `root = 全部入りリモコン📺`
* `capabilities = ボタン単位でON/OFFできるリモコン🎛️`

そしてDockerは、デフォルトで“いくつかのボタン”をコンテナに渡しています（全部は渡してない）📦🔧
どれがデフォルトで付くかは、Docker公式の一覧がそのまま参考になります。([Docker Documentation][1])

---

## 2) Dockerのデフォルト権限、実はけっこう強い😱

![Docker Default Capabilities](./picture/docker_safe_isolation_ts_study_014_02_default_risk.png)

Dockerはデフォルトで、たとえばこんなcapabilityを「付けた状態」で起動します👇
（例：`CHOWN`, `DAC_OVERRIDE`, `NET_RAW`, `NET_BIND_SERVICE` など）([Docker Documentation][1])

特に初心者が「うっかり危ない」やつはこれ：

* `DAC_OVERRIDE`：ファイル権限チェックをかなり無視できる系（読み書き関連）😵‍💫([Docker Documentation][1])
* `NET_RAW`：RAWソケット系（雑に言うと“ネットを低レベル操作”寄り）🕸️([Docker Documentation][1])
* `NET_BIND_SERVICE`：**1024未満のポート**（80とか）で待ち受けできる📮([Docker Documentation][1])

> つまり、何も考えずに起動すると「Webアプリには要らない強さ」が混ざりがち、ってことです🙃

---

## 3) まず覚える必勝パターン：**全部落として、必要分だけ戻す**🧹➡️🔧

![Drop All Strategy](./picture/docker_safe_isolation_ts_study_014_03_drop_strategy.png)

* まず `cap_drop: [ALL]` で全部落とす🧹
* 動かしてみて、必要なcapabilityだけ `cap_add` で戻す🔧

Docker CLIでも `--cap-drop` / `--cap-add` が使えて、`ALL` も指定できます。([Docker Documentation][1])
Composeでも `cap_add` / `cap_drop` が使えます。([Docker Documentation][2])

---

## 4) ハンズオン：Nodeサーバを「cap全部なし」で動かす🧪✨

狙い：**普通のNode/TS Webサーバは、capability無しでも大体動く**…を体験します😄👍
（※ 80番待ち受けだけは例外で、あとで `NET_BIND_SERVICE` を戻します）

## 4-1) ファイル用意📁✍️

![Project File Structure](./picture/docker_safe_isolation_ts_study_014_04_project_files.png)

プロジェクト直下にこんな構成を作ります：

* `compose.yaml`
* `Dockerfile`
* `package.json`
* `tsconfig.json`
* `src/server.ts`

## `src/server.ts`（超ミニHTTP）🌐

```ts
import http from "node:http";

const PORT = Number(process.env.PORT ?? 3000);

const server = http.createServer((req, res) => {
  res.statusCode = 200;
  res.setHeader("content-type", "text/plain; charset=utf-8");
  res.end(`OK 👋 path=${req.url}\n`);
});

server.listen(PORT, "0.0.0.0", () => {
  console.log(`listening on ${PORT}`);
});
```

## `package.json`（ビルドして実行）📦

```json
{
  "name": "cap-demo",
  "private": true,
  "type": "module",
  "scripts": {
    "build": "tsc -p tsconfig.json",
    "start": "node dist/server.js"
  },
  "devDependencies": {
    "@types/node": "^22.0.0",
    "typescript": "^5.0.0"
  }
}
```

## `tsconfig.json`（最小）🧩

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ES2022",
    "moduleResolution": "Bundler",
    "outDir": "dist",
    "strict": true
  },
  "include": ["src/**/*.ts"]
}
```

## `Dockerfile`（ビルド→実行）🏗️

```dockerfile
FROM node:current-bookworm-slim AS build
WORKDIR /app
COPY package.json tsconfig.json ./
RUN npm i
COPY src ./src
RUN npm run build

FROM node:current-bookworm-slim
WORKDIR /app
ENV NODE_ENV=production
COPY --from=build /app/dist ./dist
EXPOSE 3000
CMD ["node", "dist/server.js"]
```

## 4-2) まず普通に起動（基準）🚀

## `compose.yaml`（まずはcap指定なし）

```yaml
services:
  web:
    build: .
    environment:
      - PORT=3000
    ports:
      - "3000:3000"
```

起動：

```powershell
docker compose up --build
```

別ターミナルで確認：

```powershell
curl http://localhost:3000/
```

---

## 4-3) 次に「cap全部落とし」で起動🧹✨

![Node No-Caps Run](./picture/docker_safe_isolation_ts_study_014_05_node_light.png)

`compose.yaml` をこう変えます👇（これが本題！）

```yaml
services:
  web:
    build: .
    environment:
      - PORT=3000
    ports:
      - "3000:3000"
    cap_drop:
      - ALL
```

起動：

```powershell
docker compose up --build
```

また `curl`：

```powershell
curl http://localhost:3000/
```

✅ 多くの環境で、**そのまま動く**はずです🎉
→ これが「Webアプリにcapability要らんこと多い」の体験🔥

---

## 4-4) 80番で待ち受けたい時だけ：`NET_BIND_SERVICE` を戻す📮🔧

![NET_BIND_SERVICE Key](./picture/docker_safe_isolation_ts_study_014_06_port_80_key.png)

Linuxでは **1024未満のポート**でlistenするのに `NET_BIND_SERVICE` が必要です。([Docker Documentation][1])
（`NET_BIND_SERVICE` の説明はLinuxのcapabilitiesの定義にもあります。([man7.org][3])）

たとえば「コンテナ内は80でlisten、ホストは8080でアクセス」にしてみます👇
（Windowsで80を直接使うと競合しがちなので、ホスト8080に逃がすのが楽😄）

```yaml
services:
  web:
    build: .
    environment:
      - PORT=80
    ports:
      - "8080:80"
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
```

確認：

```powershell
docker compose up --build
curl http://localhost:8080/
```

---

## 5) 「Operation not permitted 😇」が出た時の考え方🧯

capabilityを落とすと、エラーがこうなりがち👇

| 症状🥲                      | だいたいの原因🧠  | まず疑うcapability🔍                                   |
| ------------------------- | ---------- | -------------------------------------------------- |
| 80番でlistenできない            | 低ポート制限     | `NET_BIND_SERVICE` ([Docker Documentation][1])     |
| `ip link` / ルーティング操作ができない | ネットワーク管理操作 | `NET_ADMIN`（※原則アプリには不要）([Docker Documentation][1]) |
| マウント/FUSE系ができない           | マウント操作     | `SYS_ADMIN`（危険寄り）([Docker Documentation][1])       |

> コツ：**エラーが出た操作を言語化**してから、必要最小限のcapabilityだけ足す✨

---

## 6) “足しちゃダメ寄り”代表：`SYS_ADMIN` 😱🚫

![SYS_ADMIN Danger](./picture/docker_safe_isolation_ts_study_014_07_sys_admin_danger.png)

`CAP_SYS_ADMIN` は Linux側でも「過剰に詰め込まれた（overloaded）危険枠」って扱いです。([man7.org][3])
つまり、**雑に付けると“ほぼ何でもあり”に近づく**と思ってOKです💥

なので判断基準はこれ👇

* `SYS_ADMIN` を足すくらいなら
  まず **別方式（設計）** を探す🔎✨
* どうしても必要なら
  「そのコンテナだけ隔離」「マウント/デバイスも最小」「目的を書いたコメント」🧱📝

---

## 7) 便利メモ：Composeでの書き方（最小）📌

Composeの `cap_add` / `cap_drop` はサービス属性として定義できます。([Docker Documentation][2])
Docker CLIだと `--cap-add/--cap-drop` で同じことができます。([Docker Documentation][1])

あと地味に重要：Dockerはcapabilityの選択に合わせて **デフォルトseccompプロファイルが調整される**ので、普通はseccompをいじらなくてOKです。([Docker Documentation][1])

---

## 8) AIに相談する時の“安全な聞き方”🤖🛡️（コピペ用）

AIが `SYS_ADMIN` とか `privileged` を雑に提案してくること、あります😂
なので、こう聞くのが安全です👇

```text
次のエラーを解消したいが、privilegedは禁止。
cap_drop: [ALL] のまま、必要最小限のcap_addだけで解決したい。
「なぜそのcapabilityが必要か」を1行で説明してから提案して。
```

---

## 9) 章末チェック✅🎯（これだけできれば勝ち）

* [ ] `cap_drop: [ALL]` で起動してもWebアプリが動くのを確認した😄
* [ ] 80番待ち受けが必要な時だけ `NET_BIND_SERVICE` を戻せる📮
* [ ] `SYS_ADMIN` は“最後の最後”だと理解した😱

---

次の章（第15章）で「privilegedを使う前のチェックリスト🧾🛑」に行くと、今日の内容がそのまま武器になりますよ🔥

[1]: https://docs.docker.com/engine/containers/run/ "Running containers | Docker Docs"
[2]: https://docs.docker.com/reference/compose-file/services/ "Services | Docker Docs"
[3]: https://man7.org/linux/man-pages/man7/capabilities.7.html "capabilities(7) - Linux manual page"
