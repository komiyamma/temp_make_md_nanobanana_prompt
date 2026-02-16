# 第14章：Caddyの基本ルール（読むだけで怖くなくなる）📘🙂

この章のゴールはシンプル！👇
「Caddyfileを見ても“うっ…”ってならない」＋「自分でルールを足したり直したりできる」ようになることだよ〜🧠💪

---

## 1) まず“交通整理”の全体図を頭に入れる🚥🗺️

リバプロの動きは、だいたいこれ👇

```
ブラウザ🌐
  │  (front.localhost / app.localhost / api.localhost)
  ▼
Caddy（入口🚪）
  │  HostやPathで振り分け
  ├─► フロント(dev server)🖥️
  └─► API(backend)🧩
```

ここで覚えるのは **「入口で受けて、ルールで振り分ける」** だけでOK🙆‍♂️✨

---

## 2) Caddyfileは“サイトの箱”を並べるだけ📦📦📦

Caddyfileは基本、**site block（サイトブロック）**の集まりだよ〜。
「このホスト名で来たら、こうする」って箱を作る感じ🙂

Caddy公式の“概念ページ”でも、Caddyfileは **site blockが基本単位**で、最初にサイトのアドレスを書いて、ブロック内にディレクティブを書く、って説明されてるよ。([Caddy Web Server][1])

---

## 3) 最低限これだけ覚えれば読める！🔑✨

## 3-1. site block（箱）📦

**1行目 = どこ宛のリクエストを扱う箱か**
その下に `{ ... }` の中身を書く（中身がルール）🧩

* site blockが1個だけなら `{}` を省略できる（省略OK）([Caddy Web Server][1])
* `{` は行末にスペース付きで置く、`}` は単独行にする、みたいな細かい決まりもあるよ（地味に大事）([Caddy Web Server][1])

例（基本の形）👇

```caddyfile
app.localhost {
	# ここにルールを書く
}
```

---

## 3-2. directive（やること命令）🧩

ブロックの中に書く **命令（キーワード）** だよ。
たとえば `reverse_proxy`（中へ流す）とか。

公式ドキュメントでも `reverse_proxy` は「リクエストを1つ以上のバックエンドにプロキシする」ディレクティブとして説明されてるよ。([Caddy Web Server][2])

---

## 3-3. matcher（どのリクエストだけ？の条件）🎯

「この命令は、**どんなリクエストにだけ適用する？**」を絞る条件だよ。

Caddyfileでは、ディレクティブの直後に **matcher token** を置ける（例：`/api/*` や `@name`）っていうルール。([Caddy Web Server][3])

matcherの代表3つ👇

* `*`：全部（だいたい省略でOK）([Caddy Web Server][3])
* `/path`：パス条件（超よく使う）([Caddy Web Server][3])
* `@name`：名前付き条件（methodやheaderなど複合条件で使う）([Caddy Web Server][3])

⚠️**パスの注意ポイント**
パス一致はデフォルトだと“前方一致”じゃなくて“完全一致寄り”。だから **prefix一致したいなら `*` を付ける** のが基本！
`/foo*` と `/foo/*` の違いも重要だよ〜（`/foobar` を拾っちゃうかどうか）。([Caddy Web Server][3])

---

## 4) ルールの核：`handle` は「当たったらここだけ」🔀🧠

`handle` は **複数並べたとき“最初にマッチした1個だけ”が動く** 仕組み！
つまり「if / else if / else」っぽいノリになる👍

公式でも「複数のhandleが並んでたら、最初にマッチしたhandleだけ評価される」「matcher無しのhandleはフォールバック（最後の受け皿）」と説明されてるよ。([Caddy Web Server][4])

例：`/api/*` はAPIへ、それ以外はフロントへ👇

```caddyfile
app.localhost {
	handle /api/* {
		reverse_proxy api:3000
	}

	handle {
		reverse_proxy front:5173
	}
}
```

この形、めちゃくちゃよく使う！🥳✨

---

## 5) 超便利：`handle_path` は「/api を剥がして渡す」🪄🧹

たとえばAPI側が `/health` を期待してるのに、入口で `/api/health` で受けてる…みたいな時あるよね？😇

そんな時の救いが `handle_path`！
これは `handle` と同じだけど、**マッチしたパスの“プレフィックスを自動でstrip”してから中へ渡す** っていう便利機能。([Caddy Web Server][5])

```caddyfile
app.localhost {
	handle_path /api/* {
		reverse_proxy api:3000
	}

	handle {
		reverse_proxy front:5173
	}
}
```

* ブラウザ：`/api/health`
* API側に届くパス：`/health`（イメージ）🧠✨

※ `handle_path` は **パスmatcher1個だけ**（`@name`とかは使えない）って制約もあるよ。([Caddy Web Server][5])

---

## 6) `reverse_proxy` の読み方：とにかく「宛先リスト」📮➡️

`reverse_proxy` は基本これだけ覚えればOK👇

* 書き方の形：`reverse_proxy [<matcher>] [<upstreams...>]`([Caddy Web Server][2])
* upstream（宛先）は **1個でも複数でもOK**（複数なら負荷分散っぽくなる）([Caddy Web Server][2])

例：シンプルに1個へ流す👇

```caddyfile
reverse_proxy api:3000
```

---

## 7) ちょい重要：HTTPSの挙動でビビらないために🔐😳

Caddyは **デフォでHTTPS** が基本思想。([Caddy Web Server][6])
さらに `localhost` みたいな **ローカル/内部ホスト名でもHTTPS（自己署名）** を使うことがあるし、初回は“信頼ストアに入れる”系でパスワードを求めることもあるよ。([Caddy Web Server][6])

「いや今日はHTTPでいいんだが？😇」って時は、公式のGlobal optionsの説明がめちゃ大事で👇

* `auto_https off` は **証明書管理やリダイレクトを止めるだけ**で、HTTPで提供する保証じゃない([Caddy Web Server][7])
* HTTPで出したいなら **サイトアドレスを `http://` で始めるか `:80` を付ける** のが推奨([Caddy Web Server][7])

例：HTTP固定で気楽にやる👇

```caddyfile
http://app.localhost {
	handle /api/* {
		reverse_proxy api:3000
	}
	handle {
		reverse_proxy front:5173
	}
}
```

この“逃げ道”知ってるだけで精神が安定するよ🧘‍♂️🍵

---

## 8) 手順：Caddyfileを編集→整形→リロード🛠️✨

「変更したのに反映されない😡」を防ぐために、流れを固定しよ〜！

## 8-1. リロード（コンテナ内で `caddy reload`）🔄

公式のDocker HubのCaddy公式イメージでも「Dockerではコンテナ内で `caddy reload` 実行が推奨」「`/etc/caddy` を作業ディレクトリにして reload できる」って書かれてるよ。([Docker Hub][8])

例（Composeならこれが楽）👇

```bash
docker compose exec -w /etc/caddy caddy caddy reload
```

## 8-2. ついでに整形（読みやすさは正義）🧹

```bash
docker compose exec -w /etc/caddy caddy caddy fmt --overwrite
```

---

## 9) よくあるミス辞典📕🧯（ここ超あるある）

## ❌ ミス1：`/api` と `/api/*` を混同する😵

* `/api` だけだと `/api/health` に当たらないことがある
* prefixで拾うなら基本 `*` を付ける！([Caddy Web Server][3])

## ❌ ミス2：`handle` の順番で詰む🫠

`handle` は「最初にマッチした1個だけ」だから、雑に書くと全部を飲み込む😇

* 具体的な条件（`/api/*`）を先
* 最後に `handle { ... }` を置く（フォールバック）([Caddy Web Server][4])

## ❌ ミス3：APIが `/api/...` を想定してなくて404💥

そんな時は `handle_path` を疑う！
「prefix strip」が公式の役割だよ。([Caddy Web Server][5])

## ❌ ミス4：Caddyfileの `{` `}` が雑でパース失敗🧱

`{` の位置や `}` 単独行ルールは地味に効く！([Caddy Web Server][1])

---

## 10) AIに聞く例（コピペで使ってOK）🤖✨

## ✅ 例1：最小のルーティング生成

「Caddyfileで、app.localhost を入口にして /api/* を api:3000 に、それ以外を front:5173 に流す設定を書いて。/api はAPI側に渡す時に strip して」

## ✅ 例2：デバッグ重視の相談

「Caddyで /api/health が 502 になる。Caddyfile・確認コマンド（curlやログの見方）・よくある原因を“上から潰す順”で教えて」

## ✅ 例3：HTTPSがしんどい時

「CaddyがローカルHTTPSを有効にしてブラウザが警告になる。いったんHTTPで運用するCaddyfileの書き方（http:// など）を提案して」([Caddy Web Server][7])

---

## 11) ミニ課題（15分で終わるやつ）⏱️🎒

## 課題A：`handle` で“if/else”を作る🔀

1. `app.localhost` を1つ用意
2. `/api/*` は `api:3000`
3. それ以外は `front:5173`
4. 最後の `handle` を消してみて、何が起きるか観察👀（たぶん404が増える）

## 課題B：`handle_path` を入れて違いを体感🧪

1. `/api/*` を `handle_path` にする
2. API側で“受け取ったパス”をログ出力できるなら出して確認（`/health` になってるか）
3. もしログ出せないなら、API側のルーティングをわざと `/health` だけにして挙動で判断でもOK👌

---

## 12) 章末チェックリスト✅✨

* `handle` は「最初にマッチした1個だけ」って言える😎([Caddy Web Server][4])
* `/api/*` の `*` の意味が分かる😺([Caddy Web Server][3])
* `/api` を剥がしたいなら `handle_path` を思い出せる🧠([Caddy Web Server][5])
* 設定変更後に `caddy reload` して反映できる🔄([Docker Hub][8])
* HTTPSで混乱したら `http://` の逃げ道を使える🧘‍♂️([Caddy Web Server][7])

---

次の第15章は、フロント（Vite系）をリバプロ越しに見た時に出がちな **HMR/WebSocketの詰まりポイント**を“事故らない設定テンプレ”として固める回にすると、めちゃ気持ちよく進むよ〜👻⚡

[1]: https://caddyserver.com/docs/caddyfile/concepts "Caddyfile Concepts — Caddy Documentation"
[2]: https://caddyserver.com/docs/caddyfile/directives/reverse_proxy "reverse_proxy (Caddyfile directive) — Caddy Documentation"
[3]: https://caddyserver.com/docs/caddyfile/matchers "Request matchers (Caddyfile) — Caddy Documentation"
[4]: https://caddyserver.com/docs/caddyfile/directives/handle "handle (Caddyfile directive) — Caddy Documentation"
[5]: https://caddyserver.com/docs/caddyfile/directives/handle_path "handle_path (Caddyfile directive) — Caddy Documentation"
[6]: https://caddyserver.com/docs/automatic-https "Automatic HTTPS — Caddy Documentation"
[7]: https://caddyserver.com/docs/caddyfile/options "Global options (Caddyfile) — Caddy Documentation"
[8]: https://hub.docker.com/_/caddy "caddy - Official Image | Docker Hub"
