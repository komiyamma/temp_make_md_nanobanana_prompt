# 第16章：bind mountの危険ポイント：“ホストの大事な場所”を渡さない🙅‍♂️💽

この章はひとことで言うと、**「共有フォルダ＝被害半径」**をちゃんと設計しようね、という話です🧯✨
bind mount は便利だけど、便利さの正体は「強い権限」になりがちです😇

---

## 1) bind mount が危ない理由（めちゃ大事）⚠️🔌

bind mount は、**ホスト（Windows）のフォルダを、コンテナの中に“直結”**します📁➡️📦
そして基本的に **書き込み可能（rw）** なので、コンテナ内のプロセスは **ホスト側のファイルを作成・改変・削除**できちゃいます😱
これ、公式ドキュメントでも「重要ファイルを壊せるからセキュリティ影響があるよ」って明確に書いてあります。([Docker Documentation][1])

さらに **Docker Desktop** だと、Docker デーモン自体は Linux VM（WSL2側）で動きますが、**仕組みとしては“ホストのパスをコンテナに共有できる”**ように作られてます。
つまり「VMだから安心だよね！」ではなく、**共有した瞬間に“その共有範囲”はコンテナから触れる**、が現実です🧨([Docker Documentation][1])

---

## 2) Windows + WSL2 だと被害半径はこう考える🪟🐧📦

イメージはこんな感じです👇

* 🪟 **Windows（あなたのPC）**：本丸
* 🐧 **WSL2（Linux環境）**：Windowsと相互に行き来できる世界
* 📦 **コンテナ**：ここにホストのフォルダを“渡す”のが bind mount

WSLは設計上、Windows 側から **`\\wsl$`** で中身を読めたりします（相互アクセスが前提の仕組み）。Docker Desktop の WSL2 統合も、このモデルの範囲で動くよ、という説明があります。([Docker Documentation][2])
より強い分離を求める場合は **Hyper-V モード**や **Enhanced Container Isolation** などの選択肢がある、という方向性も示されています。([Docker Documentation][2])

> なのでこの章の結論はシンプル：
> **「渡すフォルダを最小にする」＝最強の防御**🛡️✨

---

## 3) “絶対に渡さない”フォルダ例（NG集）🚫📂

「ここをマウントしたら負け」になりやすい代表例です😇💥

* 🙅‍♂️ **ユーザープロファイル全体**

  * `C:\Users\<you>\`（Desktop / Documents / Downloads ぜんぶ含む）
* 🙅‍♂️ **秘密が入りがちな場所**

  * `C:\Users\<you>\.ssh\`（鍵）
  * `C:\Users\<you>\.gitconfig` / 認証系ファイル
  * `C:\Users\<you>\AppData\`（トークンや設定の宝庫になりがち）
* 🙅‍♂️ **OS・アプリ本体**

  * `C:\Windows\` / `C:\Program Files\` / `C:\ProgramData\`
* 🙅‍♂️ **ルート直下ドカ盛り共有**

  * `C:\` を丸ごと共有（“便利そう”に見える最悪例）😇🔥

**ポイント**：
「自分しか使わない開発PCだし…」で広く渡すと、
AI拡張やテスト用スクリプト、依存パッケージ事故で **想定外に読む・消す・書く**が起きます🫣💣

---

## 4) “共有していいフォルダ”の基準📏✅

迷ったらこの4ルールだけでOKです😊✨

1. ✅ **プロジェクト専用フォルダだけ**（例：`C:\work\myapp\`）
2. ✅ **その中でも「本当に必要なサブフォルダだけ」**に絞る（後述の分離テク）
3. ✅ **基本は read-only（壊せない）**で考える
4. ✅ 書き込みが必要なら **“専用の書き込みフォルダ”だけ rw** にする

> 合言葉：
> **「コードは読むだけ」「生成物だけ書く」**📖✍️

---

## 5) Composeで安全に書くテンプレ📦🔒

### 5-1) まず短縮記法を避ける（地味に危険）🕳️

Compose の短い書き方（`./path:/container/path`）は、**ホスト側パスが無いとディレクトリを勝手に作る**挙動があります😱
公式にも「互換性のためにそうなってる。嫌なら long syntax + create_host_path: false で止められる」とあります。([Docker Documentation][3])

なので **“安全テンプレ”は long syntax 前提**がオススメです🧱✨

### 5-2) 「コードはro」「書き込みは専用rw」に分離する🙂📎

例：TypeScriptアプリ（コードは読めればOK、ログや一時ファイルだけ書きたい）

```yaml
services:
  app:
    build: .
    volumes:
      # ✅ コードは基本 read-only（壊せない）
      - type: bind
        source: .
        target: /workspace
        read_only: true
        bind:
          create_host_path: false

      # ✅ 書き込みが必要な場所だけ rw（専用フォルダ）
      - type: bind
        source: ./tmp
        target: /workspace/tmp
        read_only: false
        bind:
          create_host_path: true
```

これだけで **「コンテナがホストのコードを削除する」事故**は激減します💪😄

### 5-3) 「共有しない」選択肢：volumeを使う🗃️✨

`node_modules` やDBデータみたいなものは、**ホストと直結しない方が安全**なことが多いです。
ボリュームは Docker が管理して、ホストの中枢からは切り離される設計（さらに推奨の永続化手段）と説明されています。([Docker Documentation][4])

例：コードは bind、`node_modules` は volume に逃がす👇

```yaml
volumes:
  node_modules:

services:
  app:
    build: .
    volumes:
      - type: bind
        source: .
        target: /workspace
      - type: volume
        source: node_modules
        target: /workspace/node_modules
```

「host直結の範囲」を減らすのが目的です🛡️✨

---

## 6) ミニ演習：怖さを“安全に”体験しよう🧪😱➡️😌

bind mount が「本当にホストとつながってる」って体感すると、一気に判断がうまくなります😄

### 演習A：rwだとホストのファイルが書き換わる😱

PowerShell で👇

```powershell
mkdir mount-lab
cd mount-lab
"hello" | Out-File hello.txt -Encoding utf8

docker run --rm -it --mount "type=bind,src=$PWD,target=/src" ubuntu bash
```

コンテナ内で👇

```bash
cd /src
echo "container wrote" >> hello.txt
exit
```

ホスト（PowerShell）で👇

```powershell
Get-Content .\hello.txt
```

✅ **ホスト側が増えてたら成功**です😇（＝危険も理解できた）

### 演習B：read-only にすると壊せない🔒

```powershell
docker run --rm -it --mount "type=bind,src=$PWD,target=/src,readonly" ubuntu bash
```

コンテナ内で👇

```bash
echo "try" >> /src/hello.txt
```

✅ たぶん **Permission denied** になります🎉（守れた！）

※ read-only の考え方は公式でも案内されています。([Docker Documentation][1])
（「roを付けると書き込み防げるよ」ってやつ）

---

## 7) よくある詰まりポイント（Windowsあるある）🧩🪟

* 😵 **パスが合ってるのにマウントされない**
  → まず「どのフォルダを共有してるか」を疑う（Docker Desktop設定やWSLモード差など）
* 😵 **相対パスが変な動き**
  → Composeの相対パスはローカルランタイム前提の挙動（別環境に持っていくと拒否されることがある）([Docker Documentation][3])
* 😵 **“空のフォルダができた”事故**
  → short syntax 由来の「勝手に作る」挙動かも。long syntax + create_host_path: false を基本にしよう🧱([Docker Documentation][3])

---

## 8) この章の“即戦力チェックリスト”✅🔒

* ✅ bind mount は **最小共有**（プロジェクト専用フォルダだけ）
* ✅ **ホーム・AppData・.ssh を絶対に渡さない**🙅‍♂️
* ✅ **コードは read-only が基本**📖🔒
* ✅ 書き込みは **専用フォルダだけ rw**✍️📁
* ✅ short syntax を避けて **long syntax + create_host_path: false**🧱
* ✅ 共有しなくていいデータは **volume**に逃がす🗃️✨([Docker Documentation][4])

---

次の第17章は「読み取り専用マウントを“設計として標準化する”」に入って、さらに事故が減るゾーンに突入します😄🔒🚀

[1]: https://docs.docker.com/engine/storage/bind-mounts/ "Bind mounts | Docker Docs"
[2]: https://docs.docker.com/desktop/features/wsl/ "WSL | Docker Docs"
[3]: https://docs.docker.com/reference/compose-file/services/ "Services | Docker Docs"
[4]: https://docs.docker.com/engine/storage/volumes/ "Volumes | Docker Docs"
