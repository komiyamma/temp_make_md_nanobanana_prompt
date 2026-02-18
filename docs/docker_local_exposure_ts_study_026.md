# 第26章：CaddyのローカルHTTPSを使ってみる🌟🔒

この章は「ローカルの `*.localhost` でも HTTPS にしたい！」を、**Caddyの自動HTTPS（ローカル用）**でサクッと実現する回です🧁✨
（本番の証明書運用はまた別物だけど、開発で詰まりやすい“HTTPS必須機能”を動かすにはこれが超強い💪）

---

## 1) 今日のゴール🎯

* `https://hello.localhost` にアクセスして、🔒が付いた状態で表示できる
* その仕組み（**CaddyのローカルCA**）をざっくり理解できる
* 既存の `app1.localhost` / `api.localhost` にも同じ考えで適用できる

Caddyは、**公開DNS名**ならACME（例：Let’s Encrypt等）で証明書を取ってくれるし、**`localhost` やローカル/内部名**にはローカル用の証明書を自動で用意してくれます🔧✨（HTTP→HTTPSリダイレクトも自動）([Caddy Web Server][1])

---

## 2) まず超重要：ローカルHTTPSの“正体”🧠🔍

ローカルHTTPSはこういう仕組みです👇

* Caddyが **「ローカル用の認証局（CA）」** を自分のPC用に作る
* そのCAで `hello.localhost` 用の証明書をサインする✍️
* あとはブラウザ側がそのCAを「信頼する」ように登録すれば、🔒で通る！

Caddyは最初にCAを作ったとき、OSの信頼ストアへ入れようとします（入ると証明書発行者が “Caddy Local Authority” みたいな名前で見える）([Caddy Web Server][1])
ただし **Dockerコンテナ内で動かしてると、Windows側の信頼ストアには自動で入れられない**ことが多いので、**手動でroot証明書をコピーしてWindowsにインポート**します🪄([Caddy Web Server][2])

![Caddy Local CA Mechanism](./picture/docker_local_exposure_ts_study_026_caddy_local_ca.png)

---

## 3) まずは最小構成で「HTTPSできた！」を作る🚀🍞

以下の2ファイルだけ作ります✍️（場所はどこでもOK）

### `compose.yml`

```yaml
services:
  caddy:
    image: caddy:2
    ports:
      - "80:80"
      - "443:443"
      - "443:443/udp"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy_data:/data
      - caddy_config:/config

volumes:
  caddy_data:
  caddy_config:
```

ポイント：

* `80` と `443` を開ける（HTTP→HTTPSの自動リダイレクトにも使う）([Caddy Web Server][1])
* `caddy_data` を必ず永続化！（ここにローカルCAや証明書が入る）🧠
* 公式イメージでも `/data` と `/config` の永続化が推奨です([Docker Hub][3])

### `Caddyfile`

```caddyfile
hello.localhost {
  respond "Hello HTTPS 🎉" 200
  tls internal
}
```

`tls internal` は「公開CAじゃなく、ローカルCAで出してね👍」の合図です🔒([Caddy Web Server][2])

![Minimum Config for Caddy](./picture/docker_local_exposure_ts_study_026_min_config.png)

---

## 4) 起動してアクセスしてみる🐳▶️🌐

VS Codeのターミナル（PowerShell）で：

```powershell
docker compose up -d
docker compose logs -f caddy
```

次にブラウザで：

* `https://hello.localhost`

ここで最初は **警告が出るのが普通**です😇
まだ Windows が “CaddyのローカルCA” を信頼してないからね。

---

## 5) Windowsに「CaddyのローカルCA（root.crt）」を信頼させる🪟🔐

### 5-1) root.crt をコンテナから取り出す📤

Caddyのroot証明書はストレージ配下にあります（Dockerだと `/data/...` にいることが多い）([Caddy Web Server][4])
まずコピー：

```powershell
docker compose cp caddy:/data/caddy/pki/authorities/local/root.crt .\caddy-local-root.crt
```

> もしパスが違って失敗したら、コンテナ内で探せばOK👌
>
> ```powershell
> docker compose exec caddy sh -lc "find /data -name root.crt -print"
> ```

### 5-2) インポート方法は2つ（どっちでもOK）✅

**A. GUIで入れる（わかりやすい・確実）🖱️**

1. `caddy-local-root.crt` をダブルクリック
2. 「証明書のインストール」
3. 「証明書をすべて次のストアに配置する」
4. **Trusted Root Certification Authorities（信頼されたルート証明機関）** を選んで完了
   この流れは Microsoft の手順でも同じです([Microsoft Learn][5])

**B. コマンドで入れる（サクッと派）⌨️**
Caddy公式ドキュメントでも `certutil` 例が載ってます([Caddy Web Server][4])

```powershell
certutil -addstore -f "ROOT" .\caddy-local-root.crt
```

※管理者権限の有無やポリシーで弾かれることがあるので、その場合はA（GUI）が安定です🙂

![Trusting the Root Certificate](./picture/docker_local_exposure_ts_study_026_trust_root.png)

---

## 6) もう一回アクセスして🔒を確認🎉🔒

ブラウザを**いったん全部閉じて**（ウィンドウごと！）開き直してから、

* `https://hello.localhost`

これで警告が消えて🔒になれば勝ち！🏆
ブラウザは証明書状態をキャッシュしてハマることがあるので、再起動が効きます😺([Caddy Community][6])

![Browser Lock Icon Success](./picture/docker_local_exposure_ts_study_026_browser_lock.png)

---

## 7) ここで“ありがち詰まり”を先に潰す辞典📕🧯

### パターンA：まだ `ERR_CERT_AUTHORITY_INVALID` 😭

原因トップ3👇

1. **root.crt を違うストアに入れた**
   → 「信頼されたルート証明機関」に入ってるか確認([Microsoft Learn][7])

2. **/data を永続化してなくて、CAが作り直されてる**
   → `caddy_data` を消すと別CAになって“また警告”になります（だから永続化必須）([Caddy Community][6])

3. **Dockerだから自動で信頼ストアに入れられない**（それが普通）
   → 手動インポートが正解ルートです([Caddy Web Server][2])

---

### パターンB：Chrome/EdgeはOKなのにFirefoxだけ警告🦊⚠️

Firefoxは独自の証明書ストア運用になりがちで、OS側を見ない設定のことがあります😇
対処は2択：

* Firefoxに「OSのルート証明書を信頼させる」設定をON
  （`security.enterprise_roots.enabled` / `ImportEnterpriseRoots` など）([Mozilla サポート][8])
* もしくは Firefox の証明書管理画面に root.crt を直接インポート

![Common Troubleshooting Patterns](./picture/docker_local_exposure_ts_study_026_troubleshooting.png)

---

### パターンC：`https://hello.localhost` が開けない（接続できない）🌪️

* 443が別アプリに取られてるかも
  → まず `docker compose ps` と `docker compose logs -f caddy` を見る👀
* 企業PCのセキュリティでローカルCA追加が制限されてるかも
  → GUIが通らないなら、次章の **mkcert方式**（別アプローチ）を使うと突破できる場合があります🪄

---

## 8) 既存のリバプロ構成へ適用する（実戦）⚔️✨

今までの `app1.localhost` / `api.localhost` でも、やることは同じです👇

```caddyfile
app1.localhost {
  reverse_proxy app1:3000
  tls internal
}

api.localhost {
  reverse_proxy api:3000
  tls internal
}
```

* 入口は `443`（HTTPS）
* `tls internal` でローカルCAに統一
* 80→443の誘導はCaddyが自動でやってくれます([Caddy Web Server][1])

![Adapting Proxy for HTTPS](./picture/docker_local_exposure_ts_study_026_proxy_adaptation.png)

---

## 9) “信頼”の注意点（怖がらなくてOK、でも知っておく）🧯🙂

ルートCAを信頼する＝「このCAがサインした証明書は全部信頼する」なので、**自分の開発PCで自分が管理できる範囲**で使うのが基本です。
CaddyのローカルCAは信頼ストアから外すこともできます（Caddyは信頼ストアへ入れる/外すコマンドも用意してます）([Caddy Web Server][9])

![Local Trust Scope](./picture/docker_local_exposure_ts_study_026_trust_scope.png)

---

## 10) AIに頼むと爆速になるプロンプト例🤖⚡

**① 既存のCaddyfileを“HTTPS対応に直して”**

* 「`app1.localhost` と `api.localhost` を `tls internal` でHTTPS化して、HTTP→HTTPSの挙動も崩さないCaddyfileにして。WebSocketもある前提で注意点をコメントに入れて」

**② まだ警告が出るときの切り分け**

* 「Docker上のCaddyで `tls internal` を使ってる。Windowsでroot.crtをインポートしたのに警告が消えない。考えられる原因を優先度順にチェックリスト化して」

**③ “/data消してしまった…”事故復旧**

* 「Caddyの `caddy_data` を消してしまった。CAが変わって警告が復活した。安全に復旧する手順（再インポートやブラウザキャッシュ含む）を書いて」

---

## 11) ミニ課題🎒✨（10分で終わる）

1. `admin.localhost` を追加して、`respond` で別メッセージを返してみよう😺
2. `docker compose down` → `up -d` しても 🔒 が維持されるか確認しよう（**維持されないなら /data永続化が怪しい**）🔍([Caddy Community][6])
3. Firefoxを使ってるなら、OSルートを信頼する設定をONにできるか確認してみよう🦊([Mozilla サポート][8])

---

ここまでできたら、次章（mkcert）に行くと「ブラウザ警告をもっと減らす」「ワイルドカードで楽する」みたいな方向に進めます🪄✨
（でも第26章の時点で、もう開発はかなり快適になるはず！😆🔒）

[1]: https://caddyserver.com/docs/automatic-https?utm_source=chatgpt.com "Automatic HTTPS — Caddy Documentation"
[2]: https://caddyserver.com/docs/caddyfile/directives/tls?utm_source=chatgpt.com "tls (Caddyfile directive) — Caddy Documentation"
[3]: https://hub.docker.com/_/caddy?utm_source=chatgpt.com "caddy - Official Image | Docker Hub"
[4]: https://caddyserver.com/docs/running?utm_source=chatgpt.com "Keep Caddy Running — Caddy Documentation"
[5]: https://learn.microsoft.com/en-us/skype-sdk/sdn/articles/installing-the-trusted-root-certificate?utm_source=chatgpt.com "Installing the trusted root certificate"
[6]: https://caddy.community/t/https-for-local-domains-working-with-curl-but-not-with-browsers/12594?utm_source=chatgpt.com "HTTPS for local domains - working with CURL, but not ..."
[7]: https://learn.microsoft.com/en-us/windows-hardware/drivers/install/trusted-root-certification-authorities-certificate-store?utm_source=chatgpt.com "Trusted Root Certification Authorities Certificate Store"
[8]: https://support.mozilla.org/en-US/kb/setting-certificate-authorities-firefox?utm_source=chatgpt.com "Set up Certificate Authorities (CAs) in Firefox - Mozilla Support"
[9]: https://caddyserver.com/docs/command-line?utm_source=chatgpt.com "Command Line — Caddy Documentation"
