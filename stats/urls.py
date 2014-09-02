from django.conf.urls import patterns, url

from stats import views, matchesview, winratesview, matchesxplayerview, heroesxplayerview

urlpatterns = patterns('',
    url(r'^$', views.PlayersView.as_view(), name='players'),
    url(r'^search/$', views.get_player, name='get_player'),
    url(r'^player/(?P<account_id>\d+)/$', matchesxplayerview.MatchesxPlayer.as_view(), name='matchesxplayer'),
    url(r'^player/(?P<account_id>[\d,]+)/winrate/(?:(?P<num_matches>\d+)/)?$', winratesview.WinrateView.as_view(), name='winrate'),
    url(r'^player/(?P<account_id>[\d,]+)/winrate/q/$', winratesview.get_winrate_by_nummatches, name='get_winrate_by_nummatches'),
    url(r'^player/(?P<account_id>[\d,]+)/heroes/?$', heroesxplayerview.HeroesxPlayer.as_view(), name='heroesxplayer'),
    url(r'^player/(?P<account_id>[\d,]+)/heroes/(?:(?P<hero_id>\d+)/)?$', heroesxplayerview.hero_detail, name='herodetail'),
    url(r'^match/(?P<match_id>\d+)/$', matchesview.MatchDetail.as_view(), name='match'),
    url(r'^heroes/$', views.HeroesList.as_view(), name='heroes'),
    url(r'^countries/$', views.CountriesList.as_view(), name='countries'),
    url(r'^abilities/$', views.AbilitiesList.as_view(), name='abilities'),
    url(r'^items/$', views.ItemsList.as_view(), name='items'),
    url(r'^done/$', views.done, name='done'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^celery/$', views.test_celery, name='test_celery'),
)
