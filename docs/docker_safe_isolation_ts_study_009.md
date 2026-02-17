# 第09章：ユーザー名前空間（userns）の考え方だけ押さえる🧠🧷

この章は「設定をガッツリやる回」じゃなくて、**仕組みを“腹落ち”させて事故を減らす回**です😊✨
（※設定を深掘りするのは次の段階でOK）

---

## 9.1 まず一言で：userns ってなに？🤔

![User Namespace Concept](./picture/docker_safe_isolation_ts_study_009_01_userns_concept.png)

**ユーザー名前空間（user namespace / userns）**は、超ざっくり言うと…

> コンテナの中の「UID=0（root）」を、ホスト側では「ただの一般ユーザーのUID」に見せる仕組み

です🔒✨
これで、もしコンテナが破られても「ホストのroot権限をそのまま握られにくい」方向に寄せられます。
Dockerだと代表的に **`userns-remap`** という機能名で出てきます。([Docker Documentation][1])

---

## 9.2 「中のroot ≠ 外のroot」って、どういうこと？🧠💡

![UID Mapping Table](./picture/docker_safe_isolation_ts_study_009_02_uid_mapping.png)

Linuxではユーザーは数字（UID）で管理されます👤
普通はこうです👇

* コンテナ内 root → UID 0
* ホスト側でも UID 0（＝root）っぽい扱いになりがち

でも **userns-remap** を有効にすると、こうなります👇

* コンテナ内 root（UID 0）
  → ホスト側では **サブUIDの範囲の先頭（例：231072）** にマッピングされる
* つまり、ホストから見ると「特権じゃないUID」で動いてる扱いになる🛡️([Docker Documentation][1])

**図でイメージ**（数字は例だよ）👇

```text
[コンテナ内]                 [ホスト側]
root (UID 0)   ───────▶      UID 231072（一般ユーザー扱い）
app  (UID 1)   ───────▶      UID 231073
...
```

この “対応表” の元ネタが **`/etc/subuid` と `/etc/subgid`** です🧾
ここに「このユーザーにはこの範囲のUID/GIDを割り当てるよ」が書かれます。([Docker Documentation][1])

---

## 9.3 userns-remap と rootless の関係（ここ超重要）🔑

![userns-remap vs Rootless](./picture/docker_safe_isolation_ts_study_009_03_remap_vs_rootless.png)

混ざりやすいので、ここだけスッキリ整理します🧹✨

* **userns-remap**：
  Dockerデーモン（dockerd）は root 権限で動いてるけど、**コンテナ側のUIDをマッピング**して被害を小さくする方式([Docker Documentation][1])
* **rootless mode**：
  **デーモンもコンテナも userns の中で動く**（つまりデーモン自体も非root寄り）([Docker Documentation][2])

> “どっちも userns を使う”けど、
> **rootless は「デーモンも非root」**なのが違いです🙂🔒([Docker Documentation][2])

---

## 9.4 Windowsだと、どこに効くの？🪟🐧

WindowsでDockerを使うとき、内部的には **WSL2 のLinux環境でエンジンが動く**構成が一般的です。([Docker Documentation][3])
なので userns の話は、

* 「Windows本体を直接守る」というより
* **WSL2側（= Dockerエンジンが動くLinux側）での権限事故を小さくする発想**

として理解するとスッと入ります👍
（Docker DesktopがWSL2エンジンを使うこと、WSL2が“Linuxカーネル上で動く仕組み”であることは公式にも説明があります）([Docker Documentation][3])

---

## 9.5 体験ラボ：自分の環境で “マッピング” を覗く👀🔬

### ラボ1：userns が有効かどうか確認する✅

PowerShellでOKです👌

```powershell
docker info | Select-String -Pattern "userns" -CaseSensitive:$false
```

* 何か出れば「userns関連の設定が有効な可能性あり」✨
* 何も出なければ「少なくとも userns-remap は使ってない可能性が高い」🙂

（環境によって表示は違うので、**“userns という単語が出るか”**だけ見ればOKです）

---

### ラボ2：コンテナの中から `uid_map / gid_map` を見る🧩

![Terminal UID Map Output](./picture/docker_safe_isolation_ts_study_009_04_terminal_uid_map.png)

```powershell
docker run --rm alpine sh -lc "id; echo '--- uid_map'; cat /proc/self/uid_map; echo '--- gid_map'; cat /proc/self/gid_map"
```

見どころはここ👇

* **usernsが無い/効いてない**：だいたい “0→0” のような雰囲気
* **userns-remap が効いてる**：
  `0 231072 65536` みたいに **「0が別の範囲に飛ばされてる」**表示になることが多いです([Docker Documentation][1])

数字そのものは環境で変わるので、**「0が0じゃない所へ行ってる」**だけ掴めれば勝ち🏆✨

---

### ラボ3：もし userns-remap が有効なら、わざと無効化して差を見る🧯（危険なので学習目的だけ）

Dockerでは、デーモン側で userns を有効にしている場合でも、**コンテナ単体で無効化**できます。
その方法が `--userns=host` です。([Docker Documentation][4])

```powershell
docker run --rm --userns=host alpine sh -lc "cat /proc/self/uid_map; cat /proc/self/gid_map"
```

ここで超大事⚠️
`--userns` は **`host` しか指定できない**（＝“無効化スイッチ”としての意味合いが強い）です。([Docker Documentation][4])

---

## 9.6 ありがちな詰まり：マウントの権限が地獄になる😇💥

![Mount Permission Hell](./picture/docker_safe_isolation_ts_study_009_05_mount_permission_hell.png)

userns-remap を入れると、**バインドマウント**（ホストのフォルダ共有）でハマりやすいです💣

なぜかというと…

* コンテナ内 root は root のつもりで書く
* でもホスト側では「231072みたいなUID」扱い
* だからホスト側のフォルダ権限と合わず、書けない／所有者が変な数値になる

公式も「ホストのリソース（特に bind mount）にアクセスさせる時は設定が複雑になりやすい。セキュリティ的には、そういう状況は避けるのが望ましい」と言ってます。([Docker Documentation][1])

**初心者向けの割り切りルール**（まずこれでOK）👇

* 📦 **DBなどのデータは named volume を優先**（bind mount を減らす）
* 📁 bind mount は「ソースコードだけ」＋「できれば読み取り専用」へ
* 🧪 どうしても書き込みが要るなら「書き込み専用フォルダ」を別に切る
* 🧨 AIが「権限エラー直らないなら `--userns=host` で！」と言っても、**“無効化してる”**ことを理解してから使う

---

## 9.7 Compose だとどう書くの？🧩🐳

![Compose userns_mode](./picture/docker_safe_isolation_ts_study_009_06_compose_userns_mode.png)

Composeには `userns_mode` があります。
これは「そのサービスの user namespace をどうする？」を指定する項目です。([Docker Documentation][5])

例（hostに合わせて userns を無効化するイメージ）👇

```yaml
services:
  app:
    image: alpine
    userns_mode: "host"
```

ただし公式にもある通り **“サポート値はプラットフォーム依存”**なので、使える/使えないは環境次第です。([Docker Documentation][5])
（なのでこの章では「こういう指定がある」だけ把握でOK👌）

---

## 9.8 AI拡張時代の事故ポイント（プロンプト注入以前に起きがち）🤖⚠️

![AI Accident Warning](./picture/docker_safe_isolation_ts_study_009_07_ai_warning.png)

AIが出しがちな “手っ取り早い解決” は、隔離の思想と逆走しやすいです🚨

特にこの章に関係する危険ワード👇

* `--userns=host`（＝usernsを無効化）([Docker Documentation][4])
* 「daemon.json をいじって再起動」系（影響範囲がデカい）([Docker Documentation][1])
* bind mount を増やす（ホストへの接点が増える）([Docker Documentation][1])

**AIにお願いするときのテンプレ（安全寄り）**🍀

* 「“無効化で直す”じゃなく、“隔離を保ったまま直す”案を優先して」
* 「その変更で被害半径が増えるかも、を必ず一言添えて」

これだけで、だいぶマシになります🙂✨

---

## 9.9 ミニ課題（10分）⏱️📚

1. `docker info` で `userns` が出るか確認✅
2. Alpineコンテナで `uid_map/gid_map` を表示して、
   「0が0のままか？」を観察👀
3. もし userns-remap が有効そうなら、`--userns=host` を付けた場合の差を確認🧯
4. 最後に一言メモ✍️

   * 「自分の環境で userns は “効いてる/効いてない”」
   * 「効いてるなら、何が嬉しくて何が面倒そうか」

---

## 9.10 まとめ🎉

* userns は **「中のrootを外の一般ユーザーに見せる」**仕組み🔒
* Dockerでは **userns-remap** が代表で、`/etc/subuid` ` /etc/subgid` の範囲にマッピングする([Docker Documentation][1])
* **rootless mode も userns を使う**けど、デーモンまで非root寄りなのが違い([Docker Documentation][2])
* 一番ハマるのは **bind mount の権限**。避ける設計が正義🧠([Docker Documentation][1])
* `--userns=host` は “便利”だけど **無効化スイッチ**（しかも `host` しか指定できない）なので慎重に⚠️([Docker Documentation][4])

---

次の章に進むなら、第10章の「デーモンが握る力（attack surface）」で、**“どの操作がホスト級か”の嗅覚**を作ると一気に安全になります🎯🔥

[1]: https://docs.docker.com/engine/security/userns-remap/ "Isolate containers with a user namespace | Docker Docs"
[2]: https://docs.docker.com/engine/security/rootless/?utm_source=chatgpt.com "Rootless mode"
[3]: https://docs.docker.com/desktop/features/wsl/ "WSL | Docker Docs"
[4]: https://docs.docker.com/reference/cli/docker/container/run/ "docker container run | Docker Docs"
[5]: https://docs.docker.com/reference/compose-file/services/ "Services | Docker Docs"
