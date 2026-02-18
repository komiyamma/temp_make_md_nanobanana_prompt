# 第23章：TLS（HTTPS）と証明書自動化の入口🔒📜

この章は「**インターネット ↔ クラスタ**」という“境界”を安全にする話です🌐🛡️
やることはシンプルで、まずは **証明書を自動で作って更新できる状態** を作り、次に **Gateway/Ingress に食わせて HTTPS を通す** ところまで行きます🚀

---

## 1) この章のゴール🎯✨

学習後にこうなります👇

* ✅ HTTPS が何で、どこで終端（Terminate）するかを説明できる🔒
* ✅ **cert-manager** で証明書を発行して、Kubernetes の `Secret` に入る流れが追える📦
* ✅ `Certificate` が **期限更新（自動ローテ）** される仕組みの入口がわかる🔁
* ✅ （おまけ）Gateway API / Ingress に証明書を刺して HTTPS が通る✅🚪

---

## 2) 2026年の“地雷回避”ポイント⚠️🧠

* **Ingress NGINX は 2026年3月まで best-effort → 以後は修正も脆弱性対応も出ない**方針が公式に明記されています。([Kubernetes][1])
  → つまり「インターネットに面した入口」を“放置プロジェクト”で運用し続けるのは危険⚡
* その流れもあって **Gateway API v1.4.0 が GA** として発表済み（リリース日は 2025-10-06）。([Kubernetes][2])
* なお Gateway API の **`TLSRoute` は Experimental チャンネル**扱いです。([Kubernetes Gateway API][3])
  でも安心して👌：この章でまず使うのは **HTTPS Listener + HTTPRoute（Terminate）** の王道ルートです✨([Kubernetes Gateway API][3])

---

## 3) TLSって結局なに？（超ざっくり）🧸🔒

![Three pillars of TLS security](./picture/docker_multi_orch_ts_study_023_tls_functions.png)

HTTPS = **HTTP + TLS** です📦
TLSがやってくれるのは主に3つ👇

1. **暗号化**（盗み見されない）🕶️
2. **改ざん検知**（途中で書き換えられない）🛑
3. **なりすまし防止**（相手が本物か確認）🪪

そして「本物判定」に使うのが **証明書（certificate）**📜
証明書は **期限がある** ので、放置すると必ず死にます（体験談が多い世界）💀⏰

---

## 4) どこでHTTPSにする？（設計の超基本）🧠🚪

![TLS Termination Patterns](./picture/docker_multi_orch_ts_study_023_tls_termination_types.png)

よくあるパターンはこの2つ👇

## A. 境界でTLS終端（おすすめの入口）🛡️

* 入口（Gateway/Ingress/LB）で HTTPS を受けて **中はHTTP** で流す
* 証明書は入口に集約され、運用が楽になりがち✨

## B. PodまでE2EでTLS（上級の入口）🧬

* 入口→バックエンドまでずっとTLS（mTLS など）
* 強いけど設計と運用が一気に難しくなる🧠🔥

この章は **A（境界で終端）** を確実に成功させます✅

---

## 5) 証明書の自動化って何が嬉しいの？🤔🔁

![Manual vs Automated Renewal](./picture/docker_multi_orch_ts_study_023_renewal_comparison.png)

手動更新はこうなりがち👇

* 「更新日、忘れてた」→ 期限切れ💀
* 「更新したけど、反映し忘れ」→ 片系だけ死ぬ💥
* 「更新作業が怖い」→ 先送りの連鎖🌀

ここを **cert-manager** で自動化します🤖✨

---

## 6) cert-manager の“登場人物”🧩📦

![cert-manager Resource Relationships](./picture/docker_multi_orch_ts_study_023_cert_manager_actors.png)

cert-manager は Kubernetes 上で証明書を自動管理する定番OSSで、だいたいこう動きます👇

* `Issuer / ClusterIssuer`：**誰が発行する？**（自己署名、社内CA、ACME など）👮
* `Certificate`：**このドメインで証明書ほしい**📜
* `Secret`：出来上がった **鍵と証明書の置き場所**🔐
* `CertificateRequest`：裏で作られる「発行依頼」みたいなもの🧾

そして cert-manager は **数ヶ月おきに定期リリース**され、OSS版は **N+2 までのサポート方針**（LTSなし）です。([cert-manager][4])
執筆時点（2026-02-14）で GitHub の Latest 表示は **v1.19.3** です。([GitHub][5])

---

## ハンズオン①：cert-manager を入れて “証明書がSecretに入る” を体験✅🔒

ここがこの章のコア成功体験です🎉
（まずは Gateway/Ingress 関係なく **証明書発行の流れだけ** を掴みます🧠）

## Step 1. cert-manager をインストール📦

cert-manager公式ドキュメントは `kubectl apply` での導入を案内しています。([cert-manager][6])
例では v1.19.2 が書かれているので、**自分が使うバージョンに読み替え**ます（Latest は v1.19.3）。([cert-manager][6])

```bash
## vX.Y.Z は使うバージョンに合わせる（例：v1.19.3）
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/vX.Y.Z/cert-manager.yaml
```

インストール確認👇（pods が Running になればOK）([cert-manager][6])

```bash
kubectl get pods -n cert-manager
```

## つまづきやすい所💥

Webhook が立ち上がるまで少し時間がかかることがあります。公式は `cmctl check api` で確認できるよ、と案内しています。([cert-manager][6])

```bash
cmctl check api --wait=2m
```

---

## Step 2. “自己署名” Issuer と Certificate を作る🪄📜

公式ドキュメントにも「自己署名Issuer→Certificate」で動作確認する例があります。([cert-manager][6])
この章ではそれを少し読みやすくして、**`ClusterIssuer`**（全namespaceから使える）で作ります✅

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: tls-demo
---
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: demo-selfsigned
spec:
  selfSigned: {}
---
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: demo-cert
  namespace: tls-demo
spec:
  secretName: demo-cert-tls
  dnsNames:
    - demo.local
  issuerRef:
    name: demo-selfsigned
    kind: ClusterIssuer
```

適用👇

```bash
kubectl apply -f .\tls-demo.yaml
```

---

## Step 3. “できたか？”を観察する👀🔍

## 1) Certificate が Ready か？

```bash
kubectl describe certificate demo-cert -n tls-demo
```

`Ready=True` になっていれば勝ち🎉
公式の例でも `kubectl describe certificate` で状態確認しています。([cert-manager][6])

## 2) Secret ができたか？

```bash
kubectl get secret demo-cert-tls -n tls-demo
```

中身（鍵と証明書）が入ってるかをチラ見👇（表示は暗号化ではないので扱い注意⚠️）

```bash
kubectl get secret demo-cert-tls -n tls-demo -o yaml
```

---

## Step 4. うまくいかない時の“型”🧯🥋

よくある原因はこのへん👇

* 😵 `IssuerRef` の `kind` / `name` まちがい
* 😵 webhook がまだ準備できてない（`cmctl check api`）([cert-manager][6])
* 😵 `Certificate` はあるのに `Secret` ができない → `CertificateRequest` を見る

```bash
kubectl get certificaterequest -n tls-demo
kubectl describe certificaterequest -n tls-demo
```

**コツ**：迷ったら「describe → Events」を見る📌（だいたいヒントが書いてある）👀✨

---

## ハンズオン②：Gateway API で HTTPS を終端する（入口に刺す）🚪🔒

![Gateway API HTTPS Termination Flow](./picture/docker_multi_orch_ts_study_023_gateway_https_flow.png)

ここからは「第22章の Gateway API 入門」と合体です🤝✨
Gateway API のTLSガイドには、**HTTPS Listener は TLS Terminate で HTTPRoute を使う**と整理されています。([Kubernetes Gateway API][3])

## Step 1. GatewayClass 名を確認する🧭

```bash
kubectl get gatewayclass
```

表示された `NAME` をあとで使います（例：`my-gwclass`）📝

---

## Step 2. HTTPS Listener に証明書 Secret を指定する🔐

「証明書は `Secret` にある」ので、それを Gateway の `certificateRefs` で参照します📌

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: demo-gw
  namespace: tls-demo
spec:
  gatewayClassName: my-gwclass   # ←ここだけ自分の値に
  listeners:
    - name: https
      protocol: HTTPS
      port: 443
      tls:
        mode: Terminate
        certificateRefs:
          - kind: Secret
            name: demo-cert-tls
```

ポイント✨

* `TLSRoute` は Experimental 扱いですが、**HTTPS + HTTPRoute の終端**なら不要です👌([Kubernetes Gateway API][3])

---

## Step 3. HTTPRoute でアプリへ流す🚚🍔

（第7〜9章で作った Service を想定。ここでは `hello-api` という Service 名の例）

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: demo-route
  namespace: tls-demo
spec:
  parentRefs:
    - name: demo-gw
  hostnames:
    - "demo.local"
  rules:
    - backendRefs:
        - name: hello-api
          port: 3000
```

---

## Step 4. 動作確認（まずは “通った” を優先）✅✨

自己署名なのでブラウザは警告を出します（正常）⚠️
まずは `curl -k` で「HTTPSで応答が返る」だけ確認すると勝ちやすいです🏆

```bash
curl -k https://demo.local/
```

※ 入口のIP/ポート到達方法（LoadBalancer / port-forward 等）は Gateway 実装で差が出るので、まずは `kubectl get gateway -n tls-demo -o wide` と `kubectl describe gateway -n tls-demo demo-gw` で “どこに生えてるか” を確認すると迷子になりにくいです🧭👀

---

## 7) 本番の入口：自動更新の王道は ACME（例：Let’s Encrypt）🌍🔁

自己署名は学習用🧪
本番でよくあるのは ACME（無料の公開証明書）です。
cert-manager なら `ClusterIssuer` を **ACME 用**にして、`Certificate` は同じように書けます（更新も自動）🔁✨

ただし注意⚠️

* **ローカル環境**だと HTTP-01 が通らない（外から到達できない）ことが多い
* その場合は **DNS-01**（DNSで所有証明）を使うことが多い🧠

（ここは次の章以降で“外に出す/守る”話と一緒に強くなります💪）

---

## 8) AIに手伝わせると速いポイント🤖⚡（テンプレ付き）

* YAMLレビュー：

  * 「この `Certificate` と `Gateway` の接続、壊れてない？間違い候補を3つ出して」🧠
* エラー解析：

  * `kubectl describe certificate ...` を貼って
    「原因っぽい行を抜き出して、次に打つコマンドを優先度順に」🔍
* “境界”の言語化：

  * 「TLS終端を Gateway でやる設計のメリット・デメリットを、初心者向けに」🗣️

---

## 9) ミニ理解チェック✅📝

1. HTTPS は「暗号化」以外に何を守る？（2つ言えたらOK）🔒
2. cert-manager が最終的に証明書を置くのは何？📦
3. Gateway API で HTTPS を終端して HTTPRoute を使うとき、`TLSRoute` は必要？👀([Kubernetes Gateway API][3])
4. 期限切れが怖い理由を、運用視点で1行で言うと？💀⏰

---

次は「NetworkPolicy」なので、その前にここまでが固まると超ラクです🧱📡
もし今の手元の構成（Gateway実装の種類・`GatewayClass` 名・入口の到達方法）が分かれば、**あなたの構成に合わせて “動くマニフェスト一式” を第23章用に固定版として整えて**出せます🧩🔥

[1]: https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/ "Ingress NGINX Retirement: What You Need to Know | Kubernetes"
[2]: https://kubernetes.io/blog/2025/11/06/gateway-api-v1-4/ "Gateway API 1.4: New Features | Kubernetes"
[3]: https://gateway-api.sigs.k8s.io/guides/tls/ "TLS - Kubernetes Gateway API"
[4]: https://cert-manager.io/docs/releases/ "Supported Releases - cert-manager Documentation"
[5]: https://github.com/cert-manager/cert-manager/releases "Releases · cert-manager/cert-manager · GitHub"
[6]: https://cert-manager.io/docs/installation/kubectl/ "kubectl apply - cert-manager Documentation"
