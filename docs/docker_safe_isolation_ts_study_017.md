# 第17章：読み取り専用マウントで“壊せない”にする📎🔒

この章のゴールはシンプルです👇
**「コンテナがホストのコードを“読めるけど壊せない”状態にする」**✨
つまり、うっかり `rm -rf` しても、AIが変な指示で暴走しても、**被害が広がりにくい**設計にします🤖🧱

---

## 1) まず結論：コード共有は “ro”、書き込みは“専用箱”へ📦✅

![Read-Only Shield Concept](./picture/docker_safe_isolation_ts_study_017_01_ro_shield_concept.png)

バインドマウントはデフォルトだと**ホスト側のファイルをコンテナから書き換えられます**😱（削除もできる）
なので **`ro` / `readonly` を付けて読み取り専用にする**のが基本です。([Docker Documentation][1])

ここで大事な考え方👇

* **コード（srcや設定）**：基本 **read-only**（壊せない）🔒
* **書き込みが必要なもの**（node_modules / キャッシュ / 生成物 / 一時ファイル）：**別のrw領域**に逃がす🧺

![Code RO Data RW Split](./picture/docker_safe_isolation_ts_study_017_02_code_ro_data_rw_split.png)

> “共有するけど壊せない”＝事故の確率も、事故ったときの被害も減ります💪✨

---

## 2) read-onlyマウントって何が起きるの？🤔

![Read-Only Mechanism](./picture/docker_safe_isolation_ts_study_017_03_ro_mechanism_allow_deny.png)

## ✅ できること

* コンテナはマウントしたファイルを**読む**（実行も）📖

## ❌ できないこと

* マウント先に**書く / 消す / 変更する**🛑
  例：`touch`、`npm install` がその場所に書こうとすると失敗します🙅‍♂️

Docker公式も「ホストをコンテナから変更できるのはセキュリティ的に危ない。`ro/readonly`で防げる」と明記しています。([Docker Documentation][1])

---

## 3) まずは最小サンプル：`docker run` で ro を体験🧪

* `--mount ... readonly` でも
* `-v ... :ro` でもOKです。([Docker Documentation][1])

PowerShell例（概念だけ掴めればOK）👇

```bash
## 例：カレントフォルダを /app に read-only で渡す
docker run --rm -it --mount type=bind,source="$(pwd)",target=/app,readonly node:lts bash
```

コンテナに入ったら👇

```bash
ls /app
touch /app/NOPE.txt   # ← これは失敗するはず😄🔒
```

---

## 4) Composeでやる：短い書き方と、事故りにくい長い書き方🧩

![Compose Syntax Short vs Long](./picture/docker_safe_isolation_ts_study_017_04_compose_syntax_short_vs_long.png)

## A. 短い書き方（まずこれでOK）✍️

`...:ro` で read-only にできます。([docs.docker.jp][2])

```yaml
services:
  app:
    image: node:lts
    working_dir: /app
    volumes:
      - ./:/app:ro
```

## B. 長い書き方（おすすめ：意図が明確で壊れにくい）🧠✨

Compose仕様には、長い形式で **`read_only: true`** が定義されています。([docs.docker.jp][2])

```yaml
services:
  app:
    image: node:lts
    working_dir: /app
    volumes:
      - type: bind
        source: .
        target: /app
        read_only: true
```

> 長い形式は「これはbindだよ」「ここがsourceだよ」「read-onlyだよ」が見えるので、未来の自分に優しいです😊📝

---

## 5) “書き込みが必要”問題の解き方：rwは「専用フォルダ／専用ボリューム」へ🧺✅

Node/TypeScriptだと、すぐ詰まります👇

* `npm install` → `node_modules` に書きたい
* `tsc` → `dist` に書きたい
* ツール → `.cache` や `/tmp` に書きたい

解き方は「**書く場所だけ別にrwで用意**」です💡

## パターン1：`node_modules`だけ“名前付きボリューム”に逃がす📦

![Nested Mount Override](./picture/docker_safe_isolation_ts_study_017_05_nested_mount_override.png)

`/app` は ro、でも `/app/node_modules` だけ別マウントで rw にできます。

ここでポイント👇
**あるマウントの上に、より“深いパス”のマウントを重ねると、そっちが優先**されます。
（バインドマウントは「上書きして見えなくなる」挙動がある、という説明があります）([Docker Documentation][1])

```yaml
services:
  app:
    image: node:lts
    working_dir: /app
    volumes:
      # コードは read-only
      - type: bind
        source: .
        target: /app
        read_only: true

      # node_modules は別箱（rw）
      - type: volume
        source: app-node-modules
        target: /app/node_modules

volumes:
  app-node-modules:
```

## パターン2：一時ファイルは `tmpfs`（メモリ上）へ🧻⚡

![Tmpfs Memory Mount](./picture/docker_safe_isolation_ts_study_017_06_tmpfs_memory_mount.png)

Compose仕様に `tmpfs` があります。([docs.docker.jp][2])

```yaml
services:
  app:
    image: node:lts
    working_dir: /app
    tmpfs:
      - /tmp
```

---

## 6) 演習：わざと壊そうとして、壊れないのを確認😈🔒

## 演習1：roにして“削除できない”を体感

1. Composeで `/app` を `read_only: true` にする
2. 起動👇

```bash
docker compose up -d
docker compose exec app bash
```

3. 中で試す👇

```bash
echo "hack" > /app/hack.txt   # 失敗してOK😄
echo "tmp ok" > /tmp/ok.txt   # これは成功してOK👌
```

## 演習2：node_modulesだけrwにして、`npm i` できるようにする📦

1. `/app` ro + `/app/node_modules` volume を追加
2. コンテナ内で👇

```bash
npm install
```

> ✅ 成功したら「rwを最小に分離できた」ってことです🎉

---

## 7) よくある詰まりポイント集😵‍💫➡️😄

## 詰まり1：`npm install` がコケる

![Npm Install RO Fail](./picture/docker_safe_isolation_ts_study_017_07_npm_install_ro_fail.png)

原因：`/app` が ro のまま `node_modules` へ書こうとする
対策：**`/app/node_modules` を volume に分離**（上のパターン1）✅

## 詰まり2：ビルド成果物 `dist/` が作れない

原因：`dist` がコード配下で、そこへ書けない
対策案（おすすめ順）👇

* ✅ `dist` だけ別のrwマウント（volumeや別フォルダ）にする
* ✅ ビルドはホスト側で行い、コンテナは実行だけにする
* ✅ 生成物を `/tmp` や `/out` など“書ける場所”に出す

## 詰まり3：Docker Desktopの“中でLinux VM”問題が不安

Docker DesktopはデーモンがVM内で動き、バインドマウントはその橋渡し機構で動きます（透明に扱える）と説明されています。([Docker Documentation][1])
なので「**roはコンテナ内でちゃんと効く**」前提でOKです👌

## 詰まり4：サブマウント（入れ子）がroにならないことがある

Docker Engineには「再帰的read-only（recursive read-only）」の話があり、**Linuxカーネル 5.12+ が要件**など注意点があります。([Docker Documentation][1])
対策：まずは **入れ子マウントを避ける**／“roにしたい範囲をシンプルにする”が安全です🙂

---

## 8) 今日のチェックリスト✅🔍

* [ ] コード共有は **read-only** にした？📎🔒
* [ ] 書き込みは **node_modules / キャッシュ / 一時**を“別箱”に分離した？📦🧺
* [ ] 「どこがrwか」を自分で説明できる？🧠✨
* [ ] （余裕）`tmpfs` で一時ファイルをメモリ化した？🧻⚡

---

次の章（第18章）で、さらに危険度が跳ね上がる **`docker.sock` を渡す話**に行くので、
第17章の「**壊せない共有**」はここでしっかり身体に染み込ませておくと強いです😄🧱🔒

[1]: https://docs.docker.com/engine/storage/bind-mounts/ "Bind mounts | Docker Docs"
[2]: https://docs.docker.jp/compose/compose-file/ "Compose Specification（仕様） — Docker-docs-ja 24.0 ドキュメント"
