# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
from __future__ import unicode_literals

from django.db import models
from django.db import connection


class Accounts(models.Model):
    account_id = models.BigIntegerField(primary_key=True)
    communityvisibilitystate = models.SmallIntegerField(blank=True, null=True)
    profilestate = models.SmallIntegerField(blank=True, null=True)
    personaname = models.CharField(max_length=100, blank=True)
    lastlogoff = models.BigIntegerField(blank=True, null=True)
    commentpermission = models.SmallIntegerField(blank=True, null=True)
    profileurl = models.CharField(max_length=2000, blank=True)
    avatar = models.CharField(max_length=2000, blank=True)
    avatarmedium = models.CharField(max_length=2000, blank=True)
    avatarfull = models.CharField(max_length=2000, blank=True)
    personastate = models.SmallIntegerField(blank=True, null=True)
    realname = models.CharField(max_length=100, blank=True)
    primaryclanid = models.BigIntegerField(blank=True, null=True)
    timecreated = models.BigIntegerField(blank=True, null=True)
    personastateflags = models.SmallIntegerField(blank=True, null=True)
    gameserverip = models.CharField(max_length=15, blank=True)
    gameserversteamid = models.BigIntegerField(blank=True, null=True)
    gameextrainfo = models.CharField(max_length=100, blank=True)
    gameid = models.IntegerField(blank=True, null=True)
    lobbysteamid = models.BigIntegerField(blank=True, null=True)
    loccountrycode = models.CharField(max_length=100, blank=True)
    locstatecode = models.CharField(max_length=20, blank=True)
    loccityid = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = True
        db_table = 'Accounts'

class Heroes(models.Model):
    name = models.CharField(max_length = 200)
    hero_id = models.SmallIntegerField(primary_key=True)
    localized_name = models.CharField(max_length = 200)
    small_horizontal_portrait = models.URLField()
    large_horizontal_portrait = models.URLField()
    full_quality_horizontal_portrait = models.URLField()
    full_quality_vertical_portrait = models.URLField()
    hero_url = models.URLField()
    class Meta:
        managed = False
        db_table = 'Heroes'

    def __unicode__(self):
        return self.name

class Incidencias(models.Model):
    incidenciaid = models.AutoField(db_column='incidenciaId', primary_key=True) # Field name made lowercase.
    fechaincidencia = models.DateTimeField(db_column='fechaIncidencia') # Field name made lowercase.
    descripcion = models.CharField(max_length=8000)
    class Meta:
        managed = False
        db_table = 'Incidencias'

class MatchesManager(models.Manager):
    def get_all_players_xp_by_match(self, match_id):
        cursor = connection.cursor()
        result_set = None
        try:
            cursor.callproc("GetDifferenceExperienceByMatchAllPlayers", [match_id])
            result_set = cursor.fetchall()
        finally:
            cursor.close()
        return result_set

    def get_xp_by_match(self, match_id):
        cursor = connection.cursor()
        result_set = None
        try:
            cursor.callproc("GetDifferenceExperienceByMatch", [match_id])
            result_set = cursor.fetchall()
        finally:
            cursor.close()
        return result_set

    def get_match(self, match_id):
        cursor = connection.cursor()
        result_set = None
        try:
            cursor.callproc("GetMatch", [match_id])
            match_dict = result_set_to_dict(cursor)
            if cursor.nextset():
                players_dict = result_set_to_dict(cursor)
            if cursor.nextset():
                match_experience = cursor.fetchall()
        finally:
            cursor.close()
        return match_dict, players_dict, match_experience

class Matches(models.Model):
    radiant_win = models.NullBooleanField()
    duration = models.IntegerField(blank=True, null=True)
    start_time = models.BigIntegerField()
    start_time_datetime = models.DateTimeField(db_column='start_time_DateTime', blank=True, null=True) # Field name made lowercase.
    match_id = models.BigIntegerField(primary_key=True)
    match_seq_num = models.BigIntegerField()
    tower_status_radiant = models.IntegerField(blank=True, null=True)
    tower_status_dire = models.IntegerField(blank=True, null=True)
    barracks_status_radiant = models.IntegerField(blank=True, null=True)
    barracks_status_dire = models.IntegerField(blank=True, null=True)
    cluster = models.IntegerField(blank=True, null=True)
    first_blood_time = models.IntegerField(blank=True, null=True)
    lobby_type = models.IntegerField()
    human_players = models.SmallIntegerField(blank=True, null=True)
    leagueid = models.IntegerField(blank=True, null=True)
    positive_votes = models.IntegerField(blank=True, null=True)
    negative_votes = models.IntegerField(blank=True, null=True)
    game_mode = models.IntegerField(blank=True, null=True)
    radiant_captain = models.BigIntegerField(blank=True, null=True)
    dire_captain = models.BigIntegerField(blank=True, null=True)
    dire_team_id = models.IntegerField(blank=True, null=True)
    dire_name = models.CharField(max_length=100, blank=True)
    dire_logo = models.BigIntegerField(blank=True, null=True)
    dire_team_complete = models.NullBooleanField()
    radiant_team_id = models.IntegerField(blank=True, null=True)
    radiant_name = models.CharField(max_length=100, blank=True)
    radiant_logo = models.BigIntegerField(blank=True, null=True)
    radiant_team_complete = models.NullBooleanField()
    dire_guild_id = models.IntegerField(blank=True, null=True)
    dire_guild_name = models.CharField(max_length=100, blank=True)
    dire_guild_logo = models.BigIntegerField(blank=True, null=True)
    radiant_guild_id = models.IntegerField(blank=True, null=True)
    radiant_guild_name = models.CharField(max_length=100, blank=True)
    radiant_guild_logo = models.BigIntegerField(blank=True, null=True)
    objects = MatchesManager()
    class Meta:
        managed = False
        db_table = 'Matches'

    

class MatchPlayersManager(models.Manager):
    def get_winrate(self, account_id, num_matches, account_friend_id1, account_friend_id2, account_friend_id3, account_friend_id4):        
        result_set = None
        cursor = connection.cursor()
        try:
            sp_params = [account_id, num_matches, account_friend_id1, account_friend_id2, account_friend_id3, account_friend_id4]
            cursor.callproc("GetWinRate", sp_params)
            winrates = cursor.fetchall()
            if cursor.nextset():
                streaks = cursor.fetchone()
        finally:
            cursor.close()
        return winrates, streaks

class MatchPlayers(models.Model):
    match = models.ForeignKey('Matches', primary_key=True)
    account = models.ForeignKey(Accounts, blank=True, null=True)
    player_slot = models.SmallIntegerField()
    hero_id = models.SmallIntegerField(blank=True, null=True)
    item_0 = models.SmallIntegerField(blank=True, null=True)
    item_1 = models.SmallIntegerField(blank=True, null=True)
    item_2 = models.SmallIntegerField(blank=True, null=True)
    item_3 = models.SmallIntegerField(blank=True, null=True)
    item_4 = models.SmallIntegerField(blank=True, null=True)
    item_5 = models.SmallIntegerField(blank=True, null=True)
    kills = models.IntegerField(blank=True, null=True)
    deaths = models.IntegerField(blank=True, null=True)
    assists = models.IntegerField(blank=True, null=True)
    leaver_status = models.IntegerField(blank=True, null=True)
    gold = models.IntegerField(blank=True, null=True)
    last_hits = models.IntegerField(blank=True, null=True)
    denies = models.IntegerField(blank=True, null=True)
    gold_per_min = models.IntegerField(blank=True, null=True)
    xp_per_min = models.IntegerField(blank=True, null=True)
    gold_spent = models.IntegerField(blank=True, null=True)
    hero_damage = models.IntegerField(blank=True, null=True)
    tower_damage = models.DecimalField(max_digits=18, decimal_places=0, blank=True, null=True)
    hero_healing = models.DecimalField(max_digits=18, decimal_places=0, blank=True, null=True)
    level = models.IntegerField(blank=True, null=True)    
    objects = MatchPlayersManager()

    class Meta:
        managed = False
        db_table = 'Match_Players'




class AdditionalUnits(models.Model):
    match = models.ForeignKey('MatchPlayers')
    player_slot = models.ForeignKey('MatchPlayers', db_column='player_slot', related_name='units_player_slot')
    unitname = models.CharField(max_length=50)
    item_0 = models.SmallIntegerField()
    item_1 = models.SmallIntegerField()
    item_2 = models.SmallIntegerField()
    item_3 = models.SmallIntegerField()
    item_4 = models.SmallIntegerField()
    item_5 = models.SmallIntegerField()
    class Meta:
        managed = False
        db_table = 'Additional_Units'

class AbilityUpgrades(models.Model):
    match = models.ForeignKey('MatchPlayers', primary_key=True)
    player_slot = models.ForeignKey('MatchPlayers', db_column='player_slot', related_name='ability_player_slot')
    ability = models.IntegerField()
    time = models.IntegerField()
    level = models.IntegerField()
    experience = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'Ability_Upgrades'

class PicksBans(models.Model):
    match = models.ForeignKey(Matches)
    is_pick = models.BooleanField()
    hero_id = models.SmallIntegerField()
    team = models.BooleanField()
    order = models.SmallIntegerField()
    class Meta:
        managed = False
        db_table = 'Picks_Bans'

class Countries(models.Model):
    countryCode = models.CharField(max_length = 2, blank = True, null = True)
    countryName = models.CharField(max_length = 100, blank = True, null = True)
    flag_url = models.URLField(blank = True, null = True)
    isoNumeric = models.CharField(max_length = 3, blank = True, null = True)
    isoAlpha3 = models.CharField(max_length = 3, blank = True, null = True)
    fipsCode = models.CharField(max_length = 2, blank = True, null = True)
    continent = models.CharField(max_length = 2, blank = True, null = True)
    continentName = models.CharField(max_length = 25, blank = True, null = True)
    capital = models.CharField(max_length = 100, blank = True, null = True)
    areaInSqKm = models.FloatField(blank = True, null = True)
    population = models.BigIntegerField(blank = True, null = True)
    currencyCode = models.CharField(max_length = 3, blank = True, null = True)
    languages = models.CharField(max_length = 200, blank = True, null = True)
    geonameId = models.IntegerField(blank = True, null = True)
    west = models.FloatField(blank = True, null = True)
    north = models.FloatField(blank = True, null = True)
    east = models.FloatField(blank = True, null = True)
    south = models.FloatField(blank = True, null = True)
    latitude = models.FloatField(blank = True, null = True)
    longitude = models.FloatField(blank = True, null = True)
    class Meta:
        managed = True
        db_table = 'Countries'

    def __unicode__(self):
        return self.countryName + ' - ' + self.countryCode

class Items(models.Model):
    item_id = models.SmallIntegerField()
    name = models.CharField(max_length=100)
    cost = models.SmallIntegerField(blank = True, null = True)
    secret_shop = models.SmallIntegerField(blank = True, null = True)
    side_shop = models.SmallIntegerField(blank = True, null = True)
    recipe = models.SmallIntegerField(blank = True, null = True)
    item_img_url = models.URLField(blank = True, null = True)
    class Meta:
        managed = True
        db_table = 'Items'

    def __unicode__(self):
        return self.countryName + ' - ' + self.countryCode

class Abilities(models.Model):
    name = models.CharField(max_length = 200)
    ability_id = models.IntegerField()
    ability_img_url = models.URLField()
    class Meta:
        managed = True
        db_table = 'Abilities'

    def __unicode__(self):
        return self.name

#credit to http://geert.vanderkelen.org/fetching-rows-as-dictionaries-with-mysql-connectorpython/
def result_set_to_dict(cursor):
    result = []
    description = cursor.description
    rows = cursor.fetchall()
    columns = tuple( [d[0].decode('utf8') for d in description] )
    for row in rows:
        result.append(dict(zip(columns, row)))
    return result
