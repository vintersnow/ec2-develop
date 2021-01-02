# やりたいこと

- インスタンスの起動
   - [x] spot fleet request
       - インスタンス名の指定
   - [x] 開発用AMIから最新のものを選択して起動
   - route53で接続できるようにする？
       - subnetを使えばどうにかできないかな？
   - 有効期限を設定する
- 利用
    - ipが違ってもssh接続できるようにする
    - clipボードが使えるようにする
- 終了
    - [x] AMIの作成する
    - 古いAMIを削除する
    - [x] インスタンスを終了する
- その他
    - resource apiに切り替える
    - amiの保存の仕方が変かも？スナップショットをよりうまくとれるかも

# requirements

aws cliの設定
https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-mac.html

`~/.aws/credentials` があることを確認する
