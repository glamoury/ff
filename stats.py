import discord 
import requests
import json
import atexit
import pprint
import myconfig
from discord.ext import commands

allowableScopes = ['s3','lifetime']
allowableGameModes = ['solo','duo','squad','solos','duos','squads','total']
bot = commands.Bot(command_prefix='!',description='Fortnite Stats')
bot.remove_command('help')


def get_scope_str(scope):
    scope_str = " in "
    if(scope == 'lifetime'):
        scope_str += " their "
    return scope_str

def check_scope(scope):
    return scope in allowableScopes

def check_game_mode(game_mode):
    return game_mode in allowableGameModes


@bot.command(pass_context=True)
async def help(ctx):
    embed = discord.Embed(title="Fortnite stats bot", description = "Gets fortnite stats for a given user")
    embed.add_field(name="!kills", value="Gets total kills for a user based on game mode and scope.\nTakes exactly 3 arguments: \n\nusername[epic username]\nscope [lifetime, s3]\ngame_mode [solo, duo, squad]\n\nExamples: \n\t!kills PikachuDownB s3 solo\n\t!kills Faemn lifetime duo", inline=False)
    embed.add_field(name="!kdr", value ="Gets K/D ratio for a user based on game mode and scope.\nTakes exactly 3 arguments: \n\nusername[epic username]\nscope [lifetime, s3]\ngame_mode[solo,duo,squad]\n\nExamples:\n\t!kdr PikachuDownB s3 solo\n\t!kdr Ninja lifetime squad", inline =False)
    embed.add_field(name="!winrate", value ="Gets win rate for a user based on game mode and scope.\nTakes exactly 3 arguments: \n\nusername[epic username]\nscope [lifetime, s3]\ngame_mode[solo,duo,squad]\n\nExamples:\n\t!winrate PikachuDownB s3 solo\n\t!winrate Ninja lifetime squad", inline =False)
    embed.add_field(name="!trn", value ="Gets TRN rating for a user based on game mode and scope.\nTakes exactly 3 arguments: \n\nusername[epic username]\nscope [lifetime, s3]\ngame_mode[solo,duo,squad]\n\nExamples:\n\t!kdr PikachuDownB s3 solo\n\t!trn Ninja lifetime squad", inline =False)
    embed.add_field(name="!source", value="Source code for this bot", inline=True)
    await bot.say(embed = embed)

@bot.command(pass_context=True)
async def cat(ctx):
    await bot.say("https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif") 

@bot.event
async def on_ready():
    print('Logged in as', bot.user.name)
    
@bot.command()
async def hello():
    await bot.say('Hello')

@bot.command(pass_context=True)
async def kills(ctx, user, scope, game_mode='total'):
    if(not check_scope(scope)):
        await bot.say(scope + " is not an allowable scope. !help for options")
    elif(not check_game_mode(game_mode)):
        await bot.say(game_mode + " is not an allowable game mode. !help for options")
    else:
        if game_mode == 'total':
            total_kills = get_lifetime_stat('Kills', user)
            msg = user + " has " + str(total_kills) + " total kills across all game modes for all time."
            await bot.say(msg)
        else:
            kill_stats = get_stat_dict(user, scope, game_mode,'kills')
            amount = kill_stats['value']
            percentile = kill_stats['percentile'];
            scopeStr = get_scope_str(scope)
            msg = user + " has " + str(amount) + " total kills in " + game_mode + scopeStr + scope + ". This puts " + user + " in the top " +str(percentile) + " percentile."
            await bot.say(msg)

@bot.command(pass_context=True)
async def kdr(ctx, user, scope, game_mode):
    if(not check_scope(scope)):
        await bot.say(scope + " is not an allowable scope. !help for options")
    elif(not check_game_mode(game_mode)):
        await bot.say(game_mode + " is not an allowable game mode. !help for options")
    else:
        kdr_stats = get_stat_dict(user, scope, game_mode, 'kd')
        value = kdr_stats['value']
        percentile = str(kdr_stats['percentile'])
        scopeStr = get_scope_str(scope)
        msg = user + " has a K/D ratio of " + value + " for " + game_mode+ scopeStr + scope + ". This puts " + user + " in the top " + percentile + " percentile." 
        await bot.say(msg)

@bot.command(pass_context=True)
async def trn(ctx, user, scope, game_mode):
    if(not check_scope(scope)):
        await bot.say(scope + " is not an allowable scope. !help for options")
    elif(not check_game_mode(game_mode)):
        await bot.say(game_mode + " is not an allowable game mode. !help for options")
    else:
        trn_stats = get_stat_dict(user, scope, game_mode, 'trnRating')
        value = trn_stats['displayValue']
        percentile = str(trn_stats['percentile'])
        scopeStr = get_scope_str(scope)
        msg = user + " has a TRN Rating of " + value + " for " + game_mode + scopeStr + scope + ". This puts " + user + " in the top " + percentile + " percentile."
        await bot.say(msg)

@bot.command(pass_context=True)
async def winrate(ctx, user, scope, game_mode):
    if(not check_scope(scope)):
        await bot.say(scope + " is not an allowable scope. !help for options")
    elif(not check_game_mode(game_mode)):
        await bot.say(game_mode + " is not an allowable game mode. !help for options")
    else:
        win_stats = get_stat_dict(user, scope, game_mode, 'winRatio')
        value = win_stats['displayValue']
        percentile = str(win_stats['percentile'])
        scopeStr = get_scope_str(scope)
        msg = user + " has a win ratio of " + value + "% for " + game_mode + scopeStr + scope + ". This puts " + user + " in the top " + percentile + " percentile."
        await bot.say(msg)

@bot.command(pass_context=True)
async def yikes(ctx):
  embed = discord.Embed()
  embed.add_field(name="yikes", value="Y  I  K  E  S", inline=False)
  await bot.say(embed = embed)

@bot.command(pass_context=True)
async def source(ctx):
    await bot.say('Source code for this bot can be be found at https://github.com/brendan-robert-1/fortnitebot')

fnTrackerUrl="https://api.fortnitetracker.com/v1/profile/pc/"
auth={'TRN-Api-Key':myconfig.trn}
scope_dict={
        ('solo','lifetime'):'p2',
        ('solo','s3'):'curr_p2',
        ('duo','lifetime'):'p10',
        ('duo','s3'):'curr_p10',
        ('squad','lifetime'):'p9',
        ('squad','s3'):'curr_p9'
        }

def get_user_json(nickname):
    finalUrl = fnTrackerUrl+nickname
    r = requests.get(finalUrl, headers=auth)
    return r.json()

def get_stats(scope, game_mode, payload):
    stats = payload['stats']
    key = (game_mode, scope)
    statsKey = scope_dict[key]
    return stats[statsKey]

def get_lifetime_stat(key, user):
    payload = get_user_json(user)
    lifetime_stat_dict = payload['lifeTimeStats']
    for entry in lifetime_stat_dict:
        if entry['key'] == key:
            return entry['value']

def get_stat_dict(user, scope, game_mode, stat):
    payload=get_user_json(user)
    statsByScope = get_stats(scope, game_mode, payload)
    return statsByScope[stat]

def main():
    try:
        print("Starting fortnite stats bot...")
        bot.run(myconfig.appId)
    finally:
        print('Shutting down fornite bot')
        bot.close()

if __name__ == '__main__':
    main()
