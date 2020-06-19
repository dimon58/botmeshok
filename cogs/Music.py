# Imports
import discord
import youtube_dl
from youtube_dl import utils
import os
import asyncio
import math
import pymongo
from helper import *
from discord.ext import commands
from langs.bidlo import Music as lang
# Suppress annoying console message
youtube_dl.utils.bug_reports_message = lambda: ''

# Connect to mongodb database
with open('mongo.txt','r') as mongo:
    client = pymongo.MongoClient(mongo.read())
db = client['bot_meshok']
guildcol = db['prefix']
queuecol = db['queue']
playlistcol = db['playlist']
blacklist_admin = db['adminblacklist']


def blacklist_check():
    def predicate(ctx):
        author_id = ctx.author.id
        if blacklist_admin.find_one({'user_id': author_id}):
            return False
        return True
    return commands.check(predicate)


# Helper to create audio player
def create_ytdl_source(source, volume=0.5):
    player = discord.PCMVolumeTransformer(
        discord.FFmpegPCMAudio(
            source,
            before_options=" -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 1",
            options='-vn'
        ),
        volume=volume
    )
    return player


# Ensure user is connected to voice
def ensure_voice():
    async def predicate(ctx):
        if ctx.author.voice == None:
            await ctx.send(
                embed=create_embed(
                    # 'You must be connected to a voice channel to use this command'
                    # 'Вы должны присоедениться к голосовому каналу, для использования этой команды'
                    # 'Ты ебать выйди со мной раз на раз в голосовой канал, а не в текстовом пиши'
                    lang.phrases.ensure_voice_not_in_voice
                )
            )
            return False
        else:
            return True
    return commands.check(predicate)


class Music(commands.Cog, name='Music'):
    def __init__(self, client):
        self.client = client
        self.opts = {
            "default_search": "ytsearch",
            'format': 'bestaudio/best/bestvideo',
            'quiet': True,
            'noplaylist': False,
            # 'extract_flat': 'in_playlist',
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'no_warnings': True,
            'include_ads': False,
            'skip_download': True,
            'source_address': '0.0.0.0'
        }

    def extract_info(self, url, ctx):
        try:
            with youtube_dl.YoutubeDL(self.opts) as ydl:
                info = ydl.extract_info(
                    url+' ',
                    download=False
                )
        except (utils.ExtractorError, utils.DownloadError, utils.UnavailableVideoError) as error:
            asyncio.run_coroutine_threadsafe(
                ctx.send(
                    embed=create_embed(
                        # 'There is an error with Youtube service, please try again'
                        lang.phrases.extract_info_youtube_error
                    ), delete_after=10
                ), self.client.loop
            )
        return info

    def ensure_bot_alone(self, ctx):
        if ctx.voice_client == None:
            return True
        elif ctx.voice_client != None:
            if len(ctx.voice_client.channel.members) == 1:
                return True
            else:
                if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                    return False
                else:
                    return True

    def play_song(self, guild):
        item = queuecol.find_one({'guild_id': guild.id})
        pointer = item['pointer']
        text_channel = self.client.get_channel(item['text_channel'])
        while True:
            try:
                with youtube_dl.YoutubeDL(self.opts) as ydl:
                    info = ydl.extract_info(
                        item['queue'][pointer]['url']+' ',
                        download=False
                    )
            except (utils.ExtractorError, utils.DownloadError, utils.UnavailableVideoError) as error:
                asyncio.run_coroutine_threadsafe(
                    text_channel.send(
                        embed=create_embed(
                            # 'There is an error with Youtube service, retrying'
                            lang.phrases.play_song_youtube_error
                        ),
                        delete_after=10
                    ), self.client.loop
                )
            break
        volume = item['volume']
        voice = guild.voice_client
        source = create_ytdl_source(info['url'], volume)
        try:
            asyncio.run_coroutine_threadsafe(
                text_channel.send(
                    embed=create_embed(
                        f'**{lang.phrases.play_song_now_playing}**: [{info["title"]}]({info["webpage_url"]})'
                    ),
                    delete_after=info['duration']
                ), self.client.loop
            )
        except:
            pass

        def after_playing(error):
            queue = queuecol.find_one({'guild_id': guild.id})
            if queue['size'] == 0:
                asyncio.run_coroutine_threadsafe(
                    voice.disconnect(),
                    self.client.loop,
                )
                queuecol.delete_one({'guild_id': guild.id})
            elif queue['loop'] == 'all':
                if queue['pointer'] == queue['size']-1:
                    queuecol.update_one(
                        {'guild_id': guild.id},
                        {
                            '$set': {
                                'pointer': 0
                            }
                        }
                    )
                else:
                    queuecol.update_one(
                        {'guild_id': guild.id},
                        {
                            '$inc': {
                                'pointer': 1
                            }
                        }
                    )
                self.play_song(guild)
            elif queue['loop'] == 'off':
                if queue['pointer'] == queue['size']-1:
                    asyncio.run_coroutine_threadsafe(
                        voice.disconnect(),
                        self.client.loop,
                    )
                    queuecol.delete_one({'guild_id': guild.id})
                else:
                    queuecol.update_one(
                        {'guild_id': guild.id},
                        {
                            '$inc': {
                                'pointer': 1
                            }
                        }
                    )
                    self.play_song(guild)
            else:
                self.play_song(guild)

        voice.play(source, after=after_playing)

    @commands.command(
        name='join',
        aliases=['j', 'connect', ],
        # description='Connect to your current voice channel',
        description=lang.descriptions.join,
        usage='`.join`'
    )
    @ensure_voice()
    @blacklist_check()
    async def join(self, ctx, arg=None):
        if arg != None:
            await ctx.send(
                embed=create_embed(
                    # 'This command does not take in any other argument'
                    lang.phrases.join_unnecessary_arguments
                )
            )
        else:
            channel = ctx.author.voice.channel
            voice = ctx.voice_client
            if voice != None:
                if self.ensure_bot_alone(ctx):
                    await voice.move_to(channel)
                    queuecol.update_one(
                        {'guild_id': ctx.guild.id},
                        {
                            '$set': {
                                'voice_channel': voice.channel.id
                            }
                        }
                    )
                    await ctx.send(
                        embed=create_embed(
                            f'{lang.phrases.join_connected} **{channel}**'
                        ),
                        delete_after=10
                    )
                else:
                    await ctx.send(
                        embed=create_embed(
                            # 'Please wait until other members are done listening to music'
                            # 'Пожалуйста подождите, пока остальные участники дослушают музыку'
                            lang.phrases.join_wait
                        ),
                        delete_after=10
                    )
            else:
                voice = await channel.connect(reconnect=True)
                if queuecol.find_one({'guild_id': ctx.guild.id}) != None:
                    queuecol.delete_one({'guild_id': ctx.guild.id})
                queuecol.insert_one(
                    {
                        'guild_id': ctx.guild.id,
                        'text_channel': ctx.channel.id,
                        'voice_channel': voice.channel.id,
                        'state': None,
                        'loop': 'off',
                        'volume': 0.5,
                        'pointer': 0,
                        'size': 0,
                        'queue': [],
                    }
                )
                await ctx.send(
                    embed=create_embed(
                        f'Bot connected to **{channel}**'
                    ),
                    delete_after=10
                )

    @commands.command(
        name='leave',
        aliases=['dc', 'disconnect'],
        # description='Disconnect from the voice channel',
        description=lang.descriptions.leave,
        usage='`.leave`'
    )
    @blacklist_check()
    async def leave(self, ctx, arg=None):
        if arg != None:
            await ctx.send(
                embed=create_embed(
                    # 'This command does not take in any other argument'
                    lang.phrases.leave_unnecessary_arguments
                ),
                delete_after=10
            )
        else:
            voice = ctx.voice_client
            if voice != None:
                if voice.channel == ctx.author.voice.channel:
                    queuecol.update_one(
                        {'guild_id': ctx.guild.id},
                        {
                            '$set': {
                                'size': 0
                            }
                        }
                    )
                    voice.stop()
                    await ctx.send(
                        embed=create_embed(
                            f'Bot disconnected from **{voice.channel}**'
                        ),
                        delete_after=10
                    )
                else:
                    if self.ensure_bot_alone(ctx):
                        queuecol.update_one(
                                {'guild_id': ctx.guild.id},
                                {
                                    '$set': {
                                        'size': 0
                                    }
                                }
                            )
                        voice.stop()
                        await ctx.send(
                            embed=create_embed(
                                f'{lang.phrases.leave_disconnect} **{voice.channel}**'
                            ),
                            delete_after=10
                        )
                    else:
                        await ctx.send(
                            embed=create_embed(
                                # 'Please wait until other members are done listening to music'
                                lang.phrases.leave_wait
                            ),
                            delete_after=10
                        )
            else:
                await ctx.send(
                    embed=create_embed(
                        # 'Bot was not connected to any voice channel'
                        lang.phrases.leave_not_connected
                    ),
                    delete_after=10
                )

    @commands.command(
        name='play',
        aliases=['p', ],
        # description='Play music from Youtube',
        description=lang.descriptions.play,
        # usage='`.play [url or song name]`',
        usage='`.play [url или название песни]`'
    )
    @ensure_voice()
    @blacklist_check()
    async def play(self, ctx, *, url: str):
        text_channel = ctx.channel
        channel = ctx.author.voice.channel
        voice = ctx.voice_client
        if voice != None:  # Bot already in voice channel
            if voice.channel != channel:  # User in a different channel
                if self.ensure_bot_alone(ctx):   # Check if bot is available
                    info = self.extract_info(url, ctx)
                    # Delete the current queue
                    if voice.is_playing() or voice.is_paused():
                        queuecol.update_one(
                            {'guild_id': ctx.guild.id},
                            {
                                '$set': {
                                    'size': 0,
                                }
                            }
                        )
                        voice.stop()
                        voice = await channel.connect(reconnect=True)
                    else:
                        # Move the bot to the new channel
                        queuecol.delete_one({'guild_id': ctx.guild.id})
                        await voice.move_to(channel)
                        # Create a new queue
                        queuecol.insert_one(
                            {
                                'guild_id': ctx.guild.id,
                                'text_channel': ctx.channel.id,
                                'voice_channel': voice.channel.id,
                                'state': 'Playing',
                                'loop': 'off',
                                'volume': 0.5,
                                'pointer': 0,
                                'size': 0,
                                'queue': [],
                            }
                        )
                        # Check if ytdl gives a playlist
                        if "_type" in info and info["_type"] == "playlist":
                            # The playlist is not supported
                            if 'title' not in info['entries'][0]:
                                await ctx.send(
                                    embed=create_embed(
                                        # 'This playlist link is not supported'
                                        lang.phrases.play_playlist_not_supported
                                    ),
                                    delete_after=10
                                )
                            else:
                                # The playlist only have one song
                                if len(info['entries']) == 1:
                                    # Get song metadata
                                    song_info = info['entries'][0]
                                    # Insert the song into queue
                                    queuecol.update_one(
                                        {'guild_id': ctx.guild.id},
                                        {
                                            '$push': {
                                                'queue': {
                                                    'url': song_info['webpage_url'],
                                                    'title': song_info['title']
                                                }
                                            },
                                            '$inc': {
                                                'size': 1
                                            },
                                        }
                                    )
                                else:
                                    # Insert all songs into queue
                                    for song in info['entries']:
                                        queuecol.update_one(
                                            {'guild_id': ctx.guild.id},
                                            {
                                                '$push': {
                                                    'queue': {
                                                        'url': song['webpage_url'],
                                                        'title': song['title']
                                                    }
                                                },
                                                '$inc': {
                                                    'size': 1
                                                }
                                            }
                                        )
                                    await ctx.send(
                                        embed=create_embed(
                                            f'{len(info["entries"])} {lang.phrases.play_songs_from} [link]({url}) {lang.phrases.play_added_to_queue}'
                                        ),
                                        delete_after=10
                                    )
                        else:
                            # Insert song from an url
                            queuecol.update_one(
                                {'guild_id': ctx.guild.id},
                                {
                                    '$push': {
                                        'queue': {
                                            'url': info['webpage_url'],
                                            'title': info['title']
                                        }
                                    },
                                    '$inc': {
                                        'size': 1
                                    }
                                }
                            )
                            # Start playing
                        self.play_song(ctx.guild)
                else:  # Bot is not available
                    await ctx.send(
                        embed=create_embed(
                            # 'Please wait until other members are done listening to music'
                            lang.phrases.play_wait
                        ),
                        delete_after=10
                    )
            else:  # User in the same channel as bot
                if voice.is_playing() or voice.is_paused():  # Bot is playing music
                    info = self.extract_info(url, ctx)
                    # Check if ytdl gives a playlist
                    if "_type" in info and info["_type"] == "playlist":
                        # The playlist is not supported
                        if 'title' not in info['entries'][0]:
                            await ctx.send(
                                embed=create_embed(
                                    # 'This playlist link is not supported'
                                    lang.phrases.play_playlist_not_supported
                                ),
                                delete_after=10
                            )
                        else:
                            # The playlist only have one song
                            if len(info['entries']) == 1:
                                # Get song metadata
                                song_info = info['entries'][0]
                                # Insert the song into queue
                                queuecol.update_one(
                                    {'guild_id': ctx.guild.id},
                                    {
                                        '$push': {
                                            'queue': {
                                                'url': song_info['webpage_url'],
                                                'title': song_info['title']
                                            }
                                        },
                                        '$inc': {
                                            'size': 1
                                        }
                                    }
                                )
                                await ctx.send(
                                    embed=create_embed(
                                        f'{lang.phrases.play_song} [{song_info["title"]}]({song_info["webpage_url"]}) {lang.phrases.play_added_to_queue}'
                                    ),
                                    delete_after=10
                                )
                            else:
                                # Insert all songs into queue
                                for song in info['entries']:
                                    queuecol.update_one(
                                        {'guild_id': ctx.guild.id},
                                        {
                                            '$push': {
                                                'queue': {
                                                    'url': song['webpage_url'],
                                                    'title': song['title']
                                                }
                                            },
                                            '$inc': {
                                                'size': 1
                                            }
                                        }
                                    )
                                await ctx.send(
                                    embed=create_embed(
                                        f'{len(info["entries"])} {lang.phrases.play_songs_added_to_queue}'
                                    ),
                                    delete_after=10
                                )
                    else:
                        # Insert song from an url
                        queuecol.update_one(
                            {'guild_id': ctx.guild.id},
                            {
                                '$push': {
                                    'queue': {
                                        'url': info['webpage_url'],
                                        'title': info['title']
                                    }
                                },
                                '$inc': {
                                    'size': 1
                                }
                            }
                        )
                        await ctx.send(
                            embed=create_embed(
                                f'{lang.phrases.play_song} [{info["title"]}]({info["webpage_url"]}) {lang.phrases.play_added_to_queue}'
                            ),
                            delete_after=10
                        )
                else:  # Bot is not playing any music
                    info = self.extract_info(url, ctx)
                    # Check if ytdl gives a playlist
                    if "_type" in info and info["_type"] == "playlist":
                        # The playlist is not supported
                        if 'title' not in info['entries'][0]:
                            await ctx.send(
                                embed=create_embed(
                                    # 'This playlist link is not supported'
                                    lang.phrases.play_playlist_not_supported
                                ),
                                delete_after=10
                            )
                        else:
                            # The playlist only have one song
                            if len(info['entries']) == 1:
                                # Get song metadata
                                song_info = info['entries'][0]
                                # Insert the song into queue
                                queuecol.update_one(
                                    {'guild_id': ctx.guild.id},
                                    {
                                        '$push': {
                                            'queue': {
                                                'url': song_info['webpage_url'],
                                                'title': song_info['title']
                                            }
                                        },
                                        '$inc': {
                                            'size': 1
                                        }
                                    }
                                )
                            else:
                                # Insert all songs into queue
                                for song in info['entries']:
                                    queuecol.update_one(
                                        {'guild_id': ctx.guild.id},
                                        {
                                            '$push': {
                                                'queue': {
                                                    'url': song['webpage_url'],
                                                    'title': song['title']
                                                }
                                            },
                                            '$inc': {
                                                'size': 1
                                            }
                                        }
                                    )
                                await ctx.send(
                                    embed=create_embed(
                                        f'{len(info["entries"])} {lang.phrases.play_songs_from} [link]({url}) {lang.phrases.play_added_to_queue}'
                                    ),
                                    delete_after=10
                                )
                    else:
                        # Insert song from an url
                        queuecol.update_one(
                            {'guild_id': ctx.guild.id},
                            {
                                '$push': {
                                    'queue': {
                                        'url': info['webpage_url'],
                                        'title': info['title']
                                    }
                                },
                                '$inc': {
                                    'size': 1
                                }
                            }
                        )
                    # Start playing
                    self.play_song(ctx.guild)
        else:  # Bot is not connected to any voice channel
            # Connects bot to a voice channel
            voice = await channel.connect(reconnect=True)
            info = self.extract_info(url, ctx)
            # Create a new queue
            if queuecol.find_one({'guild_id': ctx.guild.id}) != None:
                queuecol.delete_one({'guild_id': ctx.guild.id})
            queuecol.insert_one(
                {
                    'guild_id': ctx.guild.id,
                    'text_channel': ctx.channel.id,
                    'voice_channel': voice.channel.id,
                    'state': 'Playing',
                    'loop': 'off',
                    'volume': 0.5,
                    'pointer': 0,
                    'size': 0,
                    'queue': [],
                }
            )
            # Check if ytdl gives a playlist
            if "_type" in info and info["_type"] == "playlist":
                # The playlist is not supported
                if 'title' not in info['entries'][0]:
                    await ctx.send(
                        embed=create_embed(
                            # 'This playlist link is not supported'
                            lang.phrases.play_playlist_not_supported
                        ),
                        delete_after=10
                    )
                else:
                    if len(info['entries']) == 1:  # The playlist only have one song
                        # Get song metadata
                        song_info = info['entries'][0]
                        # Insert the song into queue
                        queuecol.update_one(
                            {'guild_id': ctx.guild.id},
                            {
                                '$push': {
                                    'queue': {
                                        'url': song_info['webpage_url'],
                                        'title': song_info['title']
                                    }
                                },
                                '$inc': {
                                    'size': 1
                                }
                            }
                        )
                    else:
                        # Insert all songs into queue
                        for song in info['entries']:
                            queuecol.update_one(
                                {'guild_id': ctx.guild.id},
                                {
                                    '$push': {
                                        'queue': {
                                            'url': song['webpage_url'],
                                            'title': song['title']
                                        }
                                    },
                                    '$inc': {
                                        'size': 1
                                    }
                                }
                            )
                        await ctx.send(
                            embed=create_embed(
                                f'{len(info["entries"])} {lang.phrases.play_songs_from} [link]({url}) {lang.phrases.play_added_to_queue}'
                            ),
                            delete_after=10
                        )
            else:
                # Insert song from an url
                queuecol.update_one(
                    {'guild_id': ctx.guild.id},
                    {
                        '$push': {
                            'queue': {
                                'url': info['webpage_url'],
                                'title': info['title']
                            }
                        },
                        '$inc': {
                            'size': 1
                        }
                    }
                )
            # Start playing
            self.play_song(ctx.guild)

    @commands.command(
        name='pause',
        aliases=['pau', 'pa'],
        # description='Pauses the music',
        description=lang.descriptions.pause,
        usage='`.pause`'
    )
    @ensure_voice()
    @blacklist_check()
    async def pause(self, ctx, arg=None):
        if arg != None:
            await ctx.send(
                embed=create_embed(
                    # 'This command does not take in any other argument'
                    lang.phrases.pause_unnecessary_arguments
                ),
                delete_after=10
            )
        else:
            channel = ctx.author.voice.channel
            voice = ctx.voice_client
            if voice != None:
                if voice.channel == channel:
                    if voice.is_playing():
                        voice.pause()
                        queuecol.update_one(
                            {'guild_id': ctx.guild.id},
                            {
                                '$set': {
                                    'state': 'Paused'
                                }
                            }
                        )
                        await ctx.send(
                            embed=create_embed(
                                'Music paused'
                            ),
                            delete_after=10
                        )
                    elif voice.is_paused():
                        await ctx.send(
                            embed=create_embed(
                                # 'Cannot pause while bot was already paused'
                                lang.phrases.pause_already_pause
                            ),
                            delete_after=10
                        )
                    else:
                        await ctx.send(
                            embed=create_embed(
                                # 'Cannot pause while bot was not playing music'
                                lang.phrases.pause_not_playing
                            ),
                            delete_after=10
                        )
                else:
                    await ctx.send(
                        embed=create_embed(
                            # 'Please wait until other members are done listening to music'
                            lang.phrases.pause_wait
                        ),
                        delete_after=10
                    )
            else:
                await ctx.send(
                    embed=create_embed(
                        # 'Cannot pause while bot was not connected to any voice channel'
                        lang.phrases.pause_not_connected
                    ),
                    delete_after=10
                )

    @commands.command(
        name='resume',
        aliases=['res', 're'],
        # description='Resume the music',
        description=lang.descriptions.resume,
        usage='`.resume`'
    )
    @ensure_voice()
    @blacklist_check()
    async def resume(self, ctx, arg=None):
        if arg != None:
            await ctx.send(
                embed=create_embed(
                    # 'This command does not take in any other argument'
                    lang.phrases.resume_unnecessary_arguments
                ),
                delete_after=10
            )
        else:
            channel = ctx.author.voice.channel
            voice = ctx.voice_client
            if voice != None:
                if voice.channel != channel:
                    await ctx.send(
                        embed=create_embed(
                            # 'Please wait until other members are done listening to music'
                            lang.phrases.resume_wait
                        ),
                        delete_after=10
                    )
                else:
                    if voice.is_paused():
                        voice.resume()
                        queuecol.update_one(
                            {'guild_id': ctx.guild.id},
                            {
                                '$set': {
                                    'state': 'Playing'
                                }
                            }
                        )
                        await ctx.send(
                            embed=create_embed(
                                # 'Resumed music'
                                lang.phrases.resume_resumed
                            ),
                            delete_after=10
                        )
                    elif voice.is_playing():
                        await ctx.send(
                            embed=create_embed(
                                # 'Cannot resume if music is already playing'
                                lang.phrases.resume_already_resumed
                            ),
                            delete_after=10
                        )
                    else:
                        item = queuecol.find_one({'guild_id': ctx.guild.id})
                        if len(item['queue']) > 0:
                            self.play_song(ctx.guild)
                            queuecol.update_one(
                                {'guild_id': ctx.guild.id},
                                {
                                    '$set': {
                                        'state': 'Playing'
                                    }
                                }
                            )
                            await ctx.send(
                                embed=create_embed(
                                    # 'Resumed music'
                                    lang.phrases.resume_resumed
                                ),
                                delete_after=10
                            )
                        else:
                            await ctx.send(
                                embed=create_embed(
                                    # 'Cannot resume if there is no music to play'
                                    lang.phrases.resume_not_music
                                ),
                                delete_after=10
                            )
            else:
                item = queuecol.find_one({'guild_id': ctx.guild.id})
                if item == None:
                    await ctx.send(
                        embed=create_embed(
                            # 'Cannot resume while bot was not connected to any voice channel'
                            lang.phrases.resume_not_connected
                        ),
                        delete_after=10
                    )
                else:
                    guild = self.client.get_guild(item['guild_id'])
                    channel = guild.get_channel(item['voice_channel'])
                    voice = await channel.connect(reconnect=True)
                    self.play_song(ctx.guild)
                    await ctx.send(
                        embed=create_embed(
                            lang.phrases.resume_resumed
                        ),
                        delete_after=10
                    )

    @commands.command(
        name='stop',
        aliases=['s', 'st', ],
        # description='Stop playing music',
        description=lang.descriptions.stop,
        usage='`.stop`'
    )
    @ensure_voice()
    @blacklist_check()
    async def stop(self, ctx, arg=None):
        if arg != None:
            await ctx.send(
                embed=create_embed(
                    # 'This command does not take in any other argument'
                    lang.phrases.stop_unnecessary_arguments
                ),
                delete_after=10
            )
        else:
            channel = ctx.author.voice.channel
            voice = ctx.voice_client
            if voice != None:
                if voice.channel != channel:
                    await ctx.send(
                        embed=create_embed(
                            # 'Please wait until other members are done listening to music'
                            lang.phrases.stop_wait
                        ),
                        delete_after=10
                    )
                else:
                    if voice.is_playing() or voice.is_paused():
                        queuecol.update_one(
                            {'guild_id': ctx.guild.id},
                            {
                                '$set': {
                                    'loop': 'off',
                                    'pointer': 0,
                                    'size': 0,
                                    'queue': [],
                                }
                            }
                        )
                        voice.stop()
                        await ctx.send(
                            embed=create_embed(
                                # 'Stopped playing music'
                                lang.phrases.stop_stoped
                            ),
                            delete_after=10
                        )
                    else:
                        await ctx.send(
                            embed=create_embed(
                                # 'Cannot stop if no music is playing'
                                lang.phrases.stop_no_music
                            ),
                            delete_after=10
                        )
            else:
                await ctx.send(
                    embed=create_embed(
                        # 'Cannot stop while bot was not connected to any voice channel'
                        lang.phrases.stop_not_connected
                    ),
                    delete_after=10
                )

    @commands.command(
        name='skip',
        aliases=['sk', 'next'],
        # description='Skip to a song in the music queue',
        description=lang.descriptions.skip,
        # usage='`.skip [position]`',
        usage='`.skip [позиция]`'
    )
    @ensure_voice()
    @blacklist_check()
    async def skip(self, ctx, pos: int = None):
        channel = ctx.author.voice.channel
        voice = ctx.voice_client
        if voice != None:
            if voice.channel != channel:
                await ctx.send(
                    embed=create_embed(
                        # 'Please wait until other members are done listening to music'
                        lang.phrases.skip_wait
                    ),
                    delete_after=10
                )
            else:
                item = queuecol.find_one({'guild_id': ctx.guild.id})
                pointer = item['pointer']
                queue = item['queue']
                if item['size'] == 0:
                    await ctx.send(
                        embed=create_embed(
                            # 'The music queue is empty'
                            lang.phrases.skip_empty_queue
                        ),
                        delete_after=10
                    )
                elif pos == None:
                    song = queue[pointer]
                    await ctx.send(
                        embed=create_embed(
                            f'{lang.phrases.skip_skipped} [{song["title"]}]({song["url"]})'
                        ),
                        delete_after=10
                    )
                    voice.stop()
                elif pos < 1 or pos > item['size']:
                    await ctx.send(
                        embed=create_embed(
                            f'{lang.phrases.skip_the_queue_only_have} {item["size"]} {lang.phrases.skip_more_than_that}'
                        ),
                        delete_after=10
                    )
                else:
                    song = queue[pointer]
                    if item['loop'] == 'one':
                        queuecol.update_one(
                            {'guild_id': ctx.guild.id},
                            {
                                '$set': {
                                    'pointer': pos-1
                                }
                            }
                        )
                        await ctx.send(
                            embed=create_embed(
                                f'{lang.phrases.skip_skipped} [{song["title"]}]({song["url"]})'
                            ),
                            delete_after=10
                        )
                    else:
                        queuecol.update_one(
                            {'guild_id': ctx.guild.id},
                            {
                                '$set': {
                                    'pointer': pos-2
                                }
                            }
                        )
                        await ctx.send(
                            embed=create_embed(
                                f'{lang.phrases.skip_skipped} [{song["title"]}]({song["url"]})'
                            ),
                            delete_after=10
                        )
                    voice.stop()
        else:
            await ctx.send(
                embed=create_embed(
                    # 'Bot was not connected to any voice channel'
                    lang.phrases.skip_not_connected
                ),
                delete_after=10
            )

    @commands.command(
        name='volume',
        # description='Changes the volume (max=300)',
        description=lang.descriptions.volume,
        aliases=['vol', ],
        # usage='`.vol [volume]`',
        usage='`.vol [громкость]`'
    )
    @ensure_voice()
    @blacklist_check()
    async def volume(self, ctx, volume: int):
        if ctx.voice_client == None:
            await ctx.send(
                embed=create_embed(
                    # 'Bot was not connected to any voice channel'
                    lang.phrases.volume_not_connected
                ),
                delete_after=10
            )
        else:
            channel = ctx.author.voice.channel
            voice = ctx.voice_client
            if voice.channel != channel:
                await ctx.send(
                    embed=create_embed(
                        # 'Please wait until other members are done listening to music'
                        lang.phrases.volume_wait
                    ),
                    delete_after=10
                )
            elif volume == None:
                await ctx.send(
                    embed=create_embed(
                        # 'Please specify the volume that you want'
                        lang.phrases.volume_no_arg
                    ),
                    delete_after=10
                )
            else:
                if 0 <= volume <= 300:
                    queuecol.update_one(
                        {'guild_id': ctx.guild.id},
                        {
                            '$set': {
                                'volume': volume/200,
                            }
                        }
                    )
                    voice.source.volume = volume/200
                    await ctx.send(
                        embed=create_embed(
                            f'{lang.phrases.volume_changed} {volume}'
                        ),
                        delete_after=10
                    )
                else:
                    await ctx.send(
                        embed=create_embed(
                            # 'Volume cannot exceed 300'
                            lang.phrases.volume_max
                        ),
                        delete_after=10
                    )

    @commands.command(
        name='queue',
        aliases=['q', ],
        # description='Display your current music queue',
        description=lang.descriptions.queue,
        # usage='`.queue [page]`',
        usage='`.queue [страница]`'
    )
    @ensure_voice()
    @blacklist_check()
    async def queue(self, ctx, page: int = 1):
        channel = ctx.author.voice.channel
        voice = ctx.voice_client
        if voice != None:
            if voice.channel != channel:
                await ctx.send(
                    embed=create_embed(
                        # 'You are not using music'
                        lang.phrases.queue_not_using
                    ),
                    delete_after=10
                )
            else:
                item = queuecol.find_one({'guild_id': ctx.guild.id})
                if item['size'] == 0:
                    await ctx.send(
                        embed=create_embed(
                            # 'The music queue is empty'
                            lang.phrases.queue_empty
                        ),
                        delete_after=10
                    )
                else:
                    queue = item['queue']
                    pointer = item['pointer']
                    info = queue[pointer]
                    pages = math.ceil(item['size']/10)
                    output = ''
                    if 1 <= page <= pages:
                        counter = 1 + (page-1)*10
                        for song in queue[(page-1)*10:page*10]:
                            output += f'{counter}. [{song["title"]}]({song["url"]})\n'
                            counter += 1
                        embed = discord.Embed(
                            color=discord.Color.orange(),
                            description=output,
                            # title='**Music Queue**',
                            title=lang.phrases.queue_name,
                            timestamp=ctx.message.created_at
                        )
                        embed.add_field(
                            # name='Now Playing',
                            name=lang.phrases.queue_now_playing,
                            value=f"[{info['title']}]({info['url']})",
                            inline=False
                        )
                        embed.add_field(
                            # name='Entries',
                            name=lang.phrases.queue_entries,
                            value=f"{item['size']}"
                        )
                        embed.add_field(
                            # name='Repeating',
                            name=lang.phrases.queue_repeating,
                            value=item['loop']
                        )
                        embed.add_field(
                            # name='Volume',
                            name=lang.phrases.queue_volume,
                            value=f"{item['volume']*200}"
                        )
                        embed.set_footer(
                            text=f'{lang.phrases.queue_page} {page} {lang.phrases.queue_of} {pages}'
                        )
                        await ctx.send(
                            embed=embed
                        )
                    else:
                        await ctx.send(
                            embed=create_embed(
                                # 'The page you specified does not exist'
                                lang.phrases.queue_not_exist
                            ),
                            delete_after=10
                        )
        else:
            await ctx.send(
                embed=create_embed(
                    # 'Bot was not connected to any voice channel'
                    lang.phrases.queue_not_connected
                ),
                delete_after=10
            )

    @commands.command(
        name='dequeue',
        aliases=['rmq', 'rm'],
        # description='Remove a song from the music queue',
        description=lang.descriptions.dequeue,
        # usage='`.dequeue [song position in music queue]`',
        usage='`.dequeue [позиция песни в очереди]`'
    )
    @ensure_voice()
    @blacklist_check()
    async def dequeue(self, ctx, position: int, arg=None):
        if arg != None:
            await ctx.send(
                embed=create_embed(
                    # 'This command only takes in one argument'
                    lang.phrases.dequeue_arg
                ),
                delete_after=10
            )
        else:
            channel = ctx.author.voice.channel
            voice = ctx.voice_client
            if voice != None:
                if voice.channel != channel:
                    await ctx.send(
                        embed=create_embed(
                            # 'Please wait until other members are done listening to music'
                            lang.phrases.dequeue_wait
                        ),
                        delete_after=10
                    )
                else:
                    item = queuecol.find_one({'guild_id': ctx.guild.id})
                    queue = item['queue']
                    if 1 <= position <= item['size']:
                        info = queue[position-1]
                        if item['pointer'] >= position-1:
                            queuecol.update_one(
                                {'guild_id': ctx.guild.id},
                                {
                                    '$unset': {
                                        f'queue.{position-1}': ''
                                    },
                                    '$inc': {
                                        'pointer': -1,
                                        'size': -1
                                    }
                                }
                            )
                        else:
                            queuecol.update_one(
                                {'guild_id': ctx.guild.id},
                                {
                                    '$unset': {
                                        f'queue.{position-1}': ''
                                    },
                                    '$inc': {
                                        'size': -1
                                    }
                                }
                            )
                        queuecol.update_one(
                            {'guild_id': ctx.guild.id},
                            {
                                '$pull': {
                                    'queue': None
                                }
                            }
                        )

                        await ctx.send(
                            embed=create_embed(
                                f'{lang.phrases.dequeue_song} [{info["title"]}]({info["url"]}) {lang.phrases.dequeue_removed}'
                            ),
                            delete_after=10
                        )
                    else:
                        await ctx.send(
                            embed=create_embed(
                                f'{lang.phrases.dequeue_music} **{item["size"]}** {lang.phrases.dequeue_more_than_that}'
                            ),
                            delete_after=10
                        )
            else:
                await ctx.send(
                    embed=create_embed(
                        # 'Bot was not connected to any voice channel'
                        lang.phrases.dequeue_not_connected
                    ),
                    delete_after=10
                )

    @commands.command(
        name='clearqueue',
        aliases=['flush', 'empty', 'clearq'],
        # description='Clear the current queue',
        description=lang.descriptions.clearqueue,
        usage='`.clearqueue`'
    )
    @ensure_voice()
    @blacklist_check()
    async def clearqueue(self, ctx, arg=None):
        if arg != None:
            await ctx.send(
                embed=create_embed(
                    # 'This command does not take in any argument'
                    lang.phrases.clearqueue_arg
                ),
                delete_after=10
            )
        else:
            channel = ctx.author.voice.channel
            voice = ctx.voice_client
            if voice != None:
                if voice.channel != channel:
                    await ctx.send(
                        embed=create_embed(
                            # 'Please wait until other members are done listening to music'
                            lang.phrases.clearqueue_wait
                        ),
                        delete_after=10
                    )
                else:
                    queuecol.update_one(
                        {'guild_id': ctx.guild.id},
                        {
                            '$set': {
                                'pointer': 0,
                                'size': 0,
                                'queue': []
                            }
                        }
                    )
                    await ctx.send(
                        embed=create_embed(
                            # 'Queue cleared'
                            lang.phrases.clearqueue_cleared
                        ),
                        delete_after=10
                    )
            else:
                await ctx.send(
                    embed=create_embed(
                        # 'Bot was not connected to any voice channel'
                        lang.phrases.dequeue_not_connected
                    ),
                    delete_after=10
                )

    @commands.command(
        name='loop',
        aliases=['repeat', ],
        # description='Toggle between looping all, one or off',
        description=lang.descriptions.loop,
        # usage='`.loop [all/one/off]`',
        usage='`.loop [all/one/off]`'
    )
    @ensure_voice()
    @blacklist_check()
    async def loop(self, ctx, arg='all'):
        channel = ctx.author.voice.channel
        voice = ctx.voice_client
        if voice != None:
            if voice.channel != channel:
                await ctx.send(
                    embed=create_embed(
                        # 'Please wait until other members are done listening to music'
                        lang.phrases.loop_wait
                    ),
                    delete_after=10
                )
            else:
                queue = queuecol.find_one({'guild_id': ctx.guild.id})
                if arg == 'all':
                    queuecol.update_one(
                        {'guild_id': ctx.guild.id},
                        {
                            '$set': {
                                'loop': 'all'
                            }
                        }
                    )
                    await ctx.send(
                        embed=create_embed(
                            # 'Repeating all songs in the music queue'
                            lang.phrases.loop_repeat_all
                        ),
                        delete_after=10
                    )
                elif arg == 'one':
                    queuecol.update_one(
                        {'guild_id': ctx.guild.id},
                        {
                            '$set': {
                                'loop': 'one'
                            }
                        }
                    )
                    await ctx.send(
                        embed=create_embed(
                            # 'Repeating the current song in the music queue'
                            lang.phrases.loop_repeat_one
                        ),
                        delete_after=10
                    )
                elif arg == 'off':
                    queuecol.update_one(
                        {'guild_id': ctx.guild.id},
                        {
                            '$set': {
                                'loop': 'off'
                            }
                        }
                    )
                    await ctx.send(
                        embed=create_embed(
                            # 'Repeating song is now off'
                            lang.phrases.loop_repeat_off
                        ),
                        delete_after=10
                    )
                else:
                    await ctx.send(
                        embed=create_embed(
                            # 'Please use the correct argument'
                            lang.phrases.loop_incorrect_arg
                        ),
                        delete_after=10
                    )
        else:
            await ctx.send(
                embed=create_embed(
                    # 'Bot was not connected to any voice channel'
                    lang.phrases.loop_not_connected
                ),
                delete_after=10
            )

    @commands.group(
        invoke_without_command=True,
        name='playlist',
        aliases=['pl', 'plist'],
        # description='Access playlist features',
        description=lang.descriptions.playlist,
        # usage='`.playlist [option]`',
        usage='`.playlist [option]`'
    )
    @blacklist_check()
    async def playlist(self, ctx, page: int = 1):
        size = playlistcol.count_documents({'guild_id': ctx.guild.id})
        if size == 0:
            await ctx.send(
                embed=create_embed(
                    # 'There is no playlist created in this guild'
                    lang.phrases.playlist_no_in_guild
                ),
                delete_after=10
            )
        else:
            output = ''
            playlist_list = playlistcol.find({'guild_id': ctx.guild.id})
            pages = math.ceil(size/10)
            if 1 <= page <= pages:
                counter = 1+(page-1)*10
                for pl in playlist_list[(page-1)*10:page*10]:
                    output += f'{counter}. {pl["name"]}\n'
                    counter += 1
            embed = discord.Embed(
                color=discord.Color.orange(),
                description=output,
                # title=f'**Playlists in {ctx.guild.name}**',
                title=f'**{lang.phrases.playlist_on_server} {ctx.guild.name}**',
                timestamp=ctx.message.created_at
            )
            embed.set_footer(
                text=f'{lang.phrases.playlist_page} {page} {lang.phrases.playlist_of} {pages}'
            )
            await ctx.send(
                embed=embed
            )

    @playlist.command(
        name='play',
        # description='Add the playlist to queue and start playing',
        description=lang.descriptions.playlist_play,
        # usage='`.playlist play [playlist name]`',
        usage='`.playlist play [имя плейлиста]`',
        aliases=['p', ]
    )
    @ensure_voice()
    @blacklist_check()
    async def playlist_play(self, ctx, *, name: str):
        playlist = playlistcol.find_one(
            {
                'guild_id': ctx.guild.id,
                'name': name
            }
        )
        if playlist == None:
            await ctx.send(
                embed=create_embed(
                    f'{lang.phrases.playlist_play_playlist} **{name}** {lang.phrases.playlist_play_not_found}'
                ),
                delete_after=10
            )
        else:
            text_channel = ctx.channel
            channel = ctx.author.voice.channel
            voice = ctx.voice_client
            if voice != None:
                if voice.channel != channel:
                    if self.ensure_bot_alone(ctx):
                        if voice.is_playing() or voice.is_paused():
                            queuecol.update_one(
                                {'guild_id': ctx.guild.id},
                                {
                                    '$set': {
                                        'size': 0,
                                    }
                                }
                            )
                            voice.stop()
                            voice = await channel.connect(reconnect=True)
                        else:
                            queuecol.delete_one({'guild_id': ctx.guild.id})
                            await voice.move_to(channel)
                        queuecol.insert_one(
                            {
                                'guild_id': ctx.guild.id,
                                'text_channel': ctx.channel.id,
                                'voice_channel': voice.channel.id,
                                'state': 'Playing',
                                'loop': 'off',
                                'volume': 0.5,
                                'pointer': 0,
                                'size': 0,
                                'queue': [],
                            }
                        )
                        queuecol.update_one(
                            {'guild_id': ctx.guild.id},
                            {
                                '$push': {
                                    'queue': {
                                        '$each': playlist['song_list']
                                    }
                                },
                                '$inc': {
                                    'size': playlist['size']
                                }
                            }
                        )
                        await ctx.send(
                            embed=create_embed(
                                f'{lang.phrases.playlist_play_playlist} **{name}** {lang.phrases.playlist_play_added_to_queue}'
                            ),
                            delete_after=10
                        )
                        self.play_song(ctx.guild)
                    else:
                        await ctx.send(
                            embed=create_embed(
                                # 'Please wait until other members are done listening to music'
                                lang.phrases.playlist_play_wait
                            ),
                            delete_after=10
                        )
                else:
                    queuecol.update_one(
                        {'guild_id': ctx.guild.id},
                        {
                            '$push': {
                                'queue': {
                                    '$each': playlist['song_list']
                                }
                            },
                            '$inc': {
                                'size': playlist['size']
                            }
                        }
                    )
                    await ctx.send(
                        embed=create_embed(
                            f'{lang.phrases.playlist_play_playlist} **{name}** {lang.phrases.playlist_play_added_to_queue}'
                        ),
                        delete_after=10
                    )
                    if voice.is_playing() == False and voice.is_paused() == False:
                        self.play_song(voice)
            else:
                voice = await channel.connect(reconnect=True)
                if queuecol.find_one({'guild_id': ctx.guild.id}) != None:
                    queuecol.delete_one({'guild_id': ctx.guild.id})
                queuecol.insert_one(
                    {
                        'guild_id': ctx.guild.id,
                        'text_channel': ctx.channel.id,
                        'voice_channel': voice.channel.id,
                        'state': 'Playing',
                        'loop': 'off',
                        'volume': 0.5,
                        'pointer': 0,
                        'size': 0,
                        'queue': [],
                    }
                )
                queuecol.update_one(
                    {'guild_id': ctx.guild.id},
                    {
                        '$push': {
                            'queue': {
                                '$each': playlist['song_list']
                            }
                        },
                        '$inc': {
                            'size': playlist['size']
                        }
                    }
                )
                await ctx.send(
                    embed=create_embed(
                        f'{lang.phrases.playlist_play_playlist} **{name}** {lang.phrases.playlist_play_added_to_queue}'
                    ),
                    delete_after=10
                )
                self.play_song(ctx.guild)

    @playlist.command(
        name='create',
        # description='Create a playlist',
        description=lang.descriptions.playlist_create,
        # usage='`.playlist create [playlist name]`',
        usage='`.playlist create [имя плейлиста]`'
    )
    @blacklist_check()
    async def create(self, ctx, *, name: str):
        playlist = playlistcol.find_one(
            {
                'guild_id': ctx.guild.id,
                'name': name
            }
        )
        if playlist == None:
            playlistcol.insert_one(
                {
                    'guild_id': ctx.guild.id,
                    'name': name,
                    'size': 0,
                    'song_list': [],
                }
            )
            await ctx.send(
                embed=create_embed(
                    f'{lang.phrases.playlist_create_playlist} **{name}** {lang.phrases.playlist_create_created}'
                ),
                delete_after=10
            )
        else:
            await ctx.send(
                embed=create_embed(
                    # 'A playlist with the same name already exist'
                    lang.phrases.playlist_create_already_exist
                ),
                delete_after=10
            )

    @playlist.command(
        name='delete',
        # description='Delete an existing playlist',
        description=lang.descriptions.playlist_delete,
        # usage='`.playlist delete [playlist name]`',
        usage='`.playlist delete [имя плейлиста]`',
        aliases=['del', ]
    )
    @blacklist_check()
    async def delete(self, ctx, *, name: str):
        playlist = playlistcol.find_one(
            {
                'guild_id': ctx.guild.id,
                'name': name
            }
        )
        if playlist == None:
            await ctx.send(
                embed=create_embed(
                    f'{lang.phrases.playlist_delete_playlist} **{name}** {lang.phrases.playlist_delete_not_found}'
                ),
                delete_after=10
            )
        else:
            playlistcol.delete_one(
                {
                    'guild_id': ctx.guild.id,
                    'name': name
                }
            )
            await ctx.send(
                embed=create_embed(
                    f'{lang.phrases.playlist_delete_playlist} **{name}** {lang.phrases.playlist_delete_deleted}'
                ),
                delete_after=10
            )

    @playlist.command(
        name='add',
        # description='Add a song to an existing playlist',
        description=lang.descriptions.playlist_add,
        # usage='`.playlist add [playlist name] [song name or url]`',
        usage='`.playlist add [имя плейлиста] [url или название песни]`'
    )
    @blacklist_check()
    async def add(self, ctx, name: str, *, url: str):
        playlist = playlistcol.find_one(
            {
                'guild_id': ctx.guild.id,
                'name': name
            }
        )
        if playlist != None:
            info = self.extract_info(url, ctx)
            if "_type" in info and info["_type"] == "playlist":
                if 'title' not in info['entries'][0]:
                    await ctx.send(
                        embed=create_embed(
                            # 'This playlist link is not supported'
                            lang.phrases.playlist_add_not_supported
                        ),
                        delete_after=10
                    )
                else:
                    if len(info['entries']) == 1:
                        song_info = info['entries'][0]
                        playlistcol.update_one(
                            {
                                'guild_id': ctx.guild.id,
                                'name': name
                            },
                            {
                                '$push': {
                                    'song_list': {
                                        'url': song_info['webpage_url'],
                                        'title': song_info['title']
                                    }
                                },
                                '$inc': {
                                    'size': 1
                                }
                            }
                        )
                        await ctx.send(
                            embed=create_embed(
                                f'{lang.phrases.playlist_add_song} [{song_info["title"]}]({song_info["webpage_url"]}) {lang.phrases.playlist_add_added_to} **{name}**'
                            ),
                            delete_after=10
                        )
                    else:
                        for song in info['entries']:
                            playlistcol.update_one(
                                {
                                    'guild_id': ctx.guild.id,
                                    'name': name
                                },
                                {
                                    '$push': {
                                        'song_list': {
                                            'url': song['webpage_url'],
                                            'title': song['title']
                                        }
                                    },
                                    '$inc': {
                                        'size': 1
                                    }
                                }
                            )
                        await ctx.send(
                            embed=create_embed(
                                f'{len(info["entries"])} {lang.phrases.playlist_add_songs_added_to} **{name}**'
                            ),
                            delete_after=10
                        )
            else:
                playlistcol.update_one(
                    {
                        'guild_id': ctx.guild.id,
                        'name': name
                    },
                    {
                        '$push': {
                            'song_list': {
                                'url': info['webpage_url'],
                                'title': info['title']
                            }
                        },
                        '$inc': {
                            'size': 1
                        }
                    }
                )
                await ctx.send(
                    embed=create_embed(
                        f'Song [{info["title"]}]({info["webpage_url"]}) added to **{name}**'
                    ),
                    delete_after=10
                )
        else:
            await ctx.send(
                embed=create_embed(
                    f'{lang.phrases.playlist_add_song} **{name}** {lang.phrases.playlist_add_not_found}\n{lang.phrases.playlist_add_note}: {lang.phrases.playlist_add_note_content}'
                ),
                delete_after=10
            )

    @playlist.command(
        name='remove',
        # description='Remove a song from an existing playlist',
        description=lang.descriptions.playlist_remove,
        # usage='`.playlist remove [song number] [playlist name]`',
        usage='`.playlist remove [номер песни] [имя плейлиста]`',
        aliases=['rm']
    )
    @blacklist_check()
    async def remove(self, ctx, position: int, *, name: str):
        playlist = playlistcol.find_one(
            {
                'guild_id': ctx.guild.id,
                'name': name
            }
        )
        if playlist != None:
            if 1 <= position <= playlist['size']:
                info = playlist['song_list'][position-1]
                playlistcol.update_one(
                    {
                        'guild_id': ctx.guild.id,
                        'name': name
                    },
                    {
                        '$unset': {
                            f'song_list.{position-1}': ''
                        },
                        '$inc': {
                            'size': -1
                        }
                    }
                )
                playlistcol.update_one(
                    {
                        'guild_id': ctx.guild.id,
                        'name': name
                    },
                    {
                        '$pull': {
                            'song_list': None
                        }
                    }
                )
                await ctx.send(
                    embed=create_embed(
                        f'{lang.phrases.playlist_remove_song} [{info["title"]}]({info["url"]}) {lang.phrases.playlist_remove_deleted_from} **{name}**'
                    ),
                    delete_after=10
                )
            else:
                await ctx.send(
                    embed=create_embed(
                        f'{lang.phrases.playlist_remove_the_playlist_have} **{playlist["size"]}** {lang.phrases.playlist_remove_more_than_that}!'
                    )
                )
        else:
            await ctx.send(
                embed=create_embed(
                    f'{lang.phrases.playlist_remove_playlist} **{name}** {lang.phrases.playlist_remove_not_found}'
                )
            )

    @playlist.command(
        name='list',
        # description='List the songs in an existing playlist',
        description=lang.descriptions.playlist_list,
        # usage='`.playlist list [playlist name] [page]`',
        usage='`.playlist list [имя плейлиста] [страница]`',
        aliases=['ls']
    )
    @blacklist_check()
    async def _list(self, ctx, name: str, page: int = 1):
        playlist = playlistcol.find_one(
            {
                'guild_id': ctx.guild.id,
                'name': name
            }
        )
        if playlist != None:
            if playlist['size'] == 0:
                await ctx.send(
                    embed=create_embed(
                        # 'The playlist is empty'
                        lang.phrases.playlist_list_empty
                    ),
                    delete_after=10
                )
            else:
                output = ''
                song_list = playlist['song_list']
                pages = math.ceil(playlist['size']/10)
                if 1 <= page <= pages:
                    counter = 1 + (page-1)*10
                    for song in song_list[(page-1)*10:page*10]:
                        output += f'{counter}. [{song["title"]}]({song["url"]})\n'
                        counter += 1
                    embed = discord.Embed(
                        color=discord.Color.orange(),
                        description=output,
                        title=f'**{name}**',
                        timestamp=ctx.message.created_at
                    )
                    embed.add_field(
                        name='Entries',
                        value=f"{playlist['size']}"
                    )
                    embed.set_footer(
                        text=f'{lang.phrases.playlist_list_Page} {page} {lang.phrases.playlist_list_of} {pages} {lang.phrases.playlist_list_note}'
                    )
                    await ctx.send(
                        embed=embed
                    )
                else:
                    await ctx.send(
                        embed=create_embed(
                            # 'The page you specified does not exist'
                            lang.phrases.playlist_list_page_not_exist
                        ),
                        delete_after=10
                    )
        else:
            ctx.send(
                embed=create_embed(
                    # 'The playlist does not exist\nNote: Try adding " " to your playlist name'
                    lang.phrases.playlist_list_playlist_not_exist
                )
            )

    # Event listener
    @commands.Cog.listener()
    async def on_ready(self):
        queues = queuecol.find()
        for queue in queues:
            guild = self.client.get_guild(queue['guild_id'])
            voice = guild.voice_client
            if voice == None:
                voice_channel = guild.get_channel(queue['voice_channel'])
                voice = await voice_channel.connect(reconnect=True)
                if queue['state'] == 'Playing':
                    if queue['size'] >= 1:
                        self.play_song(guild)
                        text_channel = guild.get_channel(queue['text_channel'])
                        await text_channel.send(
                            embed=create_embed(
                                # 'Bot was restarted, playing from the most recent song in queue'
                                lang.phrases.on_ready_restarted
                            ),
                            delete_after=10
                        )
            else:
                if voice.is_paused():
                    if queue['state'] == 'Playing':
                        if queue['size'] >= 1:
                            voice.resume()

    @commands.Cog.listener()
    async def on_disconnect(self):
        queues = queuecol.find()
        for queue in queues:
            guild = self.client.get_guild(queue['guild_id'])
            if guild.voice_client.is_playing():
                guild.voice_client.pause()

    # Error handler
    @play.error
    async def play_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                embed=create_embed(
                    # 'The play command also need a link or search keyword to work'
                    lang.errors.play_error
                ),
                delete_after=10
            )

    @dequeue.error
    async def dequeue_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(
                embed=create_embed(
                    # 'Please use the correct argument'
                    lang.errors.dequeue_error
                ),
                delete_after=10
            )

    @add.error
    async def add_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                embed=create_embed(
                    # 'Please specify the correct argument'
                    lang.errors.add_error
                )
            )


# Add cog
def setup(client):
    client.add_cog(Music(client))
