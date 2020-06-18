import discord
import youtube_dl
from youtube_dl import utils
import os
import asyncio
import math
import pymongo
from helper import *
from discord.ext import commands
import asyncio
import random
# import nn
import discord
import youtube_dl
from discord.ext import commands
from discord.utils import get

# import cogs.service.nn as nn
import cogs.service.speach as speach
import cogs.service.utils as utils
import cogs.service.wolfram as wolfram

class Test(commands.Cog,name='Other'):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def hello(self, ctx):
        await ctx.send(f'Привет,{ctx.author.mention}, я бот Me$h0k')

    @commands.command()
    async def wolframtext(self, ctx, *, cmd):
        with ctx.typing():
            await ctx.send('Уже работаю')
            res = await wolfram.nat_lang_full_no_HoldComplete(cmd)
            cnt = 0
            for line in res:
                if line.is_this_a_file:
                    await ctx.send(file=discord.File(line.content))
                    cnt += 1
                else:
                    if not line.HoldComplete:
                        await ctx.send(line.content)
                        cnt += 1

            if cnt == 0:
                await ctx.send('Ничего не смог')
            elif (1 <= cnt) and (cnt <= 2):
                await ctx.send('Это немного, но зато честная работа')
            else:
                await ctx.send('Я гений')

    @commands.command(
        name='wolfram',
        aliases=['wl', 'wolf'],
        description='Магия вольфрама',
        usage='`.wolfram`'
    )
    async def wolfram(self, ctx, *, cmd):
        ctx.send('Работаю')
        with ctx.typing():
            _url = utils.encode_hex_for_wl(cmd)
            await ctx.send(
                file=discord.File(await utils.page_screenshot(f'https://www.wolframalpha.com/input/?i={_url}')))

    @commands.command()  # Не дописанна
    async def cfg(self, ctx):
        cfgs = []
        with open('configs.py') as conf:
            for i in conf.readlines():
                temp = utils.remove_spaces(i)
                temp = i.split('=')
                cfgs.append({temp[0]: temp[1]})
        if len(ctx.message.content) > 4:
            exp = ctx.message.content[5:]
            exp = exp.split(' ')
            name = exp[0]
            value = exp[1]
            if name is not None:
                if value is not None:
                    await ctx.send(name + '=' + value)
        else:
            for i in cfgs:
                a = i.items()
                await ctx.send(a)


    @commands.command()
    async def add(self, ctx,file,*,phrase):
        with open(f"{file}.txt", "a", encoding='utf-8') as texts:
            texts.write(phrase + ' \n')
        await ctx.send("Добавленна фраза: {}".format(phrase))

    @commands.command()
    async def phrase(self, ctx):
        with open("phrases.txt", "r", encoding='utf-8') as texts:
            text = texts.readlines()
            linesc = len(text)
            index = random.randint(a=0, b=linesc - 1)
            ph = text[index][:-1]
        await ctx.send(ph)

    @commands.command()
    async def lastphrase(self, ctx):
        with open("phrases.txt", "r", encoding='utf-8') as texts:
            text = texts.readlines()
            ph = text[-1][:-1]
        await ctx.send(ph)

    @commands.command()
    async def rap(self, ctx, *, start: str):
        await ctx.send('Начало рэпа: ' + start)
        rap = nn.pred(sentence=start.lower())
        await ctx.send(rap)
        #
        # song = speach.tell(rap)
        # ctx.voice_client.play(discord.FFmpegPCMAudio(song),
        #                       after=lambda e: print('Player error: %s' % e) if e else None)


# Add cog
def setup(client):
    client.add_cog(Test(client))
