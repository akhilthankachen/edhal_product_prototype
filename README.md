# Hydroponic Automation



A Automize code to automatically bundle dependencies from
`requirements.txt` and make them available in your `PYTHONPATH`.

**Requires Serverless >= v1.12**

## Install

```
sls plugin install -n serverless-python-requirements
```

This will automatically add the plugin to your project's `package.json` and the plugins section of its
`serverless.yml`. That's all that's needed for basic use! The plugin will now bundle your python
dependencies specified in your `requirements.txt` or `Pipfile` when you run `sls deploy`.

For a more in depth introduction on how to use this plugin, check out
[this post on the Serverless Blog](https://serverless.com/blog/serverless-python-packaging/)

If you're on a mac, check out [these notes](#applebeersnake-mac-brew-installed-python-notes) about using python installed by brew.


## Cross compiling!
Compiling non-pure-Python modules or fetching their manylinux wheels is
supported on non-linux OSs via the use of Docker and the
[docker-lambda](https://github.com/lambci/docker-lambda) image.
To enable docker usage, add the following to your `serverless.yml`:
```yaml
custom:
  pythonRequirements:
    dockerizePip: true
```
The dockerizePip option supports a special case in addition to booleans of `'non-linux'` which makes
it dockerize only on non-linux environments.


To utilize your own Docker container instead of the default, add the following to your `serverless.yml`:
```yaml
custom:
  pythonRequirements:
    dockerImage: <image name>:tag
```
This must be the full image name and tag to use, including the runtime specific tag if applicable.

Alternatively, you can define your Docker image in your own Dockerfile and add the following to your `serverless.yml`:
```yaml
custom:
  pythonRequirements:
    dockerFile: ./path/to/Dockerfile
```
With `Dockerfile` the path to the Dockerfile that must be in the current folder (or a subfolder).
Please note the `dockerImage` and the `dockerFile` are mutually exclusive.

To install requirements from private git repositories, add the following to your `serverless.yml`:
```yaml
custom:
  pythonRequirements:
    dockerizePip: true
    dockerSsh: true
```
The `dockerSsh` option will mount your `$HOME/.ssh/id_rsa` and `$HOME/.ssh/known_hosts` as a
volume in the docker container. If your SSH key is password protected, you can use `ssh-agent`
because `$SSH_AUTH_SOCK` is also mounted & the env var set.
It is important that the host of your private repositories has already been added in your
`$HOME/.ssh/known_hosts` file, as the install process will fail otherwise due to host authenticity
failure.

You can also pass environment variables to docker by specifying them in `dockerEnv`
option:
```yaml
custom:
  pythonRequirements:
    dockerEnv:
      - https_proxy
```

[:checkered_flag: Windows notes](#checkered_flag-windows-dockerizepip-notes)

## Pipenv support :sparkles::cake::sparkles:
If you include a `Pipfile` and have `pipenv` installed instead of a `requirements.txt` this will use
`pipenv lock -r` to generate them. It is fully compatible with all options such as `zip` and
`dockerizePip`. If you don't want this plugin to generate it for you, set the following option:
```yaml
custom:
  pythonRequirements:
    usePipenv: false
```


## Poetry support :sparkles::pencil::sparkles:
NOTE: Only poetry version 1 supports the required `export` command for this
feature. As of the point this feature was added, poetry 1.0.0 was in preview
and requires that poetry is installed with the --preview flag.

TL;DR Install poetry with the `--preview` flag.

If you include a `pyproject.toml` and have `poetry` installed instead of a `requirements.txt` this will use
`poetry export --without-hashes -f requirements.txt` to generate them. It is fully compatible with all options such as `zip` and
`dockerizePip`. If you don't want this plugin to generate it for you, set the following option:
```yaml
custom:
  pythonRequirements:
    usePoetry: false
```


## Dealing with Lambda's size limitations
To help deal with potentially large dependencies (for example: `numpy`, `scipy`
and `scikit-learn`) there is support for compressing the libraries. This does
require a minor change to your code to decompress them.  To enable this add the
following to your  `serverless.yml`:
```yaml
custom:
  pythonRequirements:
    zip: true
```

and add this to your handler module before any code that imports your deps:
```python
try:
  import unzip_requirements
except ImportError:
  pass
```
### Slim Package
_Works on non 'win32' environments: Docker, WSL are included_
To remove the tests, information and caches from the installed packages,
enable the `slim` option. This will: `strip` the `.so` files, remove `__pycache__`
and `dist-info` directories as well as `.pyc` and `.pyo` files.
```yaml
custom:
  pythonRequirements:
    slim: true
```
#### Custom Removal Patterns
To specify additional directories to remove from the installed packages,
define a list of patterns in the serverless config using the `slimPatterns`
option and glob syntax. These paterns will be added to the default ones (`**/*.py[c|o]`, `**/__pycache__*`, `**/*.dist-info*`).
Note, the glob syntax matches against whole paths, so to match a file in any
directory, start your pattern with `**/`.
```yaml
custom:
  pythonRequirements:
    slim: true
    slimPatterns:
      - "**/*.egg-info*"
```
To overwrite the default patterns set the option `slimPatternsAppendDefaults` to `false` (`true` by default).
```yaml
custom:
  pythonRequirements:
    slim: true
    slimPatternsAppendDefaults: false
    slimPatterns:
      - "**/*.egg-info*"
```
This will remove all folders within the installed requirements that match
the names in `slimPatterns`

#### Option not to strip binaries

In some cases, stripping binaries leads to problems like "ELF load command address/offset not properly aligned", even when done in the Docker environment. You can still slim down the package without `*.so` files with
```yaml
custom:
  pythonRequirements:
    slim: true
    strip: false
```

### Lambda Layer
Another method for dealing with large dependencies is to put them into a
[Lambda Layer](https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html).
Simply add the `layer` option to the configuration.
```yaml
custom:
  pythonRequirements:
    layer: true
```
The requirements will be zipped up and a layer will be created automatically.
Now just add the reference to the functions that will use the layer.
```yaml
functions:
  hello:
    handler: handler.hello
    layers:
      - {Ref: PythonRequirementsLambdaLayer}
```
If the layer requires additional or custom configuration, add them onto the `layer` option.
```yaml
custom:
  pythonRequirements:
    layer:
      name: ${self:provider.stage}-layerName
      description: Python requirements lambda layer
      compatibleRuntimes:
        - python3.7
      licenseInfo: GPLv3
      allowedAccounts:
        - '*'
```
## Omitting Packages
You can omit a package from deployment with the `noDeploy` option. Note that
dependencies of omitted packages must explicitly be omitted too. By default,
the following packages are omitted as they are already installed on Lambda:

 * boto3
 * botocore
 * docutils
 * jmespath
 * pip
 * python-dateutil
 * s3transfer
 * setuptools
 * six

This example makes it instead omit pytest:
```yaml
custom:
  pythonRequirements:
    noDeploy:
      - pytest
```

To include the default omitted packages, set the `noDeploy` option to an empty
list:
```yaml
custom:
  pythonRequirements:
    noDeploy: []
