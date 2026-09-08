# Discord bot that scores every message's sentiment and tracks a running
# "social credit" karma total per user, per server.
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from bigbrotherdatabase import init_db, get_user, record_message, minKarma, maxKarma
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# VADER's lexicon is baked into the Docker image at build time (see Dockerfile).
# nltk.data.find() checks whether it's already present before hitting the network,
# so a normal restart doesn't re-download it every time.
try:
    nltk.data.find('sentiment/vader_lexicon/vader_lexicon.txt')
except LookupError:
    nltk.download('vader_lexicon')

intents = discord.Intents.default()
intents.message_content = True

class BigBrotherBot(commands.Bot):
    async def setup_hook(self):
        # Runs once, before the bot connects to Discord's gateway - the right
        # place to set up the async DB connection pool.
        await init_db()

bot = BigBrotherBot(command_prefix="!", intents = intents, activity=discord.Activity(type=discord.ActivityType.listening, name="every conversation."))

analyzer = SentimentIntensityAnalyzer()

def sentiAnaly(msg):
    # VADER's "compound" score is already normalized to [-1, 1]; scale it up to
    # [-10, 10] so karma deltas feel more meaningful than tiny decimals.
    score = analyzer.polarity_scores(msg)
    print(f"{score}")
    return round(score['compound'] * 10, 2)

@bot.event
async def on_ready():
    # Re-syncs slash commands with Discord on every reconnect, not just first
    # startup - harmless at this bot's scale, just not strictly necessary.
    await bot.tree.sync()
    print(f"{bot.user} is online!")

#on every message that is sent it checks its value and adds it to correct entry in db
@bot.event
async def on_message(msg):
    if msg.author.bot or msg.guild is None:
        return  # ignore other bots and DMs (DMs have no msg.guild)

    serverid = msg.guild.id
    userid = msg.author.id

    karmaDelta = sentiAnaly(msg.content)

    await record_message(userid, serverid, karmaDelta)

#command to return sql entry data
@bot.tree.command(name="whatismysocialcreditscore", description="Lets you learn your faults by revealing your karma.")
async def whatismysocialcreditscore(interaction: discord.Interaction):
    userid = interaction.user.id
    serverid = interaction.guild.id
    serverName = interaction.guild.name

    user = await get_user(userid, serverid)

    if user is None:
        await interaction.response.send_message("You are currently not in our system. Get in line.")
    else:
        embed = discord.Embed(
        colour=discord.Colour.blue(),
        description=f"This is a report of your social credit and the number of messages sent in {serverName}.",
        title="Social Credit Report"
        )

        numMessages = user[2]
        score = user[3]

        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)

        embed.add_field(name="**UserID**", value=userid)
        embed.add_field(name="**Number of Messages**", value=numMessages)
        embed.add_field(name="**Social Credit Score**", value=round(score, 2))

        if score >= 0:
            embed.set_footer(text="You are doing your server proud by being a nice and productive citizen of society.")
        else:
            embed.set_footer(text="You will be leaving this earth at some point, I do not believe you will like where you are going. Check yourself.")

        await interaction.response.send_message(embed=embed)

# reports the highest- and lowest-karma users in the current server
@bot.tree.command(name="socialcreditranking", description="Lets learn the greatest and worst of this world.")
async def socialcreditranking(interaction: discord.Interaction):
    serverid = interaction.guild.id

    maxRow = await maxKarma(serverid)
    minRow = await minKarma(serverid)

    if maxRow is None or minRow is None:
        await interaction.response.send_message("There are not enough entries to rank them.")
        return
    else:

        userIDGood = maxRow[0]
        userIDBad = minRow[0]

        scoreGood = (await get_user(userIDGood, serverid))[3]
        scoreBad = (await get_user(userIDBad, serverid))[3]

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
