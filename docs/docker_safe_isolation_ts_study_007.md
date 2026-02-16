# 第07章：docker groupは実質つよい（＝root相当）って話💪😱

この章、いきなり結論からいきます👇
**「docker コマンドを自由に叩ける人」＝「実質、ホストを好きにできる人」**になりやすいです😱
Docker公式ドキュメントも、`docker` グループは **rootレベルの権限**を与えるとハッキリ警告しています。([Docker Documentation][1])

---

## この章のゴール🎯✨

* 「なぜ `docker group` が強すぎるのか」を腹落ちさせる🧠💡
* Windows（Docker Desktop / WSL2）でも同じ発想で “強い入口” を見分けられるようにする🪟🔍
* 個人/チームでの **安全ルール**を作れるようにする📏✅

---

## まずは脳内モデルを1枚に🗺️🧩

Dockerって、ざっくりこうです👇

* **docker コマンド（CLI）**：リモコン📺
* **Dockerデーモン（dockerd）**：実行担当（しかも強権）🦾
* CLIはデーモンに「これやって！」って指示する
* その指示を受ける入口が **ソケット**（Linuxなら `/var/run/docker.sock` など）🔌

Dockerデーモンは通常 **root権限で動く**ので、「デーモンを操作できる人」は強いです。([Docker Documentation][2])

---

## なぜ `docker group` が “root相当” になるの？😱🔒

Linuxではこういう仕組みです👇

1. Dockerデーモンは基本 root で動く（rootlessにしない限り）([Docker Documentation][2])
2. `docker` コマンドは、デーモンが持つソケットに接続して命令する🔌
3. そのソケットにアクセスできるようにするために **`docker` グループ**が使われる
4. すると… **デーモンに“何でも命令できる”＝root級**になりがち😇💥

公式も「`docker` group は root-level privileges を与える」と警告しています。([Docker Documentation][1])
さらに公式のセキュリティ解説では、Dockerは強力な機能（ホストのディレクトリ共有など）を持つので、**trusted usersだけがデーモンを操作すべき**と書いてあります。([Docker Documentation][2])

---

## Windowsだと “どこが強い入口” になる？🪟🚪

Windows（Docker Desktop）では、Linuxの `docker group` と同じ発想で👇

* **「Docker Engine / Desktop の制御に繋がる権限」**が強い入口になります💪
* Docker Desktopには、権限が必要な操作を担当する **privileged helper（Windowsサービス）**があり、
  それに接続する named pipe へのアクセスが **`docker-users` グループ**で制御されます。([Docker Documentation][3])
* つまり、Windowsでは `docker-users` が “強い操作へのパスポート🎫” になりやすいです。

さらに、WSL2バックエンドの話も重要で👇
ECI（Enhanced Container Isolation）には限界があり、**WSL2だと `wsl -d docker-desktop` でVMに直接入れて root で設定を触れてしまい、Desktop側のセキュリティ設定を迂回できる**と明記されています。([Docker Documentation][4])
（速度は良いけど、隔離強度は落ちるよ〜って感じです😇）

---

## “事故” が起きる典型パターン 3つ💥😇

## 1) 「便利だから」で権限を配りすぎる👥🎁

* 自分以外にも `docker group` / `docker-users` を追加
* いつのまにか「Docker触れる人」が増えて、実質“管理者増殖”状態に😱

## 2) 「安全そうな操作」でも、結果がホスト級になりうる🧨

Dockerは **ホスト側の資源（ファイル/ソケット/ネットワーク）**に触れられる機能が強力です。
公式も、ディレクトリ共有の強さがそのままセキュリティ上の注意点になる、と説明しています。([Docker Documentation][2])

## 3) コンテナ側から Engine API に触れたらアウト寄り🐙🔥

Docker Desktopでは過去に、**コンテナが docker.sock をマウントしなくても Docker Engine にアクセスできてしまう**脆弱性が修正されています（CVE-2025-9074）。しかも **ECIでも防げない**と明記されています。([Docker Documentation][5])
「Engineに触れる」＝「強い命令が通る」ので、入口管理がめちゃ大事です🧯

---

## 安全運用ルール（まずこれだけ）📏✅✨

## ルールA：`docker group` / `docker-users` は “管理者権限” と同格扱い👑

* **最小人数**にする（自分だけ、が基本）👤
* 増やすなら「理由」「期間」「解除条件」までセット📌

## ルールB：日常アカウントと “Docker強権アカウント” を分ける🧑‍💻➡️🧑‍🚀

* いつもの作業（ブラウザ、メール、チャット、素材DL）
* 強いDocker操作（権限が必要なこと）
  → 可能ならアカウント分離が効きます💡

## ルールC：デーモンの入口（ソケット / API）は絶対に雑に公開しない🚫🌐

DockerはデフォルトでUnix socketですが、ネットワーク越しに出す場合は保護が必須です（SSH/TLSなど）。([Docker Documentation][6])

---

## ハンズオン🔎：いまのPC、“強い入口”が誰に開いてるか確認しよう🧪🪟🐧

## ① Windows：`docker-users` を棚卸し🧾

PowerShell（管理者）で確認だけ👇

```powershell
net localgroup docker-users
```

* 想定外のユーザーが入ってたら要注意⚠️
* 「一時的に追加したまま」って、めちゃ多い事故です😇💣
  （追加/削除は管理ポリシー次第なので、チームなら手順を固定しましょう📌）

## ② WSL/Linux：`docker` グループを棚卸し🐧🧾

WSLのUbuntu等で👇

```bash
getent group docker
## または
groups
```

## ③ 「WSL2バックエンドなら bypass できる余地」も頭に入れる🧠

WSL2は便利だけど、ECI観点では **VMに直接アクセスできる**というギャップが公式に書かれています。([Docker Documentation][4])
「チームPCで本気で固くする」なら、バックエンド選定も設計ポイントになります🧱

---

## AI拡張（Copilot/Codex等）と合わせるときの注意🤖⚠️🧯

AIに「docker コマンド作って」って言うの、便利なんですが…
この章の話を踏まえると、**docker コマンド＝強権操作**になり得ます😇

おすすめ運用👇

* AIに出させたコマンドは **必ず目視レビュー**👀✅
* とくに要注意ワード：`privileged` / `pid=host` / `network=host` / 大きいマウント など🛑
* “安全寄りテンプレ”を先に決めて、AIにはその枠内で書かせる📦✨（第4章の考え方の出番！）

---

## よくある勘違いFAQ🧱😵

**Q.「sudo使わないために docker group 追加」は普通じゃない？**
A. 便利だけど、公式が「root-level privileges」って警告してるので、**追加＝権限付与**だと理解して運用ルール込みでやるのが正解です。([Docker Documentation][1])

**Q. Windowsは `docker group` 無いから関係ない？**
A. 発想は同じです！ Windowsでは `docker-users` や named pipe / privileged helper が “強い入口” になりやすいです。([Docker Documentation][3])

---

## まとめ✅🎉（この章で持ち帰ること）

* `docker group` は **root相当**（公式が警告）([Docker Documentation][1])
* “Dockerを操作できる”＝“強いことができる” を前提にする([Docker Documentation][2])
* Windowsでも `docker-users` など、**強い入口の最小化**が超大事([Docker Documentation][3])
* WSL2は便利だけど、隔離強度のギャップがある（公式にも明記）([Docker Documentation][4])

---

次の第8章（Rootless mode入門🧑‍🚀🔒）では、この章の「強すぎる入口問題」を、もう一段安全側に倒す選択肢として整理していきます🙂✨

[1]: https://docs.docker.com/engine/install/linux-postinstall/ "Post-installation steps | Docker Docs"
[2]: https://docs.docker.com/engine/security/ "Security | Docker Docs"
[3]: https://docs.docker.com/desktop/setup/install/windows-permission-requirements/ "Windows permission requirements | Docker Docs"
[4]: https://docs.docker.com/enterprise/security/hardened-desktop/enhanced-container-isolation/limitations/ "Limitations | Docker Docs"
[5]: https://docs.docker.com/security/security-announcements/ "Security announcements | Docker Docs"
[6]: https://docs.docker.com/engine/security/protect-access/ "Protect the Docker daemon socket | Docker Docs"
