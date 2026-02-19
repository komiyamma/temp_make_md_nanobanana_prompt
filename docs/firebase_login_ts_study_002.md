# 第02章：Console設定：Authプロバイダ有効化＆最低限の安全設定🧯

この章は「**Firebase Consoleで“認証が動く土台”を作る回**」だよ🙂
コードを書く前に、ここがズレてると後で確実に詰まるので、サクッと固めよう💪✨

---

## この章でできるようになること🎯

* ✅ **メール/パスワード**ログインを使えるようにする🔑
* ✅ **Googleログイン**を使えるようにする🌈
* ✅ ローカル開発で出がちな **unauthorized-domain系**の事故を防ぐ🧨
* ✅ ついでに“最低限の安全設定”を入れておく🛡️

---

## 1) 読む（3分）📚👀

* Email/Password を有効化して使う流れ（公式）([Firebase][1])
* Firebase Authの全体像（必要なときに戻ってこれる）([Firebase][2])
* AI連携（Firebase AI LogicでGemini/Imagenを扱う入口）([Firebase][3])

---

## 2) 手を動かす（15分）🛠️🔥

![Console Overview](./picture/firebase_login_ts_study_002_01_console_overview.png)

## Step A：Authentication を開く🧭

1. Firebase Consoleで対象プロジェクトを開く
2. 左メニューで **Build → Authentication** を開く
3. まだ初回なら「Get started」的なボタンが出るので進む🏃‍♂️💨

（ここからは「Sign-in method」周りを触るよ🙂）

---

![Email Toggle](./picture/firebase_login_ts_study_002_02_email_switch.png)

## Step B：メール/パスワードを有効化する🔑📧

1. **Sign-in method** タブへ
2. **Email/Password** を選ぶ
3. **Enable** をON → **Save** 💾

公式でもこの流れが基本になってるよ([Firebase][1])

---

![Google Provider Setup](./picture/firebase_login_ts_study_002_03_google_setup.png)

## Step C：Googleログインを有効化する🌈

1. 同じく **Sign-in method** で **Google** を選ぶ
2. **Enable** をON
3. 「サポート用メール（Project support email）」を選べるなら、自分の連絡用メールを設定📮
4. **Save** 💾

これで「Googleでログインする権利」がプロジェクトに生える🌱✨

---

![Authorized Domains](./picture/firebase_login_ts_study_002_04_domain_list.png)

## Step D：Authorized domains（承認済みドメイン）を設定する🌍✅

Googleログイン（Popup/Redirect）でよく出る地雷がこれ💣
**ドメインが未承認だと `auth/unauthorized-domain` 系で止まる**やつ。

1. **Authentication → Settings**（歯車っぽい所）へ
2. **Authorized domains** を探す
3. ローカル開発用に、まずこれを追加：

   * `localhost`
   * （必要なら）`127.0.0.1`

🔥ここ超重要：**2025/04/28以降に作ったFirebaseプロジェクトでは、`localhost` がデフォで入らない**仕様になってるよ。だから手動追加が必要になることがある🧯([Firebase][4])

---

## 3) 最低限の安全設定（ここだけでOK版）🛡️✨

![Security Toggle](./picture/firebase_login_ts_study_002_05_security_toggle.png)

## 安全設定①：Email enumeration protection（メール存在バレ対策）📨🕵️‍♂️

これをONにすると、「このメールは登録済み/未登録」みたいな情報が攻撃者にバレにくくなる👍
ただし、エラーメッセージは**“ぼかした表現”**に寄せるのがコツ（これは第9章あたりで綺麗に整える予定🙂）

Consoleで見つかる場合はこう：

1. **Authentication → Settings**
2. **User account management → User actions** みたいな項目へ
3. **Email enumeration protection（recommended）** をON → Save ([Google Cloud Documentation][5])

> もしこの項目が見当たらない/有効化を促されるなら、プロジェクトが **Identity Platform（Firebase Authentication with Identity Platform）** 側の機能になってる可能性があるよ。
> アップグレードすると料金・上限が変わるので、必要になったタイミングででOK🙆‍♂️ ([Google Cloud Documentation][6])

---

## 安全設定②：ユーザーの「勝手な新規作成/削除」を止める（クローズド運用向け）🚪🔒

たとえば「βテストで招待制にしたい」ときに便利✨
Identity Platform側の説明では、**ユーザーのサインアップや削除を無効化できる**とされてるよ([Google Cloud Documentation][7])

* 無効化すると、クライアント側の作成/削除で
  `auth/admin-restricted-operation` が返ることがある（想定通り）([Google Cloud Documentation][7])

✅ まだ学習段階で「普通にサインアップさせたい」なら、ここは触らなくてOK！🙂
（“公開前の締め”として覚えておく感じで十分👌）

---

## 4) ミニ課題（5分）🧪✨

![Add User Modal](./picture/firebase_login_ts_study_002_06_add_user.png)

## 「テスト用ユーザー」をConsoleで作る👤

1. **Authentication → Users** タブへ
2. **Add user**（ユーザー追加）
3. テスト用メール（例：自分のメールの +test とか）と適当なパスワードで作成
4. Users一覧に追加されるのを確認✅

※ 公式でも「Consoleから作れるよ」って書かれてるよ([Firebase][8])

---

## 5) つまずきレスキュー🧯🧠

## ❓ Googleログインで `unauthorized-domain` が出る

* だいたい **Authorized domains に今のドメインが入ってない**
* ローカルなら `localhost` / `127.0.0.1` を追加
* 本番なら `your-domain.com` を追加

「設定場所がSign-in methodじゃなくてSettings側に移動してる」系の話もよく出るので、迷ったら **Authentication → Settings → Authorized domains** を探すのが早いよ🙂([Firebase][4])

---

![AI Settings Audit](./picture/firebase_login_ts_study_002_07_ai_audit.png)

## 6) AIを使って“設定漏れゼロ”にする🤖🔎✨

## Antigravity / Gemini に投げる用プロンプト例🧠📝

（コピペして使ってOK）

```text
Firebase Authentication のConsole設定チェックリストを作って。
目的：Webアプリ（React）で Email/Password と Googleログインを動かす。
確認観点：Sign-in providers、Authorized domains（localhost含む）、User actions、Email enumeration protection。
漏れがあると出やすいエラー名（例：auth/unauthorized-domain）も添えて。
```

さらに Gemini CLI が使えるなら、「この章の作業ログ（自分メモ）を貼って、抜けを指摘して」も強い👍

---

## 7) チェック（セルフ採点）✅🧾

* [ ] Email/Password が **Enabled** になってる🔑
* [ ] Google が **Enabled** になってる🌈
* [ ] Authorized domains に **localhost**（必要なら127.0.0.1）を入れた🌍([Firebase][4])
* [ ] Users にテストユーザーが見える👤([Firebase][8])
* [ ] （見つかるなら）Email enumeration protection をONにできた🛡️([Google Cloud Documentation][5])

---

## 次章の予告👣✨

次の **第3章** で、React側に `firebase/app` と `firebase/auth` を入れて、**SDK初期化（モジュラー流儀）**を作るよ🧩🔥
ここまでできてれば、あとは“コードで繋ぐだけ”になる🙂

[1]: https://firebase.google.com/docs/auth/web/password-auth?utm_source=chatgpt.com "Authenticate with Firebase using Password-Based Accounts ..."
[2]: https://firebase.google.com/docs/auth?utm_source=chatgpt.com "Firebase Authentication"
[3]: https://firebase.google.com/docs/ai-logic?utm_source=chatgpt.com "Gemini API using Firebase AI Logic - Google"
[4]: https://firebase.google.com/support/faq?utm_source=chatgpt.com "Firebase FAQ - Google"
[5]: https://docs.cloud.google.com/identity-platform/docs/admin/email-enumeration-protection?utm_source=chatgpt.com "Enable or disable email enumeration protection"
[6]: https://docs.cloud.google.com/identity-platform/docs/product-comparison?utm_source=chatgpt.com "Differences between Identity Platform and Firebase ..."
[7]: https://docs.cloud.google.com/identity-platform/docs/concepts-manage-users "Identity Platform users in projects  |  Google Cloud Documentation"
[8]: https://firebase.google.com/docs/auth/web/manage-users?utm_source=chatgpt.com "Manage Users in Firebase - Google"
