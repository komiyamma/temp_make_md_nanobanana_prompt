# 第26章：ポート公開は最小限：公開するのは“入口だけ”🚪🌐

この章では「どのポートを外に出して、どれを絶対に外に出さないか」を、**迷わず決められる設計の型**にします😄🧠
（結論：**外に見せるのは “入口” だけ**。DBとかRedisは中に閉じ込める🍱🔐）

---

## 1) まずイメージ：ポート公開＝“外に穴を開ける”🕳️😱

コンテナの中でアプリが `3000` 番で待ち受けていても、それだけでは外（PCの外）からは基本来れません。
でも `ports:`（または `-p`）で公開すると、**ホスト側に穴が開いて外から到達できる**状態になります🌍💥

しかも大事ポイント👇
**ポート公開はデフォルトだと “外の世界にも” 開きがち**です⚠️（LANや状況によってはインターネット側まで…）
なので「公開は最小限」が超重要です🛡️
([Docker Documentation][1])

---

## 2) “最小公開”の黄金ルール 7つ🏆🔒

## ルール1：公開していいのは基本「Web/API」だけ🧑‍💻➡️🌐

* ブラウザやアプリがアクセスする入口（例：APIサーバー）だけ公開✅
* 入口が1つなら、守る場所も1つで済む🎯✨

## ルール2：DB/Redis/Queue は外に出さない🙅‍♂️🗄️

* DBを公開すると「見つけられる→殴られる（総当たり）→設定ミスで死亡」コースが早いです😇💣
* **アプリからだけDBに行ける**のが正解🙆‍♀️🍱

## ルール3：開発中は “localhost バインド” が基本🔥

`127.0.0.1` で縛ると **自分のPCからしか触れない**ので、事故が激減します🧯✨
([Docker Documentation][1])

## ルール4：`0.0.0.0` は「全開放」になりがち😱

Composeの `ports:` は **IPを書かないと全インターフェース（0.0.0.0）にバインド**しやすいです⚠️
([matsuand.github.io][2])

## ルール5：Docker Desktop は “ポートのデフォルト挙動” を設定できる🧩

Docker Desktop には、ポートバインドを **デフォルトで localhost に寄せる / 強制する**設定があります🔧
（事故を減らす系の神設定🙏）
([Docker Documentation][3])

## ルール6：`EXPOSE` は「公開」じゃない📌

Dockerfile の `EXPOSE` は「このアプリはこのポート使うよ」という**目印**で、**ホストに公開はしません**👀
([Docker Documentation][4])

## ルール7：「公開してから守る」より「公開しない」が最強🛡️✨

ファイアウォールや認証より前に、まず穴を開けないのが最強コスパです💪😄
（特に個人開発はこれが効く！）

---

## 3) Composeで“安全な公開”を作る（ここ超重要）💥🧠

## A. 一番よくある危険パターン😇

「とりあえず動けばOK」でこうしがち👇

```yaml
services:
  api:
    ports:
      - "3000:3000"
```

これ、IP指定がないので **0.0.0.0 にバインド（全開放寄り）**になりやすいです⚠️
([matsuand.github.io][2])

---

## B. 開発での鉄板：localhost に縛る🔒✨

```yaml
services:
  api:
    ports:
      - "127.0.0.1:3000:3000"
```

これなら基本「自分のPCからだけ」アクセスできます👍
（Dockerのポート公開は“外にも開く”のがデフォルトで危ないよ、って公式も強めに言ってます）
([Docker Documentation][1])

---

## C. “長い書き方”で安全を明示する（おすすめ）🧾✨

```yaml
services:
  api:
    ports:
      - name: web
        target: 3000
        published: "3000"
        host_ip: 127.0.0.1
        protocol: tcp
```

`host_ip: 127.0.0.1` を明示できるので、レビューしやすいです👀✅
([matsuand.github.io][2])

---

## 4) ハンズオン：APIだけ公開、DBは完全に内部専用🍱🔐

## 例：api + db の compose（DBは公開しない）

```yaml
services:
  api:
    build: .
    ports:
      - "127.0.0.1:3000:3000"
    environment:
      DATABASE_URL: "postgres://app:app@db:5432/appdb"
    depends_on:
      - db

  db:
    image: postgres:16
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: app
      POSTGRES_DB: appdb
    # ports: は “書かない” ←これがポイント！
```

ポイント解説🧠✨

* `api` だけ `ports` で入口を作る🚪
* `db` は **portsなし**＝ホストから触れない🧊
* `api` → `db:5432` は **内部ネットワーク**でつながる（公開いらない）🍱

---

## 5) “公開しすぎ事故”ミニ演習😇💥（超おすすめ）

## 演習1：わざとDBを公開してみる（危険を体感）🧪

`db` にこれを足す👇

```yaml
  db:
    ports:
      - "5432:5432"
```

そしてPowerShellで確認👇（外から到達できる穴が開いてるか）

```powershell
Test-NetConnection 127.0.0.1 -Port 5432
```

通ったら「穴あいてる！」です🕳️😱

## 演習2：localhost縛りにして被害半径を縮める🔒

```yaml
  db:
    ports:
      - "127.0.0.1:5432:5432"
```

## 演習3：最終形：DBの `ports:` を消す🗑️✨

これが最強です💪😄
（アプリ経由でしかDBに行けない＝守りやすい）

---

## 6) “いま何が公開されてる？”確認するコマンド🔍👀

## Docker側で見る🐳

* 公開ポートの一覧を見る（Compose）

```bash
docker compose ps
```

→ `PORTS` 欄に出てるやつが「外に穴あいてる可能性」高いです⚠️

* もっと細かく見る（コンテナ単位）

```bash
docker port <container_name>
```

## Windows側で「待ち受け」を見る🪟

```powershell
Get-NetTCPConnection -State Listen | Sort-Object LocalPort
```

「思ったより色々待ち受けてる😇」が見えると、設計が一段上がります📈✨

---

## 7) よくある詰まりポイント集🧯😵‍💫

## Q1. ブラウザで `http://localhost:3000` が開かない😭

* ポート被り（別アプリが3000使ってる）➡️ `published` を変える
* アプリが `0.0.0.0` じゃなく `127.0.0.1` だけで待ってる（コンテナ内の待受が原因）

  * コンテナ内はだいたい `0.0.0.0` で待ち受けが無難（外への公開は `ports` で制御）🌐

## Q2. LANの別PC/スマホからアクセスできない🤔📱

* それはむしろ「閉じてる」ので安全寄りです👍
* どうしても必要なときだけ、公開範囲やFW含めて設計（本番の話に近い）に寄せます🔥

## Q3. “全部 localhost に縛りたい” を強制したい😤🔒

Docker Desktop に「ポートバインドの挙動」を変える設定があります（localhost デフォルト化 / 強制）
事故が減るので、個人開発だとかなりアリです🙏✨
([Docker Documentation][3])

---

## 8) AI補助（Copilot / Codex）を“安全に使う”コツ🤖🛡️✨

コード生成でポート公開が増殖しがちなので、AIには **公開ポート監査役**をやらせるのが強いです😄
（例：GitHub Copilot、OpenAI Codex、Microsoft系の拡張など）

使えるプロンプト例👇

* 「このcompose.ymlで外部公開されるポートを一覧化して、公開の必要性を説明して」
* 「DB/Redisなど“内部専用”にすべきサービスが ports で公開されてないかチェックして」
* 「`0.0.0.0` バインドになってるポートがあったら理由と直し方を提案して」

あと超大事⚠️
AIが「とりあえず `ports: - "5432:5432"`」みたいに言い出したら、**“穴を開ける前提”になってる合図**です😇💣
まず「公開しなくて済む設計」に戻すのが勝ちです🏆✨

---

## 9) まとめ：第26章のセルフ監査チェック✅🔍

* [ ] 外に出してるのは Web/API だけ？🚪
* [ ] DB/Redis/Queue は `ports:` なし？🍱
* [ ] 公開が必要でも `127.0.0.1` 縛りにできてる？🔒
* [ ] `ports` のIP省略（0.0.0.0寄り）を“うっかり”で使ってない？😇
* [ ] `docker compose ps` で公開ポートを定期的に見てる？👀
* [ ] `EXPOSE` と `ports` を混同してない？📌
* [ ] 「公開して守る」より「公開しない」を先に検討した？🛡️

---

次の第27章で、ここに **Compose networks（内部ネットワーク）** を足して「DBは内部だけで会話する🍱🔐」をさらに強固にします🕸️✨

[1]: https://docs.docker.com/engine/network/port-publishing/ "Port publishing and mapping | Docker Docs"
[2]: https://matsuand.github.io/docker.docs-ja/reference/compose-file/services/ "services | Docker Docs"
[3]: https://docs.docker.com/desktop/settings-and-maintenance/settings/ "Change settings | Docker Docs"
[4]: https://docs.docker.com/get-started/docker-concepts/running-containers/publishing-ports/?utm_source=chatgpt.com "Publishing and exposing ports"
