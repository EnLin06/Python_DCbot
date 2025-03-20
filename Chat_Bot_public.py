#pip install discord
#need ollama environment
import discord
import time
import ollama
import asyncio
import os
import aiohttp
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)
inuse = False

@bot.event
async def on_ready():
    global bg
    print(f"目前登入身份 --> {bot.user}")
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send("啟動成功")
                await channel.send("輸入 /Help 取得幫助，H要大寫，很重要")
                break 

def load_bg(filename):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print(f"錯誤：找不到 {filename}，請確保檔案存在！")
        return "你是一個沒有背景資訊的 AI。"


bg = {}
chat_history = {}
inuse = {}
user_msg = {}
temperature = {}
max_token = {}
@bot.command()
async def start(ctx):
    global bg, inuse
    id = ctx.author.id
    if not inuse.get(id, False):
        await ctx.send("機器人已上線 ! ")
        inuse[id] = True
    else:
        await ctx.send("我已經在線啦 !")

@bot.command()
async def end(ctx):
    global inuse
    id = ctx.author.id
    if inuse.get(id, False):
        await ctx.send("機器人已下線 ! ")
        inuse[id] = False
    else:
        await ctx.send("我本來就不在線 !")

@bot.command()
async def history(ctx):
    global chat_history
    id = ctx.author.id
    if id in chat_history and chat_history[id]:   
        await ctx.send("以下是機器人的記憶內容")
        for i in range(0, len(chat_history[id]), 2):
            await ctx.send(f"輸入({int(i/2) + 1}) : {chat_history[id][i]['content']} \n\n")
            await ctx.send(f"AI輸出({int(i/2) + 1}) : {chat_history[id][i+1]['content']} \n\n")
    else:
        await ctx.send("沒有任何對話紀錄 !")

@bot.command()
async def clear(ctx):
    global chat_history
    id = ctx.author.id
    if id in chat_history and chat_history[id]:
        chat_history[id].clear()
        await ctx.send("已清除對話紀錄")
    else:
        await ctx.send("沒有任何對話紀錄 !")

@bot.command()
async def earase(ctx, msg=1):
    global chat_history
    id = ctx.author.id
    try:
        msg = int(msg)
    except:
        await ctx.send("請輸入整數 ! ")
    if id in chat_history and chat_history[id]:
        try:
            msg -= 1
            msg *= 2
            await ctx.send(f"正在刪除 : {chat_history[id][msg]['content']}")
            del chat_history[id][msg]
            await ctx.send(f"正在刪除 : {chat_history[id][msg]['content']}")
            del chat_history[id][msg]
        except:
            await ctx.send("發生錯誤 ! 可能是你輸入的值超出範圍 !")
    else:
        await ctx.send("沒有任何對話紀錄 !")

@bot.command()
async def load(ctx, dataname='save'):
    global chat_history
    id = ctx.author.id
    user_id = ctx.author.id
    os.makedirs(f"ChatBot/savefile/{user_id}", exist_ok=True)
    try:
        with open(f'ChatBot/savefile/{user_id}/{dataname}.txt', mode='r', encoding='utf-8') as f:
            if id not in chat_history:
                chat_history[id] = []
            try:
                chat_history[id].clear()
            except:
                pass
            tmp = f.readlines()
            for i in range(len(tmp)):
                tmp[i] = tmp[i].strip()
            for i in range(0, len(tmp) , 2):
                chat_history[id].append({"role": "user", "content": tmp[i]})
                chat_history[id].append({"role": "assistant", "content": tmp[i+1]})

            await ctx.send("讀取成功 ! ")
    except:
        await ctx.send("讀取失敗 ! 請確認你的檔名是否正確")
            
@bot.command()
async def save(ctx, dataname='save'):
    global chat_history
    id = ctx.author.id
    user_id = ctx.author.id
    os.makedirs(f"ChatBot/savefile/{user_id}", exist_ok=True)
    try:
        if id in chat_history and chat_history[id]:
            with open(f"ChatBot/savefile/{user_id}/{dataname}.txt", mode='w', encoding='utf-8') as f:
                for i in range(len(chat_history[id])):
                    cleaned_content = " ".join(chat_history[id][i]['content'].splitlines())
                    print(cleaned_content, file=f)
                await ctx.send(f"存檔成功 ! 檔案名 {dataname} (.txt)")
        else:
            await ctx.send("沒有可儲存的紀錄 ! ")
    except Exception as e:
        await ctx.send(f"存檔失敗 ! 請檢查指令是否出錯，狀況 : {e}")

@bot.command()
async def setbg(ctx, dataname = 'bg'):
    global bg
    id = ctx.author.id
    try:
        if not os.path.exists(f'ChatBot/background/{dataname}.txt'):
            await ctx.send(f"檔案 {dataname} (.txt) 不存在，無法讀取")
            return
        bg[id] = load_bg(f'Chatbot/background/{dataname}.txt')
        await ctx.send("載入成功")
    except:
        await ctx.send("讀取失敗 ! 請確認你的檔名是否正確")

@bot.command()
async def retry(ctx):
    global user_msg, chat_history, temperature, max_token
    id = ctx.author.id
    try:
        if inuse.get(id, False):
            if id not in chat_history or len(chat_history[id]) < 2:
                await ctx.send("沒有可重試的對話！")
                return
            async with ai_lock:
                if id not in chat_history:
                    chat_history[id] = []
                if id not in user_msg:
                    user_msg[id] = ""
                if id not in temperature:
                    temperature[id] = 0.5
                if id not in max_token:
                    max_token[id] = 128

                chat_history[id] = chat_history[id][:-2]
                if len(chat_history[id]) > 30:
                    chat_history[id] = chat_history[id][-30:]
                start = time.time()

                messages = [{"role": "system", "content": bg[id]}]
                messages.extend(chat_history[id]) 
                messages.append({"role": "user", "content": user_msg[id]})

                try:
                    response = await asyncio.wait_for(
                    asyncio.to_thread(ollama.chat,
                                       model="TAIDE-8B",
                                        messages=messages,
                                        options = {'temperature' : temperature[id], 'max_tokens' : max_token[id]},
                                        stream = True
                                    ),
                    timeout=30
                    )
                    reply= ""
                    msg = await ctx.send("輸入中...")
                    last = 0
                    for chunk in response:
                        reply += chunk["message"]["content"]
                        if len(reply)-last >= 3:
                            await msg.edit(content=f"{reply}\n輸入中...")
                            last = len(reply)     

                    finish = time.time()
                    lasting = int(finish - start)
                    await msg.edit(content = f"{reply} \n(消耗時間 : {lasting} 秒)")
                    
                    chat_history[id].append({"role": "user", "content": user_msg[id]})
                    chat_history[id].append({"role": "assistant", "content": reply})

                except asyncio.TimeoutError:
                    await ctx.send(" AI 回應超時！請再試一次或稍後再試。")
                    print(" AI 回應超時！")
                except Exception as e:
                    await ctx.send(f"發生錯誤 ! {e}")
        else:
            return
    except:
        await ctx.send("出現錯誤 ! ")

@bot.command()
async def bglist(ctx):
    try:
        i = 1
        files = os.listdir('ChatBot/background')
        embed=discord.Embed(title=f"你的背景檔案清單 : ",description="",  color=0x58c5e9)
        for file in files:
            with open(f"ChatBot/background/{file}", mode='r', encoding='utf-8') as f:
                preview = f.read(50).replace('\n', ' / ')
                if preview == '':
                    preview = '(nothing)'
                file_name, _ = os.path.splitext(file)
                embed.add_field(name=f"{i} : {file_name}", value=f"預覽 : {preview}...", inline=False)
                i += 1
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"發生錯誤 ! {e}")

@bot.command()
async def savelist(ctx):
    try:
        i = 1
        user_id = ctx.author.id
        os.makedirs(f"ChatBot/savefile/{user_id}", exist_ok=True)
        files = os.listdir(f'ChatBot/savefile/{user_id}')
        embed=discord.Embed(title=f"你的存檔檔案清單 : ",description="",  color=0x58c5e9)
        for file in files:
            with open(f"ChatBot/savefile/{user_id}/{file}", mode='r', encoding='utf-8') as f:
                preview = f.read(50).replace('\n', ' / ')
                if preview == '':
                    preview = '(nothing)'
                file_name, _ = os.path.splitext(file)
                embed.add_field(name=f"{i} : {file_name}", value=f"預覽 : {preview}...", inline=False)
                i += 1
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"發生錯誤 ! {e}")
        
@bot.command()
async def Help(ctx):
    embed=discord.Embed(title=f"{ctx.author.name}，歡迎來到ChatBot",description="這是一個Discord上的聊天機器人 ! 以下是指令清單",  color=0x58c5e9)
    embed.add_field(name="/Help", value=f"叫出這個清單，H要大寫，很重要", inline=False)
    embed.add_field(name="/start", value=f"讓機器人啟動", inline=False)
    embed.add_field(name="/end", value=f"讓機器人停止運作", inline=False)
    embed.add_field(name="/clear", value=f"清除對話紀錄", inline=False)
    embed.add_field(name="/history", value=f"查看對話紀錄", inline=False)
    embed.add_field(name="/earase (num)", value=f"清除指定的對話記憶，(num)用於指定清除對象，可用/history確認", inline=False)
    embed.add_field(name="/retry", value=f"讓機器人重新生成", inline=False)
    embed.add_field(name="/save (filename)", value=f"存檔，(filename)為檔案名，不用加副檔名，預設為 save (.txt)", inline=False)
    embed.add_field(name="/load (filename)", value=f"讀檔，(filename)為檔案名，不用加副檔名，預設為 save (.txt)", inline=False)
    embed.add_field(name="/setbg (filename)", value=f"載入其他背景，(filename)為檔案名，不用加副檔名，預設為 bg (.txt)", inline=False)
    embed.add_field(name="/savelist", value=f"查看目前的所有存檔", inline=False)
    embed.add_field(name="/bglist", value=f"查看目前的所有背景文檔", inline=False)
    embed.add_field(name="/settoken (num)", value=f"改變AI的最大token(生成長度，10~1024之間)，預設為128 (注意 : 值太高會導致AI很慢)", inline=False)
    embed.add_field(name="/settemp (float)", value=f"改變AI的temperature(創造力，0~1之間)，預設為0.5 (注意 : 值太高會導致AI亂講話)", inline=False)
    embed.add_field(name="/delete (filename)", value=f"刪除存檔，(filename)為檔案名，不用加副檔名，預設為 save (.txt)", inline=False)
    embed.add_field(name="/upload (filename) (content)", value=f"創建一個新的背景文件，第一個參數為檔名，後續為內容，換行請改用空格(每個空格換一行)，也可以直接上傳.txt檔案", inline=False)
    embed.set_footer(text="玩得開心 :)")
    await ctx.send(embed=embed)

@bot.command()
async def settemp(ctx, temp):
    global temperature
    id = ctx.author.id
    try:
        num = float(temp)
        if num < 0 or num > 1:
            await ctx.send("temperature應該在0和1之間 ! ")
            return
    except:
        await ctx.send("請確認輸入無誤 ! ")
        return
    temperature[id] = num
    await ctx.send(f"更新完成 ! 現在 temperature : {num}")

@bot.command()
async def settoken(ctx, token):
    global max_token
    id = ctx.author.id
    try:
        num = int(token)
        if num < 10 or num > 1024:
            await ctx.send("max_token應該在10和1024之間 ! ")
            return
    except:
        await ctx.send("請確認輸入無誤 ! ")
        return
    max_token[id] = num
    await ctx.send(f"更新完成 ! 現在最大token : {num}")


@bot.command()
async def offline(ctx):
    await ctx.send ("下次見 ! ")
    await bot.close()

@bot.command()
async def upload(ctx, *args):
    if ctx.message.attachments:
        attachment = ctx.message.attachments[0]
        file_path = os.path.join('ChatBot/background', attachment.filename)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(attachment.url) as resp:
                    if resp.status == 200:
                        with open(file_path, "wb") as f:
                            f.write(await resp.read()) 
                        await ctx.send(f"上傳成功 ! 檔案 : {attachment.filename}")
                        return
                    else:
                        await ctx.send("上傳檔案失敗！")
                        return
        except Exception as e:
            await ctx.send(f"上傳失敗！錯誤: {e}")
            return
        
    try:
        with open(f"ChatBot/background/{args[0]}.txt", mode='w', encoding='utf-8') as f:
            words = list(args)
            filename = words[0]
            del words[0]
            for i in range(len(words)):
                print(words[i], file = f)
            print("此外，不要使用刪除線，不要用中文以外的語言\n還有 **不要呈現你的思考過程**\n以下是對話紀錄 (空白代表沒有紀錄)\n", file = f)
        await ctx.send(f"創建成功 ! 檔案 : {filename} (.txt)")
    except Exception as e:
        await ctx.send(f"創建失敗 : {e}")

@bot.command()
async def delete(ctx, dataname='save'):
    id = ctx.author.id
    path = f'ChatBot/savefile/{id}/{dataname}.txt'
    if not os.path.exists(path): 
        await ctx.send(f"檔案 {dataname} (.txt) 不存在，無法刪除！")
        return

    try:
        os.remove(path) 
        await ctx.send(f"{dataname} (.txt) 已成功刪除！")
    except Exception as e:
        await ctx.send(f"刪除失敗！錯誤: {e}")


ai_lock = asyncio.Lock()
@bot.event
async def on_message(message):
    global bg, chat_history, inuse, user_msg, temperature, max_token
    if message.author == bot.user:
        return 
   
    await bot.process_commands(message)
    
    id = message.author.id
    if inuse.get(id, False):
        if message.content.startswith(("/", "!", "！")):
            return
        async with ai_lock:
            if id not in chat_history:
                chat_history[id] = []
            if id not in user_msg:
                user_msg[id] = ""
            if id not in temperature:
                    temperature[id] = 0.5
            if id not in max_token:
                max_token[id] = 128

            if id not in bg:
                bg[id] = load_bg('ChatBot/background/bg.txt')

            if len(chat_history[id]) > 30:
                chat_history[id] = chat_history[id][-30:]
            start = time.time()
            user_msg[id] = message.content

            messages = [{"role": "system", "content": bg[id]}] 
            messages.extend(chat_history[id]) 
            messages.append({"role": "user", "content": user_msg[id]})

            try:
                response = await asyncio.wait_for(
                    asyncio.to_thread(ollama.chat,
                                       model="TAIDE-8B",
                                        messages=messages,
                                        options = {'temperature' : temperature[id], 'max_tokens' : max_token[id]},
                                        stream = True
                                    ),
                    timeout=30
                )
                reply = ""
                msg = await message.channel.send("輸入中...")
                last = 0
                for chunk in response:
                    reply += chunk["message"]["content"]

                    if len(reply) - last >= 3:
                        await msg.edit(content=f"{reply}\n輸入中...") 
                        last = len(reply)             

                finish = time.time()
                lasting = int(finish - start)
                await msg.edit(content = f"{reply} \n(消耗時間 : {lasting} 秒)")
                chat_history[id].append({"role": "user", "content": user_msg[id]})
                chat_history[id].append({"role": "assistant", "content": reply})

            except asyncio.TimeoutError:
                await message.channel.send(" AI 回應超時！請再試一次或稍後再試。")
                print(" AI 回應超時！")
            except Exception as e:
                await message.channel.send(f"發生錯誤 ! {e}")
    else:
        return

bot.run("DCBot TOKEN")