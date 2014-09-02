from django.views import generic
from stats.models import Heroes, MatchPlayers, Matches, Accounts
from django.conf import settings
import datetime

class MatchesxPlayer(generic.ListView):
    template_name = 'stats/matchesxplayer.html'
    context_object_name = 'match_list'
    def get_queryset(self):
        account_id = self.kwargs['account_id']
        heroes = Heroes.objects.all()
        playermatches = MatchPlayers.objects.filter(account_id = account_id).order_by('-match__match_id').select_related('match')
        matches = []
        for matchxplayer in playermatches:
            try:
                match = matchxplayer.match
                if not match.game_mode in settings.VALID_GAME_MODES and match.human_players != 10:
                    continue
                try:
                    hero = [h for h in heroes if h.hero_id == matchxplayer.hero_id][0]
                    match.hero = hero.localized_name
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