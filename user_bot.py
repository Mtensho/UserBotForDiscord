import discord
import torch
import random
import csv
import re
import datetime
from transformers import AutoModelForCausalLM, AutoTokenizer

##前準備
#GPU使えるようにする
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

#トークナイザの定義
tokenizer = AutoTokenizer.from_pretrained("rinna/japanese-gpt2-medium")
tokenizer.do_lower_case = True

#ユーザの発言に対する応答文を生成するモデルの定義
model = AutoModelForCausalLM.from_pretrained('output/')
model.to(device)
model.eval()

special_tokens = ["User1:", "User2:","<input1>","<input2>","<input3>","<input4>"]
special_tokens_dict = {"additional_special_tokens": special_tokens}
num_added_toks = tokenizer.add_special_tokens(special_tokens_dict)

#botのトークンと発言するチャンネルのIDを定義
TOKEN = '' # TOKENを貼り付け
CHANNELID =  # チャンネルIDを貼り付け
TODOCHANNELID =  # やることチャンネルIDを貼り付け

#intentsの定義
intents = discord.Intents.all()  # デフォルトのIntentsオブジェクトを生成
client = discord.Client(intents=intents)

#入力文及び出力文をきれいにするための正規表現の定義
pattern = r"[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF0-9０-９a-zA-Z、。！？!?….]+"

#フラグの定義
skip_flag=False
memo_flag=False
edit_flag=False
current_user=0
before_do=""
log=[]

#bot起動時のアクション
@client.event
async def on_ready():
    print('ログインしました')
    channel = client.get_channel(CHANNELID)
    await channel.send("ログインしました")

#botがメッセージを受け取ったときのアクション
@client.event
async def on_message(message):
    global skip_flag
    global memo_flag
    global edit_flag
    global before_do
    global current_user
    global log
    
    #botの発言するチャンネル以外の入力は無視する
    if message.channel.id != CHANNELID:
        return

    #メッセージの送信者がBotだった場合は無視
    if message.author.bot:
        return
    
    #受け取った「やること」から「やることリスト」を作成し「やることチャンネル」に書く
    elif message.content and memo_flag:
        if current_user!=message.author.id:
            skip_flag=True
            channel = client.get_channel(CHANNELID)
            await channel.send("取込み中")
            return
        memo_flag = False
        skip_flag=True
        #「キャンセル」と言われたら中断する
        if message.content == "キャンセル":
            channel = client.get_channel(CHANNELID)
            await channel.send("キャンセルしました。")
            return
        to_do=message.content.split("、")
        to_do=set(to_do)
        print("やること：")
        print(to_do)
        dt_now = datetime.datetime.now()
        channel = client.get_channel(TODOCHANNELID)
        to_do_text=message.author.name +"のやることリスト\n"
        head_line="=====" + str(dt_now.year) + "/" + str(dt_now.month) + "/" + str(dt_now.day) + "/" + str(dt_now.strftime('%a')) + "====="
        to_do_text=to_do_text+head_line
        under_line="\n"
        for i in range(len(head_line)):
            under_line=under_line+"="
        for now in to_do:
            if now == "全部":
                channel = client.get_channel(CHANNELID)
                await channel.send("「全部」は入力できません。") 
                return
            if now == "やることリスト":
                channel = client.get_channel(CHANNELID)
                await channel.send("「やることリスト」は入力できません。") 
                return
            to_do_text=to_do_text+"\n□"+now
        to_do_text=to_do_text+under_line
        await channel.send(to_do_text)
        
        sent="やることリストを作成しました。\n\n"+to_do_text
        channel = client.get_channel(CHANNELID)
        await channel.send(sent)                 
        
    #受け取った「やること」を「やることリスト」から選んで編集する
    elif message.content and edit_flag:
        if current_user!=message.author.id:
            skip_flag=True
            channel = client.get_channel(CHANNELID)
            await channel.send("取込み中")
            return
        end_flag=False
        edit_flag = False
        skip_flag=True
        #「キャンセル」と言われたら中断する
        if message.content == "キャンセル":
            channel = client.get_channel(CHANNELID)
            await channel.send("キャンセルしました。")
            return
        after_do=message.content
        print(before_do,after_do)
        search_list=message.author.name +"のやることリスト"
        channel = client.get_channel(TODOCHANNELID)
        async for message in channel.history(limit=200):
            if message.author == client.user:
                if search_list in message.content:
                    result=message.content
                    result=result.split("\n")
                    replace_result=""
                    for i,now in enumerate(result):
                        if i > 1:
                            print(now)
                            if now.replace("□","").replace("☑","") == before_do.replace("□","").replace("☑",""):
                                now="□"+after_do
                                end_flag=True
                        replace_result=replace_result+now+"\n"
                    await channel.send(replace_result)
                    await message.delete()#メッセージの削除
                    end_flag=True
                    break
        if end_flag:
            sent="変更しました。\n\n"+replace_result
            channel = client.get_channel(CHANNELID)
            await channel.send(sent)
        else:
            channel = client.get_channel(CHANNELID)
            await channel.send("やることが見つかりませんでした。")
        
    #受け取ったメッセージが「やることリスト作成して」のとき、「やることリスト」を作成
    elif message.content=="やることリスト作成して":
        current_user=message.author.id
        memo_flag=True
        skip_flag=True
        channel = client.get_channel(CHANNELID)
        await channel.send("やることを「、」区切りで入力してください。")
        
    #受け取ったメッセージが「全部終わったよ」のとき、一番新しい「やることリスト」の全ての「やること」にチェックをつける
    elif message.content=="全部終わったよ":
        skip_flag=True
        search_list=message.author.name +"のやることリスト"
        channel = client.get_channel(TODOCHANNELID)
        async for message in channel.history(limit=200):
            if message.author == client.user:
                if search_list in message.content:
                    replace_result=message.content.replace("□","☑")
                    await channel.send(replace_result)
                    await message.delete()#メッセージの削除
                    break
                    
        sent=replace_result+"\n\nやることリストを更新しました。"
        channel = client.get_channel(CHANNELID)
        await channel.send(sent)
        
    #受け取ったメッセージが「全部終わってない」のとき、一番新しい「やることリスト」の全ての「やること」のチェックをはずす
    elif message.content=="全部終わってない":
        skip_flag=True
        search_list=message.author.name +"のやることリスト"
        channel = client.get_channel(TODOCHANNELID)
        async for message in channel.history(limit=200):
            if message.author == client.user:
                if search_list in message.content:
                    replace_result=message.content.replace("☑","□")
                    await channel.send(replace_result)
                    await message.delete()#メッセージの削除
                    break
                    
        sent=replace_result+"\n\nやることリストを更新しました。"
        channel = client.get_channel(CHANNELID)
        await channel.send(sent)
        
    #受け取ったメッセージが「やることリスト消して」のとき、一番新しい「やることリスト」を消す
    elif message.content=="やることリスト消して":
        skip_flag=True
        end_flag=False
        search_list=message.author.name +"のやることリスト"
        channel = client.get_channel(TODOCHANNELID)
        async for message in channel.history(limit=200):
            if message.author == client.user:
                if search_list in message.content:
                    await message.delete()#メッセージの削除
                    channel = client.get_channel(CHANNELID)
                    await channel.send("やることリストを消去しました。")
                    break
                    
        skip_flag=True 
        channel = client.get_channel(TODOCHANNELID)
        async for message in channel.history(limit=200):
            if message.author == client.user:
                if search_list in message.content:
                    result=message.content
                    end_flag=True
                    break
                    
        if end_flag:
            sent=result+"\n\n現在のやることリストです。"
            channel = client.get_channel(CHANNELID)
            await channel.send(sent)
        else:
            channel = client.get_channel(CHANNELID)
            await channel.send("やることリストがありません。")
        
    #受け取ったメッセージが「（やることの名前）終わったよ」のとき、その「やること」にチェックをつける
    elif re.search(r".*終わったよ", message.content):
        skip_flag=True
        end_flag=False
        count=0
        match=re.search(r"(.*)終わったよ", message.content)
        do_text=match.group(1)
        print(do_text)
        search_list=message.author.name +"のやることリスト"
        channel = client.get_channel(TODOCHANNELID)
        async for message in channel.history(limit=200):
            if message.author == client.user:
                if search_list in message.content:
                    if do_text in message.content:
                        result=message.content
                        result=result.split("\n")
                        replace_result=""
                        do=[]
                        for i, now in enumerate(result):
                            if do_text in now:
                                if i>1:
                                    now=now.replace("□","☑")
                                    do.append(do_text)
                                    end_flag=True
                            replace_result=replace_result+now+"\n"
#                         if len(do) == 1:
                        await channel.send(replace_result)
                        await message.delete()#メッセージの削除                  
                        break
        if end_flag:
            sent=replace_result+"\nやることリストを更新しました。"
            channel = client.get_channel(CHANNELID)
            await channel.send(sent)
        else:
            channel = client.get_channel(CHANNELID)
            await channel.send("やることが見つかりません。")
            
    #受け取ったメッセージが「（やることの名前）終わってない」のとき、その「やること」のチェックをはずす
    elif re.search(r".*終わってない", message.content):
        skip_flag=True
        end_flag=False
        match=re.search(r"(.*)終わってない", message.content)
        do_text=match.group(1)
        print(do_text)
        search_list=message.author.name +"のやることリスト"
        channel = client.get_channel(TODOCHANNELID)
        async for message in channel.history(limit=200):
            if message.author == client.user:
                if search_list in message.content:
                    if do_text in message.content:
                        result=message.content
                        result=result.split("\n")
                        replace_result=""
                        for i, now in enumerate(result):
                            if do_text in now:
                                if i>1:
                                    now=now.replace("☑","□")
                                    end_flag=True
                            replace_result=replace_result+now+"\n"
                    await channel.send(replace_result)
                    await message.delete()#メッセージの削除
                    break
        if end_flag:
            sent=replace_result+"\nやることリストを更新しました。"
            channel = client.get_channel(CHANNELID)
            await channel.send(sent)
        else:
            channel = client.get_channel(CHANNELID)
            await channel.send("やることが見つかりません。")
        
    #受け取った「やること」を「やることリスト」から消去する
    elif re.search(r".*消して", message.content):
        skip_flag=True
        end_flag=False
        match=re.search(r"(.*)消して", message.content)
        do_text=match.group(1)
        print(do_text)
        search_list=message.author.name +"のやることリスト"
        channel = client.get_channel(TODOCHANNELID)
        async for message in channel.history(limit=200):
            if message.author == client.user:
                if search_list in message.content:
                    result=message.content
                    result=result.split("\n")
                    replace_result=""
                    for i,now in enumerate(result):
                        if do_text not in now:
                            replace_result=replace_result+now+"\n"
                        else:
                            if i <= 1:
                                replace_result=replace_result+now+"\n"
                    await channel.send(replace_result)
                    await message.delete()#メッセージの削除
                    end_flag=True
                    break
                    
        if end_flag:
            sent=replace_result+"\nやることリストを更新しました。"
            channel = client.get_channel(CHANNELID)
            await channel.send(sent)
        else:
            channel = client.get_channel(CHANNELID)
            await channel.send("やることが見つかりません。")
       
    #受け取った「やること」を「やることリスト」に追加する
    elif re.search(r".*追加して", message.content):
        skip_flag=True
        end_flag=False
        match=re.search(r"(.*)追加して", message.content)
        do_text=match.group(1)
        for now in to_do:
            if now == "全部":
                channel = client.get_channel(CHANNELID)
                await channel.send("「全部」は入力できません。") 
                return
            if now == "やることリスト":
                channel = client.get_channel(CHANNELID)
                await channel.send("「やることリスト」は入力できません。") 
                return
        do_text="□"+do_text
        print(do_text)
        search_list=message.author.name +"のやることリスト"
        channel = client.get_channel(TODOCHANNELID)
        async for message in channel.history(limit=200):
            if message.author == client.user:
                if search_list in message.content:
                    result=message.content
                    result=result.split("\n")
                    replace_result=""
                    for i,now in enumerate(result):
                        if i == len(result)-1:
                            replace_result=replace_result+do_text+"\n"
                        replace_result=replace_result+now+"\n"
                    await channel.send(replace_result)
                    await message.delete()#メッセージの削除
                    end_flag=True
                    break
        if end_flag:
            sent=replace_result+"\nやることリストを更新しました。"
            channel = client.get_channel(CHANNELID)
            await channel.send(sent)
        else:
            channel = client.get_channel(CHANNELID)
            await channel.send("やることが見つかりません。")
            
    #受け取った「やること」を「やることリスト」に追加する
    elif re.search(r".*変えて", message.content):
        current_user=message.author.id
        end_flag=False
        edit_flag=True
        skip_flag=True
        match=re.search(r"(.*)変えて", message.content)
        do_text=match.group(1)
        search_list=message.author.name +"のやることリスト"
        channel = client.get_channel(TODOCHANNELID)
        async for message in channel.history(limit=200):
            if message.author == client.user:
                if search_list in message.content:
                    result=message.content
                    result=result.split("\n")
                    for i,now in enumerate(result):
                        if do_text in now:
                            if i > 1:
                                before_do=now
                                end_flag=True
                                break
        print(before_do)
        if end_flag:
            channel = client.get_channel(CHANNELID)
            await channel.send("変更後のやることを入力してください。")
        else:
            channel = client.get_channel(CHANNELID)
            await channel.send("やることが見つかりません。")
            
    #受け取ったメッセージが「やること見せて」のとき、一番新しい「やることリスト」を表示する
    elif message.content=="やること見せて":
        end_flag=False
        search_list=message.author.name +"のやることリスト"
        channel = client.get_channel(TODOCHANNELID)
        async for message in channel.history(limit=200):
            if message.author == client.user:
                if search_list in message.content:
                    sent=message.content
                    end_flag=True
                    break
        if end_flag:            
            sent=sent+"\n\n現在のやることリストです。"
            channel = client.get_channel(CHANNELID)
            await channel.send(sent)
        else:
            channel = client.get_channel(CHANNELID)
            await channel.send("やることリストがありません。")
        
    #メッセージを受け取ったとき、応答文を生成
    elif message.content:
        print("入力時会話履歴:")
        print(log)
        if len(log)>=4:
                log=log[-3:]
        print("変更後会話履歴:")
        print(log)
        output_flag=False
        text = re.findall(pattern, message.content)
        text="".join(text)
        text="User1:"+text
        log.append(text)
        input_text = '<s>'
        for i,l in enumerate(log):
            input_text=input_text+"<input"+str(len(log)-i)+">"+l
        input_text = input_text + "[SEP]"
        print("入力：")
        print(input_text)
        input_ids = tokenizer.encode(input_text, return_tensors='pt').to(device)
        out = model.generate(input_ids, 
                             do_sample=True, 
                             top_p=0.95, 
                             top_k=40, 
                             num_return_sequences=1, 
                             max_length=256, 
                             pad_token_id=tokenizer.pad_token_id,
                             bad_words_ids=[[1], [5]])
        print("出力トークン：")
        print(tokenizer.batch_decode(out))
        print(out)
        for sent in tokenizer.batch_decode(out):
            sent = sent.split('[SEP]</s>')[1]
            sent=sent.replace('<input1>', '').replace('<input2>', '').replace('<input3>', '').replace('<input4>', '').replace('</s>', '').replace('<unk>', '').replace('!', '！').replace('?', '？')
            output_flag=True
            if 'User1:' in sent:
                sent = sent.split('User1:')[0]
            if 'User2:' in sent:
                sent = sent.split('User2:')[1]
            sent="User2:"+sent
            log.append(sent)
            print("出力後会話履歴:")
            print(log)
            sent=sent.replace('User2:', '')
            sent = re.findall(pattern, sent)
            sent="".join(sent)
            if len(sent) > 0:
                channel = client.get_channel(CHANNELID)
                await channel.send(sent)
            else:
                channel = client.get_channel(CHANNELID)
                await channel.send("...")
    else:
        # テキストがない場合は無視する
        return

client.run(TOKEN)