# -*- coding: utf-8 -*-
import disnake
from disnake.ext import commands
from utils.client import BotCore

class GuideView(disnake.ui.View):
    def __init__(self, bot: BotCore):
        super().__init__(timeout=None)
        self.bot = bot
        # Nome do arquivo que vamos anexar
        self.banner_name = "dracofy_guide_banner.png"

    def main_embed(self):
        embed = disnake.Embed(
            title="🐉 Central de Ajuda DracoFy DJ",
            description=(
                "Bem-vindo ao manual oficial do **DracoFy DJ**! Aqui você encontrará tudo o que precisa "
                "para dominar a música no seu servidor.\n\n"
                "**Como navegar:**\n"
                "Utilize os botões abaixo para explorar as categorias de comandos."
            ),
            color=0x2ecc71
        )
        embed.add_field(name="🚀 Início Rápido", value="Para tocar sua primeira música, digite `/play` seguido do nome ou link.", inline=False)
        # Referenciando o anexo
        embed.set_image(url=f"attachment://{self.banner_name}")
        embed.set_footer(text="DracoFy DJ - Sinta o Poder do Som")
        return embed

    @disnake.ui.button(label="Essencial", style=disnake.ButtonStyle.green, emoji="🎵")
    async def essential(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        embed = disnake.Embed(
            title="🎵 Comandos Essenciais",
            description="Estes são os comandos que você mais usará no dia a dia.",
            color=0x2ecc71
        )
        embed.add_field(name="/play [musica]", value="Busca e toca uma música (YouTube, Spotify, etc).", inline=True)
        embed.add_field(name="/skip", value="Pula para a próxima música da fila.", inline=True)
        embed.add_field(name="/stop", value="Para a música e limpa a fila.", inline=True)
        embed.add_field(name="/pause / resume", value="Pausa ou continua a reprodução atual.", inline=True)
        embed.add_field(name="/queue", value="Mostra a lista de músicas que serão tocadas.", inline=True)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        await interaction.response.edit_message(embed=embed)

    @disnake.ui.button(label="Controles", style=disnake.ButtonStyle.blurple, emoji="🎚️")
    async def controls(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        embed = disnake.Embed(
            title="🎚️ Ajustes e Controles",
            description="Comandos para ajustar a experiência sonora.",
            color=0x3498db
        )
        embed.add_field(name="/volume [0-150]", value="Ajusta o volume do robô.", inline=True)
        embed.add_field(name="/loop", value="Alterna entre repetir a música ou a fila inteira.", inline=True)
        embed.add_field(name="/shuffle", value="Mistura as músicas da fila atual.", inline=True)
        embed.add_field(name="/seek [tempo]", value="Pula para um minuto específico da música.", inline=True)
        embed.add_field(name="/lyrics", value="Busca a letra da música atual.", inline=True)
        await interaction.response.edit_message(embed=embed)

    @disnake.ui.button(label="Extras", style=disnake.ButtonStyle.grey, emoji="✨")
    async def extras(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        embed = disnake.Embed(
            title="✨ Recursos Extras",
            description="Funcionalidades avançadas para usuários frequentes.",
            color=0x95a5a6
        )
        embed.add_field(name="/favs", value="Gerencia suas músicas favoritas para tocar rápido.", inline=True)
        embed.add_field(name="/filters", value="Aplica efeitos como Bassboost, Nightcore, etc.", inline=True)
        embed.add_field(name="/now_playing", value="Mostra detalhes e a barra de progresso da música.", inline=True)
        embed.add_field(name="/save", value="O bot envia o nome da música atual no seu PV.", inline=True)
        await interaction.response.edit_message(embed=embed)

    @disnake.ui.button(label="Voltar", style=disnake.ButtonStyle.red, emoji="🏠")
    async def home(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.edit_message(embed=self.main_embed())

import os

class Guide(commands.Cog):
    def __init__(self, bot: BotCore):
        self.bot = bot
        # Caminho dinâmico para funcionar em qualquer pasta
        self.banner_path = os.path.join(os.getcwd(), "assets", "guide_banner.png")

    @commands.slash_command(
        name="guia_setup",
        description="[Admin] Envia o manual de uso do DracoFy DJ neste canal.",
        default_member_permissions=disnake.Permissions(manage_guild=True)
    )
    async def guia(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=True)
        view = GuideView(self.bot)
        
        # Criando o arquivo para anexo
        file = disnake.File(self.banner_path, filename=view.banner_name)
        
        await inter.edit_original_message(content="✅ **Manual do DracoFy DJ gerado com sucesso!**")
        await inter.channel.send(file=file, embed=view.main_embed(), view=view)

def setup(bot: BotCore):
    bot.add_cog(Guide(bot))
