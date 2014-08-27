from django.http import HttpResponseRedirect
from django.core.cache import cache
from django.utils.encoding import smart_str, smart_unicode
from django.core.urlresolvers import reverse
from django.views import generic
#from stats.models import Player, Match, PlayerInfo, Hero, AbilityUpgrade, Country, Ability, Item
from stats.models import Heroes, Countries, Abilities, Items, Matches, AbilityUpgrades, MatchPlayers, Accounts, Matches
from django.conf import settings
from django.db.models import Q
import modules
import datetime
import clusters_json
import lobbies_json
import types_json
import heroes_json
import abilities_json
import urllib
import steam_countries_json
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.contrib.auth import logout as auth_logout
from social_auth.db.django_models import UserSocialAuth
from django.shortcuts import render
import tasks
from operator import itemgetter
import time

class PlayersView(generic.ListView):
    template_name = 'stats/players.html'
    context_object_name = 'players_list'    

    def get_queryset(self):
        pl = MatchPlayers.objects.filter(~Q(account_id__in = settings.INVALID_ACCOUNT_IDS))[:20]
        new_pl = []
        for player in pl:        
            if any(player.account_id ==  s.account_id for s in new_pl):
                continue
            else:
                try:
                    pi = Accounts.objects.get(account_id = player.account_id)
                    player.personaname = pi.personaname
                except Accounts.DoesNotExist:
                    player.personaname = player.account_id
                new_pl.append(player)
        return new_pl

class MatchesxPlayer(generic.ListView):
    template_name = 'stats/matchesxplayer.html'
    context_object_name = 'match_list'
    def get_queryset(self):
        account_id = self.kwargs['account_id']
        heroes = Heroes.objects.all()
        #modules.updatePlayerInfo([account_id])
        #task = tasks.updatePlayer.delay(account_id)
        playermatches = MatchPlayers.objects.filter(account_id = account_id).order_by('-match__match_id').select_related('match')
        matches = []
        for matchxplayer in playermatches:
            try:
                #match = Matches.objects.get(Q(match_id = matchxplayer.match_id), Q(game_mode__in = settings.VALID_GAME_MODES), Q(human_players = 10))
                match = matchxplayer.match
                if not match.game_mode in settings.VALID_GAME_MODES and match.human_players != 10:
                    continue
                #hero = next((h for h in heroes.JSON['heroes'] if h['id'] == matchxplayer.hero_id), None)
                try:
                    #hero = heroes.get(hero_id = matchxplayer.hero_id)
                    hero = [h for h in heroes if h.hero_id == matchxplayer.hero_id][0]
                    match.hero = hero.localized_name
                    #match.hero_img = heroes.IMG_URL % hero['name']
                    match.hero_img = 'sprite-' + hero.name[14:] + '_sb'
                except Heroes.DoesNotExist:
                    hero = None
                
                match.duration = datetime.timedelta(seconds=match.duration)
                match.kills = matchxplayer.kills
                match.deaths = matchxplayer.deaths
                match.assists = matchxplayer.assists
                team = matchxplayer.player_slot      
                if match.radiant_win and team < 128 or not match.radiant_win and team >= 128:
                    match.result = 'Won Match'
                else:
                    match.result = 'Lost Match'
                matches.append(match)
            except Matches.DoesNotExist:
                continue     
        return matches
    
    def get_context_data(self, **kwargs):
        context = super(MatchesxPlayer, self).get_context_data(**kwargs)
        account_id = self.kwargs['account_id']
        context['account_id'] = account_id
        try:            
            pi = Accounts.objects.get(account_id = account_id)
            personaname = pi.personaname
        except Accounts.DoesNotExist:
            personaname = 'Anonymous'
        context['personaname'] = personaname
        return context
    
class HeroesxPlayer(generic.ListView):
    template_name = 'stats/heroesxplayer.html'
    context_object_name = 'hero_list'
    
    def get_queryset(self):
        account_id = self.kwargs['account_id']
        heroes = Heroes.objects.all()
        #modules.updatePlayer(account_id)
        #task = tasks.updatePlayer.delay(account_id)        
        
        h_list = []
        #hero_var = heroes.JSON['heroes']
        playermatches = MatchPlayers.objects.filter(account_id = account_id).order_by('-match__match_id').select_related('match')
        for pm in playermatches:
            try:
                #match = Matches.objects.filter(Q(match_id = pm.match_id), Q(game_mode__in = settings.VALID_GAME_MODES), Q(human_players = 10)).get()
                match = pm.match
                if match and match.game_mode in settings.VALID_GAME_MODES and match.human_players == 10:
                    hero = None
                    for h in h_list:
                        if h.hero_id == pm.hero_id:
                            hero = h
                            break                    
                    if not hero:
                        #hero = next((h for h in hero_var if h['id'] == pm.hero_id), None)
                        hero = [h for h in heroes if h.hero_id == pm.hero_id][0]
                        hero.matches = 0
                        hero.wins = 0
                        hero.loses = 0
                        hero.winrate = 0.0
                        hero.name = 'sprite-' + hero.name[14:] + '_sb'
                        h_list.append(hero)
                    
                    hero.matches += 1
                    team = int(pm.player_slot)
                    if team < 128 and match.radiant_win or team >= 128 and not match.radiant_win:
                        hero.wins += 1
                    else:
                        hero.loses += 1
                    hero.winrate = round(((hero.wins * 1.0 / hero.matches * 1.0) * 100.0), 2)
                    hero.account_id = account_id
            except Matches.DoesNotExist:
                continue   
        return sorted(h_list, key=lambda k: k.matches, reverse = True)
    
def HeroDetail(request, account_id, hero_id):
    heroes = Heroes.objects.all()
    if account_id and hero_id:
        matchesxplayer = MatchPlayers.objects.filter(Q(account_id = account_id), Q(hero_id = hero_id)).order_by('-match__match_id').select_related('match')
        matches = []
        for matchxplayer in matchesxplayer:
            try:
                #match = Matches.objects.get(Q(match_id = matchxplayer.match_id), Q(human_players = 10))
                match = matchxplayer.match
                #hero = next((h for h in heroes.JSON['heroes'] if h['id'] == matchxplayer.hero_id), None)
                #hero = heroes.get(hero_id = matchxplayer.hero_id)
                hero = [h for h in heroes if h.hero_id == matchxplayer.hero_id][0]
                match.hero = hero.localized_name
                match.hero_img = 'sprite-' + hero.name[14:] + '_sb'
                match.kills = matchxplayer.kills
                match.deaths = matchxplayer.deaths
                match.assists = matchxplayer.assists
                match.duration = datetime.timedelta(seconds=match.duration)
                team = matchxplayer.player_slot      
                if match.radiant_win and team < 128 or not match.radiant_win and team >= 128:
                    match.result = 'Won Match'
                else:
                    match.result = 'Lost Match'
                matches.append(match)
            except Matches.DoesNotExist:
                continue
        context = {'match_list' : matches, 'account_id' : int(account_id)}
    return render(request, 'stats/matchesxplayer.html', context )
        
    
class MatchDetail(generic.ListView):
    template_name = 'stats/match.html'
    context_object_name = 'match' 
    
    def get_queryset(self):
        match_id = self.kwargs['match_id']
        try:
            match = Matches.objects.get(match_id = match_id)
        except Matches.DoesNotExist:
            #match = modules.saveMatch(self.kwargs['match_id'])
            print('Do not save match yet!')
        
        cluster_list = clusters_json.JSON['regions']
        lobby_list = lobbies_json.JSON['lobbies']
        type_list = types_json.JSON['mods']
        match.cluster = next((c['name'] for c in cluster_list if c['id'] == match.cluster), None)
        match.lobby_type = next((l['name'] for l in lobby_list if l['id'] == match.lobby_type), None)
        match.game_mode = next((l['name'] for l in type_list if l['id'] == match.game_mode), None)
        new_xp = [['time','xp']]
        xp = Matches.objects.getXPByMatch(match_id)
        for (time,x) in xp:
            new_xp.append([str(datetime.timedelta(seconds=time)), x])
        match.xp = new_xp

        return match

    def get_context_data(self, **kwargs):
        match_id = self.kwargs['match_id']
        context = super(MatchDetail, self).get_context_data(**kwargs)
        players = MatchPlayers.objects.filter(match_id = match_id).order_by('player_slot')
        player_abilities = list(AbilityUpgrades.objects.filter(match_id = match_id))

        ab_set = [ab.ability for ab in player_abilities]
        abilities = list(Abilities.objects.filter(ability_id__in = ab_set))

        hero_set = []
        item_set = []
        acc_ids = []
        for p in players:
            hero_set.append(p.hero_id)
            item_set.append(p.item_0)
            item_set.append(p.item_1)
            item_set.append(p.item_2)
            item_set.append(p.item_3)
            item_set.append(p.item_4)
            item_set.append(p.item_5)
            acc_ids.append(p.account_id)

        heroes = Heroes.objects.filter(hero_id__in = hero_set)
        items = Items.objects.filter(item_id__in = item_set)
        countries = Countries.objects.all()

        coordinates = []
        i = 0
        player_info_list = modules.updatePlayerInfo(acc_ids)

        hero_list = []
        for p in players:

            if i < 5:
                p.radiant = True
            else:
                p.radiant = False

            h = [h for h in heroes if h.hero_id == p.hero_id]
            if h:
                h = h[0]            
                p.hero_id = h.hero_id
                p.hero_img = h.small_horizontal_portrait
                p.hero_localized_name = h.localized_name
                p.hero_name = 'sprite-' + h.name.replace('npc_dota_hero_','') + '_sb'
                hero_list.append(str(h.localized_name))

            else:
                h = Hero(name = 'Abandoned', localized_name = 'Abandoned' )

            p_ab_list = []
            for pa in player_abilities:
                if pa.player_slot_id == p.player_slot:
                    ability = next((a for a in abilities if a.ability_id == pa.ability), None)
                    pa.name = 'sprite-' + ability.name + '_hp1'
                    p_ab_list.append(pa)
            p.abilities = p_ab_list
            i += 1
            
            item = [item for item in items if item.item_id == p.item_0]
            if item:
                p.item_0_name = 'sprite-' + item[0].name.replace('item_','') + '_lg'
            else:
                p.item_0_name = None

            item = [item for item in items if item.item_id == p.item_1]
            if item:
                p.item_1_name = 'sprite-' + item[0].name.replace('item_','') + '_lg'
            else:
                p.item_1_name = None

            item = [item for item in items if item.item_id == p.item_2]
            if item:
                p.item_2_name = 'sprite-' + item[0].name.replace('item_','') + '_lg'
            else:
                p.item_2_name = None

            item = [item for item in items if item.item_id == p.item_3]
            if item:
                p.item_3_name = 'sprite-' + item[0].name.replace('item_','') + '_lg'
            else:
                p.item_3_name = None

            item = [item for item in items if item.item_id == p.item_4]
            if item:
                p.item_4_name = 'sprite-' + item[0].name.replace('item_','') + '_lg'
            else:
                p.item_4_name = None

            item = [item for item in items if item.item_id == p.item_5]
            if item:
                p.item_5_name = 'sprite-' + item[0].name.replace('item_','') + '_lg'
            else:
                p.item_5_name = None


            pi = [pi for pi in player_info_list if str(pi.account_id) == str(p.account_id)]
            if pi:
                pi = pi[0]
                p.personaname = pi.personaname
                p.avatar = pi.avatar
                c = [c for c in countries if c.countryCode == pi.loccountrycode]
                if c:
                #try:
                    #c = Countries.objects.get(countryCode = pi.loccountrycode)
                    c = c[0]
                    p.country = c.countryName
                    p.flag = 'sprite-' + c.countryCode.lower()

                    country = steam_countries_json.countries.get(pi.loccountrycode)
                    if country:
                        state = country['states'].get(pi.locstatecode)
                        if state:
                            city = state['cities'].get(str(pi.loccityid))
                            if city:
                                coordinates.append(city['coordinates'])
                            else:
                                coordinates.append(state['coordinates'])
                        else:
                            coordinates.append(country['coordinates'])
                #except Countries.DoesNotExist:
                else:
                    p.country = None
                    p.flag = None
            else:
                p.personaname = 'Anonymous'
                p.country = None
                p.flag = None

        #hero_list.append('Total XP Diff')
        allplayersxp = MatchPlayers.objects.getAllPlayersXPByMatch(match_id)

        radxp = hero_list[:5]
        direxp = hero_list[5:]
        radxp.insert(0, 'Time')
        direxp.insert(0, 'Time')
        radxp = [radxp]
        direxp = [direxp]
        matchxp = [['Time','XP Diff']]

        print(radxp)
        print(direxp)
        for (time, rad0, rad1, rad2, rad3, rad4, dir128, dir129, dir130, dir131, dir132, xp) in allplayersxp:
            matchxp.append([str(datetime.timedelta(seconds=time)), xp])
            radxp.append([str(datetime.timedelta(seconds=time)), rad0, rad1, rad2, rad3, rad4])
            direxp.append([str(datetime.timedelta(seconds=time)), dir128, dir129, dir130, dir131, dir132])
        context['matchxp'] = matchxp
        context['radxp'] = radxp
        context['direxp'] = direxp

        context['players_list'] = players
        context['invalid_account_ids'] = settings.INVALID_ACCOUNT_IDS
        context['gmap_img'] = modules.gmap_img(coordinates)
        context['anon_img'] = settings.PLAYER_ANON_AVATAR
        return context
    
class HeroesList(generic.ListView):
    template_name = 'stats/heroes.html'
    context_object_name = 'heroes_list'
    
    def get_queryset(self):
        start = time.time()
        heroes = Heroes.objects.all()
        if not heroes:
            heroes = modules.getHeroes()['result']['heroes']
            for h in heroes:
                name = h['name'][14:]
                hero_id = h.pop('id')
                small_horizontal_portrait = settings.STEAM_CDN_HEROES_URL % (name , 'sb.png')
                large_horizontal_portrait = settings.STEAM_CDN_HEROES_URL % (name , 'lg.png')
                full_quality_horizontal_portrait = settings.STEAM_CDN_HEROES_URL % (name , 'full.png')
                full_quality_vertical_portrait = settings.STEAM_CDN_HEROES_URL % (name , 'vert.jpg')
                h.update({'hero_id' : hero_id,
                    'small_horizontal_portrait' : small_horizontal_portrait,
                    'large_horizontal_portrait' : large_horizontal_portrait,
                    'full_quality_horizontal_portrait' : full_quality_horizontal_portrait,
                    'full_quality_vertical_portrait' : full_quality_vertical_portrait,
                    'hero_url' : settings.HERO_URL % (h['localized_name'].replace(' ', '_'))})
                hero = Heroes(**h)
                hero.save()
        else:
            #Parranda agrego un Heroe NA en la tabla hero_id = 0.
            heroes = heroes[1:]
        for h in heroes:
            h.name = 'sprite-' + h.name[14:] + '_sb'

        end = time.time()
        total_time = end - start
        print('total time: %s') %str(total_time)
        return heroes

class CountriesList(generic.ListView):
    template_name = 'stats/countries.html'
    context_object_name = 'countries_list'
    
    def get_queryset(self):
        countries = Countries.objects.all()
        if countries:
            for c in countries:                
                c.countryCode_sprite = 'sprite-' + c.countryCode.lower()
            return countries
        else:
            countries = modules.getCountries()
            if countries:
                countries = countries['geonames']
            for c in countries:
                c['flag_url'] = settings.FLAG_URL % c['countryCode'].lower()
                if c['areaInSqKm'] == '':
                    c['areaInSqKm'] = 0.0
                coords = modules.getCountryCoordinates(smart_str(c['countryCode']), smart_str(c['countryName']))['geonames'][0]
                c['latitude'] = coords['lat']
                c['longitude'] = coords['lng']
                country = Countries(**c)           
                country.save()
        return countries

class AbilitiesList(generic.ListView):
    template_name = 'stats/abilities.html'
    context_object_name = 'abilities_list'

    def get_queryset(self ):
        abilities = Abilities.objects.all()
        if abilities:
            for a in abilities:
                a.sprite_name = 'sprite-' + a.name + '_hp1'
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
                        'ability_img_url' : ability_img_url
                        }
                ability = Abilities(**ability)
                ability.save()
        return abilities

class ItemsList(generic.ListView):
    template_name = 'stats/items.html'
    context_object_name = 'items_list'

    def get_queryset(self):
        items = Items.objects.all()
        if items:
            for i in items:
                i.sprite_name = 'sprite-' + i.name[5:] + '_lg'
                i.name = i.name[5:]
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
                        'item_img_url' : item_img_url
                }
                item = Items(**item)
                item.save()
        return items

def getWinratebynummatches(request, account_id):
    num_matches = request.POST['num_matches']
    return HttpResponseRedirect(reverse('player:winrate', args=(account_id, num_matches,)))

class WinrateView(generic.ListView):
    template_name = 'stats/winrate.html'
    context_object_name = 'playerdata'
    
    def get_queryset(self):
        account_id = self.kwargs['account_id']
        account_ids = account_id.split(',')

        ids = [None, None, None, None, None]
        error = ''
        print('len ' + str(len(account_ids)))
        if len(account_ids) > 5:
            account_ids = account_ids[:4]
        
        num_matches = self.kwargs['num_matches']
        personaname = ''
        i = 0
        for aid in account_ids:
            ids[i] = aid
            try:
                pi = Accounts.objects.get(account_id = aid)
                personaname += pi.personaname + ' '
            except Accounts.DoesNotExist:
                personaname += 'Anonymous '
            i += 1

        wr_data = [['x', 'Winrate (%)']]
        winrate = list(MatchPlayers.objects.getWinrate(ids[0], num_matches, ids[1], ids[2], ids[3], ids[4]))

        if len(winrate) > 0:
            for (match_id, win_rate, wins, loses, total_matches) in winrate:
                wr_data.append([str(match_id), float(win_rate)])
            (m, w, ww, l, total_matches) = winrate[len(winrate)-1]
        else:
            total_matches = 0
            wr_data.append([0 , 0])
            error = 'There are no matches with those players...'

        player_data = {'plot_data' : wr_data,
                        'win_streak' : '0',
                        'lose_streak' : '0',
                        'personaname' : personaname,
                        'account_id' : ids[0],
                        'total_matches' : total_matches,
                        'error' : error}
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