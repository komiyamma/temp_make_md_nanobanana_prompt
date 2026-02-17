# 第10章：Composeでのサービス間通信の基本🧩🔗

この章は「**コンテナ同士はどうやって話すの？**」を、最短で腹落ちさせる回だよ〜🙂✨
ここが分かると、次の「リバースプロキシで入口を1つにする🚪」が一気に楽になる！

---

## 1) まずは“2つの世界”を分けて考えよう🌍🧠

![_01_two_worlds](./picture/docker_local_exposure_ts_study_010_01_two_worlds.png)

Docker/Composeには、大きく **2種類の通信** があるよ👇

**A. 外の世界（ホストPC＝Windows）から入る通信**🪟➡️🐳

* ブラウザで `http://localhost:xxxx` みたいにアクセスするやつ
* これは **`ports:` で“公開”したときだけ**入れる
* Docker Desktop は公開ポートをホスト側で受けて、VM内のコンテナへ転送する仕組みになってるよ📦➡️🧊
  ([Docker Documentation][1])

**B. 中の世界（コンテナ同士）の通信**🐳↔️🐳

* こっちが本題！
* Composeはデフォで **プロジェクト専用ネットワーク**を作って、サービス同士をそこに参加させる
* そして **サービス名（例：`api`）が、そのまま名前解決（DNS）できる**ようになるよ📛✨
  ([Docker Documentation][2])

---

## 2) 超重要：Host Port と Container Port は別物だよ🚦🔌

![_02_port_mapping](./picture/docker_local_exposure_ts_study_010_02_port_mapping.png)

ここ、いちばん事故るポイント😂💥

* `ports: "8080:3000"` のとき

  * **ホスト側**（Windows）からは `localhost:8080`
  * **コンテナ同士**では `api:3000`（コンテナのポート）

Compose公式も「**サービス間通信は CONTAINER_PORT を使う**」って明言してるよ✅
([Docker Documentation][2])

---

## 3) まずは“動く最小構成”を作ろう🚀🍞

![_03_single_entry_arch](./picture/docker_local_exposure_ts_study_010_03_single_entry_arch.png)

例：`front`（Web）→ `api`（API）→ `db`（DB）でつなぐよ！
ポイントは **front が api を `http://api:3000` で呼ぶ**こと👀✨

```yaml
services:
  front:
    image: node:24-alpine
    working_dir: /app
    volumes:
      - ./front:/app
    command: sh -lc "npm i && npm run dev -- --host 0.0.0.0 --port 5173"
    ports:
      - "5173:5173"   # 👈 Windowsブラウザから入る“入口”だけ公開
    depends_on:
      api:
        condition: service_started

  api:
    image: node:24-alpine
    working_dir: /app
    volumes:
      - ./api:/app
    command: sh -lc "npm i && node server.js"
    # portsは付けない！←ここ大事（中だけで会話できる）
    expose:
      - "3000"        # 👈 “中で使うポートのメモ”的に置いてOK（任意）

  db:
    image: postgres:18
    environment:
      POSTGRES_PASSWORD: example
    # dbも外に出さない（中だけ）
    expose:
      - "5432"
```

**なぜ `api` と `db` は `ports` を付けないの？**🤔
👉 ローカル公開の整理では「**入口は基本1つに寄せる**」のがキレイだから！
DBや内部APIまでホストに出すと、ポートが増えて管理が破綻しがち😇🌀
（この方針が後で“リバプロ1本化”に直結するよ！）

> ちなみに `expose` は“公開”ではなく、「このコンテナはこのポートを使うよ」の表明（メタ情報）として扱われることが多いよ📌
> `ports` が“ホストへ公開”、`EXPOSE/expose` は“公開ポートのヒント”という整理が分かりやすい👍
> ([Docker Documentation][3])

---

## 4) つながってるか確認するコマンド🔍🧪（VS CodeターミナルでOK）

![_04_verification_cmd](./picture/docker_local_exposure_ts_study_010_04_verification_cmd.png)

**(1) 起動して状態を見る**👀

```bash
docker compose up -d
docker compose ps
```

**(2) “中の世界”で名前解決できるかテスト**📛
`front` から `api` を引いてみるよ👇

```bash
docker compose exec front sh -lc "getent hosts api || ping -c 1 api"
```

**(3) 実際にHTTPで叩く（超おすすめ）**🧪

```bash
docker compose exec front sh -lc "wget -qO- http://api:3000/health || true"
```

> Composeは「サービス名でdiscoverできる」って公式に書いてある通り、`api` が引ければ勝ち🎉
> ([Docker Documentation][2])

---

## 5) “localhost病”に注意！💊😵‍💫（あるある最強）

![_05_localhost_trap](./picture/docker_local_exposure_ts_study_010_05_localhost_trap.png)

コンテナの中で `localhost` って書くと…

* それは **“自分自身のコンテナ”** を指すんだよね😂
* だから `front` から `localhost:3000` に行っても、`front` 自分を見に行くだけ（apiじゃない）

✅ 正解：`http://api:3000`
✅ DBなら：`postgres://db:5432`（公式例にも出てくるやつ）
([Docker Documentation][2])

---

## 6) 起動順のワナ：depends_on は“準備完了”までは待たない⚠️⏳

![_06_startup_wait](./picture/docker_local_exposure_ts_study_010_06_startup_wait.png)

ここも大事！

* `depends_on` は基本「**先に起動する順番**」は作れる
* でも Compose公式が言う通り、**“ready（利用可能）”までは待たず、running まで**なんだよね😅
* ちゃんと待ちたい時は `healthcheck` と `condition: service_healthy` を使うのが王道✅
  ([Docker Documentation][4])

---

## 7) この章のミニ課題📝✨（設計の筋トレ）

**課題A：front→api のURLをわざと壊して直す**😈🔧

1. `http://localhost:3000` にして壊す
2. `http://api:3000` に戻して復旧
3. 「なぜ？」を一言で説明できたら勝ち🏆

**課題B：db を外に出さずに、api からだけ触れる設計にする**🧠🧱

* `db` に `ports` を付けないまま
* `api` の接続文字列を `db:5432` にする
* これが“入口を絞る”の基本姿勢だよ🚪✨

---

## 8) AI（Copilot/Codex）に投げる“勝ちテンプレ”🤖✅

そのまま貼って使える系いくよ👇

**設計相談プロンプト（短いのに強い）**💪

* 「Composeで `front` が `api` を呼ぶ。`ports` は入口だけにしたい。`front→api` のURLはどう書く？理由も」

**デバッグ用プロンプト（ログと状況を渡す）**🕵️‍♂️

* 「`front` から `api` に繋がらない。`docker compose ps` と `docker compose logs api --tail=200` を貼るので、原因候補を3つに絞って確認手順を出して」

**健康診断プロンプト（構成レビュー）**🩺

* 「この compose.yaml は“入口1つ、内部通信はサービス名”の方針になってる？改善点を箇条書きで」

---

## 9) 次章につながる“超大事なまとめ”🎁✨

* **サービス間通信は “サービス名:コンテナポート”**（例：`api:3000`）
  ([Docker Documentation][2])
* **ホスト公開は `ports`、内部はネットワーク（＝同じネットに居れば会話できる）**
  ([Docker Documentation][2])
* **起動順は `depends_on`、準備完了待ちは `healthcheck + service_healthy`**
  ([Docker Documentation][4])
* Docker Desktop の公開ポートはホスト側で受けてコンテナへ流す（だから `localhost` で見える）
  ([Docker Documentation][1])

---

次の章（リバースプロキシ）では、この「中の世界の通信」をそのまま使って、**入口だけを1つに束ねる**よ🚪✨
「front/api/admin…が増えてもURLが綺麗なまま」って世界に入っていこ〜🥳🎉

[1]: https://docs.docker.com/desktop/features/networking/ "Networking | Docker Docs"
[2]: https://docs.docker.com/compose/how-tos/networking/ "Networking | Docker Docs"
[3]: https://docs.docker.com/get-started/docker-concepts/running-containers/publishing-ports/?utm_source=chatgpt.com "Publishing and exposing ports"
[4]: https://docs.docker.com/compose/how-tos/startup-order/ "Control startup order | Docker Docs"
