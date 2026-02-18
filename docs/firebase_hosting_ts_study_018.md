# 第18章：ロールアウト制御（勝手に出ないようにする）🧯

この章で身につくこと👇✨

* App Hostingの「ロールアウト（＝ビルド→デプロイの一連）」の見方がわかる👀
* **自動ロールアウトを止める／再開する**判断ができる⚖️（事故防止！）
* **手動ロールアウト**で「このコミットだけ出す」ができる🎯
* いざという時の**ロールバック（巻き戻し）**で即復旧できる🧯

---

## 1) まず “ロールアウト” って何？🤔🚀

App Hosting は、GitHub の **liveブランチ**に変更が入ると、アプリをビルドして新しいバージョンを出す「ロールアウト」を走らせられます。自動ロールアウトがONなら、基本は **push/merge → 自動でロールアウト開始** になります。([Firebase][1])

ロールアウトの進み具合は、**Firebase コンソール**でも見れるし、GitHub 側のチェック（Check）でも追えます。([Firebase][1])

---

## 2) “自動ロールアウトを止めたい” のはどんな時？🧠🛑

CI/CDは強いけど、運用してると「今日は勝手に出てほしくない😇」って日が来ます。よくあるのは👇

* **未完成の機能**が live に混ざりそう（mergeはしたいが公開は後日）🧩⏳
* **DB/外部APIの切り替え**など、出すタイミングを合わせたい🔁
* **大きめ改修**で、監視や手動チェックしてから出したい👀🛡️
* **イベント/キャンペーン**に合わせて「この時間に出す」したい🎉🕰️

このために、Firebase コンソールの **Deployment settings** から **自動ロールアウトを無効化/有効化**できます。([The Firebase Blog][2])

---

## 3) ざっくりおすすめ運用パターン🍱✨（初心者でも事故りにくい）

## パターンA：普段は自動ON、危ない日はOFF🔁🧯

* ふだん：自動ONでサクサク🚀
* 大事な日：自動OFFにして、**手動で出す**🎯

## パターンB：常に自動OFF、リリース担当が手動で出す🧑‍✈️🚢

* “勝手に出ない安心感”が強い💪
* 手動ロールアウト（後述）が前提になる

---

## 4) 手を動かす：自動ロールアウトを止める／再開する🛠️🧯

## 4-1. いまの設定を確認する👀

1. ブラウザで Firebase コンソールを開く🌐
2. App Hosting のバックエンドを選んで「View」👆
3. **Deployment settings**（または同等の設定画面）を探す🔎
4. **Automatic rollouts（自動ロールアウト）** がONかOFFか確認✅

> この画面で liveブランチやルートディレクトリも編集できることがあります。([The Firebase Blog][2])

## 4-2. 自動ロールアウトをOFFにする🛑

* トグルを **OFF** にするだけ（基本はこれ）🧯
* OFFにすると「liveブランチに変更が入っても自動で出ない」運用ができるようになります。([The Firebase Blog][2])

## 4-3. OFFにしたことを “安全に確認” する🧪

* liveブランチに小さなコミット（例：README変更）を入れる✍️
* コンソールの Rollouts 画面を見て、**勝手に新ロールアウトが始まらない**のを確認👀

  * ロールアウト一覧はバックエンドの **Rollouts** タブで見られます。([Firebase][1])

## 4-4. 自動ロールアウトをONに戻す▶️

* リリースが落ち着いたらトグルを **ON** に戻す🔁
* “戻し忘れ” が一番多い事故なので、後半のミニ課題で対策します🧯📝

---

## 5) 手を動かす：手動ロールアウトで「このコミットだけ出す」🎯🚀

自動OFFでも大丈夫。App Hosting は **手動でロールアウト作成**できます。([Firebase][1])

## 5-1. コンソールから手動ロールアウト（いちばん簡単）🖱️

1. コンソール → 対象バックエンド → ダッシュボードへ👣
2. **Create rollout** を押す➕([Firebase][1])
3. 出したい **ブランチ** を選ぶ🌿
4. 出したい **コミット** を選ぶ（最新 or コミットID指定）🧷([Firebase][1])
5. 作成したら Rollouts で進行を確認👀

> 「特定の日/時間にだけ出したい」みたいな運用にも、この手動方式がハマります。([Firebase][1])

## 5-2. CLIで手動ロールアウト（自動化したい人向け）⌨️🤖

ロールアウト作成コマンドがあります。([Firebase][1])

```bash
firebase apphosting:rollouts:create BACKEND_ID
```

ブランチを指定する例👇

```bash
firebase apphosting:rollouts:create BACKEND_ID --git_branch main
```

> ここは「CI/CDで“リリースボタン”だけ別で作りたい」時に便利です🎛️

---

## 6) ロールアウトの見張り方👀🧭（不安を減らすコツ）

Rollouts の各行には、だいたい👇が並びます：

* ロールアウトの状態（進行中/成功/失敗）🚦
* どの変更（GitHubコミット等）で起きたか🔖
* Cloud Build ジョブへのリンク（ログが見れる）🧾([Firebase][1])

まず見る順番はこれでOK👇

1. Rollouts で「どのロールアウトが失敗したか」特定👀
2. Cloud Build ログで「失敗したステップ」を見る🧾
3. 直したら、手動で再ロールアウト or 自動ONに戻して再試行🔁

---

## 7) 緊急ブレーキ：ロールバック（巻き戻し）🧯⏪

「出したら壊れた😱」はゼロにできないので、**戻し方**を先に持っておくのが大事です。

## 7-1. Instant rollback（ビルドし直さずに即戻す）⚡

App Hosting には、**過去のコンテナイメージをそのまま live に戻す** “instant rollback” があります。ビルドをスキップできるので復旧が速いです。([Firebase][1])

コンソールで以前のビルドを選んで「このビルドにロールバック」的な操作をします（表記はコンソール側のUIに従ってOK）。([The Firebase Blog][3])

## 7-2. “戻す前チェック” の超ミニ版✅

* いま障害が出てる範囲はどこ？（全員？一部？）👀
* 直すより「まず戻す」が早い？⚖️
* 戻したら、原因調査の時間が稼げる？🧠

---

## 8) AIでロールアウト事故をさらに減らす🤖🧯（Antigravity / Gemini CLI も活用）

## 8-1. Firebase MCP server を入れると “調べ物” が速くなる⚡

Firebase MCP server は、MCPクライアント（Antigravity、Gemini CLI、Firebase Studio など）と連携できます。([Firebase][4])
また、**Firebase用のプロンプトカタログ**も用意されていて、Gemini CLI の拡張機能を使うとスラッシュコマンド的に呼べることがあります。([Firebase][5])

## 8-2. Antigravity 側で MCP を追加する（超ざっくり）🧩

Antigravity のエージェント画面から MCP Servers を開いて Firebase をインストール、という流れが紹介されています。([The Firebase Blog][6])

## 8-3. Gemini CLI に Firebase 拡張を入れる（例）⌨️

公式ドキュメントでは、Firebase MCP を使う方法として Gemini CLI 拡張の導入が案内されています。([Firebase][4])

```bash
gemini extensions install https://github.com/gemini-cli-extensions/firebase/
```

## 8-4. AIに投げると強い “運用系プロンプト” 例📝🤖

* 「自動ロールアウトをOFFにしたい。戻し忘れ防止のチェックリスト作って」✅
* 「今回の変更内容（PR差分）から、リリース前に確認すべき項目を箇条書きで」🔎
* 「ロールアウト失敗ログを貼るので、原因候補と切り分け手順を3段階で」🧯

---

## ミニ課題✍️🎯（15〜25分）

1. 自動ロールアウトを **OFF** にする🛑
2. liveブランチに小さな変更を入れて、**勝手に出ない**のを確認👀
3. コンソールで **Create rollout** を使い、手動で最新コミットを出す🚀([Firebase][1])
4. Rollouts 画面で「Cloud Buildログへ行ける場所」を見つける🧾([Firebase][1])
5. **ONに戻す**（←ここ重要！）🔁

---

## チェック✅😆（できたら合格！）

* 「自動ロールアウトON/OFFの使い分け」を自分の言葉で説明できる🗣️
* “自動OFFでも手動で出せる” を理解してる🎯([The Firebase Blog][2])
* Rollouts から Cloud Buildログに辿り着ける🧾([Firebase][1])
* いざとなったらロールバックで戻せるイメージがある🧯⏪([Firebase][1])

---

次の章（第19章）で「Functions / Cloud Run をどこに置く？」に入る前に、ここまでの内容で **“勝手に出ない安心”** が手に入ると、運用が一気にラクになります😎🚢

[1]: https://firebase.google.com/docs/app-hosting/rollouts "Manage rollouts and releases  |  Firebase App Hosting"
[2]: https://firebase.blog/posts/2024/09/app-hosting-environments/ "Firebase App Hosting: Environments & deployment settings"
[3]: https://firebase.blog/posts/2025/03/apphosting-march-update/ "App Hosting updates: rollbacks, SDK auto-configuration, and more"
[4]: https://firebase.google.com/docs/ai-assistance/mcp-server "Firebase MCP server  |  Develop with AI assistance"
[5]: https://firebase.google.com/docs/ai-assistance/prompt-catalog?hl=ja "Firebase の AI プロンプト カタログ  |  Develop with AI assistance"
[6]: https://firebase.blog/posts/2025/11/firebase-mcp-and-antigravity/ "Antigravity and Firebase MCP accelerate app development"
