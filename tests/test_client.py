from chemcloud.client import CCClient


def test_version():
    client = CCClient()
    assert isinstance(client.version, str)
