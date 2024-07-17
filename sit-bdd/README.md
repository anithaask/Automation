# SITBDD

SIT-BDD is a Python package for the automated integration testing of RPOS, primarily through the use of product team packages.

## Creating a system for SITBDD testing

To get system, follow [this guide](https://confluence.ncr.com/display/PCR/Get+DevTestLab+environment).
It is highly recommended to create a new system through this guide for running tests.

Alternatively, you can just grab any RPOS site environment with the same nodes as the environment above, and run the provisioning steps manually.

## Setting up the SITBDD environment

Before running tests, it is crucial to run [`one_click_setup.py`](one_click_setup.py) beforehand.

In order to run this script, [`run_bdd.py`](run_bdd.py) must be present in the same folder.

Note that [`run_bdd.py`](run_bdd.py) can also be used for starting, stopping or restarting apps after the environment has already been set up.

[`one_click_setup.py`](one_click_setup.py) has the following arguments:
```
  -h, --help            show this help message and exit
  --deployment          Switches the one_click to deployment version. If --sit-bdd-version is not specified, it installs latest sitbdd package.
  --sit-bdd-version SIT_BDD_VERSION
                        Specify the verison of SIT BDD to be installed. Only use with argument --deployment.
  --unattended-mode     Serves for one_click to be able to run in unattended mode.
  --run-behave          Serves for one_click to determine if we want to run behave at the end or not.
  --feature FEATURE     Serves for run-behave, if we want to run some specific feature file only e.g. 'BasicTest.feature'. Runs all by default.
  --collect-logs        Specify for one_click to collect logs from SC and nodes.
  --cfrpos_version CFRPOS_VERSION
                        Defines the version of product package cfrpos
  --cfrsc_version CFRSC_VERSION
                        Defines the version of product package cfrsc
  --cfrrcmserver_version CFRRCMSERVER_VERSION
                        Defines the version of product package cfrrcmserver
  --cfrfuelbdd_version CFRFUELBDD_VERSION
                        Defines the version of product package cfrfuelbdd
  --cfrsmtaskman_version CFRSMTASKMAN_VERSION
                        Defines the version of product package cfrsmtaskman
```


[`run_bdd.py`](run_bdd.py) has the following arguments:
```
  -h, --help            show this help message and exit
  --run {startapps,closeapps,restartapps,behave}
                        Defines what the program will do.
  --unattended-mode     Serves for the script to be able to run in unattended mode. True/False
  --feature FEATURE     Serves for run-behave, if we want to run some specific feature file only e.g. 'BasicTest.feature'. Runs all by default.
```

### Deployment mode

Download the [`one_click_setup.py`](one_click_setup.py) and [`run_bdd.py`](run_bdd.py) scripts from
either this repository or from jfrog. Note that both python files must be in the same directory.

Run the following command:

```
.\one_click_setup.py --unattended-mode --deployment --sit-bdd-version SIT_BDD_VERSION
```

Optionally, you may omit `--sit-bdd-version` to install the latest SITBDD version.

### Development

Download sit-bdd repository and run the following command:

```
.\one_click_setup.py --unattended-mode
```

For development environment it is recommended to use VS Code and its remote development, see:
https://confluence.ncr.com/display/PCR/VS+Code+usage+with+Ansible+system

## Running tests

There are a few different ways to run the tests.

### Using one_click_setup.py

When you are running the [`one_click_setup.py`](one_click_setup.py), you can choose to run all the tests which are **not tagged as @wip, @manual or @waitingforfix**.
This option is the easiest and is used while the sit-bdd is executed in CI/CD pipeline.

To run a test feature file at the end of [`one_click_setup.py`](one_click_setup.py), add the following argument to the end:

```
.\one_click_setup.py --run-behave --feature FEATURE_FILE.feature
```

Optionally, you may omit `--feature` to run the whole SITBDD test suite.

### Using run_bdd.py

When your environment is already set up, you may still run tests the same way you would with
[`one_click_setup.py`](one_click_setup.py) by using [`run_bdd.py`](run_bdd.py).

```
.\run_bdd.py --run behave --feature FEATURE_FILE.feature
```

Optionally, you may omit `--feature` to run the whole SITBDD test suite.

### Using behave

You can use the `behave` command directly from the command line.

Navigate to where the folder "features" is located:
- In deployment mode, the folder "features" is in `C:/Python311/lib/site-packages/sitbdd/`
- In development mode, the folder "features" is wherever you put your sit-bdd repository in `./sitbdd/`

If you wish to run a single feature file of tests, run the following command:
```
behave features/FEATURE_FILE.feature --k --tags==~@wip --tags==~@manual --tags==~@waitingforfix --junit --junit-directory C:/Staging/Staging_sitbdd/SITBDD_logs/junit
```

If you wish to run the entire SITBDD test suite, run the following command:
```
behave --k --tags==~@wip --tags==~@manual --tags==~@waitingforfix --junit --junit-directory "C:/Staging/Staging_sitbdd/SITBDD_logs/junit"
```

If you wish to save the output of running these tests to a separate file while also viewing the output in the terminal,
you can append the following command, provided that you're using a PowerShell terminal:
```
| Tee-Object -FilePath "LOG_FILE.log"
```

# Help

If you need more information about the setup scripts, see their parameters.

All the relevant logs (automation outcome) are stored in `C:/Staging/Staging_sitbdd/SITBDD_logs`, including junit reports from behave.
