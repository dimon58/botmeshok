# Imports
import os

import pymongo
from discord.ext import commands

# # Load environmental variables
# try:
#     exec(open('variable.py').read())
# except:
#     print('shit does not work, abort mission')

# Connect to mongodb database
try:
    os.mkdir('temp')
except:
    pass
with open('mongo.txt', 'r') as mongo:
    client = pymongo.MongoClient(mongo.read())
db = client['bot_meshok']
guildcol = db['prefix']
queuecol = db['queue']
playlistcol = db['playlist']
blacklist_admin = db['adminblacklist']


# Load custom prefixes
def get_prefix(client, message):
    extras = guildcol.find_one({'guild_id': message.guild.id})
    prefixes = extras['prefixes']
    return commands.when_mentioned_or(*prefixes)(client, message)


def blacklist_check():
    def predicate(ctx):
        author_id = ctx.author.id
        if blacklist_admin.find_one({'user_id': author_id}):
            return False
        return True

    return commands.check(predicate)


# Start the bot
client = commands.Bot(
    command_prefix=get_prefix,
    owner_id=int('491210801609310208')
)

# Remove default help command
client.remove_command('help')

# Load up cogs
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

# Run the bot
with open('TOKEN.txt', 'r', encoding='utf-8') as TOKEN:
    client.run(TOKEN.read(), reconnect=True)
