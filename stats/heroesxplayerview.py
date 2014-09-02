import datetime
from django.views import generic
from stats.models import Heroes, MatchPlayers, Matches
from django.conf import settings
from django.db.models import Q
from django.shortcuts import render

class HeroesxPlayer(generic.ListView):
    template_name = 'stats/heroesxplayer.html'
    context_object_name = 'hero_list'
    
    def get_queryset(self):
        account_id = self.kwargs['account_id']
        heroes = Heroes.objects.all()
        
        h_list = []
        playermatches = MatchPlayers.objects.filter(account_id = account_id).order_by('-match__match_id').select_related('match')
        for pm in playermatches:
            try:
                match = pm.match
                if match and match.game_mode in settings.VALID_GAME_MODES and match.human_players == 10:
                    hero = None
                    for h in h_list:
                        if h.hero_id == pm.hero_id:
                            hero = h
                            break                    
                    if not hero:
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
                match = matchxplayer.match
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