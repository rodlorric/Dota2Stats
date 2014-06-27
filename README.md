Dota2Stats
==========

A rough dotabuff clone, just for the sake of learning python/django

Quick Overview:
* Uses python and django as framework.
* Fetches data from Steam/Dota2 WebAPI
  * Fetches Player's Match History (up to 500 matches, as per API limit).
  * Fetches Match Detail for any given match ID.
  * Fetches Player Steam Summary.
* Login through Steam OpenID using social_auth.
* Match XP difference over time using google chart API.
* Deferred task upon fetching player's history, using django-celery and RabbitMQ.
* sqlite3 database.
* Geolocation using google staticmaps API and https://github.com/Holek/steam-friends-countries.
