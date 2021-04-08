[![Build Status](https://github.com/SpatialBuzz/django-redis-sentinel/actions/workflows/ci.yml/badge.svg)](https://github.com/SpatialBuzz/django-redis-sentinel/actions/workflows/ci.yml/badge.svg)

# django-redis-sentinel
Plugin for django-redis that supports Redis Sentinel

# Installation

```
pip install django-redis-sentinel
```

# Usage

Location format: master_name/sentinel_server:port,sentinel_server:port/db_id

In your settings, do something like this:

```
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis_master/sentinel-host1:2639,sentinel-host2:2639/0"
            "OPTIONS": {
                "PASSWORD": 's3cret_passw0rd!',
                "ALWAYS_MASTER": True,
                "CLIENT_CLASS": "django_redis_sentinel.SentinelClient",
            }
        }
    }
```

## Settings
These are top-level settings in settings.py

`DJANGO_REDIS_CLOSE_CONNECTION` - Close connection after each request, off will allow persistant connections (default `False`)