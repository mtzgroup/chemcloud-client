from qccloud.client import QCClient


def test_version():
    client = QCClient()
    assert isinstance(client.version, str)
