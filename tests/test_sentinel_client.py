from pretend import stub
import pytest


@pytest.fixture
def Client():
    from django_redis_sentinel import SentinelClient
    return SentinelClient


@pytest.fixture
def client(Client):
    c = Client(
        server="redis_master/foo:1000,foo:1000/1",
        params={},
        backend=object()
    )
    return c


@pytest.fixture
def ImproperlyConfigured():
    from django.core.exceptions import ImproperlyConfigured
    return ImproperlyConfigured


@pytest.fixture
def MockSentinel():
    class MockSentinel(object):
        def __init__(self, hosts, socket_timeout):
            pass

        def discover_master(self, master_name):
            return ("write_host", 6379)

        def discover_slaves(self, master_name):
            return [
                ("slave_host", 6379),
                ("slave_host2", 6379),
            ]
    return MockSentinel


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


def test_get_client_write(client, monkeypatch):
    monkeypatch.setattr(client, 'connect', lambda write: write)
    actual = client.get_client(write=True)
    assert actual is True


def test_get_client_read(client, monkeypatch):
    monkeypatch.setattr(client, 'connect', lambda write: write)
    actual = client.get_client(write=False)
    assert actual is False


def test_connect_write(client, monkeypatch, MockSentinel):
    monkeypatch.setattr(client, 'connection_factory', stub(connect=lambda url: url))
    monkeypatch.setattr(client, 'parse_connection_string', lambda x: ("foo", 0, "1"))

    assert "redis://write_host:6379/1" == client.connect(True, MockSentinel)


def test_connect_read(client, monkeypatch, MockSentinel):
    monkeypatch.setattr(client, 'connection_factory', stub(connect=lambda url: url))
    monkeypatch.setattr(client, 'parse_connection_string', lambda x: ("foo", 0, "1"))

    expected_results = [
        "redis://slave_host:6379/1",
        "redis://slave_host2:6379/1",
        "redis://write_host:6379/1"
    ]
    assert client.connect(False, MockSentinel) in expected_results


def test_close_read(client, monkeypatch):
    stub_client = stub(connection_pool=stub(_available_connections=[
        stub(disconnect=lambda: True),
        stub(disconnect=lambda: True),
    ]))
    monkeypatch.setattr(client, "_client_read", stub_client)
    monkeypatch.setattr(client, "_client_write", None)

    client.close()

    assert client._client_write is None
    assert client._client_read is None


def test_close_write(client, monkeypatch):
    stub_client = stub(connection_pool=stub(_available_connections=[
        stub(disconnect=lambda: True),
        stub(disconnect=lambda: True),
    ]))
    monkeypatch.setattr(client, "_client_read", None)
    monkeypatch.setattr(client, "_client_write", stub_client)

    client.close()

    assert client._client_write is None
    assert client._client_read is None


def test_close_both(client, monkeypatch):
    stub_client = stub(connection_pool=stub(_available_connections=[
        stub(disconnect=lambda: True),
        stub(disconnect=lambda: True),
    ]))
    monkeypatch.setattr(client, "_client_read", stub_client)
    monkeypatch.setattr(client, "_client_write", stub_client)

    client.close()

    assert client._client_write is None
    assert client._client_read is None
