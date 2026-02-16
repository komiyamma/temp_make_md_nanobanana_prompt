# 第10章：「デーモンが握る力」を知る：攻撃面（attack surface）入門🎯🧨

この章はひとことで言うと、**「Dockerで“本当に強い権限”がどこに集まってるかを地図にする回」**です🗺️✨
地図があると、AIがうっかり危険な提案をしても😇、あなたが「それは強い操作だから別手順ね！」って止められるようになります🛑🤖

---

## この章でできるようになること✅

* **Dockerの“強い入口”**（＝攻撃面）を、言葉と図で説明できる📌
* **危険度が高い操作**をパッと分類できる（誤爆しにくくなる）🧯
* 強い操作を **「手順として固定」**して、うっかり事故を減らせる🧱

---

## 10-1. まず結論：Dockerデーモンは“最強の受付”🏢🦾

Dockerを動かす中心には **Dockerデーモン（dockerd / Docker Engine）**がいます。
こいつが強い理由はシンプルで、**「コンテナを作る＝ホストの重要リソースを操作する」**を代行してるからです💪

Docker公式も、デーモンは基本的に強い権限（root相当）で動き、**信頼できる人だけが操作できるべき**だと明確に言っています。さらに、ホストの `/` をコンテナにマウントして、コンテナからホストのファイルを無制限にいじれる例まで出しています😱💥 ([Docker Documentation][2])

👉 つまり、

* **デーモンに命令できる人（またはプロセス）**
  = **ホスト級の操作に近いことができる可能性が高い**🔥

これが「攻撃面（attack surface）」の中心です🎯

---

## 10-2. 「攻撃面（attack surface）」ってなに？👀🔍

**攻撃面**＝「悪いことが起きうる入口の集合」🚪🧨
セキュリティの話でよく出る言葉だけど、Dockerでは特にこう考えると分かりやすいです👇

* **入口A**：Docker CLI が話しかける“APIの入口”（ソケット / パイプ / TCP）
* **入口B**：Docker Desktopの裏側（特権ヘルパーなど）
* **入口C**：コンテナ作成時に渡す“強い設定”（マウント、特権、ネットワーク等）
* **入口D**：ビルド（DockerfileのRUNは“実行”そのもの）🏗️💣

このうち、**入口AとBは「そこを握られたら負けやすい」入口**です😇

---

## 10-3. Windowsの全体図：どこが強い？どこが入口？🪟🗺️

Docker Desktopは、Windows上で「ちょっと複雑な役割分担」をしています。
Docker公式の “Windows permission requirements” には、**特権ヘルパーがWindowsサービスとして SYSTEM 権限で動く**こと、**特定の名前付きパイプでやり取りする**こと、そして **`docker-users` グループが特権操作へのアクセス制御に使われる**ことが書かれています🔒 ([Docker Documentation][3])

ざっくり図にするとこんな感じ👇

```text
あなた（ターミナル / VS Code）
   │  docker / docker compose
   ▼
Docker CLI
   │  (APIで命令)
   ▼
Docker Desktop（アプリ）
   │
   ├─（非特権の入口：一部のパイプは起動ユーザー/管理者等に限定）
   │
   └─（特権ヘルパー：Windowsサービス com.docker.service / SYSTEM権限）
          ▲  ※ docker-users によってアクセス制御される領域がある
          │
          ▼
Linux側のDocker Engine（WSL2/VM上）
   │
   ▼
Containers
```

🎯 この図のポイントは2つだけ覚えればOK！

1. **“Docker Engineに命令できる”経路が強い**（入口A/B）
2. **その命令で“強い設定のコンテナ”を作れるのがヤバい**（入口C）

---

## 10-4. 「強い操作」カードを分類しよう🃏⚠️（誤爆防止）

ここからが超重要！
Dockerのコマンドは便利だけど、便利なものほど“強い”です😇✨

## Aランク：ホストのファイルに触る系💽🔥

* **bind mount**（ホストのフォルダをコンテナへ渡す）

  * 例：`-v C:\something:/work` みたいなやつ
  * これ、やり方によっては「コンテナからホストの大事な場所を触れる」になります💥
  * Docker公式が “ホストの `/` をコンテナに見せられる” と明示してるくらい強いです😱 ([Docker Documentation][2])

## Sランク：Docker Engine API に触る系（= ほぼ最強）🐙🔥

* **`docker.sock` をコンテナに渡す**（Linux側でよくある）
* **Docker Engine をTCPで公開する**（`2375` など）

  * これ系は「入口Aを大きく広げる」行為です🚪💣
  * Docker公式も、リモートからデーモンへ接続できるようにするのは危険で、対策なしだと **リモートの非rootユーザーでもホストのroot相当に到達しうる**と警告しています⚠️ ([Docker Documentation][4])

## Aランク：特権コンテナ系🦾🧨

* `--privileged`
* `--pid=host`（ホストのプロセス空間を共有）
* `--net=host`（ネットワーク分離を弱める）
* `--cap-add`（権限を足す）

（この章では深入りしないけど）こういうのは「隔離が薄くなるスイッチ」だと思ってください🔁🧯

## Bランク：ビルド系🏗️💣

* `docker build` は “ビルド中にコマンド実行” が普通に起きます（Dockerfileの `RUN`）
* つまり、**怪しいDockerfile / 怪しいビルドコンテキスト**を食べるのは危険になり得ます😇

---

## 10-5. 今日から使える！「強い操作」は手順で固定🧱✅

ここがこの章のゴールです🎉
**強い操作を “気合い” で避けるのはムリ**なので、ルールと手順で潰します🧯

## ルール①：Docker Desktopは更新をサボらない🆙🛡️

Docker Desktopは過去に、**コンテナからDocker Engine APIへ到達できてしまう脆弱性（CVE-2025-9074）**が報告され、修正されています。しかも「docker.sock をマウントしてなくても」起きうるタイプでした😱
Docker公式のセキュリティ告知に修正内容が書かれており、NVDにも概要があります📚 ([Docker Documentation][5])

✅ だから結論：**更新は“隔離の一部”**です🧱✨

## ルール②：デーモンの入口をネットに出さない🌐🚫

「Expose daemon on tcp://... without TLS」みたいなのは、学習用でも癖になるので基本オフ推奨🙅‍♂️
もしリモート接続が必要なら、Docker公式が推している **SSH や TLS で守る方法**に寄せましょう🔐
（`docker context` で安全に切り替える例も公式にあります） ([Docker Documentation][6])

## ルール③：特権が要る操作は“場所”を分ける🧑‍🚀🧯

* 普段：いつもの開発用ターミナル（普通の `docker compose up` だけ）
* 例外：強い操作だけをやる“専用ターミナル / 専用手順”

「同じ場所でやる」から誤爆するんです💥
**場所を分ける**だけで事故率がガクッと下がります📉✨

## ルール④：`docker-users` を増やさない👥✂️

Docker Desktopの特権ヘルパーは Windowsサービス（SYSTEM権限）で動き、`docker-users` がアクセス制御に関係する領域があります🔒 ([Docker Documentation][3])
つまり、ここに人を増やすのは “権限が強い入口を増やす” のに近いです😇

---

## 10-6. ハンズオン①：自分のPCの「入口」を棚卸し🧾🔍

まずは現状把握！5分で終わります🕔✨

## ① Dockerのバージョンと接続先（context）を見る👀

```powershell
docker version
docker context ls
docker context inspect default
```

* **context** を見ると「どのEngineに話してるか」が分かります📌
* うっかり別マシンや別環境に向けて操作して事故るの、あるあるです😇💥
  （安全運用の基本として、公式も `docker context` を使った切替を案内しています） ([Docker Documentation][6])

## ② `docker-users` のメンバーを確認👥

```powershell
net localgroup docker-users
```

いたら「強い入口を触れる人が誰か」が一発で分かります✅

## ③ “危険スイッチ” を自己点検（チェックするだけ）🧯

* Docker Desktopの設定で「デーモンをTCPで公開」系がオンになってない？
* もしオンにするなら **TLS/SSHで守る**（公式推奨）🔐 ([Docker Documentation][6])

---

## 10-7. ハンズオン②：危険コマンド分類ゲーム🎮🃏（答え付き）

次のコマンド、危険度で分類してみてください👇
A: わりと安全 / B: 注意 / C: 強い（手順固定推奨）

1. `docker compose up -d`
2. `docker run -v C:\Users\you\project:/app ...`
3. `docker run --privileged ...`
4. `docker run -p 3000:3000 ...`
5. `dockerd -H tcp://0.0.0.0:2375`

---

## ✅答え

1. **A**（いつもの開発運用の範囲になりやすい）🙂
2. **B〜C**（共有する場所次第。ホストの重要領域を渡すと一気にC）💽⚠️
3. **C**（隔離を薄くする代表格）🦾💥
4. **B**（公開範囲を広げる＝入口が増える）🚪🌐
5. **C**（デーモンの入口をネットに出すのは危険。公式も強く警告）🔥 ([Docker Documentation][4])

---

## 10-8. ありがちな事故パターン集😇💣（先に潰す）

## 事故①：AIの提案をそのまま貼って、`--privileged` が混ざる🤖🧨

✅ 対策：**強い操作は“別手順”ルール**（この章のルール③）
AIは便利だけど、最終判断はあなたの地図🗺️✨

## 事故②：「動かないから」と `2375` を開ける😇🌐

✅ 対策：リモート接続が必要なら **SSH/TLS** に寄せる（公式）🔐 ([Docker Documentation][6])

## 事故③：なんとなく `docker-users` に追加しちゃう👥💥

✅ 対策：増やさない。増やすなら理由と期限を書く📝
（特権ヘルパー周りの説明は公式にあります） ([Docker Documentation][3])

---

## 10-9. まとめ🎉✅（この章の“合言葉”）

* **攻撃面＝入口の集合**。Dockerでは **「デーモンに命令できる入口」**が中心🎯
* デーモンは強い。だから **信頼できる人だけ**が触るべき（公式も明言）🔒 ([Docker Documentation][2])
* **強い操作は、気合いじゃなくて“手順固定”で防ぐ**🧱
* TCP公開みたいに入口を広げるのは危険。やるなら **SSH/TLS**（公式）🔐 ([Docker Documentation][6])
* Docker Desktopも脆弱性が出る世界。**更新は隔離の一部**🆙🛡️ ([Docker Documentation][5])

---

次の章（第11章）では、この「強い入口」を前提にして、**Nodeアプリをrootじゃないユーザーで動かす（USER運用）**に入っていきます🙂👟
ここから一気に「事故りにくいコンテナ」に寄せていくよ〜！🚀✨

[1]: https://chatgpt.com/c/698c1239-01b4-83a7-a298-99dc4459e21f "docker groupの権限"
[2]: https://docs.docker.com/engine/security/ "Security | Docker Docs"
[3]: https://docs.docker.com/desktop/setup/install/windows-permission-requirements/ "Windows permission requirements | Docker Docs"
[4]: https://docs.docker.com/engine/daemon/remote-access/ "Configure remote access for Docker daemon | Docker Docs"
[5]: https://docs.docker.com/security/security-announcements/?utm_source=chatgpt.com "Docker security announcements"
[6]: https://docs.docker.com/engine/security/protect-access/ "Protect the Docker daemon socket | Docker Docs"
