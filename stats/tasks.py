from djcelery import celery
import modules
from views import Player, Match, PlayerInfo
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

@celery.task
def add(x,y):
	return x + y
 
@celery.task
def sleeptask(i):
	from time import sleep
	sleep(i)
	return i

@celery.task
def updatePlayer(account_id):
    #steamid = modules.getSteamID64bit(int(account_id))
    print('Updating player: ' + str(account_id))
    last_match_stored = None
    player = Player.objects.filter(account_id = account_id).order_by('-match_id')
    if player:
        last_match_stored = player[0].match_id
    else:
        last_match_stored = None
    matches = []
    player_history  = modules.getMatchHistory(account_id, 100, None)
    #player_history  = modules.getMatchHistory(account_id, 10, None)
    if player_history and player_history['result']['status'] == 1:
        num_results = player_history['result']['num_results']
        total_results = player_history['result']['total_results']
        matches = player_history['result']['matches']
        
        x = 0
        while x < total_results/num_results:
            last_match_id = matches[len(matches)-1]['match_id']-1
            if not any(m.get('match_id', None) == str(last_match_stored) for m in matches) and last_match_stored is not None:
                break  
            next_matches = modules.getMatchHistory(account_id, num_results, last_match_id)['result']['matches']            
            matches += next_matches
            x += 1
        
    matches = [m for m in matches if m['match_id'] > last_match_stored]
    for ph in matches:
        match_id = ph['match_id']
        try:
            Match.objects.get(match_id = match_id)
        except Match.DoesNotExist:
            modules.saveMatch(match_id)
    return HttpResponseRedirect(reverse('player:matchesxplayer', args=(account_id,)))