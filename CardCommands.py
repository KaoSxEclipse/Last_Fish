import csv
import random

import discord
from discord import app_commands
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    case_insensitive=True,
    Activity="Playing LastFish",
)


class CardSearch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.card_names = set()

        with open("cards.csv", "r") as csvfile:
            reader = csv.DictReader(csvfile)
            self.card_names = set([row["Name"] for row in reader])

    @commands.hybrid_command(name="card", description="View a Card!")
    async def card(self, ctx, *, lookup):
        print(f"Card name: {lookup}")
        # Load CSV
        with open("cards.csv", "r") as file:
            reader = csv.DictReader(file)
            # Search CSV and Generate Embed
            for row in reader:
                if row["Name"].lower() == lookup.lower():
                    embed = discord.Embed(title=row["Name"])
                    embed.set_image(url=row["Art"])
                    embed.add_field(
                        name="Description", value=row["Description"], inline=False
                    )
                    embed.set_footer(text=row["FlavorText"])
                    embed.add_field(name="Type", value=row["CardType"], inline=True)
                    embed.add_field(name="Artist", value=row["Artist"], inline=False)
                    embed.set_thumbnail(url=row["Icon"])

                    color = int(row["Border"][1:], 16)
                    embed.colour = discord.Colour(color)
                    await ctx.send(embed=embed)
                    break
            # If card not found -> Send Error embed.
            else:
                embed = discord.Embed(
                    title="**Uh Oh!**",
                    description="Something went wrong!",
                    color=0xFF2027,
                )
                embed.add_field(
                    name="__Try__",
                    value=f"•Make sure the Card Name is not in quotes.\n•Check your spelling\n•Make sure it is a valid card",
                )
                embed.set_footer(
                    text="Contact KaoSxEclipse#0111 if it still isn't working."
                )
                await ctx.send(embed=embed)

    @card.autocomplete("lookup")
    async def cardname_autocomplete(
        self,
        ctx,
        cardname: str,
    ) -> list[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=name, value=name)
            for name in self.card_names
            if cardname.lower() in name.lower()
        ]

    @commands.hybrid_command(name="randcard", aliases=["rc"])
    async def randcard(self, ctx):
        cards = []
        with open("cards.csv") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                cards.append(row)
        card = random.choice(cards)
        embed = discord.Embed(title=card["Name"])
        embed.set_image(url=card["Art"])
        embed.add_field(name="Description", value=card["Description"], inline=False)
        embed.set_footer(text=card["FlavorText"])
        embed.add_field(name="Type", value=card["CardType"], inline=True)
        embed.add_field(name="Artist", value=card["Artist"], inline=False)
        embed.set_thumbnail(url=card["Icon"])
        color = int(card["Border"][1:], 16)
        embed.colour = discord.Colour(color)
        await ctx.send(embed=embed)
