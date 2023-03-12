UserBotの使い方



==Botの作成==

まずはこのサイトでBotを作成
https://discord.com/developers/applications

1.New ApplicationでBotの名前を決めてCreateを押す

2.作成したBotを選択し、左のタブから「Bot」に移動

3.「Add Bot」をクリックして、「Yes, do it!」で確定

4.PUBLIC BOTのチェックを外す（Botを公開したくない場合）

5.Click to Reset Tokenを押した後、Copyを押してトークンをコピー

6.user_bot.pyのTOKENに貼り付け

7.Botを追加したいDiscordのチャンネルIDをコピー（IDをコピーできない場合、Discordの設定から「詳細設定」を選択し、開発者モードを有効にする）

8.user_bot.pyのCHANNELIDに貼り付け

9.やることリストを管理したいDiscordのチャンネルIDをコピー

10.user_bot.pyのTODOCHANNELIDに貼り付け



==GPT-2のファインチューニング==

1.LINEのトーク履歴をこのディレクトリに配置
(LINEのトーク履歴は対象となる人物とのトーク画面へ行き、右上のハンバーガーメニューを押して、一番下のその他を押すと
トーク履歴を送信というメニューがあるのでこれを押すとテキストファイルが生成される)

2.UserBotをディレクトリごとGoogle Driveにアップロード

3.LINEの会話履歴を用いたGPT-2のファインチューニング.ipynbをGoogle Colaboratory上で実行

4.LINEの会話履歴を用いたGPT-2のファインチューニング.ipynbの中の「データセットの作成」の部分で、
User1に自分のLINE名、User2に会話相手のLINE名を入力

5.「追加学習の実行」まで実行すると、しばらくたってから学習済みモデルがoutputディレクトリに出力される

6.UserBotディレクトリをGoogle Driveからダウンロードし、ローカルに移動

※Google Colaboratory上でBotを起動すると一定時間後にタイムアウトしてしまうため、
学習済みモデルを出力した時点でローカルにUserBotディレクトリを移すとずっと起動できる

※WindowsにPythonをインストールしていない場合、以下のサイトからPython3.9あたりをインストール
(Add Python 3.x to PATHのチェック忘れず！)
https://pythonlinks.python.jp/ja/index.html

7.ローカルでBotを起動する場合、以下のライブラリをインストール

#Windowsの場合
py -3 -m pip install -U discord.py
pip install torch
pip install sentencepiece
pip install protobuf==3.20.1
pip install git+https://github.com/huggingface/transformers

※最後のコマンドは以下のサイトからGit for Windowsをインストールしないと実行できない
https://gitforwindows.org/

installが完了したらGit Bash上で実行

8.コマンドプロンプト上でUserBotディレクトリへ行き、「python user_bot.py」とコマンド入力すると、Botが起動



==このBotの機能==

会話文を入力すると、その人の言いそうな応答文を生成し、Discordのチャンネル上で発言

おまけで「やることリスト」の作成、管理が可能

やることリストに関する機能一覧

・「やることリスト作成して」：「、」区切りでやることを入力することでやることリストを作成

・「やること見せて」：最新のやることリストを表示

・「（やることの名前）終わったよ」：入力したやることにチェックマークを付ける

・「（やることの名前）終わってない」：入力したやることのチェックマークをはずす

・「全部終わったよ」：すべてのやることにチェックマークを付ける

・「全部終わってない」：すべてのやることのチェックマークをはずす

・「（やることの名前）消して」：入力したやることをやることリストから削除

・「（やることの名前）追加して」：入力したやることをやることリストに追加

・「（やることの名前）変えて」：入力したやることを新しいやることに変更

※（やることの名前）は名前の一部でも可

※「やることリスト作成して」、「（やることの名前）変えて」をやめたい場合、「キャンセル」を入力








