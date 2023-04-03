import asyncio
import random
from discord.ext import tasks
from dotenv import load_dotenv
import os, sys, json
from Cogs import *
from CardCommands import CardSearch
import discord
from discord import *
import logging
from discord.ext import commands
from Modals import PlayerSelect, Suggestion

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    case_insensitive=True,
    Activity="Playing LastFish",
)
bot.help_command = None
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(level    qname)s - %(message)s",
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()],
)

logger = logging.getLogger()
bot.help_command = None
load_dotenv()
TOKEN = os.getenv("LastFish")


# Loads Cogs When bot gets initiated
@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    await bot.add_cog(Rulebook(bot))
    await bot.add_cog(syncCog(bot))
    await bot.add_cog(about(bot))
    await bot.add_cog(CardSearch(bot))
    await bot.add_cog(PlayerSelect(bot))
    await bot.add_cog(Suggestion(bot))
    await bot.add_cog(Help(bot))
    statusloop.start()


with open("reminder_config", "r") as f:
    reminder_config = json.load(f)


async def send_reminder():
    while reminder_config["reminder_toggle"]:
        rem_channel = await bot.fetch_channel(942891846949011516)
        message = discord.Embed(
            title=f"Important Reminders", description="", color=discord.Color.teal()
        )
        message.add_field(
            name="**__Kickstarter__**",
            value="Thank you all! We had **538** supporters and raised $*25,220* out of our $*10,000* goal!",
        )
        message.add_field(
            name="**__Shipping__**",
            value="All orders should be shipped by the end of July!",
        )
        message.set_image(url="https://i.imgur.com/v7xfUZv.png")
        message.set_footer(
            text=f"*Shipping date may be inaccurate. Please confirm with Sage Max or Rico.*",
            icon_url=bot.user.avatar,
        )
        await rem_channel.send(embed=message)
        # gets a random numner 8 -> 24 then multiplies it by 3600 to turn the into that many hours. (Asyncio takes seconds) 
        time_delay = random.randint(8, 24) * 3600
        formatted = time_delay / 3600
        logger.info(f"Waiting {formatted} hours before next reminder.")
        await asyncio.sleep(time_delay)



@bot.command()
async def reminder(ctx, toggle: str):
    if ctx.author.id not in [301494278901989378, 106082367847858176, 549321165441597447]:
        logger.info(f'{ctx.author.id} has attempted to toggle the reminder.')
        return
    else:
        if toggle.lower() == "on":
            reminder_config["reminder_toggle"] = True
            enabled = discord.Embed(title="Reminder Enabled", description="", color=discord.Color.teal())
            await ctx.send(embed=enabled, ephemeral=True)
            # Start the reminder loop
            await bot.loop.create_task(send_reminder())
        elif toggle.lower() == "off":
            reminder_config["reminder_toggle"] = False
            disabled = discord.Embed(title="Reminder Disabled", description="", color=discord.Color.red())
            await ctx.send(embed=disabled, ephemeral=True)
        else:
            await ctx.send("Invalid argument. Please use `on` or `off`.")

    # Save reminder config to file
    with open('reminder_config.json', 'w') as f:
        json.dump(reminder_config, f)



# Dev only, turns off bot in case of double instances or bugs / I can't get to my laptop
@bot.command()
async def terminate(ctx):
    if ctx.author.id != 301494278901989378:
        return
    else:
        await ctx.send("Terminating the bot")
        logger.info(f" {ctx.message.author} has terminated {bot.user.name}")
        await bot.close()
    # About Embed Command


class about(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="about", description="Information about the Bot", usage="!about or /about"
    )
    async def about(self, ctx):
        embed = discord.Embed(
            title=f"{bot.user} | About",
            description=f"{bot.user.mention} was made to explain and guide Last Fish! players through the game",
            color=6750182,
        )
        KaoSxEclipse = bot.get_user(301494278901989378)
        version = "3.5.1"
        arrow = "<:KaoArrow:1068047981309345852>"
        discordlogo = "<:discordlogo:1068760141954023505>"
        support = "<:tools:1068752038122504293>"
        pythonlogo = "<:pythonlogo:1068760140389560320>"

        information = (
                f"{arrow} **Developer:** {KaoSxEclipse}\n"
                + f"{arrow} **Python:** 3.9.7\n"
                + f"{arrow} **Pycharm** 2022.3.2\n"
                + f"{arrow} **Latency:** {round(bot.latency * 1000)} ms\n"
                + f"{arrow} **Version:** {version}"
        )
        links = (
                f"{arrow} **Library:** {pythonlogo} [discord.py 2.1.0](https://github.com/Rapptz/discord.py)\n"
                + f"{arrow} **Support:** {support} [Click me](https://twitter.com/KaoSxEclipseYT)\n"
                + f"{arrow} **Whiskers Discord:** {discordlogo} [Click me](https://discord.gg/thegreatpond)"
        )
        embed.add_field(name="__Information__", value=information, inline=False)
        embed.add_field(name="__Links__", value=links, inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="credits", description="Card Art Credits")
    async def Credits(self, ctx):
        embed = discord.Embed(title="**Credits and Notable Mentions**", description="")
        embed.add_field(
            name="Artists",
            value="[Cliff Elivert](https://twitter.com/cliffBallin), [Zwistillus](https://twitter.com/Zwistillus), [Winnie Liu](https://twitter.com/winniestudio), [CheeryBee](https://twitter.com/HanhTran1112)",
        )

        await ctx.send(embed=embed, ephemeral=True)


@tasks.loop(minutes=2.0)
async def statusloop() -> None:
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(type=discord.ActivityType.playing, name=f"LastFish!"),
    )
    await asyncio.sleep(30)
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(type=discord.ActivityType.watching, name="!help"),
    )
    await asyncio.sleep(30)
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(
            type=discord.ActivityType.watching, name="Rico shuffle the decks"
        ),
    )
    await asyncio.sleep(30)
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(
            type=discord.ActivityType.custom, name="Reading the !Rulebook"
        ),
    )
    await asyncio.sleep(30)


# Runs the but using the TOKEN variable from os.getenv("LastFish")
bot.run(TOKEN)
