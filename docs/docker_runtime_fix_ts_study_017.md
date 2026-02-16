# 第17章：**node_modules問題**（初心者が100%踏むやつ）💣📦

## 0) この章のゴール🎯✨

* 「Dockerで開発したいから、ソースはマウントするぞ！」→ **なぜか動かない…**を卒業する😇
* **node_modules を “混ぜない” 設計**を身につける🧠🔒
* 迷ったらコレ！の結論を、手癖にする✍️

---

## 1) まず結論（合言葉）📌🗣️

✅ **コードは bind mount（共有）**
✅ **node_modules は volume（コンテナ側で管理）**

これが最強の安定ルートです👍✨
理由はシンプルで、**bind mount はコンテナ内の既存フォルダを“上書きで隠す”**ことがあるからです。([Docker Community Forums][5])

---

## 2) 何が起きてるの？（初心者あるある症状）😵‍💫🧨

### 症状A：`node_modules` が消える（あるいは空っぽ）🫥

* Dockerfileで `npm ci` したはずなのに、起動すると

  * `Error: Cannot find module ...`
  * `node_modules` が存在しない
    みたいになるやつ。

👉 原因：**`- .:/app` みたいな bind mount が /app を丸ごと覆って、イメージ内の /app/node_modules を見えなくする**
（USBをマウントしたら元の中身が見えなくなるのと同じ説明が公式系にもあります）([Docker Community Forums][5])
この「見えなくなる」挙動が、node_modules事故の元凶です💥

### 症状B：Windowsの `node_modules` をコンテナで使って爆死💥🪟🐧

* ホスト（Windows）で作られた `node_modules` を、Linuxコンテナが読もうとして…

  * ネイティブ依存（C/C++ビルド系）が絡むと特に地獄🔥
  * `sharp` とか `bcrypt` とか `sqlite3` 系で事故りがち

👉 “環境差を消したくてDocker使ってるのに、node_modulesだけ環境差の塊” になりやすいです😇

### 症状C：`node_modules` がホスト側に root で生えて権限で泣く😭🔐

* いつの間にかホストに `node_modules` ができてて消せない
* Gitの差分が汚れる

---

## 3) 仕組みを1分で理解👀⏱️（なぜ “混ぜると” 壊れる？）

### bind mount と volume の違い（超ざっくり）📦🆚🔗

* **bind mount**：ホストのフォルダを“そのまま”コンテナへ📁
* **volume**：Dockerが管理する領域に置く（ホストのファイル事情から切り離す）🗄️

Docker公式の入門でも、bind mount と named volume の違いが整理されています。([Docker Documentation][6])

そして重要なのがこれ👇
✅ **mount すると、マウント先に元からあった中身は隠れる**([Docker Community Forums][5])

だから、`/app` を bind mount した瞬間、Dockerfileで作った `/app/node_modules` が“見えなくなる”ことが起きます💣

---

## 4) 正解の“型”①：Compose（いちばん王道）👑📄

### ✅ これが基本形（node_modulesをvolumeに逃がす）🛟

```yaml
services:
  app:
    build: .
    volumes:
      - .:/app
      - node_modules:/app/node_modules
    command: npm run dev

volumes:
  node_modules:
```

ポイントはここだけ👇

* `.:/app` → **ソース共有（編集即反映）**🌀
* `node_modules:/app/node_modules` → **依存はコンテナ側に隔離**🔒

この形にすると「ホストのnode_modules」と混ざりにくくなって、事故が激減します👍

> 「build時に入れたnode_modulesが、composeで消える/見えない」系の話は、まさにこの衝突が原因として解説されがちです。([Baeldung on Kotlin][7])

---

## 5) 正解の“型”②：docker run（Composeなしでやるなら）🏃‍♂️🐳

```powershell
docker run --rm -it ^
  -v ${PWD}:/app ^
  -v node_modules:/app/node_modules ^
  -w /app ^
  node:24-bookworm-slim ^
  npm run dev
```

* `-v ${PWD}:/app` でソース
* `-v node_modules:/app/node_modules` で依存を隔離

※PowerShellは改行がややこしいので、最初はComposeが楽です😆

---

## 6) “依存を入れ直したい”とき、どうする？🔁📦

### ありがちな罠😇

* `package.json` を更新したのに、コンテナ側のnode_modulesが古いまま

### 安全ルート（おすすめ）✅

1. **イメージを作り直す**（Dockerfileで `npm ci` してる前提）
2. それでも変なら **volumeを捨てて作り直す**

例：

```powershell
docker compose down -v
docker compose up --build
```

`-v` は volume も消すので、**node_modulesを初期化したいときの最終兵器**です🧹✨

---

## 7) `.dockerignore` もセットで効く🧹🚀

ホスト側の `node_modules` がコンテナビルドに混ざると、重いし事故るしで最悪です😵‍💫
なので `.dockerignore` に入れておくのが基本。

```text
node_modules
dist
.git
```

（第13章の内容がここで効いてきます👍）

---

## 8) Windowsで遅い・重い問題（ついでに回避）🐢💨

`node_modules` はファイル数が多いので、Windows/macOSはI/Oが遅く感じやすいです。
VS CodeのDev Containers公式も、**bind mount はWindows/macOSで遅くなる場合がある**と明言していて、改善策（配置や運用）を案内しています。([Visual Studio Code][8])

> 体感がきついときは、プロジェクトをWSL側のファイルシステムに置く…みたいな“定番ルート”が効きます（ここは第28章あたりでまた強化します🐧✨）

---

## 9) トラブルシュート チェックリスト🔍✅

### まず見る場所（コンテナ内）👀

```bash
ls -al /app
ls -al /app/node_modules | head
node -p "process.platform"
```

* `/app/node_modules` が存在する？
* `process.platform` が `linux` になってる？（普通はなる）

### “node_modulesが見えない”っぽいとき🫥

* `/app` を bind mount してるなら、**イメージ内の /app の中身は隠れる**のが仕様です([Docker Community Forums][5])
  → node_modules を volume に逃がす構成へ戻すのが最短🏁

---

## 10) AI活用ワンフレーズ🤖💬（コピペでOK）

* 「Docker Composeで、ソースは `.:/app` でbind mount、`/app/node_modules` は named volume にして、Windowsでも安定する構成にして。開発コマンドは `npm run dev`。」

* エラーが出たら：
  「このエラーは node_modules のマウント衝突っぽい？原因と最短修正案を3つ出して。`/app` を bind mount してる前提で。」

---

## まとめ🎁✨（この章で持ち帰ること）

* **bind mount は “中身を隠す”** → node_modulesが消える原因になりがち([Docker Community Forums][5])
* だから **コードはbind / 依存はvolume** が安定形💪📦
* `npm ci` のような “クリーンインストール” は再現性に強い（Dockerfileで特に相性良い）([npmドキュメント][9])

---

## 次章の予告👀✨

次の「第18章」は、この章の結論をそのまま固定化して、
**`docker compose up` で開発が始まる“完成形”**を作ります📄🚀
（node_modulesのvolumeも当然入りで！👍）

[1]: https://chatgpt.com/c/6989783d-07f0-83a2-8bc3-d330ed7e6c4d "Node選びの基本"
[2]: https://chatgpt.com/c/6989975c-6754-83a9-b605-0d041b064707 "第13章 `.dockerignore`"
[3]: https://chatgpt.com/c/69897b11-5074-83aa-b329-4aa40321fec1 "TSの固定理由と方法"
[4]: https://chatgpt.com/c/698991b3-c6e8-83ab-90ce-5df30e331d60 "ランタイム固定第11章"
[5]: https://forums.docker.com/t/why-does-the-node-modules-folder-requires-a-volume-in-order-to-be-present-in-the-container/109857?utm_source=chatgpt.com "Why does the node_modules folder requires a volume in ..."
[6]: https://docs.docker.com/get-started/workshop/06_bind_mounts/?utm_source=chatgpt.com "Part 5: Use bind mounts"
[7]: https://www.baeldung.com/ops/docker-npm_install-missing-node_modules-fix?utm_source=chatgpt.com "Fix Missing node_modules in Docker Compose After npm ..."
[8]: https://code.visualstudio.com/remote/advancedcontainers/improve-performance?utm_source=chatgpt.com "Improve disk performance"
[9]: https://docs.npmjs.com/cli/v9/commands/npm-ci/?utm_source=chatgpt.com "npm-ci"
