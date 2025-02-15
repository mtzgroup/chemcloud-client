# Authentication

Authentication is the process of supplying your credentials (usually a username and password) to `chemcloud` so that you can perform computations. `chemcloud` provides a few easy ways for you to authenticate. If you do not have a ChemCloud account you can get one for free here or at the address of the ChemCloud server you want to interact with: [https://chemcloud.mtzlab.com/signup](https://chemcloud.mtzlab.com/signup)

## `setup_profile()` (recommended for most cases)

```python
from chemcloud import setup_profile
setup_profile() # This will setup the default profile
✅ If you dont get have an account please signup at: https://chemcloud.mtzlab.com/signup
Please enter your ChemCloud username: your_username@email.com
Please enter your ChemCloud password:
Authenticating...
'default' profile configured! Username/password not required for future use.
```

Performing this action will configure your local client by writing authentication tokens to `~/.chemcloud/credentials`. You will not need to run `setup_profile()` ever again. Under the hood `chemcloud` will access your tokens, refresh them when necessary, and keep you logged in to ChemCloud. Note that this will write a file to your home directory with sensitive access tokens, so if you are on a shared computer or using a device where you would not want to write this information to disk do not use this option. If you would like to write the `credentials` file to a different directory than `~/.chemcloud`, set the `CHEMCLOUD_BASE_DIRECTORY` environment variable to the path of interest.

You can configure multiple profiles in case you have multiple logins to ChemCloud by passing a profile name to `setup_profile()`:

```python
setup_profile('mtz_lab')
✅ If you dont get have an account please signup at: https://chemcloud.mtzlab.com/signup
Please enter your ChemCloud username: your_username@email.om
Please enter your ChemCloud password:
Authenticating...
'mtz_lab' profile configured! Username/password not required for future use.
```

To use a profile other than the default profile, do one of the following:

1. Set the `chemcloud_credentials_profile` environment variable in your shell or in python.
   ```sh
   export chemcloud_credentials_profile="mtz_lab"
   ```
2. Run `configure_client` before running `compute() and pass the profile.
   ```python
   from chemcloud import configure_client
   configure_client(profile="mtz_lab")
   ```
3. Pass the profile option to a client instance and use the `client.compute()` method on it.

   ```python
   from chemcloud import CCClient
   # Use default profile
   client = CCClient()

   # Use named profile
   client = CCClient(profile="mtz_lab")
   client.compute(...)
   ```

## Environment Variables

All variables on the `config.Settings` object can be set via environment variables and chemcloud will pick them up and use them automatically.

Most commonly, users may want to modify one or many of the following:

```sh
export CHEMCLOUD_DOMAIN=https://mycustomchemcloud.com
export CHEMCLOUD_QUEUE=myqueue
export CHEMCLOUD_CREDENTIALS_PROFILE=non-default-profile-name
```

If you are operating in an environment where tokens should not be persistently saved to disk you may want to set the following. `chemcloud` will find these values and maintain all access tokens in memory only.

```sh
export CHEMCLOUD_USERNAME=myusername@chemcloud.com
export CHEMCLOUD_PASSWORD=mysupersecretpassword  # pragma: allowlist secret
```

## Username/Password when prompted after calling `client.compute(...)`

If you have not run `setup_profile()` or set environment variables you will be requested for your username and password when you submit a computation to ChemCloud using `compute(...)`. The client will use your username and password to get access tokens and ask if you'd like to save the tokens to disk for future sessions.

## Pass Username/Password to Client (not recommended)

You can directly pass a username and password to the `client` object. This is **not** recommended as it opens up the possibility of your credentials accidentally being committed to your code repo. However, it can be used in rare circumstances when necessary.

```python
from chemcloud import configure_client
configure_client = (
    chemcloud_username="your_username@email.com", chemcloud_password="super_secret_password"  # pragma: allowlist secret
    )
```
