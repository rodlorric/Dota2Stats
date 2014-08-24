import urllib2
import json
import os
import datetime
import mimetypes
#from views import Player, Match, PlayerInfo
from django.conf import settings
from urllib2 import URLError
#from stats.models import AbilityUpgrade
from stats.models import AbilityUpgrades, Accounts
from djcelery import celery
import time

def webAPICall(url):
    time.sleep(0.1)
    try:
        raw_response = urllib2.urlopen(url).read()
    except URLError:
        return  
    if raw_response:
        response = json.loads(raw_response)
    
    return response
    
def resolveVanityURL(vanity_name):
    url = settings.STEAM_BASE_URL + 'ISteamUser/ResolveVanityURL/v0001/?key=' + settings.STEAM_API_KEY + '&vanityurl=' + vanity_name
    return webAPICall(url)

def getPlayerSummaries(steam_id):
    url = settings.STEAM_BASE_URL + 'ISteamUser/GetPlayerSummaries/v0002/?key=' + settings.STEAM_API_KEY+'&steamids=' + str(steam_id)
    return webAPICall(url)

def getMatchHistory(account_id, matches_requested, start_at_match_id):
    url = settings.STEAM_BASE_URL + 'IDOTA2Match_570/GetMatchHistory/V001/?key=' + settings.STEAM_API_KEY + '&account_id=' + str(account_id) + '&matches_requested=' + str(matches_requested) + '&start_at_match_id=' + str(start_at_match_id)
    return webAPICall(url)

def getMatchDetails(match_id):
    url = settings.STEAM_BASE_URL + 'IDOTA2Match_570/GetMatchDetails/V001/?key=' + settings.STEAM_API_KEY + '&match_id=' + str(match_id)
    return webAPICall(url)

def getHeroes():
    url = settings.STEAM_BASE_URL + 'IEconDOTA2_570/GetHeroes/v0001/?key='+ settings.STEAM_API_KEY + '&language=en_us'
    return webAPICall(url)

def getItems():
    url = settings.STEAM_BASE_URL + 'IEconDOTA2_570/GetGameItems/v0001/?key=' + settings.STEAM_API_KEY
    return webAPICall(url)

def getCountries():
    url = settings.COUNTRIES_URL
    return webAPICall(url)

def getCountryCoordinates(country_code, country_name):
    url = settings.COUNTRY_INFO % (country_code, country_name)
    url = url.replace(' ', '%20')
    return webAPICall(url)

def getSteamID64bit(steam_id):
    CONST = 76561197960265728
    return CONST + steam_id

def getSteamID32bit(steam_id):
    CONST = 76561197960265728
    return long(steam_id)-CONST

def resolveSteamId(account_id):
    account_id = str(account_id)
    player = None
    if account_id not in settings.INVALID_ACCOUNT_IDS:
        if account_id.isdigit():
            #64 bits, i.e. 76561198018435337
            if len(str(account_id)) != 17:
                account_id = getSteamID64bit(int(account_id))
        else:
            try:
                account_id = getSteamID64bit(Accounts.objects.get(personaname = account_id).account_id)
            except Accounts.DoesNotExist:
                account_id = resolveVanityURL(account_id)
                if account_id['response']['success'] != 42:
                    account_id = account_id['response']['steamid']
                else:
                    account_id = 76561202255233023
    else:
        account_id = 76561202255233023
    player = Accounts(account_id = account_id)
    return player


"""
def resolveSteamId(account_id):
    account_id = str(account_id)
    player = None
    if account_id not in settings.INVALID_ACCOUNT_IDS:
        # i.e. Sphexing
        if not account_id.isdigit():
            try:
                player = Accounts.objects.get(personaname = account_id)
                account_id = player.steamid
            except Accounts.DoesNotExist:
                player = None
                account_id = resolveVanityURL(account_id)                
                if account_id['response']['success'] != 42:
                    #64 bits
                    account_id = account_id['response']['steamid']
                else:
                    account_id = 76561202255233023
        # 64 bits, i.e. 76561198018435337
        elif len(str(account_id)) == 17:
            #account_id = getSteamID32bit(int(account_id))
            pass
        #else... 32 bits
        else: 
            #64 bits
            account_id = getSteamID64bit(int(account_id))            
        try:
            player = Accounts.objects.get(account_id = getSteamID32bit(account_id))
        except Accounts.DoesNotExist:                
            player = Accounts(account_id = getSteamID32bit(account_id))
    else:
        player = Accounts(account_id = getSteamID32bit(76561202255233023))
    return player
"""

def updatePlayerInfo(account_id_list):
    player_info_list = []
    acc_list = ''
    for account_id in account_id_list:
        player = resolveSteamId(account_id)
        acc_list += str(player.account_id) + ','
    if acc_list != '':
        aclist = acc_list.split(',')
        for a in aclist[:len(aclist)-1]:
            if str(getSteamID32bit(a)) in settings.INVALID_ACCOUNT_IDS:
                p = Accounts(account_id = str(getSteamID32bit(a)), personaname = 'Anonymous')                
            else:
                try:
                    p = Accounts.objects.get(account_id = getSteamID32bit(a))
                except Accounts.DoesNotExist:
                    p = Accounts(account_id = str(getSteamID32bit(a)), personaname = 'Anonymous')
            player_info_list.append(p)
    return player_info_list

def saveMatch(match_id):
    print('Saving match: ' + str(match_id))
    match = getMatchDetails(match_id)['result']
    players_from_match = match.pop('players')
    pi_list = []
    for pfm in players_from_match:        
        if 'account_id' in pfm:
            steamid = getSteamID64bit(pfm['account_id'])
            pi_list.append(steamid)
            account_id = pfm['account_id']
        else:
            account_id = 0
        pfm.update({'account_id' : account_id, 'match_id' : match_id})
        if 'ability_upgrades' in pfm:
            ability_upgrades = pfm.pop('ability_upgrades')
            for au in ability_upgrades:
                au['match_id'] = match_id
                au['player_slot'] = pfm['player_slot']
                au['time'] = str(datetime.timedelta(seconds=au['time']))                        
                ability = AbilityUpgrade(**au)
                ability.save()
            if 'additional_units' in pfm:
                addition_units = pfm.pop('additional_units')
        try:
            player = Player.objects.get(account_id = account_id, match_id = match_id, player_slot = pfm['player_slot'])
        except Player.DoesNotExist:
            player = Player(**pfm)
            player.save()
    match['start_time'] = str(datetime.datetime.fromtimestamp(int(match['start_time'])).strftime('%Y-%m-%d %H:%M:%S'))
    match['duration'] = str(datetime.timedelta(seconds=match['duration']))
    try:
        match.pop('picks_bans')
    except:
        pass
    match = Match(**match)
    # to avoid duplicates
    try:
        Match.objects.get(match_id = match_id)
    except Match.DoesNotExist:
        match.save()
    #updating player infos    
    updatePlayerInfo(pi_list)   
    return match

def gmap_img(points):
    markers = '&'.join('markers=%s' % p 
                       for p in points)
    return settings.GMAPS_URL + markers


def stringifyImage(url):
    tmpdir = 'tmp'
    mmtp = mimetypes.guess_type(url, strict=True)
    if not mmtp[0]:
        return False
 
    ext = mimetypes.guess_extension(mmtp[0])
    if not os.path.exists(tmpdir):
        os.makedirs(tmpdir)
    f = open(tmpdir+'/tmp'+ext,'wb')
    f.write(urllib2.urlopen(url).read())
    f.close()
    img = open(tmpdir+'/tmp'+ext, "rb").read().encode("base64").replace("\n","")
    return 'data:'+mmtp[0]+';base64,' +img