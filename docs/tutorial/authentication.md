# Authentication

Authentication is the process of supplying your credentials (usually a username and password) to `qccloud` so that you can perform computation. `qccloud` provides a few easy ways for you to authenticate. If you do not have a QC Cloud account you can get one for free here: [https://qccloud.mtzlab.com/signup](https://qccloud.mtzlab.com/signup)

## Username and Password

### [client.configure()][qccloud.client:QCClient.configure] (recommended for most cases)

```python
>>> from qccloud import QCClient
>>> client = QCClient()
>>> client.configure()
✅ If you dont get have an account please signup at: https://qccloud.mtzlab.com/signup
Please enter your Quantum Chemistry Cloud username: your_username@email.com
Please enter your Quantum Chemistry Cloud password:
Authenticating...
'default' profile configured! Username/password not required for future use of QCClient
```

Performing this action will configure your local client by writing authentication tokens to `~/.qccloud/credentials`. You will not need to execute `configure()` ever again. Under the hood `QCClient` will access your tokens, refresh them when necessary, and keep you logged in to QC Cloud. Note that this will write a file to your home directory with sensitive access tokens, so if you are on a shared computer or using a device where you would not want to write this information to disk do not use this option. If you would like to write the `credentials` file to a different directory than `~/.qccloud`, set the `QCCLOUD_BASE_DIRECTORY` environment variable to the path of interest.

You can configure multiple profiles in case you have multiple logins to QC Cloud by passing a profile name to `configure()`:

```python
>>> client.configure('mtz_lab')
✅ If you dont get have an account please signup at: https://qccloud.mtzlab.com/signup
Please enter your Quantum Chemistry Cloud username: your_username@email.om
Please enter your Quantum Chemistry Cloud password:
Authenticating...
'mtz_lab' profile configured! Username/password not required for future use of QCClient
```

To use one of these profiles pass the profile option to your client instance. The "default" profile is used when no profile name is passed:

```python
>>> from qccloud import QCClient
# Use default profile
>>> client = QCClient()

# Use named profile
>>> client = QCClient(profile="mtz_lab")
```

### Environment Variables

You can set your QC Cloud username and password in your environment and the `client` will find them automatically. Set `QCCLOUD_USERNAME` and `QCCLOUD_PASSWORD`. When you create a client it will find these values and maintain all access tokens in memory only.

### Pass Username/Password when prompted after requesting a compute job

If you have not run `client.configure()` or set environment variables you will be requested for your username and password when you submit a computation to QC Cloud using `client.compute(...)`. The client will use your username and password to get access tokens and will maintain access tokens for you in memory only. Your login session will be valid for the duration of your python session.

### Pass Username/Password to Client (not recommended)

You can directly pass a username and password to the `client` object. This is **not** recommended as it opens up the possibility of your credentials accidentally being committed to your code repo. However, it can be used in rare circumstances when necessary.

```python
>>> from qccloud import QCClient
>>> client = QCClient(
    qccloud_username="your_username@email.com", qccloud_password="super_secret_password"
    )
```
