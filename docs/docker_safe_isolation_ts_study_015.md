# 第15章：privilegedは最後の最後：使う前にチェックリスト🛑🧾

この章のゴールはシンプルです👇
**「困った→とりあえず privileged」は卒業**して、**“必要最小”で解決**できる判断ができるようになること！😄✨

---

## 15.1 そもそも `privileged` って何が起きるの？😱💥

`docker run --privileged`（や Compose の `privileged: true`）は、ざっくり言うと **“コンテナをほぼホスト級にするスイッチ”** です。
公式の説明でも、`--privileged` にすると **全capability付与・既定のseccomp無効・既定のAppArmor無効・ホストデバイス全部アクセス** など、いろいろ解除されると明記されています。([Docker Documentation][1])

さらに「ホスト上のプロセスとほぼ同等のアクセスを許しうるので注意して使ってね」とも書かれています。([Docker Documentation][2])

Compose 側でも `privileged` は **“サービスを昇格権限で動かす”** で、影響はプラットフォーム依存（＝環境によって効き方が変わる）とされています。([Docker Documentation][3])

---

## 15.2 Windows（Docker Desktop）だと「安全」になる？🪟🤔

ならないです😇💣
Docker Desktop は内部に Linux VM を持っていて、`--privileged` などは **VM 内で権限が強くなります**。ただし **VM 内部や Docker Engine 側に深く触れたり**、Docker Desktop のファイル共有で渡しているフォルダには当然触れます。
Docker 側の FAQ でも、`--privileged`（や `--pid=host`, `--cap-add`）は **VM 内で elevated になり、VM 内部や Docker Engine にアクセスしうる** と説明されています。([Docker Documentation][4])

つまり Windows でも結局👇

* 共有してるプロジェクトフォルダを破壊💥
* 秘密ファイルを読み取り🕵️‍♂️
* “ホストに近い層”へ影響を出す可能性が上がる📈

…みたいな事故が起きやすくなります。

---

## 15.3 「privileged を付けたくなる瞬間」あるある😵‍💫

だいたいこの3つが多いです👇

1. **デバイス触りたい**（USB、GPU、/dev/net/tun、シリアル等）🔌
2. **ネットワーク系の操作をしたい**（iptables、ルーティング、VPN）🌐
3. **“Permission denied” を雑に消したい**（でも原因は別）🧯

ここで大事なのは…
✅ **“何がしたいか”を1行で言語化**してから対処すること！
（例：`/dev/net/tun` が必要 / `mount` が必要 / `iptables` が必要 など）

---

## 15.4 まずこれを試す！privileged の代替トップ3🥇🥈🥉

### 代替①：デバイスだけ渡す（`devices`）🔌✅

「特定のデバイスが触れればOK」なら、**全部解放じゃなくて“必要なデバイスだけ”** にします。
Compose の `devices` は `HOST_PATH:CONTAINER_PATH[:権限]` でマッピングできます。([Docker Documentation][3])

### 代替②：capability をピンポイントで足す（`cap_add`）🧤✨

「root相当の全部」じゃなくて、**必要な能力だけ**追加。
Compose には `cap_add` / `cap_drop` が用意されています。([Docker Documentation][3])

### 代替③：一時的に“作業コマンドだけ”昇格する🧪

サービスを常時 privileged にする前に、**その瞬間だけ**で済まないか？
`docker compose exec --privileged` みたいに **実行コマンドだけ拡張権限**にできるオプションもあります（常時ではなく“作業時だけ”の発想）。([Docker Documentation][5])

---

## 15.5 privileged を使う前のチェックリスト🧾🛑（これだけ守れば事故激減）

**チェック0：困ってるのは何？（1行）**✍️

* ❌「動かないから」
* ✅「/dev/net/tun が必要」「iptables を触る必要がある」「USBデバイスにアクセスしたい」

**チェック1：それ “デバイス1個” で足りない？**🔌

* 足りる → `devices:` へ
* 足りない → 次へ

**チェック2：それ “capability 1〜2個” で足りない？**🧤

* 足りる → `cap_add:` へ
* 迷う → まず `cap_add` で当てに行く（ダメなら増やす）🎯

**チェック3：privileged にするなら “対象” は最小？**📦

* アプリ本体じゃなく **補助コンテナ**に分けられない？
* その補助コンテナは **profiles（手動でON）**にできない？🙈

**チェック4：時間は最短？**⏱️

* 常時ONではなく、**作業時だけ**にできない？（`compose exec --privileged` 等）([Docker Documentation][5])

**チェック5：共有と秘密は絞れてる？**🔑📁

* bind mount が広すぎない？
* secrets / .env / 設定ファイルがコンテナに“全部”渡ってない？
  （privileged と秘密の同居は事故率UP📈）

**チェック6：説明（理由・代替・撤去条件）を書いた？**📝

* 「なぜ必要」「代替は試した」「いつ外す」の3点セットを書いとくと未来の自分が助かる🙏

---

## 15.6 ハンズオン：`--privileged` が“どれだけ強いか”を目で見る👀💥

Windows + Docker Desktop でもOK！
PowerShell or VS Code のターミナルでやれます💻✨

**(1) 普通のコンテナ**

```bash
docker run --rm -it alpine sh
cat /proc/1/status | grep CapEff
exit
```

**(2) privileged のコンテナ**

```bash
docker run --rm -it --privileged alpine sh
cat /proc/1/status | grep CapEff
mount | head
exit
```

見比べると「権限が盛られてる感」が分かります😇
（そして公式にも `--privileged` は seccomp や AppArmor の既定制限まで無効化しうる、とハッキリ書かれてます）([Docker Documentation][1])

---

## 15.7 Composeでの “悪い例→良い例” 改造🛠️✨

**悪い例（困ったから全部ON）**😵

```yaml
services:
  app:
    image: alpine
    privileged: true
    command: ["sh", "-lc", "sleep infinity"]
```

**良い例（必要なものだけON）**🙂✅
例：USBデバイスが必要（※デバイス名は環境で変わるよ）

```yaml
services:
  app:
    image: alpine
    command: ["sh", "-lc", "sleep infinity"]
    devices:
      - "/dev/ttyUSB0:/dev/ttyUSB0:rwm"   # 必要デバイスだけ
```

`devices` は公式仕様として用意されています。([Docker Documentation][3])

例：ネットワーク操作が必要（capability をピンポイント）

```yaml
services:
  app:
    image: alpine
    command: ["sh", "-lc", "sleep infinity"]
    cap_add:
      - NET_ADMIN
```

`cap_add` / `cap_drop` で調整できるのも公式仕様です。([Docker Documentation][3])

---

## 15.8 AI拡張（Copilot / Codex）で事故らないための“指示テンプレ”🤖🧯

AIは平気で「privileged 付けましょう！」って言いがちです😂
なので、最初から縛りを入れましょう👇

**安全寄りプロンプト例**

* 「`privileged` は禁止。`devices` と `cap_add` と設定変更で解決策を提案して。どうしても必要なら“理由・代替案・最小化案・撤去条件”をセットで出して」
* 「Compose の差分（Before/After）だけ出して。強い設定を入れる場合はリスクを1行で添えて」

そして最後は人間がチェック✅

* “対象は最小？” “時間は最短？” “共有と秘密は絞れてる？” 🧾

---

## 15.9 まとめ：privileged は「最終手段」だけど、使うなら“安全に使える”🎉🔒

* `privileged` は **全部解放に近い**（公式が明言）([Docker Documentation][1])
* Compose の `privileged: true` は **昇格権限**で、影響は環境依存([Docker Documentation][3])
* まずは **devices / cap_add / 一時的昇格**で“必要最小”を狙う🔌🧤⏱️([Docker Documentation][3])
* Windows(Docker Desktop)でも「安全になる」わけじゃない（VM/Engine側に影響が出る）([Docker Documentation][4])

---

次の章（第16章）は **bind mount の危険ポイント**に入るので、ここで作った「最小共有」の感覚がそのまま効いてきますよ〜📦🧷✨

[1]: https://docs.docker.com/reference/cli/docker/container/run/?utm_source=chatgpt.com "docker container run"
[2]: https://docs.docker.com/engine/containers/run/?utm_source=chatgpt.com "Running containers | Docker Docs"
[3]: https://docs.docker.com/reference/compose-file/services/ "Services | Docker Docs"
[4]: https://docs.docker.com/security/faqs/containers/?utm_source=chatgpt.com "Container security FAQs"
[5]: https://docs.docker.com/reference/cli/docker/compose/exec/?utm_source=chatgpt.com "docker compose exec"
