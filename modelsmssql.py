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

class AbilityUpgrades(models.Model):
    match = models.ForeignKey('MatchPlayers')
    player_slot = models.ForeignKey('MatchPlayers', db_column='player_slot')
    ability = models.IntegerField()
    time = models.IntegerField()
    level = models.IntegerField()
    experiencia = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'Ability_Upgrades'

class Accounts(models.Model):
    account_id = models.BigIntegerField(primary_key=True)
    fechamodificacion = models.DateTimeField(db_column='FechaModificacion') # Field name made lowercase.
    steamid = models.CharField(db_column='steamId', max_length=36, blank=True) # Field name made lowercase.
    class Meta:
        managed = False
        db_table = 'Accounts'

class AdditionalUnits(models.Model):
    match = models.ForeignKey('MatchPlayers')
    player_slot = models.ForeignKey('MatchPlayers', db_column='player_slot')
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

class Incidencias(models.Model):
    incidenciaid = models.AutoField(db_column='incidenciaId') # Field name made lowercase.
    fechaincidencia = models.DateTimeField(db_column='fechaIncidencia') # Field name made lowercase.
    descripcion = models.CharField(max_length=8000)
    class Meta:
        managed = False
        db_table = 'Incidencias'

class MatchPlayers(models.Model):
    match = models.ForeignKey('Matches')
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
    class Meta:
        managed = False
        db_table = 'Match_Players'

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
    fechamodificacion = models.DateTimeField(db_column='FechaModificacion') # Field name made lowercase.
    condetalle = models.BooleanField(db_column='ConDetalle') # Field name made lowercase.
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
    class Meta:
        managed = False
        db_table = 'Matches'

class PicksBans(models.Model):
    match = models.ForeignKey(Matches)
    is_pick = models.BooleanField()
    hero_id = models.SmallIntegerField()
    team = models.BooleanField()
    order = models.SmallIntegerField()
    class Meta:
        managed = False
        db_table = 'Picks_Bans'

class StatsHero(models.Model):
    heroid = models.IntegerField(db_column='HeroId') # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=50) # Field name made lowercase.
    class Meta:
        managed = False
        db_table = 'stats_hero'

