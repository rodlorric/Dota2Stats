Dota2Stats
==========

A rough dotabuff clone, just for the sake of learning python/django

Quick Overview:
* Uses python and django as main framework.
* Fetches data from Steam/Dota2 WebAPI
  * Fetches Player's Match History (up to 500 matches, as per API limit).
  * Fetches Match Detail for any given match ID.
  * Fetches Player Steam Summary.
* Login through Steam OpenID using social_auth.
* Match XP difference, Total Dire XP per player and Total Radiant XP per player, over time using google chart API.
* Winrates per player or group of players (up to 5 players) for all matches o a specefic number.
* Deferred task upon fetching player's history, using django-celery and RabbitMQ.
* MSSQL database.
* Geolocation using google staticmaps API and https://github.com/Holek/steam-friends-countries.
