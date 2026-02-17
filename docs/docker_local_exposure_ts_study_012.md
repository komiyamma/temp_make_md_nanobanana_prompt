# 第12章：リバプロ候補をざっくり比較する🆚😺

この章はズバリ、こういう悩みを終わらせる章です👇

* 「入口1個にまとめたいけど、どれ使えばいいの？😵‍💫」
* 「設定が難しそうで詰みそう…😇」
* 「あとから増えた時に地獄にならない？💣」

---

## 12-1. まず結論：迷ったらこの3択でOK🎯✨

用途ごとに“最初の一本”を決めちゃうのが正解です👍

* **最短で成功体験が欲しい** → **Caddy** 🍞🚀

  * 設定が読みやすい＆ローカルHTTPSが得意
* **Docker/Composeに合わせて自動化したい** → **Traefik** 🤖🚦

  * “ラベル書くだけで増える”のが強い
* **本番がNginxで、同じ作法に寄せたい** → **Nginx** 🧱🏭

  * 定番・実績・情報量は強い（ただし設定は硬め）

---

## 12-2. 2026-02-12時点の“最新寄り”状況（ざっくり把握）🗓️🔎

* **Nginx**：2026-02-04に **stable 1.28.2 / mainline 1.29.5** がリリース（CVE修正も含む）([Nginx][1])
* **Traefik**：v3 系の中でも **3.6 系がアクティブサポート**扱い（v3.6.8 が 2026-02-11）([Traefik Labs Documentation][2])
* **Compose**：Composeファイルは **Compose Specification が推奨（services/networks/volumes等）**([Docker Documentation][3])
* **Caddy**：安定版は **2.10.2（2025-08頃）**、2.11 はベータが進行中([endoflife.date][4])

「今この章で大事なこと」は、**どれも現役で選べる**ってことです😺✅

---

## 12-3. そもそも“リバプロ”に求めるもの（ローカル編）🚪➡️🏠

ローカル公開整理でリバプロに求めるのは、だいたいこの6つです👇

1. **入口が1つ**（80/443）になってほしい🚪
2. **ホスト名 or パス**で分岐できる🔀
3. **コンテナ増えても破綻しない**🧱
4. **ログで切り分けできる**🕵️
5. **HTTPSも欲しくなる日が来る**🔐（最近のWebはこれが多い）
6. **設定が“未来の自分”に読める**📘😇

この6つで比較すると、選びやすくなります👍

---

## 12-4. 3人のキャラ紹介（超ざっくり）🧑‍🤝‍🧑✨

## 🧱 Nginx：職人気質のベテラン

![Nginx Concept](./picture/docker_local_exposure_ts_study_012_04_nginx_concept.png)

* ちゃんと書けば強い
* でも設定は“お堅め”で、最初は疲れやすい😵
* mainline/stable の考え方もある（mainline推奨寄りの説明もある）([F5 NGINX Documentation][5])

## 🍞 Caddy：読みやすさ重視の優等生

![Caddy Concept](./picture/docker_local_exposure_ts_study_012_02_caddy_concept.png)

* ルールが素直で、設定が短い
* ローカルHTTPSが得意（ローカル/内部名に対してHTTPSを扱う説明あり）([Caddy Web Server][6])
* `reverse_proxy` が強力で、まず困らない([Caddy Web Server][7])

## 🤖 Traefik：Docker自動化の天才

![Traefik Concept](./picture/docker_local_exposure_ts_study_012_03_traefik_concept.png)

* Docker連携が“思想レベル”で強い
* **コンテナのラベル**からルーティングを作る([Traefik Labs Documentation][8])
* ただし最初の概念（router/service/middleware）がちょい増える😇

---

## 12-5. 比較表（ローカル公開整理の観点）🆚📋

![Comparison Matrix](./picture/docker_local_exposure_ts_study_012_05_comparison_matrix.png)

| 観点            | Nginx 🧱       | Caddy 🍞                                     | Traefik 🤖                                              |
| ------------- | -------------- | -------------------------------------------- | ------------------------------------------------------- |
| 最初の簡単さ        | △（設定が硬い）       | ◎（短く書ける）                                     | ○（概念は多いが慣れる）                                            |
| 設定の読みやすさ      | △              | ◎                                            | ○（ラベルが増えると読みにくい時あり）                                     |
| Dockerとの相性    | ○（手動/テンプレ化で対応） | ○（普通にいける）                                    | ◎（Docker providerが本体級）([Traefik Labs Documentation][9]) |
| サービス増加への強さ    | ○              | ○                                            | ◎（勝手に増やせる）                                              |
| ローカルHTTPSの手軽さ | △（自前で頑張る）      | ◎（Automatic HTTPSが売り）([Caddy Web Server][6]) | ○（できるが設定が増えがち）                                          |
| 情報量/定番感       | ◎              | ○                                            | ○                                                       |
| “本番に近い”感      | ◎（多くの現場で採用）    | ○                                            | ○（クラウド/コンテナ文脈で強い）                                       |

---

## 12-6. 選び方：3問で決める🧠💡

![Decision Funnel](./picture/docker_local_exposure_ts_study_012_01_decision_funnel.png)

## Q1：まず「2〜3個のアプリを共存」させたい？

* YES → **Caddy** が最短🍞✨
* NO（もう最初から増えまくる）→ Q2へ

## Q2：コンテナが増えた時、毎回プロキシ設定を手で編集したくない？

* YES → **Traefik**🤖✨
* NO（手でちゃんと管理したい）→ Q3へ

## Q3：本番がNginxで、同じ書き方に寄せたい？

* YES → **Nginx**🧱
* NO → CaddyかTraefikに戻る（だいたいCaddyが平和）😺

---

## 12-7. “設定の雰囲気”だけ先に見る（超ミニ）👀✨

ここでは「うわ、読める/読めない」が分かればOKです👍
（この章は“比較”なので、ガチ導入は次章以降でやる想定！）

## 🍞 Caddy（Caddyfile）の雰囲気：短い＆読める

```caddyfile
## hostで分ける例
app1.localhost {
  reverse_proxy app1:3000
}

api.localhost {
  reverse_proxy api:8787
}
```

`reverse_proxy` の仕様は公式にまとまってます([Caddy Web Server][7])

---

## 🧱 Nginx（nginx.conf）の雰囲気：ちゃんとしてるけど硬い

```nginx
server {
  listen 80;
  server_name app1.localhost;

  location / {
    proxy_pass http://app1:3000;
  }
}
```

「書ける人には強い」けど、初手はCaddyより疲れがち😇
あと mainline/stable の話も公式にあります([F5 NGINX Documentation][5])

---

## 🤖 Traefik（Composeラベル）の雰囲気：“増やすのが楽”寄り

Traefikは「Dockerのラベルでルーティングを作る」のが基本思想です([Traefik Labs Documentation][8])

```yaml
services:
  app1:
    image: your-app1
    labels:
      - traefik.enable=true
      - traefik.http.routers.app1.rule=Host(`app1.localhost`)
      - traefik.http.services.app1.loadbalancer.server.port=3000
```

この“ラベル増殖”がラクにも地獄にもなるので、後の章で**命名ルール**が効いてきます😺✨

---

## 12-8. ローカル運用でハマりやすいポイント（比較目線）💣🧯

## ① 「増えた時に誰が管理する？」問題👤📌

* **Nginx/Caddy**：設定ファイルが“台帳”。1個見れば全体が分かる📘
* **Traefik**：設定が各サービスに散る（＝各サービスが自己申告する）🧩
  → チームなら便利、個人でも増えると便利。でも**ルール無し**だと迷子🌀

## ② 「HTTPSが必要になった瞬間」🔐⚡

最近のWeb機能って「HTTPSじゃないと動かない/制限される」が増えがちです。

* **Caddy**：Automatic HTTPS を強みにしていて、ローカル/内部名にもHTTPSの説明があります([Caddy Web Server][6])
* **Traefik**：できるけど、仕組み（証明書/リゾルバ）を理解する必要が出やすい
* **Nginx**：できるけど、基本は自分でちゃんと組む必要がある

## ③ 「脆弱性修正でアップデートが来る」🩹🚨

例としてNginxは 2026-02-04 リリースでCVE修正の言及があります([Nginx][1])
→ ローカルでも「入口」役は更新する癖を付けると安心😺✅

---

## 12-9. “おすすめ学習ルート”（この教材内での勝ち筋）🏁✨

この教材の流れ的には、こうすると気持ちよく進みます👇

1. **Caddyで入口1個を作る**🍞（成功体験が早い）
2. **増えたらTraefikへ**🤖（自動化の快感）
3. 本番がNginxなら、最後に **Nginxにも触れて整合**🧱

「最初からTraefikで全部やる」は、設計超入門者だと概念負荷で疲れやすいので、**先にCaddyで勝ってから**がオススメです😺✨

---

## 12-10. ミニ課題：あなたの現場に当てはめて選ぶ📝🎯

次のチェックをして、○が多いものが“あなた向け”です👇

## 🍞 Caddy向きチェック

* [ ] 設定を“短く・読みやすく”保ちたい📘
* [ ] ローカルHTTPSも早めに触れたい🔐
* [ ] まず2〜3サービス共存できればOK😺

## 🤖 Traefik向きチェック

* [ ] サービスが増えるたびに設定ファイル編集したくない😇
* [ ] Composeで完結させたい🧩
* [ ] 将来プロジェクトが増えても同じ入口で回したい🚪

## 🧱 Nginx向きチェック

* [ ] 本番がNginxで“同じ感じ”に寄せたい🏭
* [ ] 設定をガチガチに制御したい🔧
* [ ] 既存知識/既存資産がNginxにある📚

---

## 12-11. AIに聞く例（Copilot/Codex向けプロンプト）🤖💬

欲しいのは「生成」じゃなくて「事故らない型」です✅
そのまま投げられる文にしておきます👇

## 🍞 Caddy用

* 「Caddyfileで `app1.localhost` → `app1:3000`、`api.localhost` → `api:8787` に振り分けたい。最小構成のCaddyfileを書いて。ついでにアクセスログ出力も付けて」
* 「Caddyでパス `/api/*` だけ別コンテナへ流したい。よくある落とし穴も教えて」

## 🤖 Traefik用

* 「Docker ComposeでTraefik v3系を入口にして、Hostルールで `app1.localhost` と `api.localhost` を振り分けたい。`routers/services` の命名規則も含めて例を出して」([Traefik Labs Documentation][8])
* 「Traefikのラベルが増えて破綻しないように、命名ルール案とテンプレComposeを作って」

## 🧱 Nginx用

* 「Nginxで `server_name app1.localhost` を `app1:3000` にリバプロする最小confを書いて。`proxy_set_header` で最低限入れるべき項目も付けて」

---

## 12-12. この章のまとめ（覚えるのはこれだけ）🧠✨

* **Caddy**：最短で勝てる🍞（読みやすい・HTTPS強い）([Caddy Web Server][6])
* **Traefik**：Docker自動化の王🤖（ラベルで増える）([Traefik Labs Documentation][9])
* **Nginx**：本番寄せ・職人向け🧱（強いが硬い、最新も継続更新）([Nginx][1])

---

次の第13章（Caddyで最短成功）に入ると、ここで比較した内容が一気に“体感”になります🍞🚀
続けて第13章の本文も作るよ！

[1]: https://nginx.org/2026.html?utm_source=chatgpt.com "nginx news: 2026"
[2]: https://doc.traefik.io/traefik/deprecation/releases/?utm_source=chatgpt.com "Releases - Traefik"
[3]: https://docs.docker.com/reference/compose-file/?utm_source=chatgpt.com "Compose file reference"
[4]: https://endoflife.date/caddy?utm_source=chatgpt.com "Caddy"
[5]: https://docs.nginx.com/nginx/admin-guide/installing-nginx/installing-nginx-open-source/?utm_source=chatgpt.com "Installing NGINX Open Source"
[6]: https://caddyserver.com/docs/automatic-https?utm_source=chatgpt.com "Automatic HTTPS — Caddy Documentation"
[7]: https://caddyserver.com/docs/caddyfile/directives/reverse_proxy?utm_source=chatgpt.com "reverse_proxy (Caddyfile directive) — Caddy Documentation"
[8]: https://doc.traefik.io/traefik/routing/providers/docker/?utm_source=chatgpt.com "Traefik Docker Routing Documentation"
[9]: https://doc.traefik.io/traefik/providers/docker/?utm_source=chatgpt.com "Traefik Docker Documentation"
