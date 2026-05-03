from __future__ import annotations

from typing import TYPE_CHECKING, Union, Optional

import disnake
from disnake.ext import commands

from utils.music.errors import GenericError
from utils.others import CustomContext

if TYPE_CHECKING:
    from utils.client import BotCore

category_icons = {
    "Música": "🎶",
    "Configurações": "🛠️",
    "Diversos": "🧩",
    "Ajuda": "❓"
}


class ViewHelp(disnake.ui.View):

    def __init__(self, ctx, items, *, get_cmd, main_embed, cmd_list, category_cmd=None, timeout=180):
        self.message: Optional[disnake.Message] = None
        self.page_index = 0
        self.cmd_lst = cmd_list
        self.category = category_cmd
        self.get_cmd = get_cmd
        self.items = items
        self.ctx = ctx
        self.main_embed = main_embed
        self.first_embed = main_embed
        super().__init__(timeout=timeout)
        self.process_components()

    async def interaction_check(self, interaction: disnake.Interaction):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message(f"🚫 Apenas {self.ctx.author.mention} pode usar este menu.", ephemeral=True)
            return False
        return True

    def process_components(self):
        options = []
        for category, emoji in self.items:
            options.append(disnake.SelectOption(
                label=category, value=category, emoji=emoji, 
                description=f"Comandos de {category}"
            ))

        if options:
            sel = disnake.ui.Select(placeholder='📂 Selecione uma categoria...', options=options, custom_id="help_select")
            sel.callback = self.callback_help
            self.add_item(sel)

        # Botão Home
        home_btn = disnake.ui.Button(label="Início", emoji="🏠", style=disnake.ButtonStyle.blurple, custom_id="home_btn")
        home_btn.callback = self.callback_home
        self.add_item(home_btn)

        if self.category:
            if len(self.cmd_lst[self.category]['cmds']) > 1:
                back = disnake.ui.Button(emoji="⬅️", style=disnake.ButtonStyle.grey)
                back.callback = self.callback_left
                self.add_item(back)

                forward = disnake.ui.Button(emoji="➡️", style=disnake.ButtonStyle.grey)
                forward.callback = self.callback_right
                self.add_item(forward)

    async def callback_home(self, interaction: disnake.MessageInteraction):
        self.category = None
        self.page_index = 0
        self.clear_items()
        self.process_components()
        await interaction.edit_original_message(embed=self.first_embed, view=self)

    async def callback_left(self, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        self.page_index = (self.page_index - 1) % len(self.cmd_lst[self.category]['cmds'])
        await self.response(interaction)

    async def callback_right(self, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        self.page_index = (self.page_index + 1) % len(self.cmd_lst[self.category]['cmds'])
        await self.response(interaction)

    async def callback_help(self, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        self.category = interaction.values[0]
        self.page_index = 0
        self.clear_items()
        self.process_components()
        await self.response(interaction)

    async def response(self, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        embed = await self.get_cmd(
            ctx=self.ctx,
            index=self.page_index,
            cmds=self.cmd_lst[self.category]['cmds'],
            emoji=self.cmd_lst[self.category]['emoji'],
            category=self.category
        )
        await interaction.response.edit_message(embed=embed, view=self)


async def check_perms(ctx: CustomContext, cmd: commands.Command):
    try:
        if cmd.hidden and not await ctx.bot.is_owner(ctx.author):
            return False
    except:
        return False
    return True


class HelpCog(commands.Cog, name="Ajuda"):

    def __init__(self, bot: BotCore):
        self.bot = bot
        bot.remove_command("help")
        self.emoji = "❓"

    async def get_cmd(self, ctx, cmds, index=0, category=None, emoji=None):
        cmd = cmds[index]
        prefix = ctx.prefix if str(ctx.me.id) not in ctx.prefix else f"@{ctx.me.display_name} "
        
        embed = disnake.Embed(
            title=f"{emoji} Categoria: {category}",
            color=0x2f3136 # Cor Premium Dark
        )
        
        embed.add_field(name="⌨️ Comando", value=f"`{prefix}{cmd.name}`", inline=True)
        
        if cmd.aliases:
            embed.add_field(name="🔄 Atalhos", value=f"`{'`, `'.join(cmd.aliases)}`", inline=True)
            
        embed.add_field(name="📝 Descrição", value=cmd.description or "Sem descrição disponível.", inline=False)

        if cmd.usage:
            usage = cmd.usage.replace("{prefix}", prefix).replace("{cmd}", cmd.name)
            embed.add_field(name="📘 Como usar", value=f"```\n{usage}```", inline=False)
            
        if hasattr(cmd, 'commands'):
            subs = ", ".join([c.name for c in cmd.commands if (await check_perms(ctx, c))])
            if subs:
                embed.add_field(name="🔢 Subcomandos", value=f"`{subs}`", inline=False)

        embed.set_author(name=f"Guia do {self.bot.user.name}", icon_url=self.bot.user.display_avatar.url)
        embed.set_footer(text=f"Página {index + 1} de {len(cmds)} | Use / para comandos de barra!")
        
        return embed

    @commands.command(name='help', aliases=['ajuda'], hidden=True)
    async def _help(self, ctx: CustomContext, *cmd_name):
        if cmd_name:
            # Lógica simplificada para busca direta
            query = " ".join(cmd_name)
            cmd = self.bot.get_command(query)
            if cmd and await check_perms(ctx, cmd):
                embed = await self.get_cmd(ctx, [cmd], 0, "Busca Direta", "🔍")
                await ctx.reply(embed=embed)
                return
            raise GenericError(f"Comando `{query}` não encontrado.")

        cmdlst = {}
        for cmd in sorted(self.bot.commands, key=lambda c: c.name):
            if not await check_perms(ctx, cmd): continue
            
            category = getattr(cmd, 'category', None) or (cmd.cog.qualified_name if cmd.cog else "Diversos")
            emoji = category_icons.get(category, "❓")
            
            if emoji not in cmdlst:
                cmdlst[emoji] = (category, [])
            cmdlst[emoji][1].append(cmd)

        embed = disnake.Embed(
            title="✨ Central de Comandos",
            description=f"Olá {ctx.author.mention}! Selecione uma categoria abaixo para explorar minhas funcionalidades.\n\n"
                        f"💡 **Dica:** Meus comandos de barra `/` são mais rápidos e bonitos!",
            color=0x5865F2
        )
        
        btn_id = []
        cmd_lst_new = {}
        
        for emoji, data in cmdlst.items():
            cat_name, cmds = data
            cmd_lst_new[cat_name] = {"emoji": emoji, "cmds": cmds}
            btn_id.append([cat_name, emoji])
            
            cmd_names = ", ".join([f"`{c.name}`" for c in cmds[:10]])
            if len(cmds) > 10: cmd_names += "..."
            embed.add_field(name=f"{emoji} {cat_name} ({len(cmds)})", value=cmd_names, inline=False)

        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text=f"Solicitado por {ctx.author}", icon_url=ctx.author.display_avatar.url)

        view = ViewHelp(ctx, btn_id, get_cmd=self.get_cmd, cmd_list=cmd_lst_new, main_embed=embed)
        view.message = await ctx.send(embed=embed, view=view)

def setup(bot: BotCore):
    bot.add_cog(HelpCog(bot))
