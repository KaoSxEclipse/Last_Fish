import discord, logging
from discord.ext import *
from discord import *
from discord.ext import commands
from discord.ext.commands import *
from typing import Optional, Literal
import json
from discord import app_commands
import traceback
import random

intents = discord.Intents.all()
bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    case_insensitive=True,
    Activity="Playing LastFish",
)


class PlayerModal(discord.ui.Modal, title="Enter Player Names"):
    def __init__(self):
        super().__init__()

        self.textbox = discord.ui.TextInput(
            label="Enter player names separated by commas",
            placeholder="e.g. John Doe, Jane Smith, Bob Johnson",
            min_length=1,
            max_length=2000,
        )
        self.add_item(self.textbox)

    async def on_submit(self, interaction: Interaction):
        player_names = self.textbox.value.split(",")
        player_names = [name.strip() for name in player_names]
        if len(player_names) < 2:
            minemb = discord.Embed(
                title="Not Enough Players",
                description="You need atleast two player to play LastFish!",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=minemb, ephemeral=True)
            return
        if len(player_names) > 8:
            maxemb = discord.Embed(
                title="Too many players",
                description="The maximum amount of players is 8",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=maxemb, ephemeral=True)

        if any([not name.strip() for name in player_names]):
            blankname = discord.Embed(
                title="Name Error",
                description="Please make sure your format is Player 1, Player 2 ETC.",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=blankname, ephemeral=True)
            return

        first_player = random.choice(player_names)
        SelectionEmb = discord.Embed(
            title="Selected Player:", description="", color=6750182
        )
        SelectionEmb.add_field(
            name=f"__**{first_player}**__",
            value=f"Play will continue clockwise starting with {first_player}",
        )
        await interaction.response.send_message(embed=SelectionEmb)


class PlayerSelect(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="playerselect", description="Have the bot choose the starting player."
    )
    async def playerselect(self, interaction: discord.Interaction):
        await interaction.response.send_modal(PlayerModal())


class SuggestionModal(discord.ui.Modal, title="Bot Suggestion Form"):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

        self.SuggestionInput = discord.ui.TextInput(
            min_length=1,
            max_length=2000,
            placeholder="Enter your suggestion here...",
            label="Suggestion",
        )

        self.add_item(self.SuggestionInput)

    async def on_submit(self, interaction: discord.Interaction):
        suggestion = self.SuggestionInput.value
        user = interaction.user
        content = f"New suggestion from {user.mention} \n \n {suggestion}"
        recipient = await self.bot.fetch_user(301494278901989378)
        dm = await recipient.create_dm()
        await dm.send(content)
        SuggEmb = discord.Embed(
            title="Suggestion Sent", description="", color=discord.Color.green()
        )
        SuggEmb.add_field(
            name="",
            value="Thank you for your suggestion! This may or may not be added but any ideas are appreciated!",
        )

        await interaction.response.send_message(embed=SuggEmb, ephemeral=True)


class Suggestion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="suggest", description="Send an idea what should be added to the bot!"
    )
    async def suggest(self, interaction: discord.Interaction):
        await interaction.response.send_modal(SuggestionModal(self.bot))
