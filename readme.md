# やりたいこと

- インスタンスの起動
   - [x] spot fleet request
       - インスタンス名の指定
   - [x] 開発用AMIから最新のものを選択して起動
   - route53で接続できるようにする？
       - subnetを使えばどうにかできないかな？
   - 有効期限を設定する
   - EFSの設定
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


# link

- [EFS](https://qiita.com/SSMU3/items/fe2f6b74ab363b39e2f6)
- [Spot Fleet を使って割安にリモート (AWS) に開発環境を持つためのアレコレ](https://mozami.me/2019/06/01/develop_with_ec2_spot_instance.html)
- [EC2を開発環境にする](https://qiita.com/motojouya/items/31346b968b41a10c4dd6#4-%E4%B8%80%E6%97%A6spotfleetrequest%E3%82%92%E3%81%97%E3%81%A6%E3%81%BF%E3%82%8B)
