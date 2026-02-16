# 第06章：ログを見る練習：追いかける・絞る 👀🏃‍♂️

この章は「**欲しいログだけを、最短で見つける**」練習回です🧾✨
ログが大量でも、**追いかける（follow）**＆**絞る（tail/since/service）**ができると一気にラクになります😎👍

---

## ① 今日のゴール 🎯

* **最後の10行だけ**出して、状況を説明できる 🧾🔟
* **いま起きてるログを追いかける**（止め方も含む）👀🏃‍♂️
* **サービス／時間帯**で絞って、ノイズを減らせる 🎯⏱️

---

## ② 図（1枚）🖼️

```text
（大量ログ）🧾🧾🧾🧾🧾🧾🧾🧾
   │
   ├─ サービスで絞る  → docker compose logs api
   │
   ├─ 最後だけ見る    → --tail=10
   │
   ├─ いま追う         → --follow
   │
   └─ 時間で絞る       → --since=10m  / --until=...
```

---

## ③ 手を動かす（手順 5〜10 個）🛠️

### 0) まず「誰のログを見る？」を確定する 🧩

Composeで動かしてるなら、まずこれ👇

```bash
docker compose ps
```

* `api` みたいなサービス名が見えるはずです👀
* もし「コンテナ名で指定したい」なら👇

```bash
docker ps
```

---

### 1) “最後の10行だけ”見る（最速で状況把握）🔟👀

まずはこれが基本形です🧠✨

```bash
docker compose logs --tail=10 api
```

* `--tail` は「末尾から何行見るか」🧾
* Compose側の `--tail`/`--follow`/`--since`/`--timestamps`/`--until` などが公式で用意されています。([Docker Documentation][1])

👉 期待する雰囲気（例）
`api-1  | INFO  GET /ping 200 2ms`

---

### 2) “追いかける”（リアルタイム監視）👀🏃‍♂️

いま発生してる問題を追うならこれ🔥

```bash
docker compose logs --follow api
```

* `--follow (-f)` は「新しいログが出るたびに流し続ける」やつです👀📣([Docker Documentation][1])
* 止めるときは `Ctrl + C` ⛔（たまに複数回必要な環境もあります😅）

---

### 3) “時間で絞る”（直近だけ見る）⏱️🎯

「さっきの操作のログだけ見たい！」を一発でやります👍

```bash
docker compose logs --since=10m api
```

* `--since` は **タイムスタンプ**でも **相対時間（例: 42m）**でもOKです⏱️([Docker Documentation][1])
* 「ここまで（上限）」も欲しいなら👇

```bash
docker compose logs --since=10m --until=2m api
```

`--until` も公式オプションです🧾([Docker Documentation][1])

---

### 4) “タイムスタンプ付き”で見る（時系列が崩れない）🕒📌

複数サービスを見たり、切り分けをするなら付けとくと強いです💪

```bash
docker compose logs --timestamps --tail=20 api
```

`--timestamps (-t)` は公式オプションです🕒([Docker Documentation][1])

---

### 5) “プレフィックスを消す”（読みやすくする）🧹✨

Composeのログは `api-1 |` みたいなプレフィックスが付くことが多いです。
それが邪魔なら👇

```bash
docker compose logs --no-log-prefix --tail=20 api
```

`--no-log-prefix` も公式オプションです👌([Docker Documentation][1])

---

### 6) “文字で絞る”（ERRORだけ拾う）🔎🧯

**PowerShellなら**👇

```powershell
docker compose logs api | Select-String "ERROR"
```

**cmd.exeなら**👇

```bat
docker compose logs api | findstr ERROR
```

> Compose自体には「grepみたいな正規表現フィルタ」は薄いので、パイプで絞るのが手堅いです🔎✨

---

### 7) 連打してログを増やす（観察の練習）🔁📣

`/ping` を連打してログが増えるのを体感します😆

**PowerShell**例👇

```powershell
1..20 | % { iwr http://localhost:3000/ping -UseBasicParsing | Out-Null }
```

終わったら、最後だけ見る👇

```bash
docker compose logs --tail=10 api
```

---

### 8) 「docker logs」も使える（コンテナ直指定）📦🧾

Composeじゃなく「このコンテナだけ！」なら👇
（`docker logs` は `docker container logs` の別名です🧠）([Docker Documentation][2])

```bash
docker logs --tail=10 <container_name_or_id>
```

よく使う組み合わせ👇（公式的にもOKな組み合わせです）([Docker Documentation][2])

```bash
docker logs --since=10m --tail=200 --follow <container_name_or_id>
```

* `--since` は RFC3339 / UNIXタイム / duration（例 `3h`, `1m30s`）などがOKです⏱️([Docker Documentation][2])
* タイムゾーンを省略すると「クライアント側のローカルTZ扱い」になる点も要注意です🕒（Zや+09:00を付けると安全）([Docker Documentation][2])

---

### 9) “保存して共有する”（相談・比較がラク）💾🤝

「直近10分のapiログ」をファイルに保存👇

**PowerShell**例👇

```powershell
docker compose logs --since=10m api | Out-File .\api-last10m.log -Encoding utf8
```

---

## ④ つまづきポイント（3つ）🪤😵

1. **ログが出ない**
   → アプリが標準出力（stdout/stderr）に出してない可能性大です🙈（ファイルに書いてると `logs` に出ません）

2. **サービス名を間違える**
   → `docker compose ps` でまず “正しいサービス名” を確定しましょう👀🧩

3. **時間で絞ったのに「思ったより出ない」**
   → `--since` の基準（TZ）や、そもそもその時間帯にリクエストが飛んでないケースが多いです⏱️💦
   → いったん `/ping` を数回叩いてから `--since=1m` で試すと確実👍

---

## ⑤ ミニ課題（15分）⏳🎮

**目的： “最後の10行だけ見て状況説明” ができるようになる！**🧾✨

1. `docker compose logs --tail=10 api` を実行🔟
2. `/ping` を20回叩く🔁
3. もう一度 `--tail=10` を実行して、増えたログの特徴をメモ📝
4. `--since=1m` で「直近だけ」にして読みやすさを体感⏱️
5. `Select-String "ERROR"`（または `findstr ERROR`）で絞る練習🔎

**提出（自分用メモ）**📝

* 「最後の10行から分かること」を **2行で説明**してみてください😆

---

## ⑥ AIに投げるプロンプト例（コピペOK）🤖📋

```text
docker compose のログを見たいです。
目的は「apiサービスの直近10分のログだけを見て、ERRORっぽい行だけ抽出」すること。
使うのは docker compose logs / PowerShell（Select-String）です。
最短コマンド列を3パターン（①まず全体→②絞る→③保存）で提案して。
```

```text
このログ（貼り付けます）から、原因候補を3つに絞って。
それぞれ「次に見るべきログの絞り方（--since/--tail/検索語）」もセットで出して。
```

---

次の第7章（アクセスログ）に行く前に、ここで覚える“最強4点セット”はこれです😎🔥
`--tail` 🔟 / `--follow` 👀 / `--since` ⏱️ / `--timestamps` 🕒

[1]: https://docs.docker.com/reference/cli/docker/compose/logs/ "docker compose logs | Docker Docs"
[2]: https://docs.docker.com/reference/cli/docker/container/logs/ "docker container logs | Docker Docs"
