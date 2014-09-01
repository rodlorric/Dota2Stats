"""
Django settings for Dota2Stats project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# celery settings
import djcelery
djcelery.setup_loader()
BROKER_URL = 'amqp://guest:guest@localhost:5672//'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'tg&6pje(u1e%i4ekc!wt#05fi27sgydwsow2fcj3rfjjdzn_qj'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

HTML_MINIFY = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

CACHE_BACKEND = 'memcached://127.0.0.1:11211/'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        #'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'stats',
    'social_auth',
    'celery',
    'djcelery',
)

MIDDLEWARE_CLASSES = (
    #'django.middleware.cache.UpdateCacheMiddleware',
    #'django.middleware.common.CommonMiddleware',
    #'django.middleware.cache.FetchFromCacheMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'htmlmin.middleware.HtmlMinifyMiddleware',
    'htmlmin.middleware.MarkRequestMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'Dota2Stats.urls'

WSGI_APPLICATION = 'Dota2Stats.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#    }
#}
DATABASES = {
    'default': {
        'NAME': 'Dota2',
        'ENGINE': 'sqlserver_ado',
        'HOST': '186.95.156.208',
        'PORT': '1433',
        'USER': 'pu',
        'PASSWORD': 'pu123456',
        'provider': 'SQLOLEDB',
        'OPTIONS' : {
            'provider': 'SQLOLEDB'
        },
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False

AUTHENTICATION_BACKENDS = (
    'social_auth.backends.steam.SteamBackend',    
    'django.contrib.auth.backends.ModelBackend',
)

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'social_auth.context_processors.social_auth_by_type_backends',
)

SOCIAL_AUTH_ENABLED_BACKENDS = ('steam',)
SOCIAL_AUTH_DEFAULT_USERNAME = 'new_social_auth_user'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/stats/done/'
LOGIN_ERROR_URL = '/login-error/'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]

STEAM_API_KEY = 'B12A63C050DC4C26F413739E6DB265AF'

STEAM_BASE_URL = 'https://api.steampowered.com/'

STEAM_CDN_HEROES_URL = 'http://cdn.dota2.com/apps/dota2/images/heroes/%s_%s'

COUNTRIES_URL = 'http://api.geonames.org/countryInfoJSON?username=sphex'

COUNTRY_INFO = 'http://api.geonames.org/searchJSON?country=%s&name=%s&maxRows=1&username=sphex'

FLAG_URL = 'http://cdn.steamcommunity.com/public/images/countryflags/%s.gif'

GMAPS_URL = 'http://maps.google.com/maps/api/staticmap?size=640x480&key=AIzaSyB0MIjWkYm3KpDfNCUFI1_CeuhUym7BjaQ&sensor=false&visible=0,0&'

HERO_URL = 'http://www.dota2.com/hero/%s/'

ITEM_IMG_URL = 'http://cdn.dota2.com/apps/dota2/images/items/%s_lg.png'

VALID_GAME_MODES = [1, 2 ,3 ,4, 5, 12 ,13 ,16]

INVALID_ACCOUNT_IDS = ['4294967295', '0', '-1', '76561202255233023']

PLAYER_ANON_AVATAR = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD//gA7Q1JFQVRPUjogZ2QtanBlZyB2MS4wICh1c2luZyBJSkcgSlBFRyB2NjIpLCBxdWFsaXR5ID0gOTAK/9sAQwADAgIDAgIDAwMDBAMDBAUIBQUEBAUKBwcGCAwKDAwLCgsLDQ4SEA0OEQ4LCxAWEBETFBUVFQwPFxgWFBgSFBUU/9sAQwEDBAQFBAUJBQUJFA0LDRQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQU/8AAEQgAIAAgAwEiAAIRAQMRAf/EAB8AAAEFAQEBAQEBAAAAAAAAAAABAgMEBQYHCAkKC//EALUQAAIBAwMCBAMFBQQEAAABfQECAwAEEQUSITFBBhNRYQcicRQygZGhCCNCscEVUtHwJDNicoIJChYXGBkaJSYnKCkqNDU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6g4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2drh4uPk5ebn6Onq8fLz9PX29/j5+v/EAB8BAAMBAQEBAQEBAQEAAAAAAAABAgMEBQYHCAkKC//EALURAAIBAgQEAwQHBQQEAAECdwABAgMRBAUhMQYSQVEHYXETIjKBCBRCkaGxwQkjM1LwFWJy0QoWJDThJfEXGBkaJicoKSo1Njc4OTpDREVGR0hJSlNUVVZXWFlaY2RlZmdoaWpzdHV2d3h5eoKDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uLj5OXm5+jp6vLz9PX29/j5+v/aAAwDAQACEQMRAD8A/P4mW5nmllmeSR3LMzMSSc1a07R73V72KzsILi9u5TiOC2RpJHPoFGSarQ/ef6n+de4fAn9oaL4D+DfGX9i6Uf8AhO9XSKDT9eZY3WxiDZcBGByTkn0JCZBxQB41qeiX+iXslnqNtdWF3H9+3uo2jkX6q2CKpgy208MsUzxyI4ZWViCDmvsr9rrUdT1j9nb4T6h8RBbH4qXUs0zMsSxXJ04hivnKoAU5MPGBg7uM7q+NpvvJ9R/OgAh+8/1P867T4POI/iz4Mc6U+u7NZtG/suPbuu8TKfKG4hct93njnmuKIltp5opYXjkRyrKykEHNWbDVbvSr63vbKaezvLeRZYbi3ZkkidTlWVhyCCMgjpQB6l+1F411nx58dPFWpa5a3mnXaXP2ZNOvXVpLKNBhYflJUY5PB5JJ6k15LN95PqP51a1PWr7WtQnvtRuLm/vrhzJNc3TtJLIx6lmbJJ9zVQCW5nhiiheSR3CqqqSSc0Af/9k="
