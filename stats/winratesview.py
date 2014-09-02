from django.views import generic
from stats.models import MatchPlayers
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

def get_winrate_by_nummatches(request, account_id):
    num_matches = request.POST['num_matches']
    return HttpResponseRedirect(reverse('player:winrate', args=(account_id, num_matches,)))

class WinrateView(generic.ListView):
    template_name = 'stats/winrate.html'
    context_object_name = 'playerdata'
    
    def get_queryset(self):
        account_id = self.kwargs['account_id']
        account_ids = account_id.split(',')[:5]

        ids = [None, None, None, None, None]
        error = ''
        
        num_matches = self.kwargs['num_matches']

        #this is a slower implemation :( 
        #ids = [account_ids[i] if i < len(account_ids) else None for i,x in enumerate(ids)]
        i = 0
        for aid in account_ids:
            ids[i] = aid
            i += 1

        winrate, streaks = MatchPlayers.objects.get_winrate(ids[0], num_matches, ids[1], ids[2], ids[3], ids[4])
        winrate = list(winrate)
        streaks = list(streaks)
        w_streak = streaks.pop(0)
        l_streak = streaks.pop(0)
        total_matches = 0
        wr_data =[[],[]]

        #winrate[] = [0 match_id, 1 win_rate, 2 wins, 3 loses, 4 total_matches]
        if len(winrate) > 0:
            #wr_data = wr_data[0].append(str(values[0])), wr_data[1].append(float(values[1])) for values in winrate]
            for v in winrate:
                wr_data.append([wr_data[0].append(str(v[0])), wr_data[1].append(float(v[1]))])
            #wr_data.insert(0,['Matches', 'Winrate (%)'])
            total_matches = winrate[len(winrate)-1][4]
        else:
            total_matches = 0
            wr_data.append([[0] , [0]])
            error = 'There are no matches with those players...'

        player_data = {'plot_data' : wr_data,
                        'win_streak' : w_streak,
                        'lose_streak' : l_streak,
                        'players' : streaks,
                        'player_profile' : streaks[0],
                        'account_id' : ids[0],
                        'total_matches' : total_matches,
                        'error' : error}
        return player_data