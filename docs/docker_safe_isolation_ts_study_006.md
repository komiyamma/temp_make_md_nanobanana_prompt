# 第06章：Windows環境の“権限の場所”を把握しよう🪟🧩

この章のゴールはシンプルです👇
**「いま自分が触ってるのは、Windows？WSL？コンテナ？ どの操作が“ホストに効く”？」**を、迷わず見分けられるようになることです😄🔒

---

## 6-1. まず結論：Windows + Docker Desktop は“3つの世界”が同居してる🌍🌍🌍

ざっくり、こういう階層です👇

* **世界A：Windows（あなたのPC本体）**🪟
* **世界B：WSL 2（軽量VMの中のLinux）**🐧

  * ここに、Docker Desktop のエンジン側が住む（WSLバックエンドの場合）
  * WSL 2 は “軽量のユーティリティVMでLinuxカーネルを動かす” 方式です。([Microsoft Learn][1])
* **世界C：コンテナ（Linuxのプロセス箱）**📦

  * “中のroot”とか“中のユーザー”がいる

そして重要ポイント👇
**「Cの箱の操作が、Bを経由してAに刺さることがある」** です😇💥

---

## 6-2. 「どこがLinuxなの？」をハッキリさせる🧠✨

## WSL 2 の“分布（ディストリ）”って何？📦🐧

WSL 2 は、Windowsの上で Linux を動かす仕組みで、Linux は“ディストリビューション単位”で存在します。([Microsoft Learn][1])

そして、Docker Desktop の WSLバックエンドでは👇

* Docker エンジンは **docker-desktop** という専用ディストリで動きます。([Docker Documentation][2])
* 以前（Docker Desktop 4.30より前）は **docker-desktop-data** も作られましたが、**4.30以降の新規インストールでは作られない**（代わりに仮想ディスクを管理）という扱いになっています。([Docker Documentation][2])

## Dockerのデータはどこにある？📁🧳

Docker Desktop（WSLエンジン）のデータ保存場所は、既定で
**C:\Users[USERNAME]\AppData\Local\Docker\wsl**
になっています。([Docker Documentation][2])

つまり、**「Dockerの中のデータ」でも Windows側のディスクと強く結びついてる**んですね🧩

---

## 6-3. “権限”はどこで決まる？3段階で理解する🔐🪜

ここ、初心者が一番混乱しやすいので、3段階で割ります👇

## ① Windowsの権限（管理者 / 一般ユーザー）🪟👤

Docker Desktop は **インストール時に管理者権限が必要**です（UACが出て、特権ヘルパーサービスを入れる）。([Docker Documentation][3])
インストール後は **管理者じゃなくても起動できる**けど、特定の機能は権限が要ります。([Docker Documentation][3])

さらに、Docker Desktop は必要な“強い操作”だけを **com.docker.service**（Windowsサービス）にやらせる設計で、これが **SYSTEM権限で動く**、みたいな話が出てきます。([Docker Documentation][3])
→ 「どの操作がこの“強いルート”に乗るのか？」が、隔離の入口なんです🚪🔥

## ② WSL 2 の権限（Linuxのroot / user）🐧🔑

WSL 2 の中では Linux としての root / user がいます。
ただし WSL は Windows と相互アクセスできる設計で、WSL内のファイルは Windows 側から **\wsl$** で見えます。([Docker Documentation][2])
→ “完全に別PC”ではなく、かなり近い距離感だと思ってOKです😄

## ③ コンテナの権限（箱の中のroot / user）📦👤

コンテナ内の root は、**それだけでWindows管理者になるわけじゃない**です。
でも、**ホストのファイルをマウントした瞬間**に話が変わることがあります😇💣
（マウント＝“箱の中から外の棚を触れる鍵”）

---

## 6-4. 「ホストに影響する操作」を見分けるコツ👀⚠️

迷ったら、次の5問を自分に聞いてください✅

1. **ホストのフォルダをマウントしてる？**（bind mount）📎💽
2. **ポートを公開してる？**（-p / ports）🚪🌐
3. **Docker Desktop の設定（Resources/WSL統合）を触ってる？**⚙️
4. **Windows側のサービス / 権限（docker-users等）を使ってる？**🧰
5. **“Docker Engine API”に近い操作をしてる？**（コンテナ作成・起動の権限が強い）🧨

ちなみに最近の事例として、Docker Desktop の脆弱性（CVE-2025-9074）では、**コンテナからDocker Engine APIにアクセスされ得て、追加コンテナ起動などに繋がる**問題があり、**Docker Desktop 4.44.3（2025-08-20修正）**で修正されています。しかも Enhanced Container Isolation（ECI）でも軽減できない、と明記されています。([Docker Documentation][4])
→ 「箱の中だから安全」を思い込みにしないのが大事です🙏🛡️

---

## 6-5. 演習：自分のPCの“地図”を作る🗺️✍️（10分）

## 演習A：WSLの一覧を見て「どれが何か」言えるようにする📋🐧

Windows のターミナル（PowerShell）で👇

```powershell
wsl.exe -l -v
```

出てきた一覧を見て、最低これだけ押さえればOK👇

* 自分の開発ディストリ（例：Ubuntu）
* docker-desktop（Dockerエンジンが住むやつ）([Docker Documentation][2])
* （もしあれば）docker-desktop-data（古い構成の名残）([Docker Documentation][2])

📝ミニ課題：
「このディストリは“普段の開発場所”」「これは“Dockerの中身用”」って、1行メモを書いておくと迷子が減ります😄🧭

---

## 演習B：いま開いてるシェルが“どの世界”か当てる🎯

**見分け方（超実用）**👇

* Windows側っぽい：パスが C:\ で始まる / コマンドが dir など🪟
* WSL側っぽい：パスが /home/... / uname がある🐧
* コンテナっぽい：プロンプトが変で、ファイルが最小限📦

確認コマンド例👇

```powershell
whoami
```

```bash
uname -a
whoami
id
pwd
```

ポイントは「いまの自分の身分（whoami）」と「場所（pwd）」です🙂📍

---

## 演習C：Dockerの“実体”がどこで動いてるか確認する🧠🔍

Windows から👇

```powershell
docker info
```

見どころ👇

* OS情報（Docker Desktop / WSL 2 engine の気配）
* なんとなく「今はLinuxコンテナ側なのか」雰囲気が掴めます

そして Docker公式ドキュメントには、WSL 2 を有効にすると Windows から docker コマンドが使えること、設定手順などが整理されています。([Docker Documentation][2])

---

## 演習D：“安全なマウント”を体験する（危険な場所は絶対渡さない）🧯📎

1. Windows側で安全な練習フォルダを作る（例：C:\temp\docker-lab）
2. それを **読み取り専用（ro）** でコンテナに渡す

例（PowerShell）👇

```powershell
docker run --rm -it -v C:\temp\docker-lab:/work:ro alpine sh
```

中に入ったら👇

```bash
ls -la /work
```

ここで感じてほしいのは👇
**「マウントした瞬間、箱の中からホストのファイルが見える」**という事実です😇💥
（だから “渡すフォルダ” が設計そのものになる）

---

## 6-6. VS Codeで迷子にならない開発配置🏠🧠

**結論：ファイルをどこに置くかが、速度と権限トラブルに直結**します⚡🧯

* bind mount（ホスト→コンテナ）で大量ファイルを扱うなら、**WSL 2 のファイルシステム側に置く**のが推奨されます（パフォーマンスと権限の相性が良い）。([Visual Studio Code][5])
* Docker側も WSL 2 の仕組み・セキュリティモデルに沿って動く、と説明しています。([Docker Documentation][2])

📝雑に覚えるなら：

* “Windowsのフォルダを /mnt/c/ 経由でガシガシ触る”より
* “WSLの中（/home/...）を主戦場にする”ほうがハマりにくい😄👍

---

## 6-7. よくある事故あるある😇💣（そして回避）

## あるある1：どこで作ったファイルか分からなくなる🌀

✅回避：演習Bの「pwd と whoami」を癖にする📍

## あるある2：マウントで“うっかり重要フォルダ”を渡す🫠

✅回避：**渡すのはプロジェクト専用フォルダだけ**。ホーム直下やドライブ直下は渡さない🙅‍♂️

## あるある3：Docker Desktopの権限周りがブラックボックス化👻

✅回避：
Docker Desktop は “必要な強い操作”を特権ヘルパー（com.docker.service）に寄せていて、インストール時の管理者権限や、docker-usersグループ等の話が出ます。([Docker Documentation][3])
→ 「どの操作がそれを使うのか？」を意識するだけで、安全設計に一歩近づきます🛡️✨

---

## 6-8. この章のまとめ：10秒セルフ点検✅🕔

何かを設定・実行する前に、これだけチェック👇

* いま自分は **Windows / WSL / コンテナ**のどこにいる？🪟🐧📦
* **マウント**してる？（渡していいフォルダだけ？ roにできない？）📎🔒
* **ポート公開**してる？（本当に必要？）🚪🌐
* Docker Desktop 側の **強い権限ルート**を使う操作じゃない？🧨
* 「箱の中だから安全」を思い込んでない？（過去に実際の脆弱性もある）🧯([Docker Documentation][4])

---

次の第7章で「docker group が実質つよい（root相当）」に入ると、**“誰がDockerを操作できるか”＝“誰がホスト級の操作に近づけるか”**がもっとハッキリします💪😱
この第6章の“地図”ができてると、理解がめちゃ速くなりますよ〜😄🗺️✨

[1]: https://learn.microsoft.com/en-us/windows/wsl/about "What is Windows Subsystem for Linux | Microsoft Learn"
[2]: https://docs.docker.com/desktop/features/wsl/ "WSL | Docker Docs"
[3]: https://docs.docker.com/desktop/setup/install/windows-permission-requirements/ "Windows permission requirements | Docker Docs"
[4]: https://docs.docker.com/security/security-announcements/?utm_source=chatgpt.com "Docker security announcements"
[5]: https://code.visualstudio.com/remote/advancedcontainers/improve-performance "Improve disk performance"
