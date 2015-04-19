
import pytest


@pytest.fixture
def Client():
    from django_redis_sentinel import SentinelClient
    return SentinelClient


@pytest.fixture
def ImproperlyConfigured():
    from django.core.exceptions import ImproperlyConfigured
    return ImproperlyConfigured


def test_client_exists(Client):
    c = Client(
        server="redis_master/foo:1000,foo:1000/1",
        params={},
        backend=object())
    assert c


def test_parse_connection_string(Client):
    constring = "redis_master/foo:1000,foo:1000/1"
    c = Client(
        server=constring,
        params={},
        backend=object())
    expected = (
        "redis_master",
        [("foo", 1000), ("foo", 1000)],
        "1",
    )

    assert expected == c.parse_connection_string(constring)


_bad_connection_strings = [
        "redis_master/foo:1000",
        "redis_master/foo:abcd",
]


@pytest.mark.parametrize("constring", _bad_connection_strings)
def test_connection_string_sad(Client, ImproperlyConfigured, constring):
    with pytest.raises(ImproperlyConfigured):
        c = Client(
            server=constring,
            params={},
            backend=object()
        )
        c.parse_connection_string(constring)
