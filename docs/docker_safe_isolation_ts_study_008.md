# 第08章：Rootless mode入門：デーモンも非rootで動かす発想🧑‍🚀🔒

![Rootless Daemon Concept](./picture/docker_safe_isolation_ts_study_008_01_rootless_concept.png)

この章はひとことで言うと、**「Docker を動かす“中心（デーモン）”を、root じゃなく“自分ユーザー”で動かして、事故の被害半径を小さくする」**回です🧯✨
（第7章の「docker group＝強い権限😱」の続きとして、めちゃ相性いいやつ！）

---

## 8-1. Rootless modeってなに？何がうれしいの？🎁

Docker はふつう、裏側で **Docker デーモン**が動いていて、これがかなり強い権限を握ります👑
なので「デーモンを操作できる人」は強い…というのが大前提です。

* `docker group` に入れると **root級の権限**になるよ、という警告が公式にあります⚠️ ([Docker Documentation][1])
* そして Docker では、たとえば **ホストの `/` をコンテナに渡す**みたいな強いことができて、結果ホストを好きにいじれてしまう（＝操作できる人は信頼が必要）という説明も公式にあります🧨 ([Docker Documentation][2])

そこで **Rootless mode** です👇

* **Docker デーモンもコンテナも、非rootユーザーで動かす**ことで、デーモン/ランタイムの脆弱性が刺さったときの被害を軽減する、という位置づけです🛡️ ([Docker Documentation][3])
* 仕組みは **user namespace** の中で動かす（`userns-remap` と似てるけど、rootless はデーモン自体も非root）という公式説明があります🧠 ([Docker Documentation][3])

---

## 8-2. 図でイメージ：Rootful と Rootless🗺️

![Rootful vs Rootless Architecture](./picture/docker_safe_isolation_ts_study_008_02_architecture_comparison.png)

```text
【Rootful（いつもの）】
あなた ─docker CLI─▶ Dockerデーモン（強い/root） ─▶ コンテナ
                     ▲
                     └ 強い操作（mount, 特権, host破壊…）が可能になりがち

【Rootless】
あなた ─docker CLI─▶ Dockerデーモン（あなた権限） ─▶ コンテナ（あなた権限ベース）
                     ▲
                     └ “デーモンがrootじゃない”ので、事故っても被害が縮む方向
```

ポイントは「**コンテナ内root ≠ ホストroot**」がより徹底される感じです🙂🔒
ただし「魔法の完全防御」ではなく、できること・できないことがあります（次へ）👉

---

## 8-3. どこまで守れる？どこは守れない？🥋🧩

![Protection Scope Shield](./picture/docker_safe_isolation_ts_study_008_03_shield_scope.png)

## 守れる（軽減できる）方向のもの✅

* **デーモン/ランタイムの脆弱性**が悪用されたときの被害を減らす目的（公式の主旨）🛡️ ([Docker Documentation][3])
* AI拡張やスクリプトがうっかり危険な `docker` 操作をしても、**ホストroot直撃**になりにくい（※「なりにくい」であってゼロではない）🤖🧯

## 守れない（勘違いしやすい）ところ⚠️

* **あなたのユーザー権限でできること**は、Rootless でもできます😇
  例：ホーム配下を bind mount して削除しちゃう、とかは普通に起きます🗑️💥
* 「危険な bind mount（ホスト重要ディレクトリ共有）」みたいな**設計ミス**は Rootless でも死にます☠️
  → 第16章以降の“最小共有”が超大事になるやつ！

---

## 8-4. Rootless の前提条件（ここだけ最低限）🧰

Rootless は、インストール時点から root を必須にしない（前提が揃っていれば）という説明があります✨ ([Docker Documentation][3])
必要な要素はだいたいこのへん👇

* `newuidmap` / `newgidmap`（多くのディストリでは `uidmap` パッケージ）
* `/etc/subuid` と `/etc/subgid` に **最低 65,536 の subuid/subgid** が割り当てられていること
  （公式に例つきで載ってます）🧾 ([Docker Documentation][3])

---

## 8-5. Windows での現実：Rootless をどう扱う？🪟🐧

![Windows Docker Routes](./picture/docker_safe_isolation_ts_study_008_04_windows_routes.png)

Windows で Docker を使うとき、だいたい **Docker Desktop + WSL2** ですよね🙂
Docker Desktop は WSL2 上で Linux ワークスペースを使える、という公式説明があります🐧 ([Docker Documentation][4])

ただし！ここが重要です🚨
Docker Desktop 側の公式ドキュメントに **「Docker Desktop を入れる前に、WSL の各 Linux ディストリに直接入れた Docker Engine/CLI はアンインストールしてね（競合回避）」**という注意があります⚠️ ([Docker Documentation][4])

なので、この章のおすすめは **二択**です👇（混ぜないのが安全！）

## ルートA：Docker Desktopを主役にする（ふつうの開発向け）🧑‍💻

* Desktop はインストール時に管理者権限が要るけど、基本は必要最小限の特権操作をヘルパーでやる設計、という説明があります🧯 ([Docker Documentation][5])
* もし **「不審なイメージを回す」**などが多いなら、Business で使える **Enhanced Container Isolation（ECI）** という強化策もあります🛡️
  ECI は「悪性コンテナが Desktop やホストを壊すのを防ぐ」目的の仕組み、という説明があります🔒 ([Docker Documentation][6])

→ Rootless “そのもの”ではないけど、Windows + Desktop の王道セキュリティ強化として覚えておくと強い💪✨

## ルートB：WSL2（Ubuntu等）に “Rootless Docker Engine” を入れて使う（権限最小化を優先）🐧🔒

* 「docker group が強すぎるのがイヤ」「ローカルで rootful デーモンを持ちたくない」みたいな目的なら、こちらがドンピシャ🎯
* ただし上の通り、**Docker Desktop と混在は避ける**のが無難です⚠️ ([Docker Documentation][4])

この章では **ルートB（Rootless Engine）** をハンズオンでやります👇✨

---

## 8-6. ハンズオン：WSL2で Rootless Docker を動かす🐧🧪

> 目的：**rootless デーモンに接続できてる**のを `docker info` で確認する✅

## Step 1：Rootless セットアップ（公式手順）🛠️

![Rootless Setup Script](./picture/docker_safe_isolation_ts_study_008_05_setup_script.png)

Rootless の公式ページに、`dockerd-rootless-setuptool.sh install` の実行例が載ってます📌
このスクリプトが **systemd の user service** を作って、CLI context “rootless” まで作ってくれる流れです✨ ([Docker Documentation][3])

```bash
## WSL2(Ubuntuなど)の中で実行する想定

## 1) subuid/subgid の確認（例）
grep ^$(whoami): /etc/subuid
grep ^$(whoami): /etc/subgid

## 2) rootless セットアップ（非rootユーザーで）
dockerd-rootless-setuptool.sh install

## 3) 動作確認
docker info
```

`docker info` の出力で **Context が rootless**、Security Options に **rootless** が見えればOKです🎉 ([Docker Documentation][3])

---

## Step 2：自動起動（user systemd）にする🚀

Rootless の Tips に、user systemd 管理の推奨と、linger の有効化が載っています🧷 ([Docker Documentation][7])

```bash
systemctl --user start docker
systemctl --user enable docker
sudo loginctl enable-linger $(whoami)
```

---

## 8-7. Rootless の「できない/ハマる」代表例（超重要）🧯

![Rootless Pitfalls](./picture/docker_safe_isolation_ts_study_008_06_common_pitfalls.png)

## ① 80番ポートが開かない！？（<1024問題）🚪😵

Rootless Tips に、**特権ポート(<1024)を公開したいとき**の回避策が2つ載っています👇 ([Docker Documentation][7])

* `rootlesskit` に `CAP_NET_BIND_SERVICE` を付ける
* `net.ipv4.ip_unprivileged_port_start=0` を設定する

なので最初はこう考えるのが楽です🙂✨

* **基本は 8080/3000/5173 など“1024以上”を使う**
* どうしても 80/443 が必要になってから、上の回避策を検討する🧠🔧

---

## ② `--memory` や `--cpus` が効かない！？（cgroup v2 & systemd）📉😵‍💫

Rootless Tips に、`--cpus`/`--memory`/`--pids-limit` などの **cgroup系の制限**は
**cgroup v2 + systemd のときだけサポート**、満たさない場合は無視される、と明記があります📌 ([Docker Documentation][7])

なのでハンズオン中に「あれ？制限効いてない？」となったら、

* `docker info` の **Cgroup Driver** を見る👀
* WSL2 の systemd や cgroup 周りの状態を確認する🧪

…という流れでOKです🙂

---

## ③ データ置き場がいつもと違う📦

Rootless はデータディレクトリが `~/.local/share/docker`、ソケットが `/run/user/$UID/...` などになる、という説明があります📌 ([Docker Documentation][7])
「消したい」「バックアップしたい」時に迷いがちなので、ここは覚えておくと助かります🧭✨

---

## 8-8. Compose はどうなる？🧩🐳

![Docker Context Switch](./picture/docker_safe_isolation_ts_study_008_07_compose_context.png)

Rootless セットアップは **CLI context “rootless” を作って切り替える**のが基本になっていて（自動で rootless context にする説明もあり）([Docker Documentation][3])、
その状態なら `docker compose` も **そのコンテキストのデーモンへ**普通に繋がります👍

迷ったらこれ👇

```bash
docker context ls
docker context use rootless
docker info | head
```

---

## 8-9. AI拡張と一緒に使うときの“雑に効く”安全ルール🤖🛡️

Rootless は「AIが危ない Docker コマンドを出してきた」時の**最悪を軽減**しやすいのが強みです🧯
でも、**AIが作ったコマンドは“意図せぬ bind mount”が一番事故る**ので、これだけは習慣化しちゃいましょう👇

* `-v` / `--mount` が出たら **ホスト側パスを声に出して読む**📣😆
* `/` や `C:\` っぽいのが見えたら **即停止**🛑
* `--privileged` や `docker.sock` が出たら **「第5章の危険カード」扱い**🗑️⚠️

---

## まとめ：この章の持ち帰り🎒✨

* Rootless は「**デーモンもコンテナも非root**」で動かして、事故の被害を減らす仕組み🧑‍🚀🔒 ([Docker Documentation][3])
* Windows では **Docker Desktop と WSL直インストールを混ぜると競合しやすい**ので、基本は二択で考えるのが安全🪟🐧 ([Docker Documentation][4])
* Rootless は万能ではないけど、AI時代の「うっかり強権限操作」への保険としてかなり価値あり🤖🧯
* ハマりどころは **<1024ポート** と **cgroup制限**（公式Tipsに回避策あり）📌 ([Docker Documentation][7])

---

次の第9章（usernsの考え方🧠🧷）は、この章の「中のroot≠外のroot」をもう一段だけ気持ちよく理解する回になります🙂✨

[1]: https://docs.docker.com/engine/install/linux-postinstall/?utm_source=chatgpt.com "Linux post-installation steps for Docker Engine"
[2]: https://docs.docker.com/engine/security/?utm_source=chatgpt.com "Docker Engine security"
[3]: https://docs.docker.com/engine/security/rootless/ "Rootless mode | Docker Docs"
[4]: https://docs.docker.com/desktop/features/wsl/ "WSL | Docker Docs"
[5]: https://docs.docker.com/desktop/setup/install/windows-permission-requirements/ "Windows permission requirements | Docker Docs"
[6]: https://docs.docker.com/enterprise/security/hardened-desktop/enhanced-container-isolation/ "Enhanced Container Isolation | Docker Docs"
[7]: https://docs.docker.com/engine/security/rootless/tips/ "Tips | Docker Docs"
