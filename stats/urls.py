from django.conf.urls import patterns, url

from stats import views

urlpatterns = patterns('',
    url(r'^$', views.PlayersView.as_view(), name='players'),
    url(r'^search/$', views.getPlayer, name='getPlayer'),
    url(r'^player/(?P<account_id>\d+)/$', views.MatchesxPlayer.as_view(), name='matchesxplayer'),
    url(r'^player/(?P<account_id>[\d,]+)/winrate/(?:(?P<num_matches>\d+)/)?$', views.WinrateView.as_view(), name='winrate'),
    url(r'^player/(?P<account_id>[\d,]+)/winrate/q/$', views.getWinratebynummatches, name='getWinratebynummatches'),
    url(r'^player/(?P<account_id>[\d,]+)/heroes/?$', views.HeroesxPlayer.as_view(), name='heroesxplayer'),
    url(r'^player/(?P<account_id>[\d,]+)/heroes/(?:(?P<hero_id>\d+)/)?$', views.heroDetail, name='herodetail'),
    url(r'^match/(?P<match_id>\d+)/$', views.MatchDetail.as_view(), name='match'),
    url(r'^heroes/$', views.Heroes.as_view(), name='heroes'),
    url(r'^countries/$', views.Countries.as_view(), name='countries'),
    url(r'^abilities/$', views.Abilities.as_view(), name='abilities'),
    url(r'^items/$', views.Items.as_view(), name='items'),
    url(r'^done/$', views.done, name='done'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^celery/$', views.test_celery, name='test_celery'),
)
