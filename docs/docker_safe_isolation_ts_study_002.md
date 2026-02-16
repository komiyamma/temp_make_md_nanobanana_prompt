# 第02章：Dockerの境界線：ホスト／デーモン／コンテナ／ネット🌍🚧

この章はひとことで言うと、「事故が起きる“場所”を間違えないための地図」づくりです🗺️✨
隔離って“強い設定”を覚える前に、**どこが誰の支配下で、何が漏れたり壊れたりしうるのか**を把握すると一気にラクになります🙂

---

## 1) まずは全体の地図 🗺️👀

Dockerはざっくり「命令する人（クライアント）」「実行する親玉（デーモン）」「動く箱（コンテナ）」に分かれます。Docker公式の説明もこのクライアント↔デーモンの形を前提にしています。([Docker Documentation][1])

イメージ図（超重要）👇

```
あなた（VS Code / ターミナル）
  └─ docker コマンド（クライアント）
        └─ Docker デーモン（dockerd：親玉）
              ├─ コンテナ（Node等が動く箱）
              ├─ イメージ（箱の設計図）
              ├─ ネットワーク（箱どうしの道）
              └─ ボリューム（データ置き場）
```

そしてWindowsの場合、**LinuxコンテナはWSL 2のLinux側で動く**のが基本です（Docker DesktopのWSL 2 backend）。([Docker Documentation][2])

---

## 2) 境界線①：ホスト（Windows）🪟🧱

## ホストってどこ？🤔

* いま使ってるPC本体（Windows）が“ホスト”の中心です🪟
* ただしDocker Desktop + WSL 2だと、**LinuxコンテナはWSL 2のLinux環境（実質VMっぽい領域）で実行**されます。([Docker Documentation][2])

## ここで起きがちな事故💥

* **ホストのフォルダをコンテナに共有（bind mount）**していると、コンテナ側のバグ・侵害が「ホストのファイル破壊・流出」につながります😱
  → “隔離”のつもりが、**壁に穴を開けて通路を作ってる**状態です🚪🕳️
* “Dockerが保存しているデータの場所”も意識が必要：Dockerデーモンはデータディレクトリに、コンテナ・イメージ・ボリュームなどをまとめて持ちます。([Docker Documentation][3])
  （場所は環境差がありますが「デーモンが全部握ってる」は共通🧠）

---

## 3) 境界線②：デーモン（dockerd）👑🔥

## デーモンは何者？🧠

* あなたの `docker run` とか `docker compose up` を受けて、実際に箱を作ったり壊したりする「実行役」です。
* 重要ポイント：デーモンは基本めちゃ強い権限で動きます。Docker公式も「デーモンの攻撃面（attack surface）」を明確に注意しています。([Docker Documentation][4])

## “デーモンに命令できる”＝どれくらい強い？😨

* Linuxでは、`docker` グループに入れると**rootレベル権限**になる、とDocker公式が警告しています。([Docker Documentation][5])
  → つまり **「dockerコマンドが叩ける人＝ホスト級の操作ができる人」** になりがちです💪💣
* デーモンへの入口（ソケット/API）を守る話も公式にあります（TLSで保護など）。([Docker Documentation][6])

## この章で覚える合言葉🧷

* **「コンテナが強い」じゃなくて「デーモンが強い」**👑
* だから「デーモンに触れる入口（docker.sockやAPI公開）」は、後の章で最優先で警戒します🚨

---

## 4) 境界線③：コンテナ（箱の中）📦🐣

## コンテナはVMじゃない（ここ大事）⚠️

* コンテナは“別OS”というより、Linuxの仕組み（namespaces / cgroups 等）でプロセスを分けてる感じです。Docker公式もカーネル機能（namespaces/cgroups）や設定ミス等をセキュリティの主要ポイントとして挙げています。([Docker Documentation][4])

## ここで起きがちな事故💥

* 「コンテナの中でroot」だと、できることが増えます（だから後半で **最小権限** に寄せていく）。
* でもこの章の結論はシンプル：
  **“箱の中だけで完結してる限り”は被害が箱の中で止まりやすい**🙂
  逆に、ホスト共有・デーモン共有・ポート公開で壁が薄くなります🧱→🧻

---

## 5) 境界線④：ネットワーク（道）🕸️🚦

## 「コンテナ同士の道」と「外への出口」は別物 🚪🌐

* Composeはデフォルトで**アプリ用のネットワークを1個作り**、同じCompose内のサービスはそこで相互に通信できます（サービス名で見つかる）。([Docker Documentation][7])
* 一方で、`ports:` を使うと **ホスト側に“入口”が開きます**（外から入れる道ができる）🚪😈

## もう1個ポイント：デフォルトbridgeは“古い仕組み扱い”👴

Docker公式は、デフォルト `bridge` ネットワークを「レガシーで、本番用途には推奨しない」と明言しています。([Docker Documentation][8])
→ 「ユーザー定義ネットワークを使う」が基本の考え方になってます🧠✨（Composeはそれを自動でやってくれるイメージ）

---

## 6) ミニ演習：あなたの環境で“境界線”を目で見る 👀🔍

## 演習A：ClientとServer（デーモン）が分かれてるのを確認✅

PowerShellでOKです🙂

```powershell
docker version
```

見どころ👇

* `Client:` と `Server:` が別で出ます
* **Serverの方が“実行してる側（デーモン）”**です👑

（Dockerの基本構造は「クライアントがデーモンに命令する」モデルです。([Docker Documentation][1])）

---

## 演習B：デーモンの“強さ”を意識する質問タイム🧠💣

```powershell
docker info
```

自分にこう問いかけてください👇

* 「これ（Server）が落ちたら、全部止まる？」→ 止まる🥶
* 「これ（Server）に命令できたら、何でもできそう？」→ できそう😇
  この感覚が、隔離の設計でめちゃ役立ちます🛡️

---

## 演習C：Composeネットワークの“内側/外側”を確認🕸️🚪

すでに何かComposeプロジェクトがある前提でOK（なければ後で章が進んでからでも👍）

1. ネットワーク一覧

```powershell
docker network ls
```

2. Composeが作ったっぽいネットワークを覗く
   （名前はプロジェクト名由来になりやすいです）([Docker Documentation][7])

```powershell
docker network inspect <network-name>
```

見どころ👇

* `Containers` に同じアプリのコンテナが並ぶ → **内側の道**🕸️
* `ports:` を設定してるサービスだけがホスト側に出口を持つ → **外への入口**🚪

---

## 7) よくある勘違い（ここで直すと強い）🧯🙂

* ❌「コンテナが一番偉い」
  ✅ 一番偉いのは **デーモン**（コンテナを作る/壊す/マウントする権限の中心）([Docker Documentation][4])

* ❌「秘密は.envに置いとけば隔離される」
  ✅ `.env` は“ファイル”なので、共有したら見えます。まずは**境界線（どこまで見えてる？）**の把握が先🗺️

* ❌「ネットワークはよくわからんけど ports はとりあえず全部開ける」
  ✅ `ports` は“入口を開ける”行為。まずは「内側だけで繋ぐ」が安全寄りです🕸️🔒

---

## まとめ：この章の持ち帰り🎒✨

* **ホスト**：ファイル共有した瞬間、壁が薄くなる🧱→🧻
* **デーモン**：ここが権限の王様👑（触れる入口は最重要で守る）([Docker Documentation][5])
* **コンテナ**：箱の中に閉じてれば被害が止まりやすい📦
* **ネット**：内側の道（Composeネットワーク）と外への入口（ports）は別🚪🕸️([Docker Documentation][7])

次の第3章は、この地図を“判断基準”に変える回です✂️🔐📤
つまり「最小権限・最小共有・最小公開」を、迷わず選べるようにしていきます🙂💪

[1]: https://docs.docker.com/get-started/docker-overview/?utm_source=chatgpt.com "What is Docker?"
[2]: https://docs.docker.com/desktop/features/wsl/?utm_source=chatgpt.com "Docker Desktop WSL 2 backend on Windows"
[3]: https://docs.docker.com/engine/daemon/?utm_source=chatgpt.com "Docker daemon configuration overview"
[4]: https://docs.docker.com/engine/security/?utm_source=chatgpt.com "Docker Engine security"
[5]: https://docs.docker.com/engine/install/linux-postinstall/?utm_source=chatgpt.com "Linux post-installation steps for Docker Engine"
[6]: https://docs.docker.com/engine/security/protect-access/?utm_source=chatgpt.com "Protect the Docker daemon socket"
[7]: https://docs.docker.com/compose/how-tos/networking/?utm_source=chatgpt.com "Networking in Compose"
[8]: https://docs.docker.com/engine/network/drivers/bridge/?utm_source=chatgpt.com "Bridge network driver"
