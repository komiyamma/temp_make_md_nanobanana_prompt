# 第12章：Secretの扱い方（やりすぎない安全）🔐✨

この章は「**事故りやすい“秘密情報”を、ちゃんと扱えるようになる**」がゴールです💪
（パスワード・APIキー・トークンなど🗝️）

---

## 1) まず大事な現実チェック👀💥

![Secret is NOT Encrypted](./picture/docker_multi_orch_ts_study_012_01_secret_not_encrypted.png)

**Secretは“魔法の金庫”ではない**です😇➡️😈
Secretの値は **base64でエンコードされているだけ**で、**デフォルトでは暗号化されずに保存**されます。([Kubernetes][1])
なので「Secretに入れた＝安全」ではなく、**置き方・渡し方・権限**がセットで大事になります🔐

さらにクラスタ側の話として、KubernetesのAPIサーバはデフォルトだと etcd に **平文のまま**保存します（= at-rest暗号化なし）。([Kubernetes][2])
👉 本番では「暗号化 at rest を有効化する」方向が基本になります。([Kubernetes][1])

---

## 2) SecretとConfigMapの違いを1分で🧠⚡

![ConfigMap vs Secret](./picture/docker_multi_orch_ts_study_012_02_config_vs_secret.png)

* ConfigMap：**秘密じゃない設定**（例：ログレベル、機能フラグ）🧩
* Secret：**秘密の設定**（例：DBパスワード、APIキー）🔑

この切り分け自体が、設計の第一歩です🧹✨([Kubernetes][1])

---

## 3) “やりすぎない安全”のルール8️⃣📏🔐

![Secret Injection Methods](./picture/docker_multi_orch_ts_study_012_03_secret_injection.png)

1. **Gitに生のSecretを置かない**（base64でも同じ😇）([Kubernetes][1])
2. Secretを使っても、**アプリ側でログに出したら終わり**（絶対出さない！）🪦([Kubernetes][1])
3. Podに渡す方法は2つ：

   * **環境変数**（簡単）🌱
   * **ファイル（volume）**（更新に強い）📁
4. **環境変数で渡したSecretは、更新しても自動でアプリに反映されない**（Pod再起動が必要）🔁([Kubernetes][3])
5. **ファイルでマウントしたSecretは、更新が“遅れて”反映される**（eventually-consistent）⏳([Kubernetes][4])
6. **subPathマウントだと自動更新されない**（地雷⚠️）([Kubernetes][4])
7. 変更事故が怖いなら **immutable** を検討（更新不可にして守る）🧱([Kubernetes][1])
8. 本番は「誰が読めるか（権限）」と「保存の暗号化」をセットで🔐

   * at-rest暗号化の考え方は公式でも推奨です。([Kubernetes][1])

---

## 4) ハンズオン🎮：DBパスワードをSecretで注入する（env版→file版）

ここでは、既にあるNode/TS API（Deployment）に **DB_PASSWORD** を注入します🍔
※値はダミーでOKです🙆

---

## 4-1) Secretを作る（まずはCLIで）⌨️🔐

PowerShellで例（そのままOK）👇

```powershell
kubectl create namespace demo
kubectl -n demo create secret generic app-secrets --from-literal=DB_PASSWORD="demo-password-123"
```

作れたか確認👇（中身は見なくてOK！）👀

```powershell
kubectl -n demo get secret app-secrets
```

> ⚠️ `kubectl get secret app-secrets -o yaml` は、見ようと思えば見えます（base64なだけ）なので、むやみにやらないのが吉です🫠([Kubernetes][1])

---

## 4-2) Deploymentに“環境変数”として渡す🌱🔗

Deploymentの該当コンテナに、これを足します👇

```yaml
## (Deploymentの spec.template.spec.containers[0] あたり)
env:
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: app-secrets
        key: DB_PASSWORD
```

反映👇

```powershell
kubectl -n demo apply -f .\k8s\deployment.yaml
kubectl -n demo rollout status deploy/<あなたのDeployment名>
```

**値を表示せず**に「入ったかだけ」確認するのが安全です🧯
（例：長さだけ見る）

```powershell
kubectl -n demo exec deploy/<あなたのDeployment名> -- node -e "console.log((process.env.DB_PASSWORD||'').length)"
```

---

## 4-3) 次に“ファイル（volume）”で渡す📁🔐（こっちが更新に強い）

Deploymentに追記👇

```yaml
## containers[0]
volumeMounts:
  - name: secret-vol
    mountPath: /run/secrets
    readOnly: true

## spec.template.spec
volumes:
  - name: secret-vol
    secret:
      secretName: app-secrets
```

反映👇

```powershell
kubectl -n demo apply -f .\k8s\deployment.yaml
kubectl -n demo rollout status deploy/<あなたのDeployment名>
```

ファイルができたか確認👇（値は見ない！）

```powershell
kubectl -n demo exec deploy/<あなたのDeployment名> -- node -e "const fs=require('fs'); console.log(fs.existsSync('/run/secrets/DB_PASSWORD'))"
```

---

## 5) Secret更新（ローテーション）を体感する🔄🧪

## 5-1) Secretを更新する✍️

```powershell
kubectl -n demo create secret generic app-secrets --from-literal=DB_PASSWORD="rotated-456" --dry-run=client -o yaml | kubectl apply -f -
```

## 5-2) env版の挙動：**自動では変わらない**😵‍💫

![Env Secret Update](./picture/docker_multi_orch_ts_study_012_04_env_update_restart.png)

環境変数に入ったSecretは、**Podを再起動しないと反映されません**。([Kubernetes][3])
なので運用では、Secret更新したら **rollout restart** とセットにするのが分かりやすいです🔁

```powershell
kubectl -n demo rollout restart deploy/<あなたのDeployment名>
kubectl -n demo rollout status deploy/<あなたのDeployment名>
```

## 5-3) file版の挙動：**遅れて反映されうる**⏳

![Volume Secret Update](./picture/docker_multi_orch_ts_study_012_05_volume_update_sync.png)

volumeのSecretは、Secret更新後に **eventually-consistent** で中身が更新されます。([Kubernetes][4])
ただし **subPath** を使ってると自動更新されません⚠️([Kubernetes][4])

---

## 6) “本番っぽさ”を少しだけ足すなら🧯🏗️

## A) at-rest暗号化（クラスタ側の守り）🔐🗄️

APIデータ（Secret含む）を etcd に保存する時点で暗号化する仕組みがあります。([Kubernetes][2])
そして公式のベストプラクティスでも、**Secretはデフォルト未暗号化だから設定しよう**と書かれています。([Kubernetes][1])

さらに進むと、鍵管理にKMSを使う構成もあります。Kubernetes 1.35 では **KMS v2が推奨**で、KMS v1はdeprecatedかつデフォルト無効です。([Kubernetes][5])

## B) 外部の秘密管理（クラスタ外に置く）🏦🔑

「Secretをクラスタ外に置きたい」なら、外部ストアから取得してPodにマウントする方式があります。公式のベストプラクティスでも、**Secrets Store CSI Driver** を例に挙げています。([Kubernetes][1])
（例えば Amazon Web Services / Microsoft Azure / Google Cloud の秘密管理サービスと組み合わせる、みたいなイメージです☁️🔐）

---

## 7) よくある事故あるある（先に潰す）💣🧯

![Git Secret Trap](./picture/docker_multi_orch_ts_study_012_06_git_secret_trap.png)

* `console.log(process.env.DB_PASSWORD)` しちゃった📣 → ログから漏れる（最悪）([Kubernetes][1])
* Secretをbase64にしてGitに置いた📦 → **誰でも復元できる**（暗号化じゃない）([Kubernetes][1])
* subPathでマウントして「更新されない…」😇 → 仕様です⚠️([Kubernetes][4])
* envで渡して「更新されない…」😇 → Pod再起動が必要です🔁([Kubernetes][3])

---

## 8) ミニ課題🎯📝

1. Secretを **env版** と **file版** の両方で注入して、違いを説明してみてください🗣️
2. Secret更新後、env版は「再起動しないと反映されない」を自分の目で確認👀([Kubernetes][3])
3. file版は「遅れて反映される」を体感（更新直後に見にいって、ちょっと待って再確認）⏳([Kubernetes][4])

---

## 9) AIで楽するポイント🤖✨

* YAML貼って「**Secretが漏れる設計になってない？**（ログ/Repo/権限/更新）」をチェックさせる✅
* 「envとfile、どっちで渡すべき？」を **理由つき** で出させる🧠
* Secret更新時の運用手順（restart含む）を **チェックリスト化** させる📝

---

## まとめ🎉

* Secretは **base64であって暗号ではない**。まずこの現実が重要。([Kubernetes][1])
* 渡し方は **env（簡単）** と **file（更新に強い）**。ただし癖あり。([Kubernetes][3])
* “やりすぎない安全”は、**Gitに置かない / ログに出さない / 更新の挙動を理解する**の3点セットでOKです🔐✨

（次章のProbeに行く前に、ここを押さえると運用っぽさが一気に増しますよ〜😎☸️）

---

※ 本章の参照：Kubernetes 公式ドキュメント、セキュリティのベストプラクティス、at-rest暗号化/KMSの管理者向け手順、およびSecret更新時の挙動。([Kubernetes][1])

[1]: https://kubernetes.io/docs/concepts/security/secrets-good-practices/ "Good practices for Kubernetes Secrets | Kubernetes"
[2]: https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/ "Encrypting Confidential Data at Rest | Kubernetes"
[3]: https://kubernetes.io/docs/tasks/inject-data-application/distribute-credentials-secure/ "Distribute Credentials Securely Using Secrets | Kubernetes"
[4]: https://kubernetes.io/docs/concepts/configuration/secret/ "Secrets | Kubernetes"
[5]: https://kubernetes.io/docs/tasks/administer-cluster/kms-provider/ "Using a KMS provider for data encryption | Kubernetes"
