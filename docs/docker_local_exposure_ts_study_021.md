# 第21章：Traefikのダッシュボードを安全に使う🧯📊

Traefikのダッシュボードって、ルーティングの状態が「一目でわかる」最強のデバッグ道具なんだけど…
同時に「見せちゃいけない情報」も山ほど見えるので、**安全にだけ**使う設定をここで固めます😇🔒
（本番で無防備に出すのはNGだよ〜！）([doc.traefik.io][1])

---

## この章でできるようになること🎯✨

* ダッシュボードを**自分だけ**見れるようにする（認証つき）🔐
* うっかり「LANやネットに公開」を防ぐ🧱
* 404/401で詰まったときの直し方がわかる🧰

---

## 1) まず「何が危ないの？」を5秒で理解😱💥

TraefikのAPI/ダッシュボードは、ルーター・サービス・ミドルウェアなどの設定情報をまるっと見せます。
つまり、**構成やルールが全部バレる**＝攻撃者にとって地図みたいなもの🗺️💀

ドキュメントでも、**本番で有効化は推奨されない**・有効にするなら**認証などで保護してね**と明確に言ってます。([doc.traefik.io][1])
さらに「APIのポートを公開しない（内部に閉じる）」のが推奨です。([doc.traefik.io][1])

---

## 2) やりがちな“危険な近道”🚫⚠️

## ❌ 罠：`api.insecure=true` を使う

`api.insecure` は、`traefik` という entryPoint 上でAPI/ダッシュボードを有効にする設定です。([doc.traefik.io][1])
これを使って **ポートを外に公開**すると、うっかり誰でも見れる状態になりがち😇💣

なのでこの章では、**insecureは使わない**でいきます🙅‍♂️

---

## 3) 安全にする「3点セット」🛡️✨

ここからが本題！
ダッシュボードはこの3つで守るとかなり安全です👍

## ✅ (A) “物理的に”ローカルからしか入れない🧱🏠

ポート公開を `127.0.0.1` に縛る（ローカルPC以外から叩けない）
→ これが一番強い💪✨

## ✅ (B) 専用ホスト名で分離する🏷️

`traefik.localhost` みたいな**専用の入口**にする
→ 通常アプリのURLと混ざらない🧠

## ✅ (C) BasicAuth（ID/PW）を必ずかける🔐

Traefik公式の例でも、`api@internal` にルーターを当てて **BasicAuth をミドルウェアで付ける**形が紹介されています。([doc.traefik.io][1])

---

## 4) 実装：ダッシュボードを「安全に」公開する設定🧩🐳

ここでは **Traefik自身にラベルを付けて**、`api@internal` をルーティングします。([doc.traefik.io][1])
（この形がいちばん素直で事故りにくい👍）

## 4-1. まずは htpasswd を作る🔑😺

PowerShell でOK（Dockerが動けばいける）👇

```powershell
docker run --rm httpd:2.4-alpine htpasswd -nb admin "SuperStrongPassword"
```

出力例（こんな感じの1行が出る）👇
`admin:$apr1$xxxxx$yyyyy`

この **`$` は compose の中だと特別扱い**なので、**`$$` に置き換える必要**があります（公式例でも `$$apr1$$...` になってるやつ）([doc.traefik.io][1])
ここでミスると「認証が通らない」地獄になります😇🔥

---

## 4-2. Compose（Traefikサービス）に追加する🧩✨

※ 既にTraefikを立てている想定で、**差分として**読んでOKだよ👍
（`exposedByDefault=false` を使うなら、各アプリに `traefik.enable=true` を付ける流れね🚦）

```yaml
services:
  traefik:
    image: traefik:v3.6
    command:
      - --api=true
      - --api.dashboard=true
      - --providers.docker=true
      - --providers.docker.exposedbydefault=false
      - --entryPoints.web.address=:80
    ports:
      - "127.0.0.1:80:80"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro

    labels:
      - "traefik.enable=true"

      # ✅ ダッシュボード用ルーター（/api と /dashboard を確実に拾う）
      - "traefik.http.routers.traefik.rule=Host(`traefik.localhost`) && (PathPrefix(`/api`) || PathPrefix(`/dashboard`))"
      - "traefik.http.routers.traefik.entrypoints=web"
      - "traefik.http.routers.traefik.service=api@internal"

      # ✅ BasicAuth をかける
      - "traefik.http.routers.traefik.middlewares=traefik-auth"
      - "traefik.http.middlewares.traefik-auth.basicauth.users=admin:$$apr1$$xxxxx$$yyyyy"
      - "traefik.http.middlewares.traefik-auth.basicauth.removeheader=true"
```

ポイント🧠✨

* ルーターは **`api@internal`** に向ける（公式の推奨ルート）([doc.traefik.io][1])
* ルールは `Host(...) && (PathPrefix(/api) || PathPrefix(/dashboard))` が鉄板（公式例そのまま）([doc.traefik.io][1])
* `removeheader=true` で認証ヘッダを下流に渡さない（地味に大事）([doc.traefik.io][1])
* `ports` を `127.0.0.1` に縛ってるので、**LANからは基本入れません**（それが狙い）🧱✨

---

## 4-3. アクセスして確認する✅🌐

* URL：`http://traefik.localhost/dashboard/`

重要⚠️：`/dashboard/` の **末尾スラッシュは必須**です。([doc.traefik.io][1])
（ドキュメントにも「必須」「RedirectRegexで軽減できる」って書いてあるやつ）([doc.traefik.io][1])

---

## 5) “見える化”の使いどころ3つ👀✨

ダッシュボードは、これを見るだけでだいぶ強くなる💪

## (1) Routers：いま、どのルールが効いてる？🧭

「Host/Path どっちで拾ってる？」が即わかる✨

## (2) Services：どこに流してる？🔀

ポート・ターゲットの向き先ミスが一発で見える👀

## (3) Middlewares：何が挟まってる？🧩

auth / stripPrefix / headers など、**思った通りの順番になってるか**確認できる👍

---

## 6) よくある詰まりポイント辞典📕🧯

## 😵 404になる

* ルーターの `rule` が `/api` と `/dashboard` を拾ってない
  → 公式どおり `(...PathPrefix(`/api`) || PathPrefix(`/dashboard`))` にするのが無難([doc.traefik.io][1])

## 😵 `/dashboard` に行くと変になる

* `/dashboard/` を使ってない（末尾スラッシュが必須）([doc.traefik.io][1])

## 😵 認証が通らない（毎回弾かれる）

* htpasswd の `$` を `$$` にしてないパターンが多い😇
  → 公式例でも `$$apr1$$...` 表記になってるのはそのため([doc.traefik.io][1])

---

## 7) 追加で“さらに固く”したい人へ（任意）🧊🔒

## 7-1. LANからも見たい（でも全公開は嫌）📶😺

この場合は `ports` の縛りを緩める必要が出るけど、代わりに **IPAllowList** を重ねると安全度UP✨

Traefik v3 では `IPWhiteList` が `IPAllowList` に名前変更されてます（設定自体は同じ）([doc.traefik.io][2])

例：AllowList（CIDRで指定）🧱
※ ドキュメント例は tcp のラベルだけど、考え方は同じで **sourceRange を書く**だけ。([doc.traefik.io][3])

```yaml
labels:
  - "traefik.http.middlewares.traefik-allow.ipallowlist.sourcerange=127.0.0.1/32,192.168.0.0/16"
  - "traefik.http.routers.traefik.middlewares=traefik-allow,traefik-auth"
```

---

## 8) AIに投げると爆速になるプロンプト例🤖⚡

## ✅ ダッシュボード用ラベルだけ作らせる

```text
Traefik v3 の docker compose で、traefik.localhost の /api と /dashboard/ にだけアクセスできる
ダッシュボードルーターを作りたい。
BasicAuth も付けたい。出力は labels の行だけにして。
```

## ✅ 401/404 の原因を一緒に潰す

```text
Traefik dashboard が 404(または401) になります。
私の router rule と middlewares と entrypoints を貼るので、
ありがちな原因候補を優先度順に3つ出して、確認手順も書いて。
```

---

## 9) ミニ課題🧪🎓

## 課題A（超実用）✅

* `traefik.localhost/dashboard/` にログインできる状態を作る
* そして「Routers」画面で、自分のアプリ用ルーターが見えることを確認👀✨

## 課題B（ちょい上級）🔧

* `RedirectRegex` を使って `/dashboard` を `/dashboard/` に強制リダイレクトしてみる
  （公式でも「末尾スラッシュ問題は RedirectRegex で軽減できる」って言ってる）([doc.traefik.io][1])

## 課題C（安全脳）🧠🔒

* 「自分の設定で、外部に漏れる可能性がある箇所」を3つ列挙して、対策を書く
  ヒント：ポート公開・認証・公開範囲…あたりが王道😺

---

## まとめ🎁✨

* ダッシュボードは最強のデバッグ道具👀
* でも情報が強すぎるので、**認証＋ローカル限定**で守るのが基本🛡️
* ルーティングは **`api@internal`** に当てるのが王道（公式例）([doc.traefik.io][1])
* `/dashboard/` の末尾スラッシュ必須、忘れがち⚠️([doc.traefik.io][1])

---

次の第22章は、この「共通の入口（Traefik）」を **別スタックとして切り出してテンプレ化**していくよ📦🚪✨
一気に「毎回コピペ地獄」から抜けられるところだね😆👍

[1]: https://doc.traefik.io/traefik/reference/install-configuration/api-dashboard/ "Traefik API & Dashboard Documentation - Traefik"
[2]: https://doc.traefik.io/traefik/migrate/v2-to-v3-details/ "Traefik V3 Migration Details - Traefik"
[3]: https://doc.traefik.io/traefik/reference/routing-configuration/tcp/middlewares/ipallowlist/ "Traefik TCP Middlewares IPAllowList - Traefik"
