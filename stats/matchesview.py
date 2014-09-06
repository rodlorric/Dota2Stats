from django.views import generic
from stats.models import Matches, MatchPlayers, Heroes
import datetime
import steam_countries_json
from django.conf import settings
import modules

class MatchDetail(generic.ListView):
    template_name = 'stats/match.html'
    context_object_name = 'match'


    def get_queryset(self):
        import time
        match_id = self.kwargs['match_id']
        match_dict, players_dict, allplayersxp = Matches.objects.get_match(match_id)

        match_dict = match_dict[0]
        #match header
        match = Matches(match_id = match_id)
        match.cluster = match_dict['cluster_description']
        match.lobby_type = match_dict['lobby_type_descripcion']
        match.game_mode = match_dict['game_mode_descripcion']
        match.duration = datetime.timedelta(seconds=match_dict['duration'])
        match.start_time_datetime = match_dict['start_time_DateTime']
        match.radiant_win = match_dict['radiant_win']
        
        #match details
        i = 0
        radiant_totals = MatchPlayers(level = 0, kills = 0, deaths = 0, assists = 0, last_hits = 0, denies = 0, gold_per_min = 0, xp_per_min = 0, hero_damage = 0, hero_healing = 0, tower_damage = 0)
        dire_totals = MatchPlayers(level = 0, kills = 0, deaths = 0, assists = 0, last_hits = 0, denies = 0, gold_per_min = 0, xp_per_min = 0, hero_damage = 0, hero_healing = 0, tower_damage = 0)
        hero_list = []
        players = []
        coordinates = []
        for player in players_dict:
            p = MatchPlayers()
            p.kills = player['kills']
            p.deaths = player['deaths']
            p.assists =player['assists']
            p.last_hits = player['last_hits']
            p.denies = player['denies']
            p.gold_per_min = player['gold_per_min']
            p.xp_per_min = player['xp_per_min']
            p.hero_damage = player['hero_damage']
            p.tower_damage = player['tower_damage']
            p.hero_healing = player['hero_healing']
            p.level = player['level']
            if i < 5:                
                p.radiant = True
                radiant_totals.level += p.level
                radiant_totals.kills += p.kills
                radiant_totals.deaths += p.deaths
                radiant_totals.assists += p.assists
                radiant_totals.last_hits += p.last_hits
                radiant_totals.denies += p.denies
                radiant_totals.gold_per_min += p.gold_per_min
                radiant_totals.xp_per_min += p.xp_per_min
                radiant_totals.hero_damage += p.hero_damage
                radiant_totals.hero_healing += p.hero_healing
                radiant_totals.tower_damage += p.tower_damage
                radiant_totals.radiant = True
                radiant_totals.personaname = 'Radiant Totals'
            else:
                p.radiant = False
                dire_totals.level += p.level
                dire_totals.kills += p.kills
                dire_totals.deaths += p.deaths
                dire_totals.assists += p.assists
                dire_totals.last_hits += p.last_hits
                dire_totals.denies += p.denies
                dire_totals.gold_per_min += p.gold_per_min
                dire_totals.xp_per_min += p.xp_per_min
                dire_totals.hero_damage += p.hero_damage
                dire_totals.hero_healing += p.hero_healing
                dire_totals.tower_damage += p.tower_damage
                dire_totals.radiant = False
                dire_totals.personaname = 'Dire Totals'

            if 'hero_name' in player:                
                h = Heroes(localized_name = player['localized_name'], name = player['hero_name'])                
            else:
                h = Heroes(name = 'Abandoned', localized_name = 'Abandoned' )
            p.hero_localized_name = h.localized_name
            p.hero_name = h.name.replace('npc_dota_hero_','')
            hero_list.append(str(p.hero_localized_name))


            p_ab_list = []            
            p_ab_list.append(player['ability_name1'])            
            p_ab_list.append(player['ability_name2'])            
            p_ab_list.append(player['ability_name3'])            
            p_ab_list.append(player['ability_name4'])            
            p_ab_list.append(player['ability_name5'])            
            p_ab_list.append(player['ability_name6'])            
            p_ab_list.append(player['ability_name7'])            
            p_ab_list.append(player['ability_name8'])            
            p_ab_list.append(player['ability_name9'])            
            p_ab_list.append(player['ability_name10'])            
            p_ab_list.append(player['ability_name11'])            
            p_ab_list.append(player['ability_name12'])            
            p_ab_list.append(player['ability_name13'])            
            p_ab_list.append(player['ability_name14'])            
            p_ab_list.append(player['ability_name15'])            
            p_ab_list.append(player['ability_name16'])            
            p_ab_list.append(player['ability_name17'])            
            p_ab_list.append(player['ability_name18'])            
            p_ab_list.append(player['ability_name19'])            
            p_ab_list.append(player['ability_name20'])            
            p_ab_list.append(player['ability_name21'])            
            p_ab_list.append(player['ability_name22'])            
            p_ab_list.append(player['ability_name23'])            
            p_ab_list.append(player['ability_name24'])            
            p_ab_list.append(player['ability_name25'])
            p.abilities = p_ab_list

            
            p.item_0_name = player['name_item0'].replace('item_','') if player['name_item0'] is not None else None
            p.item_1_name = player['name_item1'].replace('item_','') if player['name_item1'] is not None else None
            p.item_2_name = player['name_item2'].replace('item_','') if player['name_item2'] is not None else None
            p.item_3_name = player['name_item3'].replace('item_','') if player['name_item3'] is not None else None
            p.item_4_name = player['name_item4'].replace('item_','') if player['name_item4'] is not None else None
            p.item_5_name = player['name_item5'].replace('item_','') if player['name_item5'] is not None else None

            if player['personaname'] is not None:
                p.personaname = player['personaname']
                p.avatar = player['avatar']
                if player['loccountrycode'] is not None:
                    country = steam_countries_json.countries.get(player['loccountrycode'])
                    if country:
                        p.country = country['name']
                        p.flag = 'sprite-' + player['loccountrycode'].lower()
                        if player['locstatecode'] is not None:
                            state = country['states'].get(player['locstatecode'])
                            if state:
                                if player['loccityid'] is not None:
                                    city = state['cities'].get(str(player['loccityid']))
                                    if city:
                                        coordinates.append(city['coordinates'])
                                    else:
                                        coordinates.append(state['coordinates'])
                            else:
                                coordinates.append(country['coordinates'])
                else:
                    p.country = None
                    p.flag = None
            else:
                p.personaname = 'Anonymous'
                p.avatar = None
                p.country = None
                p.flag = None

            p.account_id = player['account_id']
            p.player_slot = player['player_slot']
            p.hero_id = player['hero_name']
            players.append(p)
            i += 1

        if players:
            players.append(radiant_totals)
            players.append(dire_totals)
            playerxp = [[],[],[],[],[],[],[],[],[],[]]
            categoriesxp = []
            matchxp = []
            vsxp = [[],[]]

            for time, rad0, rad1, rad2, rad3, rad4, dir128, dir129, dir130, dir131, dir132, xp in allplayersxp:
                vsxp.append([vsxp[0].append(rad0 + rad1 + rad2 + rad3 + rad4), vsxp[1].append(dir128 + dir129 + dir130 + dir131 + dir132)])
                matchxp.append(xp)
                playerxp.append([playerxp[0].append(rad0), playerxp[1].append(rad1), playerxp[2].append(rad2), playerxp[3].append(rad3), playerxp[4].append(rad4), playerxp[5].append(dir128), playerxp[6].append(dir129), playerxp[7].append(dir130), playerxp[8].append(dir131), playerxp[9].append(dir132)])
                categoriesxp.append(str(datetime.timedelta(seconds=time)))

            match.matchxp = matchxp
            match.players_list = players
            match.invalid_account_ids = settings.INVALID_ACCOUNT_IDS
            match.gmap_img = modules.gmap_img(coordinates)
            match.anon_img = settings.PLAYER_ANON_AVATAR
            match.hero_list = hero_list
            match.playerxp = playerxp
            match.categoriesxp = categoriesxp
            match.vsxp = vsxp
        return match