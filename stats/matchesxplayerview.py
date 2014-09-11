from django.views import generic
from stats.models import Heroes, MatchPlayers, Matches, Accounts
from django.conf import settings
import datetime

class MatchesxPlayer(generic.ListView):
    template_name = 'stats/matchesxplayer.html'
    context_object_name = 'match_list'
    
    def get_queryset(self):
        matches_list = []
        persona = 'Anonymous'
        matches = Matches.objects.get_matches_by_player(self.kwargs['account_id'])
        for match_id, localized_name, is_radiant, win, duration, kills, deaths, assists, Name, personaname, start_time_DateTime in matches:
            match = Matches(match_id = match_id, radiant_win = win)
            match.kills = kills
            match.deaths = deaths
            match.assists = assists
            match.hero_img = 'sprite-' + Name[14:] + '_sb'
            match.side = 'Radiant' if is_radiant == 1 else 'Dire'
            match.duration = datetime.timedelta(seconds=duration) if duration is not None else '00:00:00'
            persona = personaname
            match.personaname = persona
            match.result = 'Won Match' if win == 1 else 'Lost Match'
            match.start_time_DateTime = start_time_DateTime
            matches_list.append(match)
        matches_list[0].personaname = persona
        matches_list[0].account_id = self.kwargs['account_id']
        return matches_list