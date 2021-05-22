# Authentication

Authentication is the process of supplying your credentials (usually a username and password) to `tccloud` so that you can perform computation. `tccloud` provides a few easy ways for you to authenticate. If you do not have a TeraChem Cloud account you can get one for free here: [https://tccloud.mtzlab.com/signup](https://tccloud.mtzlab.com/signup)

## Username and Password

### [client.configure()][tccloud.client:TCClient.configure] (recommended for most cases)

```python
>>> from tccloud import TCClient
>>> client = TCClient()
>>> client.configure()
✅ If you dont get have an account please signup at: https://tccloud.mtzlab.com/signup
Please enter your TeraChem Cloud username: your_username@email.com
Please enter your TeraChem Cloud password:
Authenticating...
'default' profile configured! Username/password not required for future use of TCClient
```

Performing this action will configure your local client by writing authentication tokens to `~/.tccloud/credentials`. You will not need to execute `configure()` ever again. Under the hood `TCClient` will access your tokens, refresh them when necessary, and keep you logged in to TeraChem Cloud. Note that this will write a file to your home directory with sensitive access tokens, so if you are on a shared computer or using a device where you would not want to write this information to disk do not use this option. If you would like to write the `credentials` file to a different directory than `~/.tccloud`, set the `TCCLOUD_BASE_DIRECTORY` environment variable to the path of interest.

You can configure multiple profiles in case you have multiple logins to TeraChem cloud by passing a profile name to `configure()`:

```python
>>> client.configure('mtz_lab')
✅ If you dont get have an account please signup at: https://tccloud.mtzlab.com/signup
Please enter your TeraChem Cloud username: your_username@email.om
Please enter your TeraChem Cloud password:
Authenticating...
'mtz_lab' profile configured! Username/password not required for future use of TCClient
```

To use one of these profiles pass the profile option to your client instance. The "default" profile is used when no profile name is passed:

```python
>>> from tccloud import TCClient
# Use default profile
>>> client = TCClient()

# Use named profile
>>> client = TCClient(profile="mtz_lab")
```

### Environment Variables

You can set your TeraChem username and password in your environment and the `client` will find them automatically. Set `TCCLOUD_USERNAME` and `TCCLOUD_PASSWORD`. When you create a client it will find these values and maintain all access tokens in memory only.

### Pass Username/Password when prompted after requesting a compute job

If you have not run `client.configure()` or set environment variables you will be requested for your username and password when you submit a computation to TeraChem Cloud using `client.compute(...)`. The client will use your username and password to get access tokens and will maintain access tokens for you in memory only. Your login session will be valid for the duration of your python session.

### Pass Username/Password to Client (not recommended)

You can directly pass a username and password to the `client` object. This is **not** recommended as it opens up the possibility of your credentials accidentally being committed to your code repo. However, it can be used in rare circumstances when necessary.

```python
>>> from tccloud import TCClient
>>> client = TCClient(
    tccloud_username="your_username@email.com", tccloud_password="super_secret_password"
    )
```
