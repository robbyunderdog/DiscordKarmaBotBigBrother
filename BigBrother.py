import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from bigbrotherdatabase import init_db, add_user, get_user, alterRecord, minKarma, maxKarma
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
nltk.download('all')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents = intents, activity=discord.Activity(type=discord.ActivityType.listening, name="every conversation."))

init_db()
analyzer = SentimentIntensityAnalyzer()

def sentiAnaly(msg):
    score = analyzer.polarity_scores(msg)
    print(f"{score}")
    return round(score['compound'] * 10, 2)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"{bot.user} is online!")

#on every message that is sent it checks its value and adds it to correct entry in db
@bot.event
async def on_message(msg):
    if msg.author.bot == False:
        serverid = msg.guild.id
        userid = msg.author.id

        if get_user(userid, serverid) is None:
            add_user(userid, serverid)

            karmaDelta = sentiAnaly(msg.content)
            
            alterRecord(userid, karmaDelta, serverid)
        else:

            karmaDelta = sentiAnaly(msg.content)

            alterRecord(userid, karmaDelta, serverid)

#command to return sql entry data
@bot.tree.command(name="whatismysocialcreditscore", description="Lets you learn your faults by revealing your karma.")
async def whatismysocialcreditscore(interaction: discord.Interaction):
    userid = interaction.user.id
    serverid = interaction.guild.id
    serverName = interaction.guild.name

    if get_user(userid, serverid) is None:
        await interaction.response.send_message("You are currently not in our system. Get in line.")
    else:
        embed = discord.Embed(
        colour=discord.Colour.blue(),
        description=f"This is a report of your social credit and the number of messages sent in {serverName}.",
        title="Social Credit Report"
        )

        numMessages = get_user(userid, serverid)[2]
        score = get_user(userid, serverid)[3]

        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)

        embed.add_field(name="**UserID**", value=userid)
        embed.add_field(name="**Number of Messages**", value=numMessages)
        embed.add_field(name="**Social Credit Score**", value=round(score, 2))

        if score >= 0:
            embed.set_footer(text="You are doing your server proud by being a nice and productive citizen of society.")
        else:
            embed.set_footer(text="You will be leaving this earth at some point, I do not believe you will like where you are going. Check yourself.")

        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="socialcreditranking", description="Lets learn the greatest and worst of this world.")
async def socialcreditranking(interaction: discord.Interaction):
    serverid = interaction.guild.id
    
    if maxKarma(serverid) is None or minKarma(serverid) is None:
        await interaction.response.send_message("There are not enough entries to rank them.")
    else:
        
        userIDGood = maxKarma(serverid)[0]
        userIDBad = minKarma(serverid)[0]

        scoreGood = get_user(userIDGood, serverid)[3]
        scoreBad = get_user(userIDBad, serverid)[3]

        userPos = await bot.fetch_user(userIDGood)
        userNeg = await bot.fetch_user(userIDBad)

        embed = discord.Embed(
            colour=discord.Colour.blue(),
            title="Social Credit Rankings"
        )

        embed.add_field(name="**Highest Credit Score**", value=f"{userPos.name}\n {round(scoreGood, 2)}")
        embed.add_field(name="**Lowest Credit Score**", value=f"{userNeg.name}\n {round(scoreBad, 2)}")

        await interaction.response.send_message(embed=embed)

bot.run(TOKEN)