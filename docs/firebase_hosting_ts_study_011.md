# 第11章：HTTPSとカスタムドメイン（“ちゃんとしたサイト感”）🔒

この章は「**公開URLが“自分のドメイン”になる**」＋「**HTTPS（SSL）で安全に見れる**」を完成させます✨
ちなみに **Firebase Hosting はカスタムドメインごとにSSL証明書を自動で用意して、グローバルCDNで配信**してくれます。([Firebase][1])

---

## 1) まず “何が嬉しい？” を腹落ちさせよう 😆🎯

![Custom Domain Value](./picture/firebase_hosting_ts_study_011_01_domain_benefits.png)

カスタムドメイン＋HTTPSが入ると、急に“プロっぽさ”が出ます👇

* **信頼感アップ**：URLが `https://あなたのドメイン` になる🔒✨
* **共有しやすい**：覚えやすい、SNSで貼っても怪しく見えにくい📣
* **運用しやすい**：`example.com` と `www.example.com` の統一（後で効く）🔁
* **Hosting側で証明書が自動更新**：更新忘れ事故が起きにくい🧯
  （Firebase Hosting は必要に応じてSSL証明書を自動で再発行します）([Firebase][1])

---

## 2) ここだけ用語を押さえる🧠📌（超重要）

![DNS Terminology](./picture/firebase_hosting_ts_study_011_02_dns_concepts.png)

* **apex（ルート）ドメイン**：`example.com` のこと（いわゆる“裸ドメイン”）
* **サブドメイン**：`www.example.com` や `app.example.com`
* **DNS**：ドメイン名を「どこのサーバーへ行くか」に変換する住所録📮
* **レコード種類（ざっくり）**

  * **TXT**：所有確認用（「このドメインは私のです！」）🪪
  * **A / AAAA**：行き先のIP（A=IPv4、AAAA=IPv6）🧭
  * **CAA**：証明書を作っていい発行元を制限するルール（きついと詰む）🚧

---

## 3) 作業の全体像（これだけ覚えればOK）🗺️✨

![Quick Setup Steps](./picture/firebase_hosting_ts_study_011_03_setup_flow.png)

やることは基本この流れです👇

1. コンソールでドメイン追加 ➜ **必要なDNSレコードが表示される**
2. ドメイン会社（DNS設定画面）に **TXT（所有確認）** を入れる🪪
3. **A/AAAA（行き先）** を入れる🧭
4. しばらく待つ（DNS反映＋証明書発行）⏳
5. `https://` で見れるようになる🎉

Firebase側のウィザードは **Quick Setup**（簡単）と **Advanced Setup**（無停止移行向け）があります。([Firebase][1])

---

## 4) 手を動かす：Quick Setup（いちばん簡単ルート）🚀🧩

> 新規ドメイン／止めてもいいタイミングで切り替えるなら、まずこれでOK🙆‍♂️

## Step 1：コンソールでカスタムドメイン追加🖱️

![URL Unification](./picture/firebase_hosting_ts_study_011_04_redirect_strategy.png)

1. **Hosting** の画面へ
2. **Add custom domain** を押す
3. 追加したいドメインを入力（例：`example.com` または `www.example.com`）
4. （任意）**`example.com` と `www.example.com` を片方へリダイレクト**するチェックを入れる🔁

   * これ、後で地味に効きます（URLが統一されて気持ちいい）
   * ウィザード上でもこのリダイレクトが案内されています。([Firebase][1])

## Step 2：TXT（所有確認）をDNSへ入れる🪪

![DNS TXT Record](./picture/firebase_hosting_ts_study_011_08_dns_txt.png)


ウィザードに **TXTレコード** が出るので、DNS設定にそのまま入れます。
apex（ルート）ドメインの所有確認は、**サブドメイン全部の所有確認にもなる**扱いです。([Firebase][1])

* DNSの「Host（Name）」欄は会社によって書き方が違います😵
  `@` / 空欄 / `example.com` などがあり得るので、ウィザード＋ドメイン会社の表記に合わせます。([Firebase][1])

> 反映に **最大24時間** かかることがあるので焦らないでOKです⏳（数時間で終わることも多い）([Firebase][1])

## Step 3：A/AAAA（行き先）をDNSへ入れる🧭

![DNS A Record](./picture/firebase_hosting_ts_study_011_09_dns_a.png)


次にウィザードに出る **A/AAAA** を入れます。
よく見る例だと **Aレコードが `199.36.158.100`** になっているケースが多いです（プロバイダ別の例として公式にも載っています）。([Firebase][1])

⚠️超大事：**他社ホスティングに向いた A / CNAME / AAAA が残ってると、証明書が発行できない**ことがあります。
ウィザードでも「他社向きのA/CNAMEやAAAAがあるとSSLをプロビジョニングできないので消してね」と強く注意されています。([Firebase][1])

## Step 4：証明書が発行されるまで待つ🔒⏳

![DNS Propagation](./picture/firebase_hosting_ts_study_011_05_propagation_wait.png)

DNSがFirebaseを向いたあと、**SSL証明書の発行は最大24時間**かかることがあります。([Firebase][1])
途中でブラウザに「証明書が変」みたいに出ても、発行中は一時的にそう見えることがあるよ、という注意も公式にあります。([Firebase][1])

---

## 5) 手を動かす：Advanced Setup（“止めずに移行したい”人向け）🧯🧩

![Zero Downtime Migration](./picture/firebase_hosting_ts_study_011_06_advanced_setup.png)

> いま他社で運用中で、できれば**無停止で切り替えたい**ならこっち⚙️

Advanced Setupはざっくりこう👇

## フェーズ1：Prepare domain（先に“権利と証明書”を固める）🪪🔒

* **Ownership（TXT）**：`hosting-site=[site_id]` 形式のTXTを入れる（所有＆証明書更新の許可）([Firebase][1])
* **CAA（必要なときだけ）**：既存CAAが厳しすぎると、証明書が作れないので追加が案内されることがあります。([Firebase][1])
* **ACME challenge**：DNSまたはHTTPでチャレンジを解いて証明書を発行（ウィザードが出す）([Firebase][1])

## フェーズ2：Direct to Hosting（最後に行き先だけ切り替える）🧭

* 仕上げに **A/AAAA** をFirebaseへ向ける（ここでトラフィックが切り替わる）([Firebase][1])

Advanced Setupは「証明書まわりの詰まり」を先に潰せるので、移行が気持ちラクになります😎

---

## 6) Windowsで“DNS反映した？”を確認する🔎🪟

## (A) コマンドで見る（手元チェック）🧪

例：TXTが見えるか確認（ドメインは自分のに置き換え）👇

```bash
nslookup -type=TXT example.com
```

Aレコード確認👇

```bash
nslookup -type=A example.com
```

（PowerShellでも `Resolve-DnsName` が使えますが、まずは `nslookup` でOK🙆‍♂️）

## (B) 公式が案内してるオンラインDigで見る🌐

公式は **Google Admin Toolbox の Dig** でDNSが正しく更新されてるか確認できるよ、と案内しています。([Firebase][1])
「手元のDNSキャッシュが邪魔してそう…」って時にも便利です🧹✨

---

## 7) ありがちトラブル集（ここが8割）🧯😵

![Domain Troubleshooting](./picture/firebase_hosting_ts_study_011_07_troubleshooting.png)

## 症状1：いつまでも “Needs setup” 🛠️

だいたいこれ👇

* DNSの **Host欄** が違う（`@` なのに空欄、など）
* **Aレコードが他社向きのまま**
* 反映待ちが足りない（数時間〜最大24時間）([Firebase][1])

## 症状2：“Pending / 証明書が出ない” 🔒🚧

公式にある典型原因👇

* **CAAが厳しすぎる**（`letsencrypt.org` と `pki.goog` を許可してね、という案内）([Firebase][1])
* Advanced Setupの **チャレンジトークンが無効**（再生成が必要になることがある）([Firebase][1])

## 症状3：サブドメイン作りすぎ🍱💥

* 1つのapexに対して、**サブドメインは20個まで**が上限（証明書発行の制限）([Firebase][1])
  「テスト用に大量に作ってた！」はわりとあるある😇

## 症状4：カスタムドメインが “他のHostingサイトに繋がってる” 🔁

* **1つのカスタムドメインは1つのHostingサイトにしか接続できない**ルールです。([Firebase][1])

---

## 8) AIで作業を爆速にする🤖⚡（Antigravity / Gemini CLI 推し）

DNS作業って「言葉が難しい＋画面がプロバイダごとに違う」ので、AIの出番です🔥

## (A) Firebase MCP server をAIツールに繋ぐ🧩

公式いわく、Firebase MCP serverは **Antigravity や Gemini CLI を含む、MCPクライアント対応ツールから使えます。([Firebase][2])

特にGemini CLIは、Firebase拡張を入れるのが推奨ルートとして明記されています👇([Firebase][2])

```bash
gemini extensions install https://github.com/gemini-cli-extensions/firebase/
```

> これで「Firebaseの文脈（コンテキスト）つき」で相談しやすくなる、という説明もあります。([Firebase][2])

## (B) AIに投げると強い“質問テンプレ”📨✨

DNSや証明書は、こう聞くと事故りにくいです👇

* 「Firebase Hostingのカスタムドメイン設定で、**TXT/A/AAAA/CAA** をどう解釈して、どの順で入れるべき？図で」🗺️
* 「ドメイン会社のDNS画面で **Host欄が @ / 空欄 / ドメイン名** のどれになるか、一般的な見分け方は？」🔎
* 「“Pending”のときに疑う順番をチェックリストにして」✅
* 「`example.com` と `www.example.com` を統一するなら、どっちを正にするのが無難？」🔁

## (C) AIの注意点（大事）⚠️🧠

コンソール内のAIについても「それっぽいけど間違うことがあるから検証してね」「PII入れないでね」みたいな注意がちゃんと書かれてます。([Firebase][3])
つまり **“AIは加速装置、最終決定は公式ウィザードの表示”** が安全ルールです😎

---

## 9) ミニ課題（15分）✍️⏱️

## ミニ課題A：URLの“正”を決める🔁

![Assignment](./picture/firebase_hosting_ts_study_011_10_assignment.png)


次のどっちかに決めて、理由を一言で書く👇

* **`example.com` を正**（`www` をリダイレクト）
* **`www.example.com` を正**（裸ドメインをリダイレクト）

そして、ウィザードの「リダイレクト設定」に反映する🛠️([Firebase][1])

## ミニ課題B：証拠を残す📸🗂️

* DNS設定画面（TXTとA/AAAAが見えるところ）をスクショ📸
* Hostingのカスタムドメイン状態（Connectedになるまで）をスクショ📸
* `https://` でアクセスできた画面をスクショ📸

---

## 10) 理解度チェック（○×でOK）✅😆

1. TXTは「所有確認＋証明書更新の許可」に関係する（○/×）([Firebase][1])
2. 他社向きのA/CNAME/AAAAが残っていても、証明書は普通に発行される（○/×）([Firebase][1])
3. 証明書発行は最大24時間かかることがある（○/×）([Firebase][1])
4. 1つのカスタムドメインは複数のHostingサイトに同時接続できる（○/×）([Firebase][1])
5. サブドメインを作りすぎると証明書で詰むことがある（○/×）([Firebase][1])

---

## おまけ：App Hostingでも同じ発想でドメインを繋げる🧩🚀

もし将来 Firebase App Hosting 側でSSR/フルスタックを出す場合も、App Hostingの画面から **Add custom domain** で同様に設定できます。([Firebase][4])

---

次の第12章（キャッシュ基礎⚡🧠）に進むと、「速いのに壊れない」公開サイトに一気に近づきます🚀
その前に、今の第11章の状態で **どこまで進んだか（例：TXT入れた／A入れた／Pendingのまま等）** が分かれば、トラブル分岐だけピンポイントで一緒に潰せますよ🧯✨

[1]: https://firebase.google.com/docs/hosting/custom-domain "Connect a custom domain  |  Firebase Hosting"
[2]: https://firebase.google.com/docs/ai-assistance/mcp-server "Firebase MCP server  |  Develop with AI assistance"
[3]: https://firebase.google.com/docs/ai-assistance/gemini-in-firebase/try-gemini?utm_source=chatgpt.com "Try Gemini in the Firebase console"
[4]: https://firebase.google.com/docs/app-hosting/custom-domain?utm_source=chatgpt.com "Connect a custom domain - App Hosting - Firebase"
