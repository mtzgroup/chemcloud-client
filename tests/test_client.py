from tccloud.client import TCClient


def test_version():
    client = TCClient()
    assert isinstance(client.version, str)
