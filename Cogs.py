import asyncio

import discord, logging
from discord.ext import *
from discord import *
from discord.ext import commands
from discord.ext.commands import *
from typing import Optional, Literal
import json


devids = [301494278901989378]


# bot intents / privileges
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.reactions = True
bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    case_insensitive=True,
    Activity="Playing LastFish",
)


# Set up Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()],
)
logger = logging.getLogger()
# Create the help embed -> Removed DPy's automatic one as we don't need it.


# Nested Dictionary with the Select options and Embed Information

rulebook_pages = {
    "Keywords & Card Types": {
        "title": "Keywords and Card Types!",
        "description": "There are **12** Total Keywords and **7** Card Types\n   ",
        "information": "Each card uses different keywords, follow the instructions on the sheet below for the keyword specified. \n __Card types__ are also listed below."
        "\n <:5:1069133378890244106> **Instants** can be used anytime the effect is applicable *and* the  Encounter Card Resolves.\n"
        "<:1:1069133377099280414> **Spells** can be played both *Before* and/or *After* Item/Attack cards, you may play as many Spell cards as you want on your turn. \n"
        "<:2:1069133382170198068> **Curses** are similar to spells but only *1* may be played. They have two abilities and to use the 'Secondary' ability you must sacrifice HP. Players may not use *Attack* or *Curse* cards on their first turn\n"
        "<:3:1069133380635070494> **Encounter** cards are random events that a **CHAMPION** might face. They are able to affect a myriad of players at once and effects may vary.",
        "image": "https://i.imgur.com/rFiUSD0.png",
    },
    "Turn Actions": {
        "title": "Turn Actions",
        "description": "What to do and when.",
        "information": "What can I do on my turn and when do I do it?\n"
        "**__Turn Actions__**\n: -> Each player starts with **5** cards."
        "**1.** **DRAW** a card from the *Draw* deck and add it to your hand.\n"
        "**2.** **DISCOVER** a card from the *Encounter* deck and follow it's effect then discard it to the Encounter Discard Pile.\n"
        "**3.** Perform *Any* or *All* of the following actions.\n"
        "    i. Use as many *Spells* as you want\n"
        "    ii. Use as many *Instants* as you want\n"
        "    iii. Play One *Curse* Card\n"
        "    iiii. **EQUIP** an *Item* to your Champion OR *Attack* an opposing player.\n"
        "OR **DRAW** until you have 5 cards. If you already have 5 or more, draw 1.\n"
        "    *Play Continues Clockwise.*",
        "image": "https://i.imgur.com/ibbehYA.png",
    },
    "SetUp": {
        "title": "Setup and Cards",
        "description": "What do I do with all these cards?",
        "information": "**__Player Cards__**\n"
        "From Left to Right -> Champion Card, HP Cards stacked together, Equiptment/Item Cards.\n"
        "\n **__Table Cards__**\n"
        "Draw and Encounter Decks in the middle, respective discard piles on the *outside* of each deck.\n",
        "image": "https://i.imgur.com/M2QBvG5.png",
    },
    "Card Notation": {
        "title": "Card Notation",
        "description": "**__What do these things mean?__**",
        "information": "**Card Type** refers to whether it's an: *Instant, Item, Spell, Curse, Encounter, Champion,* or *Attack* (Affetcs Border Color)\n"
        "**Ability Text** explains card effects and when to perform them.\n"
        "**Flavor Text** Short blurb of lore\n"
        "**Artist's Stamp** refers to the artist who made the card art -> See /Credits.",
        "image": "https://i.imgur.com/wyM4gEW.png",
    },
    "Misc": {
        "title": "Misc.",
        "description": "**__Additional Rulings__**",
        "information": "**1.** All forms of damage can be blocked by *Item* cards, **except** for *direct* damage or damage that bypasses items and attacks HP directly.\n"
        "--> All *Items* block **1** damage point.\n"
        "**2.** The *Spell* 'Duplication' plays an additional copy of the card it's paired with when played.\n"
        "--> Even if one copy is **NEGATED** the other copy will still exist and peform the effect.\n"
        "**3.** Any card that says *you may...* means the effect is optional if you choose to use it.\n"
        "**4. **Whenever a card has you draw from the *discard pile* you **must** reveal the chosen card to the other players\n"
        "**5.** When a player must **GIFT** another player a card, they are not required to reveal it.\n"
        "**6.** __Chaining__\n"
        "A chain determines the order in which to resolve card conflicts. A general rule is cards in a chain resolve one by one starting with the last one played.\n"
        "--> EX: An *Instant* played after an *Attack* card nullifes the *Attack* card.\n"
        "**7.** Players may look through either discard pile at any time.",
        "image": None,
    },
    "Remaining Card Types": {
        "title": "**__Remaining Card Types__**",
        "description": "",
        "information": "<:4:1069133383545925663> **Champion** cards are used to represent your character in the game.\n"
        "--> Each Champion has a *Signature* card(s) in the *Draw* deck, if you draw your Champions signature card you may apply the bonus effect listed on your champions **Ability Text** when you play the signature card.\n"
        "<:7:1069134744392060928> **Attack** cards are the primary way to deal damage. Only one *Attack* card may be used on your turn so long as you have not played an *Item* card\n"
        "--> Some cards may allow for multple *Attack* cards to be played, or even an *Item* card and an *Attack* card on the same turn.\n"
        "<:6:1069133379758456862> **Items** are cards that can be equipped to your **CHAMPION** to protect from damage and offer other affects.\n"
        "--> *Items* are **DRESTROYED** after blocking damage, and *all* items block (1) point of damage, unless the attacking card bypasses *items* or directly damages *HP*. Max of **3** *Items* equipped at a time.",
        "image": "https://i.imgur.com/j4ZGYuy.png",
    },
    "Card-Based Combat": {
        "title": "Attack",
        "description": "**__How do I attack?__**",
        "information": "__Example__:\n"
        "Kaos uses **Frozen Spear** a *1* damage **ATTACK** card on Rico. Rico may now, use an *Instant* card, and/or **DESTORY** one of Kaos' items (unless a card states otherwise or specifies which item) per point of damage taken.\n"
        "If Rico has no more *Instants* or more *Items* to protect himself with. He takes the non-negated damage points to his **HP** and flips that many *Heart* cards face down.\n"
        "--> Once all of a players *Heart* cards are face down they have been eliminated. Send all of the cards in their hand to the *Discard* pile.",
        "image": "https://i.imgur.com/FucD2kb.png",
    },
}
# Emojis from JSON
with open("CustomEmoji", "r") as f:
    emojis = json.load(f)
    for key, value in emojis.items():
        exec(f"{key} = '{value}'")


class Rulebook(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Main Rulebook Command
    @commands.hybrid_command(
        name="rulebook", description="Load an Interactive LastFish! Rulebook and Guide!"
    )
    async def rulebook(self, ctx):
        """An interactive rulebook and guide!"""

        # Creates DropDown menu + Options
        class Dropdown(discord.ui.Select):
            def __init__(self):
                options = [
                    discord.SelectOption(
                        label="Keywords & Card Types",
                        description="Need help with the keyterms and card types?",
                    ),
                    discord.SelectOption(
                        label="Remaining Card Types",
                        description="Champions, HP cards, Items, etc.",
                    ),
                    discord.SelectOption(
                        label="SetUp", description="What do I do with all these cards?"
                    ),
                    discord.SelectOption(
                        label="Turn Actions", description="What to do and When."
                    ),
                    discord.SelectOption(
                        label="Card-Based Combat", description="Attacking How-To's"
                    ),
                    discord.SelectOption(
                        label="Card Notation",
                        description="Understanding what's on the card.",
                    ),
                    discord.SelectOption(
                        label="Misc", description="Additional Rulings and Information."
                    ),
                ]

                super().__init__(
                    placeholder="Please Select a Page",
                    min_values=1,
                    max_values=1,
                    options=options,
                )

            # Gets user Selected option and returns it as an Embed
            async def callback(self, interaction: discord.Interaction):
                selected_option = self.values[0]
                information = rulebook_pages[selected_option]["information"]
                for option in self.options:
                    if option.label == selected_option:
                        embed = discord.Embed(
                            title=option.label,
                            description=option.description,
                            color=6750182,
                        )
                        embed.add_field(name="", value=information)
                        embed.set_image(
                            url=rulebook_pages.get(option.label, {}).get("image", None)
                        )
                await interaction.response.send_message(embed=embed, ephemeral=True)

        # TBH idek Discord Dropdown Shenanigans
        class DropdownView(discord.ui.View):
            def __init__(self):
                super().__init__()

                # Adds the dropdown to our view object.
                self.add_item(
                    Dropdown(),
                )

        logger.info("Command Invoked")
        # Creates and Sends Beginning Embed from /rulebook command
        welcome_embed = discord.Embed(
            title="Welcome to the Rulebook",
            description=(f"{players}2-6 Players \n {clock}Gametime: 10-60 minutes"),
            color=discord.Color.teal(),
        )
        welcome_embed.add_field(
            name=f"__**Getting Started**__\n",
            value=f"First, separate all the cards by their differing backs and hand each player a *Rule  Reference* card\n"
            f"Next, shuffle the 'Draw' and 'Encounter' Decks Separately, use the areas next to each deck respectively as discard piles.",
            inline=False,
        )
        welcome_embed.add_field(
            name="**__Who Goes First?__**",
            value=(
                f"Play Rock, Paper, Scissors or your own fun game to decide who goes first! The winner picks their Champion first. Play continues to the left."
            ),
        )
        welcome_embed.set_footer(
            text="Box Contains: 1 Draw Deck, 1 Encounter Deck, 8 Champion Cards, 18 Heart Cards, and 6 Rule Reference Cards"
        )

        view = DropdownView()
        message = await ctx.send(embed=welcome_embed, view=view, ephemeral=True)
        await asyncio.sleep(180)
        await message.delete()


# Sync command -> More discord Shenanigans to update slash commands after creation or edits.


class syncCog(commands.Cog):
    @commands.command(
        description="Syncs all commands globally. Only accessible to developers."
    )
    async def sync(
        self,
        ctx: Context,
        guilds: Greedy[discord.Object],
        spec: Optional[Literal["~", "*", "^"]] = None,
    ) -> None:
        if ctx.author.id != 301494278901989378:
            return

        embed = discord.Embed(description="Syncing...", color=discord.Color.red())
        await ctx.send(embed=embed)
        print("Syncing...")
        if not guilds:
            if spec == "~":
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await ctx.bot.tree.sync()

            await ctx.send(
                embed=discord.Embed(
                    description=f"Synced `{len(synced)}` commands {'globally' if spec is None else 'to the current guild.'}.",
                    color=discord.Color.green(),
                )
            )
            print("Synced.")
            return

        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(
            embed=discord.Embed(
                description=f"Synced the tree to {ret}/{len(guilds)}.", color=self.color
            )
        )
        print("Synced.")


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="help", description="Feeling Lost?")
    async def help(self, ctx):
        HelpEmb = discord.Embed(
            title="Need a hand?",
            description="Here's a list of possible commands",
            color=0x7EA3FD,
        )
        HelpEmb.add_field(
            name="",
            value=f"{windrose} **/Rulebook** or *!rulebook*\n"
            f"{windrose} **/Card** or *!card <Card Name>*\n"
            f"{windrose} **/Suggest**\n"
            f"{windrose} **/PlayerSelect**\n"
            f"{windrose} **/Credits** or *!credits*\n"
            f"{windrose} **/About** or *!about*\n"
            f"{windrose} [LastFish Tutorial](https://youtu.be/P0x7oRNzuJM)\n"
            f"{windrose} **!lore** or **!readings**",
        )

        await ctx.send(embed=HelpEmb)

    @commands.hybrid_command(
        name="lore",
        description="Links to all the last fish lore readings!",
        aliases=["readings"],
    )
    async def lore(self, ctx):
        LoreEmbd = discord.Embed(
            title="__Lore Readings__", description="", color=0x7EA3FD
        )
        LoreEmbd.set_footer(
            text="WARNING: This takes you off Discord to Twitter. Please Verify the official twitter website."
        )
        LoreEmbd.add_field(
            name="•─────⋅☾ ☽⋅─────•",
            value="[Prologue](https://twitter.com/thegreatpond/status/1613580028788314114?s=20)\n[Book 1](https://twitter.com/thegreatpond/status/1592683748931223552?s=20)\n[Book 2 Pt. 1](https://twitter.com/venomistic736/status/1618764646433046528?s=20)\n[Book 2 Pt. 2](https://twitter.com/thegreatpond/status/1621295986864979968?s=20)",
        )
        await ctx.send(embed=LoreEmbd)
