import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
from bs4 import BeautifulSoup

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

# Lista delle voci suggerite (puoi ampliarla)
voci_wiki = [
    "Califfato di Linuxia",
    "Secondo Impero Rulboriano",
    "Guerra Gacha",
    "OSV",
    "Ropentiumal",
    "Wikicord"
]

# Evento di avvio
@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
        print(f"✅ Bot avviato come {bot.user}")
    except Exception as e:
        print(f"Errore nella sincronizzazione: {e}")

# Autocomplete per le voci
async def autocomplete_voce(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name=voce, value=voce)
        for voce in voci_wiki if current.lower() in voce.lower()
    ][:10]  # massimo 10 suggerimenti

# Comando /cerca
@bot.tree.command(name="cerca", description="Cerca una voce su Wikicord")
@app_commands.describe(voce="Titolo della voce da cercare")
@app_commands.autocomplete(voce=autocomplete_voce)
async def cerca(interaction: discord.Interaction, voce: str):
    await interaction.response.defer()

    url = f"https://wikicord.wikioasis.org/wiki/{voce.replace(' ', '_')}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                await interaction.followup.send(f"❌ Voce \"{voce}\" non trovata.")
                return

            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            content = soup.find("div", {"class": "mw-parser-output"})
            if not content:
                await interaction.followup.send("⚠️ Contenuto non trovato nella voce.")
                return

            paragrafi = []
            for tag in content.find_all(["p", "ul"], recursive=False):
                text = tag.get_text(separator=" ", strip=True)
                if text:
                    paragrafi.append(text)
                if len(paragrafi) >= 3:
                    break

            if not paragrafi:
                await interaction.followup.send("📭 Nessun contenuto utile trovato.")
                return

            testo = "\n\n".join(paragrafi)
            if len(testo) > 1000:
                testo = testo[:1000].rsplit(".", 1)[0] + "."

            embed = discord.Embed(
                title=f"{voce}",
                description=testo,
                color=discord.Color.red()
            )
            embed.set_footer(text="Fonte: wikicord.wikioasis.org")

            await interaction.followup.send(embed=embed)

# Inserisci qui il token del bot
bot.run("MTM4Nzk0MDI4NzY0NDQzODY1OA.GkFENL.YreG4ZZlsCVpEqd4LOJT3BkDA9BrNoLd9mEd3M")
