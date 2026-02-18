# 第22章：Gateway API入門（次世代の入口）🚪✨

この章が終わると、こんなことができるようになります 💪😺

* **Gateway API の登場人物（GatewayClass / Gateway / Route）**をスッと説明できる 🧠
* **HTTPRouteで「外→中」をルーティング**できる（Host / Pathで振り分け）🌐➡️📦
* 「動かない😇」ときに **status/conditions を見て原因に当たりを付ける** 🔍

---

## 1) なんで今 “Gateway API” なの？🧭⚡

![Ingress vs Gateway API Structure](./picture/docker_multi_orch_ts_study_022_ingress_vs_gateway_api.png)

前の章（Ingressの話）で触れた通り、**Ingress NGINX は 2026年3月までベストエフォート保守 → 以後はリリース/修正/脆弱性対応なし**、という公式方針が出ています。つまり「今動いてるからOK」ではなく、**中長期の入口として別ルートを持っておく**のが現実的です。([Kubernetes][1])

そしてその“別ルート”の本命が、**Gateway API（v1.4.0がGAとして発表）**です。([Kubernetes][2])

ポイントはこれ👇

* Gateway API は **Kubernetes本体に最初から全部入ってる機能**じゃなくて、**CRD（追加API）＋実装（コントローラ）**で動きます（＝実装を選ぶ必要がある）([Kubernetes][3])
* その実装（対応コントローラ）は複数あって、対応状況は公式の一覧で追えます 📌([Kubernetes Gateway API][4])

---

## 2) Gateway APIの“登場人物”を人に例えると…👥🎭

![Persona-based Resource Management](./picture/docker_multi_orch_ts_study_022_role_separation.png)

Gateway APIは「役割分担」がキモです 🧠✨
Ingress は1枚の設定に色々詰め込みがちですが、Gateway API は分けます。

## ✅ GatewayClass（プラットフォーム担当）🏗️

* 「このクラスタでは、このゲートウェイ実装を使うよ」っていう **クラス宣言**
* 実体としては「どのコントローラが面倒を見るか」を決める感じ

## ✅ Gateway（入口担当）🚪

* 「どこで受ける？」（ポート、プロトコル、TLSなど）を持つ
* “建物の玄関”みたいなもの 🏢🚪
* **Listener**（受け口）を複数持てるのが強い 💪

## ✅ Route（アプリ担当）🧭

* 「どこへ流す？」（Host/Path/ヘッダ等でマッチ → Serviceへ転送）
* HTTPなら **HTTPRoute** が主役 🌟([Kubernetes Gateway API][5])

## ✅ 重要：実装（コントローラ）がいないと何も起きない🤖❌

![Gateway API Architecture](./picture/docker_multi_orch_ts_study_022_components_diagram.png)

Gateway APIのYAMLを書くだけではルーティングされません。
**“そのAPIを解釈してプロキシやLBを動かす実装”**が必要です。([Kubernetes][3])

---

## 3) まず動かす！最短ハンズオン（Envoy Gatewayで体験）🏃💨🧪

![Envoy Gateway Quickstart Flow](./picture/docker_multi_orch_ts_study_022_envoy_gateway_setup.png)

ここでは例として **Envoy Gateway の公式Quickstart**を使います（手順がまとまってて迷子になりにくい✨）。([Envoy Gateway][6])

> ねらい：**GatewayClass / Gateway / HTTPRoute が一気に作られて動く**のを目で見る👀

## 3-1) インストール（CRD + コントローラ）📦

（公式Quickstartの例）

```bash
helm install eg oci://docker.io/envoyproxy/gateway-helm --version v1.7.0 -n envoy-gateway-system --create-namespace
kubectl wait --timeout=5m -n envoy-gateway-system deployment/envoy-gateway --for=condition=Available
```

これで **Gateway API CRD と Envoy Gateway** が入ります。([Envoy Gateway][6])

## 3-2) サンプル（GatewayClass/Gateway/HTTPRoute/アプリ）を一括で入れる🎁

```bash
kubectl apply -f https://github.com/envoyproxy/gateway/releases/download/v1.7.0/quickstart.yaml -n default
```

Quickstart.yaml が、入口〜ルーティング〜サンプルアプリまで一気に作ります。([Envoy Gateway][6])

## 3-3) 動作確認（LoadBalancer無しでもOK）🧰

ローカル環境だと LoadBalancer が無いことが多いので、公式は **port-forward** 手順も用意しています。([Envoy Gateway][6])

```bash
export ENVOY_SERVICE=$(kubectl get svc -n envoy-gateway-system --selector=gateway.envoyproxy.io/owning-gateway-namespace=default,gateway.envoyproxy.io/owning-gateway-name=eg -o jsonpath='{.items[0].metadata.name}')
kubectl -n envoy-gateway-system port-forward service/${ENVOY_SERVICE} 8888:80
```

別ターミナルで叩く👇

```bash
curl --verbose --header "Host: www.example.com" http://localhost:8888/get
```

Hostヘッダ付きで通れば成功！🎉([Envoy Gateway][6])

---

## 4) “何が作られたか”を観察して理解する👀🔍

ここが超大事！「動いた！」だけで終わらせないやつです😺

## 4-1) Gateway APIのリソースを見る🗂️

```bash
kubectl get gatewayclass
kubectl get gateway
kubectl get httproute
```

## 4-2) status/conditions を見る（詰まったらココ）🧯

![Debugging via Status](./picture/docker_multi_orch_ts_study_022_status_debugging.png)

```bash
kubectl describe gateway eg
kubectl describe httproute <route名>
```

Gateway APIは **status.conditions に理由が出る**ことが多いです。
「見て当てる」んじゃなくて「書いてあることを読む」方向に寄せると強い💪✨

---

## 5) YAMLの読み方：最低限ここだけ押さえる📄✅

## 5-1) Gatewayは「入口の定義」🚪

ざっくり言うと👇

* `gatewayClassName`：どの実装（クラス）に面倒見てもらう？
* `listeners[]`：ポート/プロトコル/ホスト名/TLS…入口の条件

（Gatewayの考え方は公式の説明でも “GatewayClassに紐づく／Listenersを持つ” が軸です）([Kubernetes Gateway API][7])

## 5-2) HTTPRouteは「振り分けルール」🧭

ざっくり👇

* `parentRefs`：どのGateway（入口）にぶら下がる？
* `hostnames`：このHostだけ通す（任意）
* `rules.matches`：PathやHeaderなど
* `backendRefs`：転送先のService（＋ポート）

（HTTPRouteの定義：Gateway listener → Serviceへルーティング）([Kubernetes Gateway API][5])

---

## 6) ありがち事故あるある😇➡️😺

![Common Gateway API Pitfalls](./picture/docker_multi_orch_ts_study_022_common_accidents.png)

## 事故1：Gateway/HTTPRoute作ったのに何も起きない🙃

✅ だいたいこれ

* **実装（コントローラ）が入ってない**
* **CRDだけ入ってる**（＝解釈する人がいない）

Gateway APIは「CRD＋実装」がセットです。([Kubernetes][3])

## 事故2：Gatewayが “Address無し” で止まってる🫠

ローカルだと **LoadBalancerが無い**ので起きがち。
公式Quickstartでも「LBが無いなら入れるのを推奨（例：MetalLB）」と書いてあります。([Envoy Gateway][6])
（今回は port-forward で回避できたのでOK👌）

## 事故3：HTTPRouteがGatewayにアタッチされない😵

✅ まず見るところ

* `kubectl describe httproute ...` の conditions
* `parentRefs` が正しいか
* hostnames/Listener条件が噛み合ってるか（Host指定してるのに合ってない等）

---

## 7) 設計超入門のコツ：まずは“分業の線引き”だけ決める✍️🧠

![Team-based Responsibility](./picture/docker_multi_orch_ts_study_022_design_separation.png)

Gateway APIの美味しさはこれ👇

* **Gateway（入口）はプラットフォーム側が管理**
* **Route（振り分け）はアプリ側が管理**

これができると、チームが増えても「入口いじって壊す😇」が減ります。

さらに実装の対応状況はバラつくので、採用するときは

* 公式の **Implementations一覧** と
* できれば **conformance情報**
  を見て決めるのが安全です。([Kubernetes Gateway API][4])

---

## 8) ミニ演習（この章の宿題）📚🔥

1. **Pathで2分岐**してみよう

* `/api` → あなたのNode/TS API
* `/` → 静的Web（ダミーでもOK）

2. **Hostで環境を分ける**（できたら）

* `dev.example.com` → dev
* `stg.example.com` → stg

3. 詰まったら、**describe結果をAIに貼って「原因候補3つ＋確認コマンド」**を出させる🤖🔍

* でも最後は **conditionsを自分の目で読む**（ここが伸びる✨）

---

## おさらい🧾✨

* Gateway API は **CRD＋実装**で動く（YAMLだけでは動かない）([Kubernetes][3])
* 役割分担は **GatewayClass（運用）／Gateway（入口）／Route（振り分け）**
* つまずいたら **status/conditions を見る**のが最短ルート🧭

次の章（TLS/証明書）で、Gateway API がさらに“本番っぽく”なっていきます 🔒📜🚀

[1]: https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/?utm_source=chatgpt.com "Ingress NGINX Retirement: What You Need to Know"
[2]: https://kubernetes.io/blog/2025/11/06/gateway-api-v1-4/?utm_source=chatgpt.com "Gateway API 1.4: New Features"
[3]: https://kubernetes.io/docs/concepts/services-networking/gateway/?utm_source=chatgpt.com "Gateway API"
[4]: https://gateway-api.sigs.k8s.io/implementations/?utm_source=chatgpt.com "Implementations"
[5]: https://gateway-api.sigs.k8s.io/api-types/httproute/?utm_source=chatgpt.com "HTTPRoute"
[6]: https://gateway.envoyproxy.io/docs/tasks/quickstart/ "Quickstart | Envoy Gateway"
[7]: https://gateway-api.sigs.k8s.io/?utm_source=chatgpt.com "Kubernetes Gateway API: Introduction"
