# 第05章：Windowsでローカルドメインを扱う基本🪟📝

この章は「リバースプロキシで複数アプリ共存」をやる前の“地ならし”だよ〜😊✨
やることはシンプルで、**「この名前（例：api.localhost）＝このIP（例：127.0.0.1）」**をWindowsに教えてあげるだけ！🌱

---

## 🎯 この章のゴール

* 「front.localhost」「api.localhost」みたいな**人間にやさしいURL**で開発できるようになる🧠💕
* “名前解決（name resolution）”の超基本（＝PCがURLをIPに変換する仕組み）をつかむ🔍
* hosts編集で起こる「あるある事故」を踏まずに進める😇💥

---

## 1) まずは“名前解決”のイメージを掴もう🧩

ざっくり言うと、ブラウザやcurlはこう動くよ👇

```text
api.localhost にアクセス
   ↓（名前解決）
127.0.0.1（自分のPC）に行けばいいんだな！
   ↓（接続）
ローカルの入口（リバースプロキシ）へ到達
```

そしてWindowsは、ホスト名をIPに解決するときに**決まった順番**で探すんだけど、重要なのはここ👇

* **hostsファイルを見る**
* それで見つからなければ **DNS（ネット側）に聞く**

この“順番”のおかげで、**hostsに書いたら（だいたい）最優先で勝つ**と思ってOK！🏆
※より正確には、Windowsのホスト名解決は「自分自身か確認 → hosts → DNS → （だめなら）NetBIOS系」という流れで説明されてるよ。([マイクロソフトサポート][1])

---

## 2) hostsファイルって何？🍞🧠

hostsは、Windowsが読む「手動の住所録」みたいなテキストファイル📒✨
1行がこういう形👇（左がIP、右が名前）

```text
127.0.0.1  api.localhost
```

Microsoftの説明でも、hostsは「ホスト名をIPに対応付けるためのファイル」で、1行ずつ「IP + ホスト名」を書く形式だよって書かれてるよ。([マイクロソフトサポート][2])

---

## 3) Windowsでhostsはどこにあるの？📍

場所はここ👇

* 「C:\Windows\System32\Drivers\Etc\hosts」

Windowsのホスト名解決の説明でも、hostsの場所として「%Systemroot%\System32\Drivers\Etc」が示されてるよ。([マイクロソフトサポート][1])

---

## 4) hosts編集：安全で失敗しにくい手順🛠️✨

Windowsはここがシビアで、**普通に編集しようとすると保存でコケる**ことが多いよ😂
なので、失敗しにくい“王道ルート”でいこう！

## 手順A：デスクトップで編集 → 戻す（おすすめ）🧁

1. エクスプローラーで「C:\Windows\System32\Drivers\Etc」を開く
2. 「hosts」を**デスクトップにコピー**する📄➡️🖥️
3. デスクトップのhostsをVS Codeで編集する✍️
4. 編集したhostsを「Etc」フォルダに**上書きコピー**する（管理者許可が出るのでOK）🛡️

この「いったんデスクトップで作って、あとでEtcに戻す」流れは、Microsoftの“hostsを既定に戻す手順”でも同じノリで案内されてる（作って→移して→管理者許可）ので、事故りにくいよ。([マイクロソフトサポート][2])

## 手順B：VS Codeを管理者で起動して直接編集（慣れたら）🚀

* スタートメニューでVS Codeを右クリック
* 「管理者として実行」
* その状態でhostsを開いて編集・保存

---

## 5) 何を書けばいいの？（最小セット）✍️🌱

## ✅ まずは3つだけ追加しよう

例：これからの章で使いやすい命名でいくよ〜🎯

```text
127.0.0.1  front.localhost
127.0.0.1  api.localhost
127.0.0.1  admin.localhost
```

## 🧠 できればIPv6（::1）も一緒に足す

最近の環境だと、アプリやブラウザがIPv6を優先することがあって、**127.0.0.1だけだと「あれ？つながらん」**が起きがち🥲
なので、同じ名前に対して::1も書くのが安全✨

```text
127.0.0.1  front.localhost
::1        front.localhost

127.0.0.1  api.localhost
::1        api.localhost

127.0.0.1  admin.localhost
::1        admin.localhost
```

---

## 6) 反映されたか確認しよう🔍✅

## ① DNSキャッシュを流す（効かない時の必殺技）🧹

編集後、すぐ反映されないことがあるので、一回これ👇

```text
ipconfig /flushdns
```

## ② 疎通チェック（3段階）🧪

**(1) ping で名前→IPになってるか**

```text
ping api.localhost
```

**(2) nslookup で名前解決の結果を見る**

```text
nslookup api.localhost
```

**(3) ブラウザで開く（あとでリバプロ入れる前提）**

* いまはまだサーバーを立ててないなら「開けない」でもOK🙆
* 大事なのは「名前が変な外のIPに飛んでない」こと！

---

## 7) やりがちミスあるある集😇💣（ここ超大事）

## ❌ ミス1：hosts.txt にしちゃう

* 拡張子が付くと、Windowsはhostsとして読まないよ〜😭
* ちゃんとファイル名が **hosts**（拡張子なし）になってるか確認！

## ❌ ミス2：保存できたつもりで保存できてない

* 管理者権限がなくて、保存が失敗してるパターン多い😂
* だから「デスクトップで編集→上書き」の手順Aが強い💪

## ❌ ミス3：書いたのに反映されない

* DNSキャッシュが残ってることがある
* まず「ipconfig /flushdns」→それでもダメならブラウザ再起動🔁

## ❌ ミス4：スペースやタブがぐちゃぐちゃ

* 1つ以上の空白で区切れてればOKだけど、見やすさ大事✨
* こういう形が安定👇（IP→空白→名前）

## ❌ ミス5：hostsに書いたせいで「本物のサイト」が開けなくなる

hostsは“強い”ので、例えば「example.com」を127.0.0.1に向けたら、当然そのサイトは開けなくなる😇
つまり、**プロジェクト用の名前だけに絞ろう**が正義🛡️

---

## 8) ちょい先取り：.localhostが強い理由🏠🔥

次章で詳しくやるけど、**“.localhost配下はループバックに解決される想定”**として仕様で扱われてるよ（localhost系は特別扱いされる）。IETFのRFC 6761でも「.localhost配下は常にループバックへ解決される前提でよい」系の書き方がある。([IETF Datatracker][3])

なので、今後は「front.localhost / api.localhost」をメインに育てると気持ちいいよ〜😊✨

---

## 9) AIに聞くと爆速になる質問例🤖⚡

（コピペして使ってOK！）

* 「Windowsのhostsを編集した。api.localhostが127.0.0.1に解決されてるか確認する最短コマンドを3つ教えて」
* 「front.localhostが開けない。原因切り分けを“名前解決→ポート→コンテナ→アプリ”の順でチェックリスト化して」
* 「hostsにIPv4とIPv6どっちも書くべき？ ありがちなハマりも含めて理由をやさしく説明して」

---

## 10) ミニ課題🎓✨（手を動かすと一気に定着する！）

## 課題1：3つの名前を生やす🌱

* hostsに「front/api/admin」を追加
* flushdns
* ping と nslookup で結果を確認✅

## 課題2：わざと1個だけ壊す😈

* api.localhost を「127.0.0.2」にしてみる（※存在しない想定のIP）
* どういうエラーになるか観察👀
* 戻す（ここ大事）🔙

## 課題3：後片付け🧹✨

* 追加した行の先頭に「#」を付けてコメントアウトしてみる
* 反映が消えるか確認（flushdnsも）✅
* “安全に戻せる”経験があると、次章以降めちゃ安心😌

---

## ✅ この章のまとめ（次に繋がる！）🚪➡️🏠

* hostsは「名前→IP」を固定する“手動住所録”📒
* Windowsはhostsを見てからDNSに行くので、ローカル開発に便利✨ ([マイクロソフトサポート][1])
* まずは「front/api/admin.localhost」を生やせれば勝ち🎉
* 次章で「.localhostの強さ」を理解すると、さらに快適になるよ〜🏠🔥 ([IETF Datatracker][3])

次（第6章）に進むと、**“hostsいじり地獄”から解放される方向**に入っていくよ😆💪

[1]: https://support.microsoft.com/en-us/topic/microsoft-tcp-ip-host-name-resolution-order-dae00cc9-7e9c-c0cc-8360-477b99cb978a "Microsoft TCP/IP Host Name Resolution Order - Microsoft Support"
[2]: https://support.microsoft.com/en-us/topic/how-to-reset-the-hosts-file-back-to-the-default-c2a43f9d-e176-c6f3-e4ef-3500277a6dae "How to reset the Hosts file back to the default - Microsoft Support"
[3]: https://datatracker.ietf.org/doc/html/rfc6761 "
            
                RFC 6761 - Special-Use Domain Names
            
        "
