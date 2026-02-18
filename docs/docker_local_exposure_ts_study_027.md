# 第27章：mkcertで「信頼されたローカル証明書」を作る🪄📜

この章はひとことで言うと――
**「ローカルHTTPSで“ブラウザ警告ゼロ”にするための、いちばん楽なやり方」**です😎✨

---

## 27.1 まず、mkcertが解決してくれる“つらみ”😇💥

ローカルでHTTPSをやりたい時って、だいたいこう👇

* OAuth / SSO のコールバックURLが HTTPS 前提😵‍💫
* Service Worker / 一部ブラウザ機能が “安全な接続” 前提🧠🔐
* そして何より… **「保護されていません」警告が邪魔**😇⚡

![Local HTTPS Pain Points](./picture/docker_local_exposure_ts_study_027_https_pain.png)

**mkcert**は、これを「ほぼコマンド数回」で解決する道具です。
ローカル専用の認証局（CA）を作って、PCに信頼させ、**そのCAでサーバー証明書を発行**してくれます。([GitHub][1])

---

## 27.2 今日のゴール🎯✨（完成イメージ）

* `https://app1.localhost`
* `https://api.localhost`
* `https://admin.localhost`

こういうのを開いても、**証明書警告なしで鍵マーク🔒が付く**状態にします。

しかも `.localhost` は「localhost扱いの特別枠」なので、（環境次第だけど）サブドメインもローカルとして扱われやすいです。([IETF Datatracker][2])

![mkcert Success Goal](./picture/docker_local_exposure_ts_study_027_mkcert_goal.png)

---

## 27.3 mkcertのインストール（Windows）🧰🪟

### A) winget（いちばんお手軽ルート）🚀

`FiloSottile.mkcert` というIDで配布されています。([GitHub][3])

```powershell
winget install -e --id FiloSottile.mkcert
```

### B) Scoop / Chocolatey でもOK🍫🥄

* Scoop（extras にある）([bjansen.github.io][4])
* Chocolatey（コミュニティパッケージあり）([Chocolatey Software][5])

![mkcert Installation Options](./picture/docker_local_exposure_ts_study_027_install_options.png)

---

## 27.4 最重要：ローカルCAを作って「信頼」させる🔑🧙‍♂️

ここが“肝”です。これをやると、作った証明書がブラウザに信頼されます✅
mkcertの基本フローはこれ（作者READMEの例そのままの流れ）です。([GitHub][1])

```powershell
mkcert -install
```

成功すると「ローカルCAを作ったよ」「OSの信頼ストアに入れたよ」みたいなメッセージが出ます⚡([GitHub][1])

#### ⚠️ 超大事（セキュリティ）💣

mkcertは `rootCA-key.pem`（ローカルCAの秘密鍵）を作ります。
これが漏れると“そのPC上のHTTPS通信を偽装できる力”があるので、**絶対に共有しない**でね。([GitHub][1])

![Local CA Trust Flow](./picture/docker_local_exposure_ts_study_027_local_ca_trust.png)

---

## 27.5 証明書を発行する（ワイルドカードでラクする）🪄✨

今回の「複数アプリ共存」では、**ワイルドカード1枚**が強いです💪

ポイントはこれ👇

* `*.localhost` は `app1.localhost` などをまとめてカバー
* でも `localhost` 自体は `*.localhost` ではカバーされない（別物）
  → なので **両方入れる**のが安心☺️

### 証明書ファイル名を固定して作る（おすすめ）📌

mkcertはデフォだと `example.com+5.pem` みたいに数字入りになりがち。
運用しやすいように、出力先を固定します（`-cert-file` / `-key-file` が公式にあります）。([GitHub][1])

```powershell
mkdir certs
cd certs

mkcert -cert-file localhost-wildcard.pem -key-file localhost-wildcard-key.pem localhost "*.localhost"
```

これで `certs` フォルダに

* `localhost-wildcard.pem`（証明書）
* `localhost-wildcard-key.pem`（秘密鍵）

ができます🔒✨

![Wildcard Certificate Power](./picture/docker_local_exposure_ts_study_027_wildcard_cert.png)

---

## 27.6 できた証明書を「リバプロ」に食わせる🍽️🚪

ここからが“公開の整理”の本番パート😺
やることは単純で、

1. `certs/` をリバプロコンテナにマウント
2. リバプロに「この証明書でTLSしてね」と教える

だけ！

### 例：Traefik（v3系でもだいたい同じ考え方）🚦🤖

（Traefik自体は Traefik Labs の製品だよ）

**docker-compose.yml（抜粋）**：証明書を `/certs` にマウントするだけ👇

```yaml
services:
  traefik:
    image: traefik:v3
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./certs:/certs:ro
      - ./traefik/dynamic.yml:/etc/traefik/dynamic.yml:ro
```

**dynamic.yml（TLS部分だけ）**：Traefikに証明書を渡す👇

```yaml
tls:
  certificates:
    - certFile: /certs/localhost-wildcard.pem
      keyFile: /certs/localhost-wildcard-key.pem
```

（ルーティングの labels や routers は前章までのやつをそのまま使えばOK👌✨）

### 例：Nginx（超ざっくり）🧱

```nginx
server {
  listen 443 ssl;
  server_name app1.localhost;

  ssl_certificate     /certs/localhost-wildcard.pem;
  ssl_certificate_key /certs/localhost-wildcard-key.pem;

  location / {
    proxy_pass http://app1:3000;
  }
}

![Mounting Certs to Proxy](./picture/docker_local_exposure_ts_study_027_mount_certs.png)
```

---

## 27.7 動作確認（“鍵マーク🔒”チェック）✅👀

1. ブラウザで `https://app1.localhost` を開く
2. 警告が出なければ勝ち🏆✨
3. ついでに PowerShell の `curl` で確認もできるよ（証明書エラーが出なければOK）👍

```powershell
curl https://app1.localhost
```

---

## 27.8 よくあるハマり集📕🧯（ここ超大事）

### ① 管理者権限が足りない😇

`mkcert -install` が失敗する時はだいたいコレ。
**管理者としてPowerShell起動**して再実行で直る率高め🛠️

### ② Firefoxだけ警告が消えない🦊⚠️

Firefoxは設定で「OSのルート証明書を自動的に信頼する」をオンにできます。
`security.enterprise_roots.enabled` でも制御できます。([Mozilla サポート][6])

（手順はMozilla公式に書いてあるやつが安心）([Mozilla サポート][6])
※ Mozilla

### ③ `*.localhost` を作ったのに `localhost` がNG

さっき言った罠😇
**`localhost` と `*.localhost` は別**なので、両方含めて作ろう。

### ④ コンテナ内のNodeが「証明書を信頼しない」💥

これは“ブラウザ”じゃなくて **NodeがHTTPSクライアントになる時**に起こるやつ。
NodeはOSの証明書ストアを使わないので、`NODE_EXTRA_CA_CERTS` が必要になる場合があります。([GitHub][1])

![mkcert Common Pitfalls](./picture/docker_local_exposure_ts_study_027_common_pitfalls.png)

---

## 27.9 後片付け（不要になったら消す）🧹🗑️

mkcertにはCAを信頼ストアから外すオプションがあります：`-uninstall`。([manpages.ubuntu.com][7])

```powershell
mkcert -uninstall
```

さらに、CAファイルがどこにあるかは `mkcert -CAROOT` で分かります。([GitHub][1])
（消すなら、そこで出たフォルダを削除対象として判断してね🧠）

---

## 27.10 ミニ課題🧪🎓（手を動かす用）

✅ 課題A：ワイルドカード証明書を作る

* `localhost` と `*.localhost` を含めて、ファイル名固定で発行する

✅ 課題B：リバプロに組み込む

* Traefik（またはNginx）に `certs/` をマウントしてTLS有効化
* `https://app1.localhost` で警告ゼロを確認

✅ 課題C：増やしてみる

* `app2.localhost` を追加しても**証明書作り直しなし**で通るのを確認🎉

---

## 27.11 AI（Copilot/Codex）に聞くと爆速なやつ🤖⚡

そのままコピペで使える“お願い文”いくよ👇

* 「Traefik v3で、ローカル証明書（PEM）を dynamic config で読み込む最小構成を書いて。certFile/keyFileのパスは `/certs/...` で。」
* 「docker-compose.ymlで、`./certs` を read-only で `traefik` にマウントする例を作って。」
* 「`app1.localhost` / `api.localhost` をHostで振り分けるlabels例を、TLS前提で作って。」

---

次の章（第28章）では、このへんをやった直後にほぼ全員が踏む
**404 / 502 / つながらない** を“辞書化”して一気に安定させるよ🧯📕✨

[1]: https://github.com/FiloSottile/mkcert "GitHub - FiloSottile/mkcert: A simple zero-config tool to make locally trusted development certificates with any names you'd like."
[2]: https://datatracker.ietf.org/doc/html/draft-ietf-dnsop-let-localhost-be-localhost-00?utm_source=chatgpt.com "draft-ietf-dnsop-let-localhost-be-localhost-00"
[3]: https://raw.githubusercontent.com/microsoft/winget-pkgs/master/manifests/f/FiloSottile/mkcert/1.4.4/FiloSottile.mkcert.locale.en-US.yaml?utm_source=chatgpt.com "https://raw.githubusercontent.com/microsoft/winget..."
[4]: https://bjansen.github.io/scoop-apps/extras/mkcert/?utm_source=chatgpt.com "Mkcert"
[5]: https://community.chocolatey.org/packages/mkcert?utm_source=chatgpt.com "Chocolatey Software | mkcert 1.4.4"
[6]: https://support.mozilla.org/ja/kb/setting-certificate-authorities-firefox "
  Firefox で認証局 (CA) をセットアップする | 法人向け Firefox ヘルプ
"
[7]: https://manpages.ubuntu.com/manpages/jammy/man1/mkcert.1.html "Ubuntu Manpage:

       mkcert - zero-config tool to make locally trusted certificates
    "
