from django.http import HttpResponseRedirect
from django.utils.encoding import smart_str, smart_unicode
from django.core.urlresolvers import reverse
from django.views import generic
from stats.models import Player, Match, PlayerInfo, Hero, AbilityUpgrade, Country, Ability, Item
from django.conf import settings
from django.db.models import Q
import time
import modules
import datetime
import clusters_json
import lobbies_json
import types_json
import time
import heroes_json
import abilities_json
import urllib
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.contrib.auth import logout as auth_logout
from social_auth.db.django_models import UserSocialAuth
from django.shortcuts import render
import tasks
from operator import itemgetter

class PlayersView(generic.ListView):
    template_name = 'stats/players.html'
    context_object_name = 'players_list'    

    def get_queryset(self):
        pl = Player.objects.filter(~Q(account_id__in = settings.INVALID_ACCOUNT_IDS))[:20]
        new_pl = []
        for player in pl:        
            if any(player.account_id ==  s.account_id for s in new_pl):
                continue
            else:
                try:
                    pi = PlayerInfo.objects.get(steamid = modules.getSteamID64bit(player.account_id))
                    player.personaname = pi.personaname
                except PlayerInfo.DoesNotExist:
                    player.personaname = player.account_id
                new_pl.append(player)
        return new_pl

class MatchesxPlayer(generic.ListView):
    template_name = 'stats/matchesxplayer.html'
    context_object_name = 'match_list'
    def get_queryset(self):
        account_id = self.kwargs['account_id']
        modules.updatePlayerInfo([account_id])
        task = tasks.updatePlayer.delay(account_id)
        playermatches = Player.objects.filter(account_id = account_id).order_by('-match_id')
        matches = []
        for matchxplayer in playermatches:
            try:
                match = Match.objects.get(Q(match_id = matchxplayer.match_id), Q(game_mode__in = settings.VALID_GAME_MODES), Q(human_players = 10))
                #hero = next((h for h in heroes.JSON['heroes'] if h['id'] == matchxplayer.hero_id), None)
                try:
                    hero = Hero.objects.get(hero_id = matchxplayer.hero_id)
                    match.hero = hero.localized_name
                    #match.hero_img = heroes.IMG_URL % hero['name']
                    match.hero_img = hero.small_horizontal_portrait_uri
                except Hero.DoesNotExist:
                    hero = None
                
                match.kills = matchxplayer.kills
                match.deaths = matchxplayer.deaths
                match.assists = matchxplayer.assists
                team = matchxplayer.player_slot      
                if match.radiant_win and team < 128 or not match.radiant_win and team >= 128:
                    match.result = 'Won Match'
                else:
                    match.result = 'Lost Match'
                matches.append(match)
            except Match.DoesNotExist:
                continue     
        return matches
    
    def get_context_data(self, **kwargs):
        context = super(MatchesxPlayer, self).get_context_data(**kwargs)
        account_id = self.kwargs['account_id']
        context['account_id'] = account_id
        try:            
            pi = PlayerInfo.objects.get(steamid = modules.getSteamID64bit(int(account_id)))
            personaname = pi.personaname
        except PlayerInfo.DoesNotExist:
            personaname = 'Anonymous'
        context['personaname'] = personaname
        return context
    
class HeroesxPlayer(generic.ListView):
    template_name = 'stats/heroesxplayer.html'
    context_object_name = 'hero_list'
    
    def get_queryset(self):
        account_id = self.kwargs['account_id']
        #modules.updatePlayer(account_id)
        task = tasks.updatePlayer.delay(account_id)        
        
        h_list = []
        start = time.time()
        #hero_var = heroes.JSON['heroes']
        playermatches = Player.objects.filter(account_id = account_id).order_by('-match_id')
        for pm in playermatches:
            try:
                match = Match.objects.filter(Q(match_id = pm.match_id), Q(game_mode__in = settings.VALID_GAME_MODES), Q(human_players = 10)).get()
                if match:
                    hero = None
                    for h in h_list:
                        if h.hero_id == pm.hero_id:
                            hero = h
                            break                    
                    if not hero:
                        #hero = next((h for h in hero_var if h['id'] == pm.hero_id), None)
                        hero = Hero.objects.get(hero_id = pm.hero_id)
                        hero.matches = 0
                        hero.wins = 0
                        hero.loses = 0
                        hero.winrate = 0.0
                        #hero['small_horizontal_portrait'] = heroes.IMG_URL % hero['name']
                        h_list.append(hero)
                    
                    hero.matches += 1
                    team = int(pm.player_slot)
                    if team < 128 and match.radiant_win or team >= 128 and not match.radiant_win:
                        hero.wins += 1
                    else:
                        hero.loses += 1
                    hero.winrate = round(((hero.wins * 1.0 / hero.matches * 1.0) * 100.0), 2)
                    hero.account_id = account_id
            except Match.DoesNotExist:
                continue
        end = time.time()
        total_time = end - start      
        return sorted(h_list, key=lambda k: k.matches, reverse = True)
    
def heroDetail(request, account_id, hero_id):
    if account_id and hero_id:
        matchesxplayer = Player.objects.filter(Q(account_id = account_id), Q(hero_id = hero_id)).order_by('-match_id')
        matches = []
        for matchxplayer in matchesxplayer:
            try:
                match = Match.objects.get(Q(match_id = matchxplayer.match_id), Q(human_players = 10))
                #hero = next((h for h in heroes.JSON['heroes'] if h['id'] == matchxplayer.hero_id), None)
                hero = Hero.objects.get(hero_id = matchxplayer.hero_id)
                match.hero = hero.localized_name
                match.hero_img = hero.small_horizontal_portrait_uri
                match.kills = matchxplayer.kills
                match.deaths = matchxplayer.deaths
                match.assists = matchxplayer.assists
                team = matchxplayer.player_slot      
                if match.radiant_win and team < 128 or not match.radiant_win and team >= 128:
                    match.result = 'Won Match'
                else:
                    match.result = 'Lost Match'
                matches.append(match)
            except Match.DoesNotExist:
                continue
        context = {'match_list' : matches, 'account_id' : int(account_id)}
    return render(request, 'stats/matchesxplayer.html', context )
        
    
class MatchDetail(generic.ListView):
    template_name = 'stats/match.html'
    context_object_name = 'match' 
    
    def get_queryset(self):
        try:
            match = Match.objects.get(match_id = self.kwargs['match_id'])
        except Match.DoesNotExist:
            match = modules.saveMatch(self.kwargs['match_id'])
        cluster_list = clusters_json.JSON['regions']
        lobby_list = lobbies_json.JSON['lobbies']
        type_list = types_json.JSON['mods']
        match.cluster = next((c['name'] for c in cluster_list if c['id'] == match.cluster), None)
        match.lobby_type = next((l['name'] for l in lobby_list if l['id'] == match.lobby_type), None)
        match.game_mode = next((l['name'] for l in type_list if l['id'] == match.game_mode), None)
        return match

    def get_context_data(self, **kwargs):
        context = super(MatchDetail, self).get_context_data(**kwargs)
        players = Player.objects.filter(match_id = self.kwargs['match_id']).order_by('player_slot')
        exp_x_lvl = [0,0,200,300,400,500,600,700,800,900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000,2100,2200,2300,2400,2500]
        coordinates = []
        i = 0
        dire_exp = 0
        rad_exp = 0
        timeline_xp = []
        player_info_list = []
        acc_ids = []
        for p in players:
            if i < 5:
                p.radiant = True
            else:
                p.radiant = False
            #h = next((h for h in heroes.JSON['heroes'] if h['id'] == p.hero_id), None)
            try:
                h = Hero.objects.get(hero_id = p.hero_id)
                p.hero_id = h.hero_id
                p.hero_img = h.small_horizontal_portrait_uri
                p.hero_localized_name = h.localized_name
            except Hero.DoesNotExist:
                h = Hero(name = 'Abandoned', localized_name = 'Abandoned' )

            acc_ids.append(p.account_id)
            player_abilities = AbilityUpgrade.objects.filter(Q(match_id = p.match_id), Q(player_slot = p.player_slot)).order_by('time')
            for ab in player_abilities:
                #ab_name = next((a['name'] for a in ability_names if a['id'] == str(ab.ability)), None)
                ability = Ability.objects.get(ability_id = ab.ability)
                ab.name = ability.name
                ab.img = ability.ability_img_uri
                xp = exp_x_lvl[ab.level] if p.player_slot<128 else -exp_x_lvl[ab.level]
                timeline_xp.append((ab.time.strftime('%H:%M:%S'), xp))
            p.abilities = player_abilities
            i += 1
            try:
                p.item_0_img_uri = Item.objects.get(item_id = p.item_0).item_img_uri
            except Item.DoesNotExist:
                p.item_0_img_uri = None
            try:
                p.item_1_img_uri = Item.objects.get(item_id = p.item_1).item_img_uri
            except Item.DoesNotExist:
                p.item_1_img_uri = None
            try:
                p.item_2_img_uri = Item.objects.get(item_id = p.item_2).item_img_uri
            except Item.DoesNotExist:
                p.item_2_img_uri = None
            try:
                p.item_3_img_uri = Item.objects.get(item_id = p.item_3).item_img_uri
            except Item.DoesNotExist:
                p.item_3_img_uri = None
            try:
                p.item_4_img_uri = Item.objects.get(item_id = p.item_4).item_img_uri
            except Item.DoesNotExist:
                p.item_4_img_uri = None
            try:
                p.item_5_img_uri = Item.objects.get(item_id = p.item_5).item_img_uri
            except Item.DoesNotExist:
                p.item_5_img_uri = None
        player_info_list = modules.updatePlayerInfo(acc_ids)
        for p in players:
            pi = [pi for pi in player_info_list if str(pi.steamid) == str(modules.getSteamID64bit(p.account_id))]
            if pi:
                pi = pi[0]
                p.personaname = pi.personaname
                p.avatar = pi.avatar
                try:
                    c = Country.objects.get(countryCode = pi.loccountrycode)
                    p.country = c.countryName
                    p.flag = c.flag_uri
                    coordinates.append({'lat' :c.latitude , 'lon' : c.longitude})
                except Country.DoesNotExist:
                    p.country = None
                    p.flag = None
            else:
                p.personaname = 'Anonymous'
                p.country = None
                p.flag = None

        sorted_xp = sorted(timeline_xp,key=itemgetter(0))
        new_xp = []
        
        diff = 0
        for xp in sorted_xp:
            diff += xp[1]
            new_xp.append([xp[0],diff])
        
        new_xp.insert(0,['time','xp'])
        context['players_list'] = players
        context['invalid_account_ids'] = settings.INVALID_ACCOUNT_IDS
        context['gmap_img'] = modules.gmap_img(coordinates)
        context['anon_img'] = settings.PLAYER_ANON_AVATAR
        context['timeline_xp'] = new_xp
        return context
    
class Heroes(generic.ListView):
    template_name = 'stats/heroes.html'
    context_object_name = 'heroes_list'
    
    def get_queryset(self):
        heroes = Hero.objects.all()
        if heroes:
            return heroes
        else:
            heroes = modules.getHeroes()['result']['heroes']
            for h in heroes:
                name = h['name'][14:]
                hero_id = h.pop('id')
                small_horizontal_portrait = settings.STEAM_CDN_HEROES_URL % (name , 'sb.png')
                small_horizontal_portrait_uri = modules.stringifyImage(small_horizontal_portrait)
                large_horizontal_portrait = settings.STEAM_CDN_HEROES_URL % (name , 'lg.png')
                large_horizontal_portrait_uri = modules.stringifyImage(large_horizontal_portrait)
                full_quality_horizontal_portrait = settings.STEAM_CDN_HEROES_URL % (name , 'full.png')
                full_quality_horizontal_portrait_uri = modules.stringifyImage(full_quality_horizontal_portrait)
                full_quality_vertical_portrait = settings.STEAM_CDN_HEROES_URL % (name , 'vert.jpg')
                full_quality_vertical_portrait_uri = modules.stringifyImage(full_quality_vertical_portrait)
                h.update({'hero_id' : hero_id,
                          'small_horizontal_portrait' : small_horizontal_portrait,
                          'small_horizontal_portrait_uri' : small_horizontal_portrait_uri,
                          'large_horizontal_portrait' : large_horizontal_portrait,
                          'large_horizontal_portrait_uri' : large_horizontal_portrait_uri,
                          'full_quality_horizontal_portrait' : full_quality_horizontal_portrait,
                          'full_quality_horizontal_portrait_uri' : full_quality_horizontal_portrait_uri,
                          'full_quality_vertical_portrait' : full_quality_vertical_portrait,
                          'full_quality_vertical_portrait_uri' : full_quality_vertical_portrait_uri,
                          'hero_url' : settings.HERO_URL % (h['localized_name'].replace(' ', '_'))})
                hero = Hero(**h)
                hero.save()
        return heroes

class Countries(generic.ListView):
    template_name = 'stats/countries.html'
    context_object_name = 'countries_list'
    
    def get_queryset(self):
        countries = Country.objects.all()
        if countries:
            return countries
        else:
            countries = modules.getCountries()
            if countries:
                countries = countries['geonames']
            for c in countries:
                c['flag_url'] = settings.FLAG_URL % c['countryCode'].lower()
                try:
                    c['flag_uri'] = modules.stringifyImage(c['flag_url'])
                except:
                    print('error')
                if c['areaInSqKm'] == '':
                    c['areaInSqKm'] = 0.0
                coords = modules.getCountryCoordinates(smart_str(c['countryCode']), smart_str(c['countryName']))['geonames'][0]
                c['latitude'] = coords['lat']
                c['longitude'] = coords['lng']
                country = Country(**c)           
                country.save()
        return countries

class Abilities(generic.ListView):
    template_name = 'stats/abilities.html'
    context_object_name = 'abilities_list'

    def get_queryset(self ):
        abilities = Ability.objects.all()
        if abilities:
            return abilities
        else:
            abilities = abilities_json.JSON['abilities']
            for a in abilities:
                ability_img_url =  abilities_json.IMG_URL % a['name']
                try:
                    ability_img_uri = modules.stringifyImage(ability_img_url)
                except:
                    ability_img_uri = None                    
                ability = {
                        'name' : a['name'],
                        'ability_id' : a['id'],
                        'ability_img_url' : ability_img_url,
                        'ability_img_uri' : ability_img_uri
                        }
                ability = Ability(**ability)
                ability.save()
        return abilities

class Items(generic.ListView):
    template_name = 'stats/items.html'
    context_object_name = 'items_list'

    def get_queryset(self):
        items = Item.objects.all()
        if items:
            return items
        else:
            items = modules.getItems()
            if items['result']:
                items = items['result']['items']
            for i in items:
                item_img_url = settings.ITEM_IMG_URL % i['name'].replace('item_','')
                try:
                    item_img_uri = modules.stringifyImage(item_img_url)
                except:
                    item_img_uri = None
                item = {
                        'item_id' : i['id'],
                        'name' : i['name'],
                        'cost' : i['cost'],
                        'secret_shop' : i['secret_shop'],
                        'side_shop' : i['side_shop'],
                        'recipe' : i['recipe'],
                        'item_img_url' : item_img_url,
                        'item_img_uri' : item_img_uri
                }
                item = Item(**item)
                item.save()
        return items

def getWinratebynummatches(request, account_id):
    num_matches = request.POST['num_matches']
    return HttpResponseRedirect(reverse('player:winrate', args=(account_id, num_matches,)))

class WinrateView(generic.ListView):
    template_name = 'stats/winrate.html'
    context_object_name = 'playerdata'
    
    def get_queryset(self):
        account_id = [self.kwargs['account_id']]
        account_ids = account_id[0].split(',')
        
        num_matches = self.kwargs['num_matches']
        personaname = ''
        for aid in account_ids:
            try:
                pi = PlayerInfo.objects.get(steamid = modules.getSteamID64bit(int(aid)))
                personaname += pi.personaname + ' '
            except PlayerInfo.DoesNotExist:
                personaname += 'Anonymous '
        account_id = account_ids.pop(0)
        if num_matches:
            matchesxplayer = Player.objects.filter(account_id = account_id).order_by('-match_id')[:num_matches]
            matchesxplayer = reversed(matchesxplayer)
        else:
            matchesxplayer = reversed(Player.objects.filter(account_id = account_id).order_by('-match_id'))
        i = 1.0
        v_acum = 0
        wins = 0
        loses = 0
        win_streak = 0
        lose_streak = 0 
        wr_data = []
        for mxp in matchesxplayer:
            try:
                match = Match.objects.filter(Q(match_id = mxp.match_id), Q(game_mode__in = settings.VALID_GAME_MODES), Q(human_players = 10)).get()
                players_from_match = Player.objects.filter(match_id = mxp.match_id)
                leaver = False
                id_counter = 0
                for pfm in players_from_match:
                    if str(pfm.account_id) in account_ids:
                        id_counter += 1
                    if pfm.leaver_status in [2,3]:
                    #if pfm.leaver_status in [9999]:
                        au = AbilityUpgrade.objects.filter(Q(match_id = mxp.match_id), Q(player_slot = pfm.player_slot)).order_by('-time')
                        if au:
                            #if pfm.leaver_status in [2,3]:
                                five_minutes = datetime.time(0, 5, 0)
                                td = datetime.timedelta(seconds=int(match.first_blood_time))
                                tds = [int(x) for x in str(td).split(':')]
                                first_blood = datetime.time(tds[0], tds[1], tds[2])
                                last_au = au[0].time
                                
                                if last_au < five_minutes and last_au < first_blood:
                                    leaver = True
                                    break
                            #else:
                            #    leaver = True
                            #    break
                        else:
                            leaver = True
                            break
                if leaver or id_counter != len(account_ids):
                    continue
            except Match.DoesNotExist:
                continue
                          
            team = int(mxp.player_slot)
            if team < 128 and match.radiant_win or team >= 128 and not match.radiant_win:
                v_acum +=1
                wins += 1
                loses = 0
                if wins > win_streak:
                    win_streak = wins
            else:
                wins = 0
                loses += 1
                if loses > lose_streak:
                    lose_streak = loses
            wr_data.append([str(mxp.match_id), round(((v_acum / i) * 100.0), 2)])
            i += 1.0
        wr_data.insert(0, ['x', 'Winrate (%)'])
        player_data = {'plot_data' : wr_data, 
                       'win_streak' : win_streak,
                       'lose_streak' : lose_streak,
                       'personaname' : personaname,
                       'account_id' : account_id,
                       'total_matches' : int(i-1)} 
        return player_data

def getPlayer(request):
    account_id = request.POST['account_id']
    if account_id:
        player_info = modules.updatePlayerInfo([account_id])[0]
        account_id = modules.getSteamID32bit(int(player_info.steamid))
    return HttpResponseRedirect(reverse('player:matchesxplayer', args=(account_id,)))


@login_required
def done(request):
    uinfo = UserSocialAuth.objects.get(user = RequestContext(request)['user'])
    account_id = modules.getSteamID32bit(uinfo.uid)
    return HttpResponseRedirect(reverse('player:matchesxplayer', args=(account_id,)))

def logout(request):
    auth_logout(request)
    return HttpResponseRedirect('/stats')
 
def test_celery(request):
    result = tasks.sleeptask.delay(10)
    result_one = tasks.sleeptask.delay(10)
    result_two = tasks.sleeptask.delay(15)
    return HttpResponse(result.task_id)