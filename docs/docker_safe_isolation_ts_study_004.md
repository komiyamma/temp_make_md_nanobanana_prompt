# 第04章：“安全デフォルト”の作り方：テンプレ→例外だけ追加📦✨

この章のゴールはシンプルです👇
**「何も考えずに `docker compose up` しても、だいたい安全」**な雛形（テンプレ）を先に固定して、**例外（便利だけど危険 / 必要な権限追加）は“別ファイル”に隔離**します😎🔒

---

## 4-1. 発想：安全は“気合い”じゃなくて“デフォルト”で作る🧠🛡️

人間って、疲れてると👇こうなります🤣

* 「とりあえず動けばOK」😇
* 「あとで戻せばOK」😇（戻さない）
* 「今回だけ `privileged`」😇（今回が増える）

だから最初からこうします👇

✅ **安全寄りのベース（base）を固定**
✅ **例外は“別ファイル”にして、毎回“明示的に”選ばせる**
✅ **合成後の設定を可視化して、誤爆を早期発見**👀

---

## 4-2. まず“テンプレの置き場所”を決める📁✨

おすすめ構成（最小だけど強い）👇

* `compose.yaml`：**安全デフォルト（本体）**📦
* `compose.override.yaml`：**ローカル開発の便利設定（例外）**🛠️
* `compose.risky.yaml`：**危険カード用（本当に必要な時だけ）**☠️
* `.env.example`：環境変数の見本（秘密は入れない）🧾
* `secrets/`：秘密ファイル置き場（Git管理しない）🔑🚫
* `.gitignore`：`secrets/` や `.env` を除外🧹

Compose はデフォルトで `compose.yaml` と `compose.override.yaml` を読み込む設計なので、**「安全本体＋開発だけの例外」**が自然に分離できます👍
（複数ファイル運用・マージの考え方は公式手順が一番安全です）([Docker Documentation][3])

---

## 4-3. “安全デフォルト”の核：よく効く5点セット✋🔒

ここからテンプレを作ります。まずは「アプリ（Node/TS想定）」に効く安全寄りセット👇

1. **rootで動かさない** → `user`（デフォルトはrootになりがち）([Docker Documentation][4])
2. **コンテナの中を基本“読み取り専用”** → `read_only`([Docker Documentation][4])
3. **書き込みは“専用の一時領域”だけ** → `tmpfs`（/tmp とか）([Docker Documentation][4])
4. **余計な権限を落とす** → `cap_drop`([Docker Documentation][4])
5. **PID1をちゃんとする** → `init: true`（地味に安定する）([Docker Documentation][4])

> 💡ポイント：**「全部ON」が基本**。困ったら“例外ファイル”で戻す、が正解🙆‍♂️

---

## 4-4. 実装：安全デフォルト `compose.yaml` を作る🧱✨

ここでは例として **app + db**（Node + Postgres）っぽい形にします。
（※dbは書き込みが必要なので、appと同じ“read_only最強セット”は使いません😄）

```yaml
## compose.yaml  ✅安全デフォルト（本体）
name: myapp

## ✅ 使い回す“安全寄りの共通パーツ”
x-app-security: &app_security
  init: true                 # PID1をちゃんとする:contentReference[oaicite:6]{index=6}
  user: "10001:10001"        # root回避:contentReference[oaicite:7]{index=7}
  read_only: true            # 基本は読めるだけ:contentReference[oaicite:8]{index=8}
  cap_drop:
    - ALL                    # 余計な権限を落とす:contentReference[oaicite:9]{index=9}
  tmpfs:
    - /tmp                   # 書き込みは一時領域へ:contentReference[oaicite:10]{index=10}
  restart: unless-stopped

services:
  app:
    <<: *app_security
    build:
      context: .
    environment:
      NODE_ENV: production
    # ✅ “安全デフォルト”では外に公開しない（portsなし）
    networks:
      - internal
    depends_on:
      - db

  db:
    image: postgres:18
    environment:
      POSTGRES_DB: app
      POSTGRES_USER: app
      # ✅ パスワードはあとで secrets/ env で渡す（ここでは仮）
      POSTGRES_PASSWORD: change_me
    volumes:
      - db_data:/var/lib/postgresql/data
    networks:
      - internal
    # ✅ DBも外に公開しない（portsなし）

volumes:
  db_data:

networks:
  internal:
    internal: true
```

## ここが「安全デフォルト」っぽいポイント🥷

* `ports:` を書かない＝**ホストへ公開されない**🚪🔒
* `internal: true` ネットワーク＝**内部だけで話させる**🕸️
* appは **root回避 + 読み取り専用 + tmpfs** で “壊しにくい” 方向へ📦✨

---

## 4-5. “例外だけ追加”のやり方：override で開発向けに戻す🛠️🧩

開発中は、だいたい👇が必要になりますよね？

* ブラウザから叩きたい → `ports`
* ローカルのソースを反映したい → `volumes`（bind mount）
* TSビルド出力やnode_modulesが書き込みたい → `read_only` を緩める（開発だけ）

それは **`compose.override.yaml`** に隔離します👇

```yaml
## compose.override.yaml  🛠️開発だけの例外（自動で合成されやすい）
services:
  app:
    # ✅ 開発だけホストへ公開
    ports:
      - "3000:3000"

    # ✅ 開発だけコード共有（必要なら）
    volumes:
      - ./:/workspace

    # ✅ 開発だけ“書き込みOK”に戻す（本体はread_only:true）
    read_only: false

    environment:
      NODE_ENV: development

    command: ["npm", "run", "dev"]
```

> ✅「本体は安全」「開発だけ例外」
> これがテンプレ化の勝ちパターンです🏆✨

---

## 4-6. 合成結果を“見える化”して事故を防ぐ👀🔍

複数ファイルはマージされます。そこで必須の習慣👇

* **今どんな設定で起動するの？** → `docker compose config` で確認
* **複数ファイルは `-f` を重ねる**（後ろが勝つ）([Docker Documentation][3])

例👇

```bash
## 合成後の最終形を表示（まずこれ！）
docker compose config

## 危険カードを“明示的に”足す（普段は使わない）
docker compose -f compose.yaml -f compose.risky.yaml config
```

---

## 4-7. マージでハマりやすい所（超重要）⚠️🧠

Compose のマージにはクセがあります。特に👇

## ✅ リスト（配列）は“足される”ことがある

`ports` / `secrets` / `security_opt` / `cap_drop` などは **シーケンス扱い**で、マージ時に結合されます（重複は消える系が多い）([Docker Documentation][4])
`tmpfs` などは結合されても重複が残るケースがある、という注意もあります([Docker Documentation][4])

**つまり**👇
「overrideで消したつもりが残ってた」事故が起きます😇

## ✅ “消す”には `!reset` / “置き換え”には `!override` を使う発想

このへんは公式のマージ仕様に沿ってやるのが安全です([Docker Documentation][5])

---

## 4-8. “危険カード”は別ファイルに隔離して、普段は触れない☠️🧱

例：**docker.sock を渡す／特権が必要**みたいなやつは、**普段の開発ファイルに絶対混ぜない**🙅‍♂️🔥
`compose.risky.yaml` を作って、使う時だけ `-f` で明示します👇

```yaml
## compose.risky.yaml  ☠️危険カード隔離（普段は使わない）
services:
  app:
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
```

そして運用ルールはこう👇

* **このファイルは“起動コマンドに -f を書いた時だけ”入る**
* **入れた理由をコメントで残す**（未来の自分救済）📝✨

---

## 4-9. さらに強くしたい人向け：テンプレを“分割可能”にする🧩📦

テンプレが育つと `compose.yaml` が太ります😂
そこで👇が便利です：

* **Extensions（`x-...`）や Fragments を使って“共通部品化”**すると、同じ安全設定を何度も書かずに済みます
* **`include`** を使うと Composeファイルをモジュール化でき、マージより“読みやすい設計”にできます（対応バージョン要件あり）([Docker Documentation][6])

---

## 4-10. 章末ミニ演習（15〜25分）🧪⏱️

## 演習A：安全デフォルトで起動してみる✅

1. `compose.yaml` を作る
2. `docker compose up -d`
3. `app` が **外部公開されてない**ことを確認（portsがないので基本叩けない）😄

## 演習B：例外（開発用）を足して動作確認🛠️

1. `compose.override.yaml` を作る
2. `docker compose up -d --build`
3. `docker compose config` を見て、`ports` が合成されたことを確認👀

## 演習C：危険カードは明示しないと入らないことを確認☠️

1. `compose.risky.yaml` を作る
2. `docker compose up -d`（←入らない）
3. `docker compose -f compose.yaml -f compose.risky.yaml up -d`（←入る）

---

## 4-11. Windowsまわりの“安全の現実”も一言だけ🪟🔐

Docker Desktop を WSL2 バックエンドで使う場合、**同じPC上の別WSLディストリビューションから Docker Desktop の中身に触れうる**（例：`wsl -d docker-desktop`）という性質があります。最大限のセキュリティを求めるなら **Hyper-V バックエンド**の検討、という公式の注意もあります

あと、**Desktop自体の脆弱性修正**も普通に入るので、更新は超大事です🧯
例として、Docker Desktop のリリースノートでは **CVE修正を含む更新**が案内されています([Docker Documentation][7])

---

## この章のまとめ📌✨

* **安全はテンプレで作る**（人間の頑張りに頼らない）😄
* **本体＝安全デフォルト／例外＝別ファイル**で分離📦🧩
* **`docker compose config` で合成後を必ず見る**👀
* **危険カードは `compose.risky.yaml` に隔離**して、`-f` 明示でしか使えないようにする☠️🧱

次の章（第5章）は、このテンプレに対して「危険カードを具体的に捨てる（privileged / docker.sock / 秘密直書き）」を“置き換え案つき”でガッツリやると、かなり強くなりますよ😎🔥

[1]: https://chatgpt.com/c/698c013f-41cc-83a2-b319-96ca4423eb38 "安全な隔離入門"
[2]: https://chatgpt.com/c/698bcc69-212c-83a2-9b2b-5c228120fcf5 "Docker教材設計ガイド"
[3]: https://docs.docker.com/compose/how-tos/multiple-compose-files/merge/?utm_source=chatgpt.com "Merge Compose files"
[4]: https://docs.docker.com/reference/compose-file/services/ "Services | Docker Docs"
[5]: https://docs.docker.com/reference/compose-file/merge/ "Merge | Docker Docs"
[6]: https://docs.docker.com/reference/compose-file/merge/?utm_source=chatgpt.com "Merge Compose files"
[7]: https://docs.docker.com/desktop/release-notes/ "Release notes | Docker Docs"
