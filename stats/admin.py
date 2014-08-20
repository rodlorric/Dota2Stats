from django.contrib import admin
#from stats.models import Player, Match, AbilityUpgrade, PlayerInfo, Hero, Country, Ability, Item
from stats.models import Heroes, Abilities, Items, Countries

class MatchAdmin(admin.ModelAdmin):
    list_display = ('match_id', 'start_time')
    list_filter = ['start_time']
    search_fields = ['match_id']

class PlayerAdmin(admin.ModelAdmin):
    list_display = ('account_id', 'match_id')
    list_filter = ['match_id']
    search_fields = ['account_id']
    
class AbilityUpgradeAdmin(admin.ModelAdmin):
    list_display = ('match_id', 'player_slot', 'time', 'ability')
    list_filter = ['match_id']

class AbilityAdmin(admin.ModelAdmin):
    list_display = ('name', 'ability_id')
    list_filter = ['ability_id']

class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'item_id')
    list_filter = ['item_id']

class PlayerInfoAdmin(admin.ModelAdmin):
    list_display = ('steamid', 'personaname')
    list_filter = ['steamid']
    search_fields = ['steamid']

#admin.site.register(Player, PlayerAdmin)
#admin.site.register(Match, MatchAdmin)
#admin.site.register(AbilityUpgrade, AbilityUpgradeAdmin)
#admin.site.register(PlayerInfo, PlayerInfoAdmin)
admin.site.register(Heroes)
admin.site.register(Countries)
admin.site.register(Abilities, AbilityAdmin)
admin.site.register(Items, ItemAdmin)