import json
import time
import subprocess

import discord
import discord.ext.commands as commands

import psutil


def setup(bot):
    bot.add_cog(Core(bot))
    print('Core is loaded !')


def duration_to_str(duration):
    """Converts a timestamp to a string representation."""
    minutes, seconds = divmod(duration, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    duration = []
    if days > 0: duration.append(f'{days} days')
    if hours > 0: duration.append(f'{hours} hours')
    if minutes > 0: duration.append(f'{minutes} minutes')
    if seconds > 0 or len(duration) == 0: duration.append(f'{seconds} seconds')

    return ', '.join(duration)


class Core(commands.Cog):
    """♡"""
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command('help')

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.start_time = time.time()

    @commands.command(pass_context=True, aliases=['infos'])
    async def info(self, ctx):
        """Shows info about the bot."""
        latest_commits = subprocess.check_output(['git', 'log', '--pretty=format:[`%h`](https://github.com/Lasauce6/jean_robo/commit/%h) %s', '-n', '5']).decode('utf-8')

        embed = discord.Embed(description='[Clique ici pour avoir ton propre jean_robo!](https://github.com/Lasauce6/jean_robo)', colour=discord.Colour.blurple())
        embed.set_thumbnail(url='https://cdn.discordapp.com/avatars/816381381654609970/7a99fb30e435d63ce20d84a92998b14a.png?size=1024')
        embed.set_author(name="Author : Lasauce6#5815", icon_url='https://cdn.discordapp.com/avatars/368688417980284928/bc29dfc4085be557ecca9ccea24d35fb.png?size=1024')
        embed.add_field(name='Command prefixes', value=f'`@{ctx.guild.me.display_name} `, `{self.bot.conf["prefix"]}`', inline=False)
        embed.add_field(name='CPU', value=f'{psutil.cpu_percent()}%')
        embed.add_field(name='Memory', value=f'{psutil.Process().memory_full_info().uss / 1048576:.2f} Mb')  # Expressed in bytes, turn to Mb and round to 2 decimals
        embed.add_field(name='Uptime', value=duration_to_str(int(time.time() - self.bot.start_time)))
        embed.add_field(name='Latest changes', value=latest_commits, inline=False)
        embed.add_field(name='\N{ZERO WIDTH SPACE}', value='Si tu as des questions sur le bot ou que tu souhaite simplement me rejoindre pour jouer tranquilement, viens sur [mon discord !](https://discord.gg/MZXV97R)')
        embed.set_footer(text='Powered by discord.py', icon_url='http://i.imgur.com/5BFecvA.png')

        await ctx.send(embed=embed)

    @commands.command(pass_context=True)
    @commands.has_permissions(manage_guild=True)
    async def load(self, ctx, name):
        """Loads an extension.

        This command requires the Manage Server permission.
        """
        cog = name.lower()
        try:
            ctx.bot.load_extension(f'cogs.{cog}')
        except commands.ExtensionAlreadyLoaded:
            await ctx.send(f'Extension {name} already loaded.')
        except commands.ExtensionNotFound:
            await ctx.send(f'Extension {name} not found.')
        else:
            self.bot.conf['extensions'].append(cog)
            with open(self.bot.conf_file, 'w') as fp:
                json.dump(self.bot.conf, fp)
            await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')

    @commands.command(pass_context=True)
    @commands.has_permissions(manage_guild=True)
    async def unload(self, ctx, name):
        """Unloads an extension.

        This command requires the Manage Server permission.
        """
        cog = name.lower()
        try:
            ctx.bot.unload_extension(f'cogs.{cog}')
        except commands.ExtensionNotLoaded:
            await ctx.send(f'Extension {name} not loaded.')
        else:
            self.bot.conf['extensions'].remove(cog)
            with open(self.bot.conf_file, 'w') as fp:
                json.dump(self.bot.conf, fp)
            await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')

    @commands.command(pass_context=True)
    @commands.has_permissions(manage_guild=True)
    async def reload(self, ctx, *extensions):
        """Reloads extensions.

        If none are provided, reloads all loaded extensions.

        This command requires the Manage Server permission.
        """
        if extensions is None:
            extensions = self.bot.conf['extensions']

        for name in extensions:
            cog = name.lower()
            try:
                ctx.bot.unload_extension(f'cogs.{cog}')
                ctx.bot.load_extension(f'cogs.{cog}')
            except commands.ExtensionError as e:
                await ctx.send(f'Error reloading extension {name} : {e}')

        await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')

    @commands.command(pass_context=True, aliases=['h'])
    async def help(self, ctx, typ="short"):

        embed = discord.Embed(colour=discord.Colour(0xb175ff), url="https://discordapp.com", description="Voici toutes les capacités de Jean_robo")
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/369542564321165322/834130549873967194/Jean_robo_PP.png")
        embed.set_author(name="Jean_robo vous fait la musique !")

        embed.add_field(name="0. Info", value=f'Je vous donne moult informations sur ma personne !\nUsage : `{self.bot.conf["prefix"]}info`', inline=False)
        embed.add_field(name="1. Join/Summon", value=f'Je rejoins le channel dans lequel vous vous situez messire !\nUsage: `{self.bot.conf["prefix"]}join` ou `{self.bot.conf["prefix"]}summon`', inline=False)
        embed.add_field(name="2. Leave/Disconnect", value=f'Je m\'en vais prenant mes caleçons sales !\nUsage: `{self.bot.conf["prefix"]}leave` ou `{self.bot.conf["prefix"]}disconnect`', inline=False)
        embed.add_field(name="3. Play", value=f'Je joue la musique demandé tel le ménestrel !\nJe peux lire aussi bien les url que les mots\nUsage: `{self.bot.conf["prefix"]}play <songname/url>` ou `{self.bot.conf["prefix"]}p <songname/url>`', inline=False)
        embed.add_field(name="4. Now Playing", value=f'Je donne moult informations sur la chanson que je joue !\nUsage: `{self.bot.conf["prefix"]}nowplaying` ou `{self.bot.conf["prefix"]}np`', inline=False)
        embed.add_field(name="5. Pause", value=f'Je pause et fait des pauses\nUsage: `{self.bot.conf["prefix"]}pause` ou `{self.bot.conf["prefix"]}ps`', inline=False)
        embed.add_field(name="6. Resume", value=f'Je repart de plus belle !\nUsage: `{self.bot.conf["prefix"]}resume` ou `{self.bot.conf["prefix"]}continue`', inline=False)
        embed.add_field(name="7. Repeat", value=f'Votre musique va tourner en boucle !\nUsage: `{self.bot.conf["prefix"]}repeat` ou `{self.bot.conf["prefix"]}r`', inline=False)
        embed.add_field(name="8. Skip", value=f'Je passe a la chanson suivante !\nUsage: `{self.bot.conf["prefix"]}skip` ou `{self.bot.conf["prefix"]}s`', inline=False)
        embed.add_field(name="9. Queue", value=f'Je vous indique la fille d\'attente !\nUsage: `{self.bot.conf["prefix"]}queue` ou `{self.bot.conf["prefix"]}q`', inline=False)

        if typ != "short" and typ != "small":
            embed.add_field(name="10. Remove", value=f'Je retire la chanson demandé par le numéro indiqué\nUsage: `{self.bot.conf["prefix"]}remove <numéro>` ou `{self.bot.conf["prefix"]}rm <nurméro>`', inline=False)
            embed.add_field(name="11. Seek", value=f'Je cherche le pasasage préféré de votre musik !\nUsage: `{self.bot.conf["prefix"]}seek <timestamp>` ou `{self.bot.conf["prefix"]}sk <timestamp>`, avec `timestamp = hh:mm:ss ou mm:ss`', inline=False)
            embed.add_field(name="12. Show NP Looped", value=f'J\'affiche moult informations sur la chanson à chaque fois que j\'en change\nChange le levier sur on ou off\nUsage: `{self.bot.conf["prefix"]}shownplooped` ou `{self.bot.conf["prefix"]}snploop`', inline=False)
            embed.add_field(name="13. Add Favourite", value=f'J\'ajoute la ou une chanson spécifique dans vos favoris !\nSi l\'on me donne pas de numéro de chanson je choisi celle que je suis en train de jouer\nUsage: `{self.bot.conf["prefix"]}addfav [numéro]` ou `{self.bot.conf["prefix"]}afav [numéro]`', inline=False)
            embed.add_field(name="14. Show Favourites", value=f'Direct messages the saved favourites data of you\nUsage: `{self.bot.conf["prefix"]}showfav` or `{self.bot.conf["prefix"]}sfav`', inline=False)
            embed.add_field(name="15. Remove Favourite", value=f'Vous n\'aimez plus votre musique ?\nVeuillez vous référer à l\'index de vos favoris pour en supprimer un avec `sfav`\nUsage: `{self.bot.conf["prefix"]}removefav <fav-index>` ou `{self.bot.conf["prefix"]}rfav <fav-index>`', inline=False)
            embed.add_field(name="16. Play from Favourite", value=f'Je joue la chanson que vous voulez de vos favoris !\nUsage: `{self.bot.conf["prefix"]}playfav <fav-index>` ou `{self.bot.conf["prefix"]}pfav <fav-index>`', inline=False)
            embed.add_field(name="17. Lyrics", value=f'Je vous affiche les paroles de la musique en cours ou d\'une musique spécifique\nJe dis des plaisanteries parfois mais j\'essaye d\'être le plus pro possible !\nUsage: `{self.bot.conf["prefix"]}lyrics [songname]` ou `{self.bot.conf["prefix"]}l [songname]`', inline=False)
        channel = ctx.message.channel
        await channel.send('Musik', embed=embed)