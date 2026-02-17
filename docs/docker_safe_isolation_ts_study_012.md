# 第12章：書き込み先の設計：/tmp・アップロード・ログ置き場を分ける🧺🗂️

「アプリが“どこにでも書ける”」状態って、便利そうで実は事故りやすいです😇💥
だからこの章では、**書いていい場所を“最小の3か所”に固定**して、被害半径をギュッと縮めます✂️🔒

---

## 0) 今日のゴール🎯

* ✅ アプリが書いていい場所を **3つの“カゴ”**に分けられる
* ✅ `EACCES` / `EROFS`（書けない！）が出たとき、**原因が即わかる**
* ✅ `read_only`（ルートFSを読取り専用）でも動く **安全寄りテンプレ**が作れる

---

## 1) まず“書き込み地図”を作ろう🗺️✍️

![3 Allowed Baskets](./picture/docker_safe_isolation_ts_study_012_01_writing_map.png)

コンテナの中の書き込み先は、基本この3つで足ります👇😊

1. **一時作業**：`/tmp`（消えてOK）🧊
2. **ユーザー生成データ**：アップロードなど（残したい）📦
3. **ログ**：できれば標準出力へ（必要なら専用の置き場）🧾

そして「それ以外」は原則 **書けない**ようにして守ります💪
Compose だと `read_only: true` で **コンテナのファイルシステムを読取り専用**にできます。([Docker Documentation][5])

---

## 2) “3つのカゴ”設計（おすすめパス）🧺✨

![Persistence Comparison](./picture/docker_safe_isolation_ts_study_012_02_persistence_comparison.png)

## A. 一時作業カゴ：`/tmp` 🧊

* 画像変換の途中ファイル、解凍作業、テンポラリなど
* **コンテナ再作成で消えてOK**なやつ

ここは `tmpfs`（メモリ上の一時FS）にすると、**ディスクに残りにくい**し、管理もラクです😊
Compose なら `tmpfs` が使えて、`uid/gid/mode` まで指定できます。([Docker Documentation][5])
Docker でも `tmpfs mount` の仕組みが公式で説明されています。([Docker Documentation][6])

---

## B. 残すデータカゴ：`/data/uploads` 📦

* ユーザーのアップロード
* 生成物（ユーザーが後でDLするファイル）
* 画像キャッシュ（残したいなら）

ここは **named volume** を使うのが定番です（環境依存が減る）🙂
Compose の volume 定義は公式リファレンスにまとまっています。([Docker Documentation][7])

> 🪟Windowsあるある注意：bind mount で Windows 側のパスを大量に触ると遅くなりがち…
> Docker Desktop の WSL ベストプラクティスでは、bind-mount するデータは **Linux 側ファイルシステムに置く**のが推奨されています。([Docker Documentation][8])

---

## C. ログカゴ：まずは `stdout/stderr` 🧾➡️📺

基本は **ファイルに書かず、`console.log` などで標準出力へ**が強いです💡
Docker の logging driver はコンテナの **stdout/stderr を集める**前提で動きます（例：`local` driver の説明）。([Docker Documentation][9])

どうしても「ログファイルが必要」なときだけ、`/var/log/app` みたいな専用置き場を **volume で**切ります🧾📦
（＝ログの増え方でコンテナ内部がパンパンにならない）

---

## 3) 図で一発：安全な“書き込み地図”🧠✨

![Read-Only Filesystem Map](./picture/docker_safe_isolation_ts_study_012_03_readonly_fs.png)

```
[イメージ(読取り専用)]  ← read_only: true
  ├─ /app            (コード・依存)    ✋基本書かない
  ├─ /etc            (設定)            ✋書かない
  ├─ /tmp            (一時)            ✅ tmpfs（消えてOK）
  ├─ /data/uploads   (ユーザーデータ)  ✅ volume（残す）
  └─ /var/log/app    (ログ任意)         ✅ volume（必要な時だけ）
```

---

## 4) 実装：Compose で“3つのカゴ”を作る🧩🐳

![Compose Configuration](./picture/docker_safe_isolation_ts_study_012_04_compose_setup.png)

ここでは **Node/TS アプリ**を例に、最小構成で作ります🙂✨
ポイントはこれ👇

* `read_only: true` で「基本書けない」を作る([Docker Documentation][5])
* `tmpfs:` で `/tmp` を用意（uid/gid も指定可）([Docker Documentation][5])
* `volumes:` で `/data/uploads` だけ書けるようにする([Docker Documentation][5])

```yaml
services:
  app:
    build: .
    read_only: true
    tmpfs:
      - /tmp:mode=1777,uid=1000,gid=1000
    volumes:
      - uploads:/data/uploads
    ports:
      - "3000:3000"

volumes:
  uploads:
```

* `mode=1777` は `/tmp` っぽい権限（誰でも作れるけど、他人のは消せない）でよく使われます🙂🔐
* `uid/gid` は “コンテナ内で動かすユーザー” に合わせます（この章では 1000 想定）

> 🧷bind mount を使うなら「ro を基本」に！
> Docker の bind mount は `ro/readonly` オプションで **書き込み禁止**にできます。([Docker Documentation][10])

---

## 5) 実装：Dockerfile 側で“書ける場所だけ”所有権を渡す🧤🛠️

![Dockerfile Basket Prep](./picture/docker_safe_isolation_ts_study_012_05_dockerfile_prep.png)

やることはシンプル😄
**書く場所だけ `mkdir` して `chown`** しておきます。

```dockerfile
## 例：Node系のイメージ想定
WORKDIR /app

## ここは「書いていい場所」だけ作る
RUN mkdir -p /data/uploads /var/log/app /tmp \
  && chown -R 1000:1000 /data/uploads /var/log/app /tmp

## 以降、非rootで動かす（第11章の流れ）
USER 1000:1000

CMD ["node", "dist/index.js"]
```

> ✅ `/app` 配下をむやみに `chown` しない
> 「アプリがどこでも書ける」を作りやすいからです😇💥
> 書くなら `/data/uploads` や `/tmp` みたいな **“カゴ”の中だけ**に限定します🧺

---

## 6) アプリ側（TypeScript）：書く場所を“定数で固定”する📌🧠

![Environment Variable Path](./picture/docker_safe_isolation_ts_study_012_06_env_path.png)

アプリが迷子になりがちな原因はだいたいコレ👇

* 適当に `./uploads` に保存してる（＝どこ？）😵
* ライブラリが勝手に `/app` とかにキャッシュを作ろうとする😇

だから、**保存先は環境変数 or 定数で固定**して、カゴに入れます📦✨

```ts
import { promises as fs } from "node:fs";
import path from "node:path";

const UPLOAD_DIR = process.env.UPLOAD_DIR ?? "/data/uploads";
const TMP_DIR = process.env.TMP_DIR ?? "/tmp";

export async function saveUpload(fileName: string, bytes: Uint8Array) {
  await fs.mkdir(UPLOAD_DIR, { recursive: true });
  const p = path.join(UPLOAD_DIR, fileName);
  await fs.writeFile(p, bytes);
  console.log("saved:", p); // ログはstdoutへ🧾
}
```

ログは `console.log` でOK（まずは stdout へ）🧾📺
Docker は stdout/stderr を logging driver で扱う前提なので、観測しやすいです。([Docker Documentation][9])

---

## 7) 動作確認：VS Code で“書ける/書けない”を体で覚える💻🧪

![Verification Touch](./picture/docker_safe_isolation_ts_study_012_07_verification.png)

起動👇

```bash
docker compose up -d --build
```

中に入ってテスト👇

```bash
docker compose exec app sh
id
touch /tmp/ok.txt
touch /data/uploads/ok.txt
touch /app/ng.txt
```

期待する結果はこれ😊

* ✅ `/tmp`：作れる
* ✅ `/data/uploads`：作れる
* ❌ `/app`：`Read-only file system` とか `Permission denied` で落ちる（それでOK！）🎉

> `read_only` は “アプリが変な場所に書いてないか” を一発であぶり出せます。([Docker Documentation][5])

---

## 8) ミニ演習（超おすすめ）🏋️‍♀️✨

## 演習1：アップロードが“残る”のを確認📦

1. `/data/uploads/ok.txt` を作る
2. `docker compose down` → `up`
3. **まだ残ってる**か確認✅
   → named volume だから残るはず😄（volumes の考え方）([Docker Documentation][7])

## 演習2：/tmp は“消える”のを確認🧊

1. `/tmp/ok.txt` を作る
2. コンテナ作り直し（`down` → `up`）
3. **消える**のを確認✅
   → 一時作業は “消えてOK” のカゴに入れてるから安心😄
   （tmpfs の考え方）([Docker Documentation][6])

## 演習3：ログを `docker compose logs` で追う🧾

```bash
docker compose logs -f app
```

stdout に出しておくと、まずこれで追えるので強いです💪
（logging driver が stdout/stderr を扱う前提）([Docker Documentation][9])

---

## 9) よくある詰まりポイント集😵‍💫🧯

## ① `EACCES: permission denied`

**原因**：書き込み先の owner / 権限が合ってない
**対策**：

* Dockerfile で `mkdir` + `chown` を “カゴだけ” にやる🧤
* `tmpfs` の `uid/gid` を実行ユーザーに合わせる（Compose の `tmpfs` で指定可）([Docker Documentation][5])

## ② `EROFS: read-only file system`

**原因**：`/app` や `/` 側に書こうとしてる
**対策**：

* 保存先を `/data/uploads` / `/tmp` に固定📌
* ライブラリのキャッシュ先も環境変数で誘導（例：`TMPDIR=/tmp`）

## ③ Windows の bind mount が遅い🐢

**原因**：Windows 側のパスを Linux コンテナに bind mount して I/O 多発
**対策**：

* プロジェクト/データを **Linux 側（WSL のファイルシステム）**に置くのが推奨([Docker Documentation][8])

---

## 10) AI拡張を使うときの“事故防止”🤖🛡️

GitHub の AI や OpenAI 系ツールに設定を作らせると、たまにこういう提案が混ざります😇💣

* `./uploads` とか曖昧パスで保存（消える/権限で詰む）
* `/app` 配下にキャッシュ/ログを書かせる（`read_only` で即死）
* 便利そうに `bind mount rw` を広く貼る（被害半径がデカい）

**対策はシンプル**👇😄
✅ 「書く場所は3か所だけ」ルールに反してないかを見る（1分レビュー）👀
✅ `read_only: true` を入れて、変な書き込みを早期発見する([Docker Documentation][5])

---

## まとめ：第12章の“合格チェック”✅🎉

* ✅ `/tmp`（tmpfs）：一時作業だけ
* ✅ `/data/uploads`（volume）：残すデータだけ
* ✅ ログはまず stdout（必要なら `/var/log/app` を volume）([Docker Documentation][9])
* ✅ それ以外は **書けない**（`read_only: true`）([Docker Documentation][5])
* ✅ Windows では bind mount する場所に注意（WSL 側推奨）([Docker Documentation][8])

---

次の第13章（read-only root filesystem を本格運用するやつ📖🔒）に行く前に、もし希望があればこの第12章の内容をベースに「Node/TSの簡易アップロードAPI（multer等）付きミニ教材プロジェクト」まで一気に形にできますよ😄✨

[1]: https://chatgpt.com/c/698c0c90-7ca8-83a3-bd16-5704274b7b55 "危険カード3兄弟"
[2]: https://chatgpt.com/c/698c013f-41cc-83a2-b319-96ca4423eb38 "安全な隔離入門"
[3]: https://chatgpt.com/c/698bcc69-212c-83a2-9b2b-5c228120fcf5 "Docker教材設計ガイド"
[4]: https://chatgpt.com/c/698c09bc-4a74-83a5-904a-8540dac8476a "New chat"
[5]: https://docs.docker.com/reference/compose-file/services/ "Services | Docker Docs"
[6]: https://docs.docker.com/engine/storage/tmpfs/?utm_source=chatgpt.com "tmpfs mounts"
[7]: https://docs.docker.com/reference/compose-file/volumes/?utm_source=chatgpt.com "Define and manage volumes in Docker Compose"
[8]: https://docs.docker.com/desktop/features/wsl/best-practices/?utm_source=chatgpt.com "Best practices"
[9]: https://docs.docker.com/engine/logging/drivers/local/?utm_source=chatgpt.com "Local file logging driver"
[10]: https://docs.docker.com/engine/storage/bind-mounts/?utm_source=chatgpt.com "Bind mounts"
