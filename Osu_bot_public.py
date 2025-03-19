import discord
from discord.ext import commands
import requests
import gettoken

intents = discord.Intents.all()
bot = commands.Bot(command_prefix = "/", intents = intents)
gamestart = False
@bot.event
async def on_ready():
    global gamestart
    slash = await bot.tree.sync()
    print(f"目前登入身份 --> {bot.user}")
    gamestart = False
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send("啟動成功")
                await channel.send("使用 /commandlist 檢查指令表")
                break 

token = gettoken.get("ClientID", "ClientSecret")
headers = {
    "Authorization": f"Bearer {token}"
}

@bot.command()
async def osu(ctx, msg, Type = 'basic', num = '1'):
    username = msg
    url = f"https://osu.ppy.sh/api/v2/users/{username}?key=username"
    response = requests.get(url, headers=headers)     
    if response.status_code == 200:
        data = response.json()
        if Type == 'basic':
            try:
                embed=discord.Embed(title=f"{username} 的基本資料 : ",
                                    description=f"國家/地區 : {data['country_code']} | 世界排名 : {data['statistics']['global_rank']}",url=f"https://osu.ppy.sh/users/{data['id']}",
                                    color=0x58c5e9)
                embed.add_field(name="PP : ", value=f"{int(data['statistics']['pp'])}", inline=True)
                embed.add_field(name="ACC : ", value=F"{data['statistics']['hit_accuracy']}%", inline=True)
                embed.add_field(name="PC : ", value=F"{data['statistics']['play_count']}次", inline=True)
                embed.add_field(name="國內排名 : ", value=F"{data['statistics']['country_rank']}", inline=True)
                embed.add_field(name="常玩模式 : ", value=F"{data['playmode']}", inline = True)
                embed.add_field(name="Miss數 : ", value=F"{data['statistics']['count_miss']}次", inline=True)
                embed.add_field(name="SS : ", value=F"{data['statistics']['grade_counts']['ss'] + data['statistics']['grade_counts']['ssh']}", inline = True)
                embed.add_field(name="S : ", value=F"{data['statistics']['grade_counts']['s'] + data['statistics']['grade_counts']['sh']}", inline = True)
                embed.add_field(name="A : ", value=F"{data['statistics']['grade_counts']['a']}", inline = True)
                embed.set_thumbnail(url= f"{data['avatar_url']}")
                embed.set_image(url=f"{data['cover_url']}")
                await ctx.send(embed=embed)
            except:
                await ctx.send("發生錯誤")
        elif Type == 'record':
            try:
                n = int(num)
            except ValueError:
                await ctx.send("指令錯誤 ! record後方應該是一個整數")
                return
            try:
                url_ = f'https://osu.ppy.sh/api/v2/users/{int(data['id'])}/scores/best?mode={data['playmode']}&limit={n}'
                r_response = requests.get(url_, headers=headers)
                Data = r_response.json()
                for d in Data:
                    MOD = ''
                    Acc = d['accuracy'] * 100
                    embed=discord.Embed(title=f"{d['beatmapset']['artist']} - {d['beatmapset']['title']} ({d['beatmap']['version']}, {d['beatmap']['difficulty_rating']}*)",
                                        description=f"made by : {d['beatmapset']['creator']} | played by {username}",url=f"{d['beatmap']['url']}",  color=0x58c5e9)
                    embed.add_field(name="圖譜資訊 : ",
                                     value=f"BPM : {d['beatmap']['bpm']} | 圈圈大小 : {d['beatmap']['cs']} | 出現速度 : {d['beatmap']['ar']} | HP : {d['beatmap']['drain']} \n 圈圈/滑條/轉盤數量 : {d['beatmap']['count_circles']} / {d['beatmap']['count_sliders']} / {d['beatmap']['count_spinners']}", inline=False)
                    embed.add_field(name="玩家表現 : ",
                                     value=f"ACC : {Acc:.2f} | PP : {int(d['pp'])} \n 300/100/50/Miss : {(d['statistics']['count_300'])} / {(d['statistics']['count_100'])} / {(d['statistics']['count_50'])} / {(d['statistics']['count_miss'])} \n 最大連擊 : {d['max_combo']} | 評級 : {d['rank']} | 得分 : {d['score']}", inline=False)
                    for i in range(len(d['mods'])):
                        MOD += d['mods'][i]
                        if i < len(d['mods']) - 1:
                            MOD += " / "
                    if len((d['mods'])) == 0:
                        MOD = '沒使用Mod (classic)'
                    embed.add_field(name="使用mod : ", value=f"{MOD}", inline=True)
                    embed.set_image(url=f"{d['beatmapset']['covers']['cover']}")
                    embed.set_thumbnail(url= f"{d['beatmapset']['covers']['list']}")
                    await ctx.send(embed=embed)
            except:
                await ctx.send("發生錯誤 ! ")
        elif Type == 'recent':
            try:
                url_ = f'https://osu.ppy.sh/api/v2/users/{int(data['id'])}/scores/recent?mode={data['playmode']}&limit=1'
                r_response = requests.get(url_, headers=headers)
                Data = r_response.json()
                for d in Data:
                    MOD = ''
                    Acc = d['accuracy'] * 100
                    embed=discord.Embed(title=f"{d['beatmapset']['artist']} - {d['beatmapset']['title']} ({d['beatmap']['version']}, {d['beatmap']['difficulty_rating']}*)",
                                        description=f"made by : {d['beatmapset']['creator']} | played by {username}",url=f"{d['beatmap']['url']}",
                                        color=0x58c5e9)
                    embed.add_field(name="圖譜資訊 : ",
                                     value=f"BPM : {d['beatmap']['bpm']} | 圈圈大小 : {d['beatmap']['cs']} | 出現速度 : {d['beatmap']['ar']} | HP : {d['beatmap']['drain']} \n 圈圈/滑條/轉盤數量 : {d['beatmap']['count_circles']} / {d['beatmap']['count_sliders']} / {d['beatmap']['count_spinners']}", inline=False)
                    embed.add_field(name="玩家表現 : ",
                                     value=f"ACC : {Acc:.2f} | PP : {int(d['pp'])} \n 300/100/50/Miss : {(d['statistics']['count_300'])} / {(d['statistics']['count_100'])} / {(d['statistics']['count_50'])} / {(d['statistics']['count_miss'])} \n 最大連擊 : {d['max_combo']} | 評級 : {d['rank']} | 得分 : {d['score']}", inline=False)
                    for i in range(len(d['mods'])):
                        MOD += d['mods'][i]
                        if i < len(d['mods']) - 1:
                            MOD += " / "
                    if len((d['mods'])) == 0:
                        MOD = '沒使用Mod (classic)'
                    embed.add_field(name="使用mod : ", value=f"{MOD}", inline=True)
                    embed.set_image(url=f"{d['beatmapset']['covers']['cover']}")
                    embed.set_thumbnail(url= f"{d['beatmapset']['covers']['list']}")
                    await ctx.send(embed=embed)
                if len(Data) == 0:
                    await ctx.send("沒有最近的遊玩紀錄 !")
            except:
                await ctx.send("發生錯誤，該玩家最近一次遊玩的紀錄可能未上榜")
        else:
            await ctx.send("未知的指令")
            
    else:
        await ctx.send(f"出現錯誤 ! 代碼 : {response.status_code}")

@bot.command()
async def commandlist(ctx):
    embed=discord.Embed(title="指令列表",  color=0x58c5e9)
    embed.add_field(name="/osu (玩家名) (basic)", value="查詢該玩家基本資料，其中(basic)可以省略", inline=False)
    embed.add_field(name="/osu (玩家名) record (num)", value="查詢該玩家的bestplay，其中(num)是查詢筆數，預設為num = 1", inline=False)
    embed.add_field(name="/osu (玩家名) recent", value="查詢該玩家的近期遊戲紀錄", inline=False)
    await ctx.send(embed=embed)

bot.run("DCBot TOKEN")