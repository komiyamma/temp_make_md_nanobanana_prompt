# 第24章：ポート競合を永久に起こさないコツ📛🔒

この章はズバリ、**「ポート番号のケンカ（3000取り合い問題😇）」を構造で根絶**する回です！
結論から言うと、勝ちパターンはこれ👇

* **外に出すポートは“入口”だけ（基本 80/443）** 🚪✨
* **中のサービス（DB/Redis/内部APIなど）は外に出さない** 🧊
* **どうしてもホストから触りたい時は“例外ルール”で安全に** 🧯

---

## この章のゴール🎯

* 「このポートもう使われてる😡」を**二度と起こさない**
* DBやRedisをうっかり外に晒さない（地味に超重要）🧨
* 複数プロジェクトを同時に立ち上げても、ポートが衝突しない🥳

---

## 1) まず“ポート競合”の正体を1分で理解🧠💡

Dockerでよくある地獄はこれ👇

* Aプロジェクトが `localhost:3000` を使う
* Bプロジェクトも `localhost:3000` を使う
* すると **どっちかが起動できない**（先に掴んだ者勝ち）⚔️

ここで大事なのは：

* **衝突するのは「ホスト側のポート」**（Windowsの `localhost:3000` の方）
* コンテナの中は別世界なので、**コンテナ内の3000同士は衝突しない** 🌍

---

## 2) 永久解決の“設計ルール”はこれだけ✅✨

## ルールA：`ports:` を書くのは「入口」だけ🚪

**リバースプロキシ（Caddy/Traefik/Nginx）**だけが `80/443` を握る。
それ以外は、原則 `ports:` を消す！✂️

> なお、ポート公開（publish）は「やると危険が増える」前提で注意書きが公式にもあります。ホストIPを `127.0.0.1` に縛ると「自分のPCからだけアクセス」にできます。([Docker Documentation][1])

## ルールB：DB/Redis/Queueは “外に出さない” が標準🧊🧱

* DBを外に出すと、**セキュリティ的に事故りやすい** 🔥
* しかもポート競合の温床（5432/6379など）😇

## ルールC：例外は「ローカル限定 + 一時的」にする🧯

* `127.0.0.1` に縛って公開（外から来れない）
* もしくは **ランダムポート**に逃がす（競合しづらい）🎲

---

## 3) 入口だけ公開の完成イメージ図🗺️✨

```
[ブラウザ] 
   ↓  http://app1.localhost  /  http://api.localhost
[リバースプロキシ]  ←←（ここだけ 80/443 を公開）
   ↓
[app1]  [api]  [admin]  [db]  [redis]
（ここから下は “外に出さない世界”）
```

* 外に見せるのは「入口の80/443」だけ
* 中は **サービス名で通信**（ComposeのネットワークDNS）🌐

  * Composeは同一ネットワーク上で、サービス名で到達できるのが基本です。([Docker Documentation][2])

---

## 4) “ダメな例” → “勝ち構成”に直す🛠️✨

## ❌ ダメな例：全部 `ports:` で外に出す（競合・事故の元）

```yaml
services:
  web:
    build: ./web
    ports:
      - "3000:3000"

  api:
    build: ./api
    ports:
      - "8787:8787"

  db:
    image: postgres:16
    ports:
      - "5432:5432"  # ← これが事故りやすい😇
```

## ✅ 勝ち構成：外に出すのは proxy の 80/443 だけ

```yaml
services:
  proxy:
    image: caddy:2
    ports:
      - "80:80"
      - "443:443"
    networks:
      - edge
      - internal

  web:
    build: ./web
    networks:
      - internal
    # ports: は書かない！

  api:
    build: ./api
    networks:
      - internal
    # ports: は書かない！

  db:
    image: postgres:16
    networks:
      - internal
    # ports: は絶対に書かない（基本）🧊

networks:
  edge:
  internal:
```

ポイント🌟

* proxyだけが外界と接してる
* web/api/db は “internal ネットワーク”に閉じ込める🔐
* これで **プロジェクトが何個増えてもポート競合しにくい** 🥳

---

## 5) 「でもDBをGUIツールから触りたい…」問題の解き方🍪🧯

ここ、めちゃくちゃ現実的に困りますよね😅
解決は3パターンあります👇（おすすめ順）

---

## パターン①：ホストに出さずに `exec` で触る（最強）💪🐳

```bash
docker compose exec db psql -U postgres
```

* **ポート競合ゼロ**
* **外部公開ゼロ**
* 慣れるとこれが一番ラク😋

---

## パターン②：公開するけど “127.0.0.1 限定” に縛る🔒

```yaml
db:
  image: postgres:16
  ports:
    - "127.0.0.1:5432:5432"
```

* `127.0.0.1` に縛ると、**自分のPCからだけアクセス**
  （「公開は危険」「localhost縛りで限定可能」は公式の説明あり）([Docker Documentation][1])

⚠️ただし：

* 5432は他プロジェクトとも被りやすいので、**競合はまだ起こり得る** 😇

---

## パターン③：公開するけど “ランダムポート” にして逃がす🎲✨

ホスト側ポートを空欄にすると、Dockerが空いてるポートを割り当てます（競合回避に強い）🕊️
`EXPOSE` を自動でランダム公開する考え方も公式で紹介されています。([Docker Documentation][3])

Compose例（短縮形）👇

```yaml
db:
  image: postgres:16
  ports:
    - "127.0.0.1::5432"   # ← ホスト側が空欄＝自動割り当て
```

割り当て確認👇

```bash
docker compose port db 5432
```

* これで **ポート競合しにくい** 🙌
* ただし毎回変わるので、ツール設定は“都度確認”になる 🥹

---

## 6) “長い構文”でキレイに書く（読みやすさUP）📚✨

「127.0.0.1 に縛る」「published/target を明示」みたいな時は、長い構文が便利です👇
Compose仕様にも `host_ip / published / target` が載っています。([GitHub][4])

```yaml
db:
  image: postgres:16
  ports:
    - name: postgres-local
      target: 5432
      published: "15432"
      host_ip: 127.0.0.1
      protocol: tcp
      mode: host
```

---

## 7) よくあるミス集（即死回避）🧯📕

## ミス1：DBを `0.0.0.0:5432` で公開してた😱

* “自分だけのつもり”でも、環境次第で外から届くことがあります
* まずは **127.0.0.1縛り**、できれば **公開しない** が基本🧊
  （公開は危険、localhost縛りで限定可能：公式）([Docker Documentation][1])

## ミス2：`expose:` を書いたからホストから入れると思った🤔

* `expose:` は **コンテナ間で見せる**だけ（ホストには公開しない）という位置づけで語られます([Stack Overflow][5])
* ただし実運用では「同一ネットワークなら普通にサービス名で到達できる」ので、`expose:` は“説明用”になることも多いです（なくても動く場面が多い）🌿

## ミス3：複数Composeを起動したら名前解決が混乱した🌀

* Composeのネットワーク名は「プロジェクト名」由来になります（ディレクトリ名等）([Docker Documentation][2])
* 入口を共通化して複数プロジェクトを共存させるなら、前章でやった **external network** 設計が効いてきます🧵✨

---

## 8) AIに投げる例（コピペで使える）🤖💬

## 例1：ポート公開を“入口だけ”に整理してもらう

```text
次のdocker composeを「proxyだけが80/443をportsで公開」し、
web/api/db/redisは外に出さない構成に書き換えて。
内部通信は同一networkでサービス名解決する前提で。
あわせて、dbをホストから触りたい時のために
(1) execで入る方法 (2) 127.0.0.1縛り (3) ランダムポート
の3案も提示して。
```

## 例2：いま起きてる競合の原因特定

```text
Windowsで docker compose up したら
"bind: address already in use" が出た。
原因になりやすい ports 設定の見方と、
衝突しない設計（入口だけ公開）に直す手順を説明して。
```

---

## 9) ミニ課題🎓✨（15分で“永久解決”が体に入る）

## 課題A：DBの `ports:` を消してもアプリが動くのを確認🧪

1. `db:` の `ports:` を削除
2. `docker compose up -d`
3. API→DB接続が生きてるか確認（アプリ動作でOK）

## 課題B：DBに入りたい時は `exec` で入る🐳

```bash
docker compose exec db psql -U postgres
```

## 課題C：どうしてもGUIで触りたい場合は“例外ルール”を追加🔒

* `127.0.0.1:15432:5432` にして、**固定だけど安全寄り**にする
* もしくは `127.0.0.1::5432` の **ランダム割り当て**にして競合回避🎲

---

## まとめ：この章の“合言葉”📣✨

* **portsは入口だけ！** 🚪
* **DB/Redisは外に出さない！** 🧊
* **例外は 127.0.0.1 縛り or ランダムポート！** 🔒🎲

次の章（ローカルHTTPS）に進むと、さらに「本番っぽい入口運用」に近づいて気持ちよくなります😆🔐

[1]: https://docs.docker.com/engine/network/port-publishing/?utm_source=chatgpt.com "Port publishing and mapping"
[2]: https://docs.docker.com/compose/how-tos/networking/?utm_source=chatgpt.com "Networking in Compose"
[3]: https://docs.docker.com/get-started/docker-concepts/running-containers/publishing-ports/?utm_source=chatgpt.com "Publishing and exposing ports"
[4]: https://github.com/compose-spec/compose-spec/blob/master/spec.md?utm_source=chatgpt.com "compose-spec/spec.md at main"
[5]: https://stackoverflow.com/questions/40801772/what-is-the-difference-between-ports-and-expose-in-docker-compose?utm_source=chatgpt.com "What is the difference between ports and expose in docker- ..."
