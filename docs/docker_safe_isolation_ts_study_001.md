# 第01章：なぜ隔離が必要？「個人開発で起きがちな事故」あるある😇💣

個人開発って自由で楽しいんだけど、**「便利そうだから」で権限や共有を広げる**と、ミスった瞬間に被害が“ホストPCまで”飛びやすいんだよね…🥲
Dockerはまさにその代表で、**境界（ホスト／デーモン／コンテナ）を勘違い**すると事故がデカくなるタイプです。([Docker Documentation][1])

この章のゴールはシンプル👇
**「事故の種類」と「被害半径（どこまで燃えるか🔥）」を先に把握して、最低限の守りラインを決める**こと🛡️✨

---

## まず“被害半径”ってなに？🗺️💥

被害半径＝「やらかした時に、どこまで巻き添えになるか」だよ😇

ざっくり3段階で考えるとラク👇

* **小（コンテナだけ）**：コンテナが壊れても、ホストは無事🙂
* **中（ホストまで）**：PC内のファイル消えた／書き換えられた😱
* **大（クラウド・アカウントまで）**：GitHubトークン漏れ→リポジトリ改ざん、クラウド課金爆死💸💥

Dockerは、設定次第で**「コンテナだけ」→「ホストまで」へ一気に拡大**します。理由は「Dockerデーモンが強い権限を握る」から。([Docker Documentation][1])

---

## 個人開発の「事故あるある」7連発😇💣

「あるあるｗ」って笑ってる間に、いつか自分に来るやつです（怖）😇

---

## あるある1：`.env` をコミットして秘密が公開😇🔑➡️🌍

**よくある流れ**

1. 動いた！うれしい！🎉
2. `.env` にAPIキー書く
3. `git add .`
4. そのままPush…（終了）😇

**なにが起きる？**

* APIキー／DBパスワードが流出
* 料金爆発・データ抜かれ・改ざん…💸🧨

**今日の教訓**
✅ 秘密は「コード・ログ・Git」に置かない（置いたら漏れる前提）
（秘密の安全な渡し方は後半で *Compose secrets / Build secrets* をやるよ）([Docker Documentation][2])

---

## あるある2：ログやエラーに秘密を出してしまう🫣🧯

**例：一瞬だけデバッグのつもりが永遠に残るやつ**

* `console.log(process.env.API_KEY)`
* 例外スタックに接続文字列が出る

ログは「自分だけが見るもの」と思いがちだけど、

* CIログ
* エラートラッキング
* チーム共有
* 画面共有
  で普通に漏れる😇

**今日の教訓**
✅ 「秘密っぽいものは出力禁止」ルールを先に決める🛑

---

## あるある3：Dockerfileに秘密を書いて「イメージに残る」🏗️😇

**よくある罠**

* `ARG TOKEN=...`
* `ENV API_KEY=...`
* `RUN echo $TOKEN > ...`

これ、レイヤや履歴に残って、**イメージを配った瞬間アウト**になりがち😇
**ビルド時の秘密は BuildKit secrets を使って“レイヤに残さない”**が公式の方針。([Docker Documentation][3])

---

## あるある4：フォルダ共有（bind mount）しすぎてホストが燃える🔥💽

**よくある流れ**

* 便利だから `.:/app`
* さらに便利だから `C:\Users\あなた\:/host` みたいな発想へ…😇

もしコンテナ内のプロセスが暴走・侵害されたら、
**共有したフォルダは“そのまま被害範囲”**になるよ😱

**今日の教訓**
✅ 共有は「必要最小」
✅ できれば **読み取り専用** を基本にする（後でやるよ）📎🔒

---

## あるある5：`docker.sock` を渡して“ほぼホスト権限”🐙🔥

`/var/run/docker.sock` をコンテナに渡すと、
**コンテナがDockerデーモンを操作できる**＝結果的にホスト級の操作ができることがある😱
Dockerは「デーモンの攻撃面（attack surface）」として注意喚起してる。([Docker Documentation][1])

**今日の教訓**
✅ `docker.sock` は“最終手段カード”🃏⚠️（基本は封印）

---

## あるある6：権限を盛りすぎ（root/privileged）で事故が拡大💪😱

* rootで動かす
* `privileged: true`
* capを盛る

…このへんは、侵害された時の“伸びしろ”が大きい😇
Dockerは **rootless mode** で「デーモンもコンテナも非root寄り」に倒す考え方を提供してるよ。([Docker Documentation][4])

---

## あるある7：AI拡張に“見せたくない物”まで見せる🤖🧨

ここ、2026っぽい新しい事故ゾーン😇

AI拡張（Copilot系、Codex系、エージェント系）は、

* 開いてるファイル
* ワークスペース内のテキスト
* ターミナル履歴
  などを“文脈”として扱いがち。

**さらに怖いのが「間接プロンプト注入（indirect prompt injection）」**
＝READMEやIssueやWebページみたいな“外部の文章”に、
「秘密を貼れ」「このコマンドを実行しろ」みたいな指示を混ぜて、AIに誤爆させる攻撃ね😱([Microsoft][5])

実際、VS Code拡張まわりの調査で「トークン漏えい・機密ファイルアクセス・コマンド実行」につながり得る話が報告されていて、VS Code側には“同意”や“信頼境界”で守る設計があるよ。([Visual Studio Code][6])

そして最近だと、Varonis が **Microsoft Copilot** への“1クリックで始まる攻撃（Reprompt）”を紹介して話題になった（※既に修正済みとされる）という流れもあった。
「AIに渡した入力が、いつの間にか“命令”として働く」って現実味があるんだよね…😇([varonis.com][7])

**今日の教訓**
✅ AIに見せる範囲＝被害半径
✅ “信用できない文章”をAIに食わせる時は特に警戒
（この教材ではAIの被害半径も最小化していくよ）🧱🤖

---

## この教材で守る「最低ライン」🛡️✨（まずここだけ死守！）

細かい設定の前に、**判断基準（3原則）**を置いとくね👇

## ✅ 3原則：最小権限・最小共有・最小公開✂️🔐📤

* **最小権限**：できることを減らす（root/privilegedを避ける）
* **最小共有**：ホストのフォルダを渡しすぎない
* **最小公開**：ポート公開は入口だけにする

---

## ✅ 最低ライン（今日から運用ルール化）📌

**Secrets（秘密）**🔑

* 秘密は **Gitに置かない**（`.env` 直コミット禁止）
* 秘密は **ログに出さない**（例外メッセージも含む）
* ビルドに秘密が必要なら **BuildKit secrets**（後で実践）([Docker Documentation][3])
* 実行時に秘密を渡すなら **Compose secrets**（後で実践）([Docker Documentation][2])

**権限**👤

* “とりあえずroot”をやめる（後で `USER` を徹底）
* 可能なら **rootless** の考え方を知る（後で入門）([Docker Documentation][4])

**共有（マウント）**📦

* bind mountは最小に
* 可能なら読み取り専用を基本に（後で実践）

**危険カード封印**🗑️⚠️

* `privileged`
* `docker.sock` マウント
* 秘密の直書き
  → これらは「最終手段」扱い（後で代替を用意する）

**AI拡張**🤖

* ワークスペースは“信頼できるか？”をまず判断
* **Workspace Trust（信頼/制限モード）**を味方につける([Visual Studio Code][8])
* AIに貼るのは“必要最小のコード断片”だけ（秘密は貼らない）
* 外部の文章（README/Issue/Web）由来の指示は疑う（プロンプト注入対策の基本）([cheatsheetseries.owasp.org][9])

※このへんの“AIの安全”は OWASP もチェックリストを出してる（後半で噛み砕くよ）([cheatsheetseries.owasp.org][9])

---

## 2分でできる「ミニ監査」🕔🔍（演習）

今の自分のプロジェクトに、地雷がないか確認しよ💣👀
VS Codeのターミナル（PowerShell）でOK👍

## ① 秘密っぽい文字列が入ってない？🔑

```powershell
## よくあるキーワードをざっくり探索（必要に応じて追加してOK）
Select-String -Path .\* -Recurse -ErrorAction SilentlyContinue `
  -Pattern "API_KEY|SECRET|TOKEN|PASSWORD|PRIVATE_KEY|BEGIN\s+PRIVATE\s+KEY"
```

## ② `.env` がGitに乗ってない？😇

```powershell
git status
```

（`.env` が “Changes to be committed” に見えたら、ほぼ事故寸前😇）

## ③ Compose / Dockerfile に危険カードない？🗑️⚠️

* `docker-compose.yml` / `compose.yml` を開いて

  * `privileged:` がないか
  * `docker.sock` をマウントしてないか
  * ホストの広すぎるフォルダをマウントしてないか
  * `ports:` が必要以上に開いてないか
    を目視チェック👀

## ④ AI拡張を使う時の“自分ルール”を1行で決める🤖🧱

例👇

* 「AIに貼るのは **該当ファイルとエラーだけ**、`.env` と設定は貼らない」
* 「知らないリポジトリは **Restricted Mode** で開く」([Visual Studio Code][8])

---

## よくある勘違い（ここで事故る）😇🧠

* 「ローカルだから大丈夫」→ ローカルが一番燃える（全部ある）🔥
* 「環境変数なら安全」→ ログに出したら終わり🫣
* 「コンテナだから隔離されてる」→ マウントと権限次第で“直結”💽
* 「AIは賢いから危ない指示は無視する」→ “指示とデータの境界”が曖昧なのが本質リスク（だから設計で守る）([Microsoft][5])

---

## まとめ🎯✨

この章で覚えてほしいのはこれだけ👇

* **被害半径は「権限・共有・公開・AIの見える範囲」で決まる**🗺️
* まずは **最低ライン（ルール）** を決めて、迷ったら「削る」✂️
* 次章から、この最低ラインを“設定とテンプレ”に落としていく📦✨

---

次（第2章）は、Dockerの「境界線」を図でスッキリさせて、どこを守ればいいか迷子にならない地図を作るよ🧭😄

* [Windows Central](https://www.windowscentral.com/artificial-intelligence/microsoft-copilot/copilot-ai-reprompt-exploit-detailed-2026?utm_source=chatgpt.com)
* [tomsguide.com](https://www.tomsguide.com/computing/online-security/this-microsoft-copilot-vulnerability-only-requires-a-single-click-and-your-personal-data-could-be-stolen?utm_source=chatgpt.com)

[1]: https://docs.docker.com/engine/security/?utm_source=chatgpt.com "Docker Engine security"
[2]: https://docs.docker.com/compose/how-tos/use-secrets/?utm_source=chatgpt.com "Secrets in Compose"
[3]: https://docs.docker.com/build/building/secrets/?utm_source=chatgpt.com "Build secrets"
[4]: https://docs.docker.com/engine/security/rootless/?utm_source=chatgpt.com "Rootless mode"
[5]: https://www.microsoft.com/en-us/msrc/blog/2025/07/how-microsoft-defends-against-indirect-prompt-injection-attacks?utm_source=chatgpt.com "how-microsoft-defends-against-indirect-prompt-injection- ..."
[6]: https://code.visualstudio.com/docs/copilot/security?utm_source=chatgpt.com "Security"
[7]: https://www.varonis.com/blog/reprompt?utm_source=chatgpt.com "Reprompt: The Single-Click Microsoft Copilot Attack that ..."
[8]: https://code.visualstudio.com/docs/editing/workspaces/workspace-trust?utm_source=chatgpt.com "Workspace Trust"
[9]: https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html?utm_source=chatgpt.com "LLM Prompt Injection Prevention Cheat Sheet"
