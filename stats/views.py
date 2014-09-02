from django.http import HttpResponseRedirect
from django.core.cache import cache
from django.utils.encoding import smart_str, smart_unicode
from django.core.urlresolvers import reverse
from django.views import generic
#from stats.models import Player, Match, PlayerInfo, Hero, AbilityUpgrade, Country, Ability, Item
from stats.models import Heroes, Countries, Abilities, Items, Matches, AbilityUpgrades, MatchPlayers, Accounts
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
        #modules.update_player_info([account_id])
        #task = tasks.update_player.delay(account_id)
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
        #modules.update_player(account_id)
        #task = tasks.update_player.delay(account_id)        
        
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
    
def hero_detail(request, account_id, hero_id):
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
                match.duration = datetime.timedelta(seconds=match.duration if match.duration is not None else 0)
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
    
class HeroesList(generic.ListView):
    template_name = 'stats/heroes.html'
    context_object_name = 'heroes_list'
    
    def get_queryset(self):
        heroes = Heroes.objects.all()
        if not heroes:
            heroes = modules.get_heroes()['result']['heroes']
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
            countries = modules.get_countries()
            if countries:
                countries = countries['geonames']
            for c in countries:
                c['flag_url'] = settings.FLAG_URL % c['countryCode'].lower()
                if c['areaInSqKm'] == '':
                    c['areaInSqKm'] = 0.0
                coords = modules.get_country_coordinates(smart_str(c['countryCode']), smart_str(c['countryName']))['geonames'][0]
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
                    ability_img_uri = modules.stringify_image(ability_img_url)
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
            items = modules.get_items()
            if items['result']:
                items = items['result']['items']
            for i in items:
                item_img_url = settings.ITEM_IMG_URL % i['name'].replace('item_','')
                try:
                    item_img_uri = modules.stringify_image(item_img_url)
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

def get_player(request):
    account_id = request.POST['account_id']
    if account_id:
        player_info = modules.update_player_info([account_id])[0]
        account_id = player_info.account_id
    return HttpResponseRedirect(reverse('player:matchesxplayer', args=(account_id,)))


@login_required
def done(request):
    uinfo = UserSocialAuth.objects.get(user = RequestContext(request)['user'])
    account_id = modules.get_steamid_32bit(uinfo.uid)
    return HttpResponseRedirect(reverse('player:matchesxplayer', args=(account_id,)))

def logout(request):
    auth_logout(request)
    return HttpResponseRedirect('/stats')
 
def test_celery(request):
    result = tasks.sleeptask.delay(10)
    result_one = tasks.sleeptask.delay(10)
    result_two = tasks.sleeptask.delay(15)
    return HttpResponse(result.task_id)