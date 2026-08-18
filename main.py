import matplotlib
matplotlib.use('Agg') # iPad/Replit環境でグラフを描くための必須設定

import discord
from discord.ext import commands
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt

# ボットのインテント設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "xp_data.json"

# データの読み込み
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# データの保存
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

@bot.event
async def on_ready():
    print(f"ログインしました: {bot.user.name}")

# ① XPを記録するコマンド
@bot.command(name="xp")
async def record_xp(ctx, xp_value: float):
    user_id = str(ctx.author.id)
    user_name = ctx.author.name
    current_time = datetime.now().strftime("%m/%d %H:%M")

    data = load_data()

    if user_id not in data:
        data[user_id] = {"name": user_name, "history": []}
    
    data[user_id]["history"].append({"time": current_time, "xp": xp_value})
    save_data(data)

    await ctx.send(f"【記録】{ctx.author.mention} さんのXPを **{xp_value}** として記録しました！")

# ② 全員のグラフを表示するコマンド
@bot.command(name="グラフ")
async def show_graph(ctx):
    data = load_data()
    
    if not data:
        await ctx.send("まだ誰のXPも記録されていません。")
        return

    plt.figure(figsize=(10, 6))
    
    for user_id, user_info in data.items():
        history = user_info["history"]
        if not history:
            continue
        
        times = [item["time"] for item in history]
        xps = [item["xp"] for item in history]
        
        plt.plot(times, xps, marker='o', label=user_info["name"])

    plt.title("Splatoon 3 - XP Transition")
    plt.xlabel("Date/Time")
    plt.ylabel("X Power")
    plt.grid(True)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    image_path = "xp_chart.png"
    plt.savefig(image_path)
    plt.close()

    with open(image_path, "rb") as f:
        picture = discord.File(f)
        await ctx.send("現在の全員のXP推移グラフです！", file=picture)
    
    os.remove(image_path)

@record_xp.error
async def xp_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("使用方法: `!xp [数値]` (例: `!xp 2450.5`)")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("XPは半角の数値（整数または小数）で入力してください。")

# ⚠️ トークンを直接書かず、サーバーの秘密の保管庫から読み込むように変更
import os
TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
