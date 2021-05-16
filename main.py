import json
import logging
import discord
import time
import asyncio
import sys
from discord.ext import commands

from Implementation import *
from config import Config


rlog = logging.getLogger()
rlog.setLevel(logging.INFO)
handler = logging.FileHandler('jean_robo.log', encoding='utf-8')
handler.setFormatter(logging.Formatter('{asctime}:{levelname}:{name}:{message}', style='{'))
rlog.addHandler(handler)

logging.getLogger('discord').setLevel(logging.WARNING)

config = Config('conf/config.json')

class jean_robo(commands.Bot):
    def __init__(self):
        self.conf_file = 'conf/config.json'
        with open(self.conf_file) as fp:
            self.conf = json.load(fp)

        super().__init__(commands.when_mentioned_or(self.conf['prefix']), description='Jean_robo le beau robo')

        for cog_name in self.conf['extensions']:
            self.load_extension(f'cogs.{cog_name}')

client = jean_robo()


youtubers = config.getYouTubersList() if (config.getYouTubersNr() != 0) else sys.exit()
streamers = config.getStreamerList() if (config.getStreamerNr() !=0) else sys.exit()
id = ''
GOOGLE_API = config.getConnectionData()[0]
TWITCH_APP_ID = config.getConnectionData()[1]
TWITCH_APP_SECRET = config.getConnectionData()[2]
pingEveryXMinutes = config.getPingTime()
threads = []
processes = []
tthreads = []
tprocesses = []


i = 0
while i < config.getYouTubersNr():
    temp_list = []
    temp_list.append(config.getYouTubersList()[str(i)]['name']) # Name
    temp_list.append(id) if not config.getYouTubersList()[str(i)]['channelID'] else temp_list.append(config.getYouTubersList()[str(i)]['channelID'])
    temp_list.append(True) if not id else temp_list.append(False)
    temp_list.append(config.getYouTubersList()[str(i)])
    temp_list.append('')
    threads.append(temp_list)
    i += 1
i = 0

while i < config.getYouTubersNr():
    processes.append(YouTuber(GOOGLE_API, threads[i][1], threads[i][2]))
    i += 1
i = 0

while i < config.getStreamerNr():
    temp_list = []
    temp_list.append(config.getStreamerList()[str(i)]['name'])
    temp_list.append(id) if not config.getStreamerList()[str(i)]['channelID'] else temp_list.append(config.getStreamerList()[str(i)]['channelID'])
    temp_list.append(True) if not id else temp_list.append(False)
    temp_list.append(config.getStreamerList()[str(i)])
    temp_list.append('')
    tthreads.append(temp_list)
    i += 1
i = 0

while i < config.getStreamerNr():
    tprocesses.append(Streamer(TWITCH_APP_ID, TWITCH_APP_SECRET, tthreads[i][0]))
    i += 1


async def youtube():
    item = 0
    while item < config.getYouTubersNr():
        # data = processes[item].update()
        # print('Checking for new videos from {}'.format(threads[item][0]))
        sys.stdout.write('Checking for new videos from {}'.format(threads[item][0]) + '\n')
        if processes[item].isNewVideo():
            # print('{} UPLOADED A NEW VIDEO! PUSHING UPDATE ON DISCORD.'.format(threads[item][0]))
            sys.stdout.write('{} UPLOADED A NEW VIDEO! PUSHING UPDATE ON DISCORD.'.format(threads[item][0]) + '\n')
            for x in range(0, config.getYoutuberDiscordChannelNr(threads[item][3])):
                newvideo = config.getYoutuberDiscordChannelList(threads[item][3])[str(x)]['New video'].format(threads[item][0]) + '\n{}'.format(processes[item].getVideoLink(processes[item].videosData[0][1]))
                channel = client.get_channel(config.getYoutuberDiscordChannelList(threads[item][3])[str(x)]['channelID'])
                await channel.send(newvideo)

        if processes[item].isUserLive():
            if not processes[item].liveId == threads[item][4]:
                # print('{} IS STREAMING ON YOUTUBE NOW! PUSHING UPDATE ON DISCORD.'.format(threads[item][0]))
                sys.stdout.write('{} IS STREAMING ON YOUTUBE NOW! PUSHING UPDATE ON DISCORD.'.format(threads[item][0]) + '\n')
                threads[item][4] = processes[item].liveId
                for x in range(0, config.getYoutuberDiscordChannelNr(threads[item][3])):
                    livestream = config.getYoutuberDiscordChannelList(threads[item][3])[str(x)]['Livestream'].format(threads[item][0]) + '\n{}'.format(processes[item].getVideoLink(processes[item].getUserLiveData()))
                    channel = client.get_channel(config.getYoutuberDiscordChannelList(threads[item][3])[str(x)]['channelID'])
                    await channel.send(livestream)

        item += 1

async def twitch():
    count = 0
    while count < config.getStreamerNr():
        # data = tprocesses[count].update()
        # print('Checking for live on Twitch from {}'.format(tthreads[count][0]))
        sys.stdout.write('Checking for live on Twitch from {}'.format(tthreads[count][0]) + '\n')
        if tprocesses[count].isStreaming() and not tprocesses[count].lockStatus():
            tprocesses[count].lock()
            # print('{} IS LIVE, PUSHING INFO ON DISCORD !'.format(tthreads[count][0]))
            sys.stdout.write('{} IS LIVE, PUSHING INFO ON DISCORD !'.format(tthreads[count][0]) + '\n')
            for x in range(0, config.getDiscordChannelNr()):
                livestream = config.getStreamerDiscordChannelList(tthreads[count][3])[str(x)]['Twitch'].format(tthreads[count][0]) + '\n{}'.format(tprocesses[count].getStreamLink())
                embed = discord.Embed(title=tprocesses[count].getTitle(), colour=discord.Colour(0x9013fe), url=tprocesses[count].getStreamLink())

                embed.set_image(url=tprocesses[count].getThumbnail())
                embed.set_thumbnail(url=tprocesses[count].getProfilePicture())
                embed.set_author(name=tprocesses[count].getStreamerName(), icon_url=tprocesses[count].getProfilePicture())

                embed.add_field(name='Game', value=tprocesses[count].getGame())
                embed.add_field(name='Viewers', value=tprocesses[count].getViewers())
                channel = client.get_channel(config.getStreamerDiscordChannelList(tthreads[count][3])[str(x)]['channelID'])
                await channel.send(content=livestream, embed=embed)
        elif tprocesses[count].isStreaming() and tprocesses[count].lockStatus():
            # print('Still Streaming !')
            sys.stdout.write('Still Streaming ! \n')
        elif not tprocesses[count].isStreaming() and tprocesses[count].lockStatus():
            tprocesses[count].unlock()
        count += 1


async def update():
    while True:
        try:
            waittime = pingEveryXMinutes * 60
            await twitch()
            await youtube()


        except:
            pass
        while waittime > 0:
            mins, secs = divmod(waittime, 60)
            timeformat = '{:02d}:{:02d}'.format(mins, secs)
            sys.stdout.write('Rechecking in ' + str(timeformat) + '\r')
            # print('Rechecking in ' + str(timeformat) + '\r')
            waittime -= 1
            await asyncio.sleep(1)

@client.event
async def on_ready():
    print('Logged in as:')
    print(client.user.name)
    print(client.user.id)
    print('---------------------------------------')
    print('Bot running.')
    # asyncio.ensure_future(update())
    # await update()
    client.loop.create_task(update())


client.run(client.conf['token'])


