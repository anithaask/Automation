import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
import importlib
import zipfile
import winreg
import site
import time
import warnings
from typing import Tuple, Union
from datetime import datetime
from stat import S_ISDIR


warnings.simplefilter('ignore', category=UserWarning)

SERVER_ID = "Default-Server"
REPOSITORY = "cfr-pypi-group"
config = None
log_file_name = None

# Equivalent to C:\Program Files\Radiant\Fastpoint\Bin. Simulators do not like spaces in paths.
DEFAULT_BIN_DIRECTORY = "C:\PROGRA~1\Radiant\Fastpoint\Bin"


def parse_args() -> argparse.Namespace:
    """Parse arguments to file.

    :return: Arguments.
    """
    parser = argparse.ArgumentParser(description="Install SIT BDD.")

    parser.add_argument(
        '-v',
        '--verbose',
        help="Hightens logging verbosity level to DEBUG. Default is INFO.",
        action="store_true",
    )
    parser.add_argument(
        "--deployment",
        help="Switches the one_click to deployment version. If --sit-bdd-version is not specified, it installs latest sitbdd package.",
        action="store_true",
    )
    parser.add_argument(
        "--sit-bdd-version",
        help="Specify the verison of SIT BDD to be installed. Only use with argument --deployment.",
        type=str,
        default=None,
    )
    parser.add_argument(
        "-u",
        "--unattended-mode",
        help="Serves for one_click to be able to run in unattended mode.",
        action="store_true",
    )
    parser.add_argument(
        "--run-behave",
        help="Serves for one_click to determine if we want to run behave at the end or not.",
        action="store_true",
    )
    parser.add_argument(
        "--feature",
        help="Serves for run-behave, if we want to run some specific feature file only e.g. 'BasicTest' or 'BasicTest.feature'. Runs all by default.",
        type=str,
        default="",
    )
    parser.add_argument(
        "--part",
        help="Serves for run-behave, if we want to run the suite in parts. A simple integer, works in cooperation with parts.json",
        choices=[1, 2, 3],
        type=int,
        default=None,
    )
    parser.add_argument(
        "--cfrpos_version",
        help="Defines the version of product package cfrpos",
        type=str,
        default=None,
    )
    parser.add_argument(
        "--cfrsc_version",
        help="Defines the version of product package cfrsc",
        type=str,
        default=None,
    )
    # TODO: this package version has to be manually updated
    parser.add_argument(
        "--cfrrcmserver_version",
        help="Defines the version of product package cfrrcmserver",
        type=str,
        default="2099.2.2181",
    )
    parser.add_argument(
        "--cfrfuelbdd_version",
        help="Defines the version of product package cfrfuelbdd",
        type=str,
        default=None,
    )
    parser.add_argument(
        "--cfrsmtaskman_version",
        help="Defines the version of product package cfrsmtaskman",
        type=str,
        default="2099.0.1.5379",
    )
    parser.add_argument(
        "--jfrog_artifact_path",
        help="Defines the path of jfrog artifacts.",
        type=str,
        default="main",
    )
    parser.add_argument(
        "--collect-logs",
        help="Collect various logs from SC and nodes.",
        action="store_true",
    )

    return parser.parse_args()


def set_root_logger(level: Union[int, str] = logging.DEBUG) -> None:
    """Set root logger.

    :param level: Log level. Defaults to debug.
    """
    global log_file_name

    formatter = logging.Formatter("[%(levelname)-8s] %(message)s")
    date_time = datetime.now().strftime("%m-%d-%Y-%H%M%S")
    log_file_name = f'{date_time}_one_click.log'

    logger = logging.getLogger()
    logger.setLevel(0)

    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setLevel(level)
    stream_handler.setFormatter(formatter)

    local_log_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), log_file_name)
    file_handler = logging.FileHandler(local_log_file)
    file_handler.setLevel(0)
    file_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)


def save_log_file() -> None:
    """Copy the complete one_click.log file to sitbdd staging log folder.
    """
    os.makedirs(os.path.join(config["staging"], config['log_folder']), exist_ok=True)

    local_log_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), log_file_name)
    log_folder_log_file = os.path.join(config["staging"], config['log_folder'], log_file_name)
    shutil.copy(local_log_file, log_folder_log_file)


def log_subprocess_run(subprocess_args: list, **popen_kwargs) -> Tuple[int, str, str]:
    """Run a subprocess and automatically log STDOUT and STDERR output.
    Do not use with keyword arguments "stdout", "stderr", "shell", and "text" (or "universal_newlines").
    These arguments are set by this function and are intentionally left in the popen_kwargs param
    in order to notify the user of overlapping arguments.
    Arguments "stdout" and "stderr" are always set to subprocess.PIPE.
    Argument "shell" is always set to True.
    Argument "text" (alternative to "universal_newlines") is always set to True.

    :param subprocess_args: Arguments to be used in subprocess.run().
    :param popen_kwargs: Keyword arguments to be used in subprocess.run(), same as Popen() kwargs.
    :return: Return subprocess.run() result value.
    """
    process = subprocess.Popen(
        subprocess_args,
        **popen_kwargs,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        text = True,
        shell = True,
    )

    stdout, stderr = process.communicate()
    return_code = process.wait()

    subprocess_name = " ".join(subprocess_args) if type(subprocess_args) == list else subprocess_args

    logging.debug(f'Logging lines from STDOUT of "{subprocess_name}":')
    for line in stdout.split('\n'):
        logging.debug(">\t" + line)

    logging.debug(f'Logging lines from STDERR of "{subprocess_name}":')
    for line in stderr.split('\n'):
        logging.debug(">\t" + line)

    return return_code, stdout, stderr


def pip_install_from_jfrog(package_name: str, version: str = None) -> int:
    """Install a Python package from jfrog using pip.

    :param package_name: Python package name.
    :param version: Python package version.
    :return: Return code from the installation.
    """
    package = package_name if version is None else (package_name+'=='+version)
    logging.info(f"Installing {package} with jfrog pip.")
    returncode, stdout, stderr = log_subprocess_run(['jfrog', 'pip', 'install', package])
    importlib.invalidate_caches()
    return returncode


def install_prerequisites() -> None:
    """ Installs needed python packages for sitbdd.
    """
    packages_list = ["wheel", "bs4", "lxml", "paramiko", "pywin32", "importlib_metadata", "paho_mqtt"]
    for package in packages_list:
        if pip_install_from_jfrog(package):
            logging.error(f"The package {package} was not installed successfully.")
            raise Exception("The installation of prerequisites was not successful.")


def get_local_ip() -> str:
    """Finds the local ip of the machine.

    :return: Returns local IP address from RADIO registry.
    """
    subkey = r"SOFTWARE\\WOW6432Node\\Radiant\\Radio"
    registry = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    try:
        key = winreg.OpenKeyEx(registry, subkey)
        value = winreg.QueryValueEx(key, "IPAddressTXT")
        if key:
            winreg.CloseKey(key)
        return value[0]
    except Exception as e:
        print(e)
    return None


def get_rcm_host_name() -> str:
    """ Finds rcm server host name in SiteServerConfig.xml
    """
    with open(config['nodes']['sc']["site_server_config"]) as file:
        server_config_file = file.read()

    soup = bs4.BeautifulSoup(server_config_file, "xml")

    rcm_is_linked = False
    for element in soup.find_all("HostContact"):
        if element.ContactName.string == "RCM":
            rcm_is_linked = True
            host_name = element.URLMsgReader.string.split("/")[2]
            return host_name.split(":")[0]

    if not rcm_is_linked:
        raise Exception('Element "RCM" does not exist in the SiteServerConfig.xml file.')


def get_installed_versions() -> Tuple[str, str]:
    """Finds installed versions of RPOS and Jag

    :return: RPOS version and Jag version
    """
    subkey = "SOFTWARE\\WOW6432Node\\Radiant\\Installed Products\\"
    registry = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)

    key = winreg.OpenKey(registry, subkey)

    rpos_version = None
    jag_version = None

    for i in range(0, winreg.QueryInfoKey(key)[0]):
        tmp_subkey = winreg.OpenKey(key, winreg.EnumKey(key, i))
        if (winreg.QueryValueEx(tmp_subkey, "FeatureName")[0].lower() == "Radiant POS".lower()):
            rpos_version = winreg.QueryValueEx(tmp_subkey, "InstalledVersion")[0]
        if (winreg.QueryValueEx(tmp_subkey, "FeatureName")[0].lower() == "Radiant Jag SDK".lower()):
            jag_version = winreg.QueryValueEx(tmp_subkey, "InstalledVersion")[0]

    return rpos_version, jag_version


def enable_bdd_config(args: argparse.Namespace, unattended_mode: bool = False) -> None:
    """Prepare bdd configuration for sitbdd (config.json).

    :param args: Temporarily it takes args for all product package versions
    :param unattended_mode: Parameter if the one_click is being run in unattended mode.
    """
    from sitbdd.config import Config
    global config

    config = Config(args.deployment)

    # in unattended_mode, the new config.user.json file will be always generated
    if os.path.exists(config.config_user_file) and not unattended_mode:
        user_input = input("Would you like to generate a new user config file? (y/[n]): ")
        if user_input != "y":
            return

    if os.path.exists(config.config_user_file):
        os.remove(config.config_user_file)

    rpos_version, jag_version = get_installed_versions()

    host = get_local_ip()
    ip_address = ".".join(host.split(".")[:-1])

    if not os.path.exists(config.config_file):
        raise FileNotFoundError(f"Config file {config.config_file} not found.")
    with open(config.config_file) as file: 
        config_bdd = json.load(file)

    config_bdd['nodes']['rcm']['server']['hostname'] = get_rcm_host_name()

    config_bdd['subnet'] = ip_address
    config_bdd['jfrog_packages']['rpos_version'] = rpos_version
    config_bdd['jfrog_packages']['rpos_path'] = "cfr-generic-group/rpos/" + args.jfrog_artifact_path.replace("release/", "")
    config_bdd['jfrog_packages']['jag_version'] = jag_version

    sc_ip = '.'.join([config_bdd['subnet'], config_bdd['nodes']['sc']['hostname_node']])
    http_sim = config_bdd['nodes']['sc']['hosts']['httpSimulator']
    http_sim = http_sim.replace('localhost', sc_ip)
    config_bdd['nodes']['sc']['hosts']['httpSimulator'] = http_sim

    site_server = config_bdd['nodes']['sc']['hosts']['siteServer']
    site_server = site_server.replace('localhost', sc_ip)
    config_bdd['nodes']['sc']['hosts']['siteServer'] = site_server

    dict_of_paths = site.getsitepackages()
    for path in dict_of_paths:
        if path.endswith('site-packages'):
            barcodes_path = config_bdd['nodes']['pos']['scan_sim']['scan_sim_barcodes']
            config_bdd['nodes']['pos']['scan_sim']['scan_sim_barcodes'] = os.path.join(path, barcodes_path)
            break

    # Adding versions to bdd_packages
    bdd_packages = []
    version = ""
    package = ""
    for package_name in config_bdd['jfrog_packages']['bdd_packages']:
        if package_name.lower() == "cfrpos":
            version = args.cfrpos_version if args.cfrpos_version else rpos_version
        elif package_name.lower() == "cfrsc":
            version = args.cfrsc_version if args.cfrsc_version else rpos_version
        elif package_name.lower() == "cfrrcmserver":
            version = args.cfrrcmserver_version
        elif package_name.lower() == "cfrfuelbdd":
            version = args.cfrfuelbdd_version if args.cfrfuelbdd_version else jag_version
        elif package_name.lower() == "cfrsmtaskman":
            version = args.cfrsmtaskman_version
        else:
            raise Exception(f"Unknown package name {package_name}")
        package = package_name.lower()+"=="+version
        bdd_packages.append(package)
    logging.info(f"Setting up versions of product packages: {bdd_packages}")
    config_bdd['jfrog_packages']['bdd_packages'] = bdd_packages

    with open(config.config_user_file, "w+") as file:
        json.dump(config_bdd, file, indent=2)

    config = Config(args.deployment)  # reload config to use freshly modified values


def uninstall_sit_bdd() -> None:
    """ Uninstalls sitbdd from the system.
    """
    logging.info(f"Uninstalling sitbdd with pip.")
    returncode, stdout, stderr = log_subprocess_run([sys.executable, "-m", "pip", "uninstall", "-y", "sitbdd"])
    if returncode:
        raise Exception("SIT BDD package was not uninstalled successfully.")


def install_sit_bdd_deployment(version: str = None) -> None:
    """ Install sitbdd for deployment provided a specific version.

    :param version: Version of the sitbdd package.
    """
    installed_version = get_installed_package_version("sitbdd")

    if version != installed_version or installed_version == None:
        if installed_version != None:
            uninstall_sit_bdd()
        if pip_install_from_jfrog("sitbdd", version):
            raise Exception("SIT BDD deployment package was not installed successfully.")


def install_sit_bdd_development() -> None:
    """ Install sitbdd package for development as editable.
    """
    package_path = os.path.join(os.getcwd())
    returncode, stdout, stderr = log_subprocess_run([sys.executable, '-m', 'pip', 'install', '--editable', package_path])
    importlib.invalidate_caches()
    if returncode:
        raise Exception("SIT BDD development package was not installed successfully.")

    # Extend path because path is not updated when the editable package is installed.
    if package_path not in sys.path:
        sys.path.append(package_path)


def update_jaglessjag() -> None:
    """ Updates SimPumpsJaglessJag.xml file on FC for simpumps to match our RCM settings.
    """
    logging.info('Setting up SimPumpsJaglessJag.xml file on SC.')
    config_name = config['nodes']['jag']['simpumps']['config_file_name']
    config_local_file = os.path.join(config['nodes']['jag']['simpumps']['config_file_location'], config_name)

    with open(config_local_file, "r") as file:
        config_local_file_opened = file.read()

    soup = bs4.BeautifulSoup(config_local_file_opened, "xml")

    if soup.find(string='Help'):
        return

    # find all the occurences and replace them with something else in the soup
    [string.replace_with('Diesel') for string in soup.find_all(string='Regular')]
    [string.replace_with('Regular') for string in soup.find_all(string='Plus')]
    [string.replace_with('Midgrade') for string in soup.find_all(string='Super')]
    [string.replace_with('Help') for string in soup.find_all(string='Fill Tank')]

    with open(config_local_file, "w") as file:
        file.write(str(soup))


def run_bddservices_on_jag() -> None:
    """ Deploys and runs BDDServices.exe on Jag node.
    """
    logging.info("Setting up Jag node.")
    bdd_services = "BDDServices.exe"
    jag_ip = ".".join([config['subnet'], config['nodes']['jag']['hostname_node']])
    staging_folder = config['staging']
    program_path = os.path.join(staging_folder, bdd_services)
    if not os.path.exists(program_path):
        raise FileNotFoundError(f"The file {program_path} does not exist.")
    action = f"New-ScheduledTaskAction -Execute '{program_path}'"
    trigger = "New-ScheduledTaskTrigger -AtLogOn"
    task = f'powershell.exe Register-ScheduledTask -Action ({action}) -Trigger ({trigger}) -TaskName {bdd_services.split(".")[0]}'
    registry_add_command = "reg add HKLM\\Software\\RadiantSystems\\Jag3 /reg:32 /v DiagnosticWeb /t REG_SZ /d True-ish /f"

    logging.info("Adding registry value on SC as it needs to be. (overrides the old one if there is already one)")
    returncode, stdout, stderr = log_subprocess_run(registry_add_command)
    if returncode:
        raise Exception("The command to add registry to Jag3 failed.")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(jag_ip, username='ansible', password='ansible')

    logging.info("Killing running BDDServices on Jag node, if needed.")
    exec_ssh_command(ssh, f'tasklist | find /i "{bdd_services}" && taskkill /im "{bdd_services}" /F || echo process "{bdd_services}" not running.')

    logging.info("Adding registry value on Jag to open ports for BDDServices. (overrides the old one if there is already one)")
    exec_ssh_command(ssh, registry_add_command)

    logging.info("Remove and create staging folder in Jag node")
    # Forced delete, if the folder is not there, the command fails, but the exec_command does not
    exec_ssh_command(ssh, f'rmdir "{staging_folder}" /s /q')
    exec_ssh_command(ssh, f'mkdir "{staging_folder}"')

    logging.info("Copy files to Jag node")
    ftp_client = ssh.open_sftp()
    ftp_client.put(program_path, program_path)
    ftp_client.close()

    logging.info(f"Adding BDDServices on Jag node to scheduled tasks.")
    exec_ssh_command(ssh, task)
    ssh.close()


def run_sims_on_pos() -> None:
    """ Deploys and runs print_sim and scan_sim on POS node.
    """
    logging.info("Setting up POS node.")
    pos_ip = ".".join([config['subnet'], config['nodes']['pos']['hostname_node']])
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(pos_ip, username='ansible', password='ansible')

    out, err, status_code = exec_ssh_command(ssh, f'jfrog pipc --server-id-resolve {SERVER_ID} --repo-resolve {REPOSITORY}')
    if status_code:
        raise Exception('Setting of repository on POS failed. Please check logs.')

    out, err, status_code = exec_ssh_command(ssh, 'pip install wheel')
    if status_code:
        raise Exception('Installation of wheel package on POS failed. Please check logs.')

    # Command to find path to folder site-packages, where the sim4cfrpos package is installed
    out, err, _status_code = exec_ssh_command(ssh, 'python -c "import site; print(site.getsitepackages())"')
    dict_of_paths = eval(out)
    sitepackages_path = ""
    for path in dict_of_paths:
        if path.endswith('site-packages'):
            sitepackages_path = path
            break
    rpos_version = config["jfrog_packages"]["rpos_version"]
    trigger = "New-ScheduledTaskTrigger -AtLogOn"

    for simulator in config['nodes']['pos']['simulators']:
        task_name = config['nodes']['pos']['simulators'][simulator]["task_name"]
        logging.info(f"Killing running {task_name} on POS node, if needed.")
        exec_ssh_command(ssh, f'tasklist | find /i "{task_name}" && taskkill /im "{task_name}" /F || echo process "{task_name}" not running.')

    # Install cfrpos with it's dependencies (including sim4cfrpos) on POS - sim4cfrpos is dependant on cfrpos anyway
    logging.info(f'Running command to install new cfrpos on POS node')
    out, err, status_code = exec_ssh_command(ssh, f'jfrog pip install cfrpos=={rpos_version}')

    for simulator in config['nodes']['pos']['simulators']:
        task_name = config['nodes']['pos']['simulators'][simulator]["task_name"]
        sim = os.path.join(sitepackages_path, f'sim4cfrpos\\runtime\\{simulator}\\app.py')
        sim_action = f"New-ScheduledTaskAction -Execute '{sim}' -Argument '--address {pos_ip} --bin_folder {DEFAULT_BIN_DIRECTORY}'"
        sim_task = f'powershell.exe Register-ScheduledTask -Action ({sim_action}) -Trigger ({trigger}) -TaskName {task_name}'
        logging.info(f"Adding {task_name} on POS node to scheduled tasks.")
        exec_ssh_command(ssh, sim_task)

    ssh.close()


def exec_ssh_command(ssh, command: str) -> Tuple[str, str, int]:
    """ Execute ssh command for paramiko

    :param paramiko.SSHClient ssh: Connected ssh client from paramiko.
    :param command: Command to execute in string form
    :return: Decoded stdout and stderr into a string
    """
    logging.debug(f"Executing command: {command}")
    (stdin, stdout, stderr) = ssh.exec_command(command)
    out = stdout.read().decode("utf-8")
    err = stderr.read().decode("utf-8")
    status_code = stdout.channel.recv_exit_status()
    if out:
        logging.debug(f'Logging lines from STDOUT of remotely executed ssh command "{command}":')
        for line in out.split('\n'):
            logging.debug(">\t" + line)
    if err:
        logging.debug(f'Logging lines from STDERR of remotely executed ssh command "{command}":')
        for line in err.split('\n'):
            logging.debug(">\t" + line)
    return out, err, status_code


def get_installed_packages() -> list:
    """ Calls pip freeze and returns all installed python packages and its versions.

    :return: Installed python packages
    """
    returncode, packages, stderr = log_subprocess_run('pip freeze')
    packages = packages.split('\n')
    return packages


def install_bdd_packages() -> None:
    """ Install all product packages used by SITBDD.
    """
    installed_packages = get_installed_packages()
    for package in config["jfrog_packages"]["bdd_packages"]:
        # the package with version is not listed in installed packages, e.g. 'cfrpos==2099.0.1.6368'
        if not package in installed_packages:
            # this, because cfrrcmserver==2099.2.2134 installs as cfrrcmserver==2099.2.2134.0
            if not package+".0" in installed_packages:
                if not uninstall_bdd_package(package):
                    raise Exception("Uninstallation of BDD packages failed.")
            if pip_install_from_jfrog(package):
                raise Exception(f"Package {package} was not installed successfully from jfrog repository.")
            continue
        logging.info(f"Correct version package {package} already installed.")


def uninstall_bdd_package(package_name: str) -> bool:
    """Uninstall all product packages used by SITBDD.
    :return: False if any uninstallation of some package was not successful, otherwise True.
    """
    logging.info(f"Uninstalling {package_name} with pip.")
    returncode, stdout, stderr = log_subprocess_run([sys.executable, "-m", "pip", "uninstall", "-y", package_name])
    if returncode:
        logging.error(f"Uninstallation of {package_name} was not successful. Uninstallation failed with code {returncode}")
        return False
    return True


def download_file_from_jfrog(file: str, jfrog_dest: str) -> bool:
    """ Download one file from jfrog. Function used in download_files_from_jfrog.

    :param file: File which is being downloaded from jfrog.
    :param jfrog_dest: Destination of the file in jfrog repository.
    :return: False if a file download was not successful, otherwise True.
    """
    local_file_name = file.split('/')[-1]
    local_file = os.path.join(config['staging'], local_file_name)
    logging.info(f"Downloading file: {local_file}")
    returncode, stdout, stderr = log_subprocess_run(['jfrog', 'rt', 'curl', '-XGET', jfrog_dest, '--output', local_file])
    if returncode:
        logging.error(f"The file {local_file_name} was not downloaded properly. The result code was {returncode}")
        return False
    # If the file is zip, extract it
    if local_file_name.endswith('.zip'):
        with zipfile.ZipFile(local_file) as zf:
            zf.extractall(config['staging'])
    return True


def download_files_from_jfrog() -> None:
    """ Download files from JFrog artifactory and puts them into defined staging folder.
        If the file is .zip file, it will extract it.
    """
    # removes all stuff in staging folder and cleans up
    if os.path.exists(config['staging']):
        for file_or_folder_name in os.listdir(config['staging']):
            full_path = os.path.join(config['staging'], file_or_folder_name)
            if file_or_folder_name != config['log_folder'].replace('/', ''):
                if os.path.isdir(full_path):
                    shutil.rmtree(full_path)
                if os.path.isfile(full_path):
                    os.remove(full_path)

    # Download files from RPOS artifactory
    for file in config['jfrog_packages']['rpos_artifacts']:
        jfrog_dest = '/'.join([config['jfrog_packages']['rpos_path'], config['jfrog_packages']['rpos_version'], file])
        if not download_file_from_jfrog(file, jfrog_dest):
            raise Exception(f"An error occured while downloading files from RPOS repository.")

    # Download files needed from Jag artifactory
    for file in config['jfrog_packages']['jag_artifacts']:
        jfrog_dest = '/'.join([config['jfrog_packages']['jag_path'], config['jfrog_packages']['jag_version'], file])
        if not download_file_from_jfrog(file, jfrog_dest):
            raise Exception(f"An error occured while downloading files from Jag repository.")


def run_enable_automation_script(unattended_mode: bool = False) -> None:
    """ Run the enable-automation script on the SC.

    :param unattended_mode: True/False if we want to skip user input.
    """
    user_input = ""
    if not unattended_mode:
        user_input = input("Would you like to run SC enable-automation script? ([y]/n): ")
    if user_input != "n" or unattended_mode:
        logging.info("Running SCBDD automation script...")
        # Getting cwd of the enable_automation as it needs to be run from the same dir as it is placed
        enable_automation_dir = os.path.join(config['staging'], '/'.join(config['enable_automation'].split('/')[:-1]))
        returncode, stdout, stderr = log_subprocess_run([os.path.join(config['staging'], config['enable_automation'])], cwd=enable_automation_dir)
        if returncode:
            raise Exception(f"The enable automation script failed with code {returncode}")
        logging.info("SCBDD automation script finished with success.")


def reboot_nodes() -> None:
    """ Reboot all nodes besides SC and RCM server.
    """
    logging.info("Restarting nodes to apply changes.")
    for key, value in config['nodes'].items():
        # excluding following nodes, as there is no need to reboot SC or RCM server
        if key in ["sc", "rcm", "eps_and_loyalty"]:
            continue
        node_ip = ".".join([config['subnet'], value['hostname_node']])
        reboot_node(node_ip, key)


def reboot_node(node_ip: str, node_name: str = None) -> None:
    """ Reboot node with given IP.

    :param node_ip: IP of the node
    :param node_name: Name of the node. ["CSS", "JAG", "KPS", "POS", "RCM", "SC"]
    """
    if node_name is None:
        node_name = node_ip
    logging.info(f"  -- restart node: {node_name}")
    returncode, stdout, stderr = log_subprocess_run(['powershell.exe', 'Restart-Computer', '-ComputerName', node_ip, '-Force'])
    if stderr:
        logging.warning(f"The node {node_name} is already rebooting.")


def run_bdd_script(function: str, unattended_mode: bool = False, feature: str = "", part: int = 0) -> None:
    """ Run run_bdd.py script provided a given function.

    :param unattended_mode: True/False if we want to skip user input.
    :param function: Function that will be ran from run_bdd.py. Either startapps, closeapps, restartapps, or behave.
    :param feature: Run specific feature only. If empty str is given, whole suite is executed. Use only with "behave" function.
    :param feature: Run specific part only. If not zero, this will override feature parameter. Use only with "behave" function.
    """
    import run_bdd
    run_bdd.set_module_logger()
    logging.getLogger("run_bdd").setLevel(logging.CRITICAL)

    match (function.lower()):
        case "startapps":
            run_bdd.start_apps(unattended_mode=unattended_mode)
        case "closeapps":
            run_bdd.close_apps()
        case "restartapps":
            run_bdd.close_apps()
            run_bdd.start_apps(unattended_mode=unattended_mode)
        case "behave":
            run_bdd.run_tests(feature=feature, part=part)


def configure_jfrog() -> None:
    """ Initialization steps to allow pip using Jfrog repository.
    """
    returncode, stdout, stderr = log_subprocess_run(['jfrog', 'pipc', '--server-id-resolve', SERVER_ID, '--repo-resolve', REPOSITORY])
    if returncode:
        raise Exception(f"The configuration of connection to jfrog repository was not successful.")


def get_radio_version_from_node(node_ip: str) -> str:
    """ Gets the version of Radio from the node.

    :param node_ip: IP of the node.
    :return: Version of Radio.
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(node_ip, username='ansible', password='ansible')
    # get installed software
    logging.debug(f"Executing \"psinfo -s\" on remote node with ip: {node_ip}")
    out, err, status_code = exec_ssh_command(ssh, 'psinfo -s')
    out = out.split('\r\n')
    for software in out:
        if software.startswith('Radio Host Service'):
            return software.split(' ')[-1]


def check_for_running_task_on_node(node_ip: str, task: str) -> bool:
    """ Checks if the task is running on the node.

    :param node_ip: Ip of the node.
    :param task: Task we are looking for.

    :return: If task is running or not.
    """
    logging.debug(f'Executing tasklist /S and looking for running "{task}" on remote node with ip: {node_ip}')
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(node_ip, username='ansible', password='ansible')

        out, err, status_code = exec_ssh_command(ssh, f'tasklist | find /i "{task}"')

        logging.debug(f'The task {task} was found running on node: {bool(out)}.')
        ssh.close()
        return bool(out)
    except Exception as e:
        logging.debug(f"Couldn't connect to node {node_ip}")
        logging.debug(e, exc_info=True)
        return False



def check_for_running_devman_on_node(node_ip: str) -> bool:
    """ Checks if the DevMan.exe is running on the node.

    :param node_ip: Ip of the node.

    :return: If devman.exe is running or not.
    """
    return check_for_running_task_on_node(node_ip, "devman.exe")


def check_for_running_security_service_on_node(node_ip: str) -> bool:
    """ Checks if the Ncr.SiteTrust.SecuritySer is running on the node.

    :param node_ip: Ip of the node.

    :return: If Ncr.SiteTrust.SecuritySer is running or not.
    """
    return check_for_running_task_on_node(node_ip, "Ncr.SiteTrust.SecuritySer")


def check_for_logged_on_node(node: str = None) -> Union[bool, list]:
    """ Checks if the node is logged on or not.

    :param node: Name of the node. ["CSS", "JAG", "KPS", "POS", "RCM", "SC"]
    :return: True if the node is logged on, false if not. If param Node is None, return list of logged on nodes.
    """
    online_nodes = []
    if node:
        node = node.upper()
    # check if node has logged in user with psloggedon
    returncode, stdout, stderr = log_subprocess_run('psloggedon -x ansible -nobanner')
    output = stdout.split('\n')
    for line in output:
        line = line.strip()
        # this works thanks to ansible user from SC being logged to every node remotely
        if "logged onto" in line and line.endswith("remotely."):
            if node:
                if node in line:
                    return True
            else:
                online_nodes.append(line.split(" ")[-2])
    if node:
        logging.debug(f"The node {node} is not logged on.")
        return False
    else:
        return online_nodes


def check_radio_version_on_node(node_ip: str, node_name: str, node_rebooted: bool, radio_version: str) -> Tuple[bool, str, bool]:
    """ Checks for radio version on the node.

    :param node_ip: Ip of the node
    :param node_name: Name of the node for logging
    :param node_rebooted: Flag if the node was already rebooted
    :param radio_version: Version of desired Radio version

    :return: Radio version is correct on the node, version of the Radio and flag if the node was already rebooted
    """
    node_radio_version = None
    # check for running security service just for sake of debugging/logging
    # security service needs to be running before devman
    # sometimes happen that security service does not start up and node does not start up (ever) 
    logging.debug(f"Check for runnning Security service on {node_name} node...")
    check_for_running_security_service_on_node(node_ip)
    # check for running devman on node
    logging.debug(f"Check for running devman on {node_name} node..")
    if check_for_running_devman_on_node(node_ip):
        logging.debug(f"Devman is running on {node_name} node!")
        node_radio_version = get_radio_version_from_node(node_ip)
        logging.debug(f"Got radio version {node_radio_version} on node {node_name}.")
        if not node_radio_version == radio_version and not node_rebooted:
            logging.debug(f"The {node_name} node does not have correct Radio version, rebooting {node_name} node to correct the version..")
            reboot_node(node_ip, node_name)
            node_rebooted = True
    return (node_radio_version == radio_version), node_radio_version, node_rebooted


def check_radio_versions(timeout: int = 3, attempts: int = 300) -> None:
    """ Checks if the POS and Jag have correct radio versions.

    :param timeout: Determines how long the cycle waits for another attempt.
    :param attempts: Number of attempts for the cycle.
    """
    logging.info("Checking radio versions on POS and Jag.")
    folder_files = os.listdir("C:\\Program Files\\Radiant\\Radio\\Rom")
    for file in folder_files: 
        if file.startswith("Radio_POS_"):
            radio_version = file.strip('.msi').split('_')[-1]

    pos_ip = ".".join([config['subnet'], config['nodes']['pos']['hostname_node']])
    jag_ip = ".".join([config['subnet'], config['nodes']['jag']['hostname_node']])

    pos_radio_is_correct = False
    pos_radio_version = ""
    pos_first_reboot = False
    pos_second_reboot = False
    jag_radio_is_correct = False
    jag_radio_version = ""
    jag_first_reboot = False
    jag_second_reboot = False
    success = False

    duration = attempts*timeout
    start_time = time.time()
    # while cycle to determine if POS or JAG nodes are logged on and have correct Radio version
    while(True):
        logging.info(f"Trying to get versions of Radio on nodes.. Passed {time.time()-start_time:.2f} seconds.")
        # check for POS node
        if not pos_radio_is_correct and check_for_logged_on_node("POS"):
            # POS is logged in, check running devman on POS
            pos_radio_is_correct, pos_radio_version_temp, pos_first_reboot = check_radio_version_on_node(pos_ip, "POS", pos_first_reboot, radio_version)
            pos_radio_version = pos_radio_version_temp if pos_radio_version_temp is not None else pos_radio_version
            if pos_radio_is_correct:
                logging.info(f"The POS node has correct Radio version. Success in {time.time()-start_time:.2f} seconds.")
            # sometimes happens, that the nodes do not boot up correctly for the first time, so we try second reboot in the middle of the duration
            if not pos_radio_is_correct and not pos_second_reboot and time.time()-start_time > duration/2:
                reboot_node(pos_ip, "POS")
                pos_second_reboot = True
        # check for Jag node
        if not jag_radio_is_correct and check_for_logged_on_node("JAG"):
            # JAG is logged in, check running devman on JAG 
            jag_radio_is_correct, jag_radio_version_temp, jag_first_reboot = check_radio_version_on_node(jag_ip, "JAG", jag_first_reboot, radio_version)
            jag_radio_version = jag_radio_version_temp if jag_radio_version_temp is not None else jag_radio_version
            if jag_radio_is_correct:
                logging.info(f"The Jag node has correct Radio version. Success in {time.time()-start_time:.2f} seconds.")
            # sometimes happens, that the nodes do not boot up correctly for the first time, so we try second reboot in the middle of the duration
            if not jag_radio_is_correct and not jag_second_reboot and time.time()-start_time > duration/2:
                reboot_node(jag_ip, "JAG")
                jag_second_reboot = True

        if pos_radio_is_correct and jag_radio_is_correct:
            logging.info(f"Updated Radio on nodes in {time.time()-start_time:.2f} seconds.")
            success = True
            break
        if time.time()-start_time > duration:
            break
        # wait timeout seconds before another try - nodes are rebooting
        time.sleep(timeout)

    if not success:
        logging.error(f"The Radio versions were not corrected in {duration} seconds.")
        if not pos_radio_is_correct:
            logging.error(f"The POS Radio version is not correct.")
            logging.error(f" - radio version: {radio_version}; POS radio version: {pos_radio_version}")
        if not jag_radio_is_correct:
            logging.error(f"The Jag Radio version is not correct.")
            logging.error(f" - radio version: {radio_version}; Jag radio version: {jag_radio_version}")
        raise Exception(f"Radio version is not correct on either POS or Jag after {duration} seconds. Please check logs.")


def get_logs_from_nodes() -> None:
    """ Collects various logs from SC, POS, and JAG.
    """
    system_logs_dir = os.path.join(config["staging"], config['log_folder'], config['system_logs'])
    if os.path.exists(system_logs_dir):
        shutil.rmtree(system_logs_dir)

    os.makedirs(os.path.join(system_logs_dir, "SC/Fastpoint"))
    os.makedirs(os.path.join(system_logs_dir, "SC/Support"))
    os.makedirs(os.path.join(system_logs_dir, "POS"))
    os.makedirs(os.path.join(system_logs_dir, "JAG"))

    # Collect logs from SC dir: C:/Program Files/Radiant/Fastpoint/Log
    get_logs_from_sc(config["fastpoint_logs"], os.path.join(system_logs_dir, "SC/Fastpoint"))

    # Collect logs from SC dir: C:/Support
    get_logs_from_sc(config["nodes"]["sc"]["support_dir"], os.path.join(system_logs_dir, "SC/Support"))

    # Collect logs from JAG and POS dir: C:/Program Files/Radiant/Fastpoint/Log
    pos_ip = ".".join([config['subnet'], config["nodes"]["pos"]['hostname_node']])
    jag_ip = ".".join([config['subnet'], config["nodes"]["jag"]['hostname_node']])
    node_ips = {"POS": pos_ip, "JAG": jag_ip}

    for node, ip in node_ips.items():
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username='ansible', password='ansible')
            sftp = ssh.open_sftp()
            get_logs_from_node(ip, config["fastpoint_logs"], os.path.join(system_logs_dir, node), sftp)
            ssh.close()
        except Exception as e:
            logging.debug(f"Couldn't connect to node {ip}")
            logging.debug(e, exc_info=True)


def get_logs_from_node(node_ip: str, remote_dir: str, local_dir: str, sftp) -> None:
    """ Collect logs from a provided node.

    :param node_ip: IP of node.
    :param remote_dir: Directory on target node to collect logs from.
    :param local_dir: Local directory to copy logs to.
    """
    files_list = sftp.listdir_attr(remote_dir)

    for entry in files_list:
        remote_path = os.path.join(remote_dir, entry.filename)
        local_path = os.path.join(local_dir, entry.filename)

        if S_ISDIR(entry.st_mode):
            os.makedirs(remote_path.replace(remote_dir, local_dir))
            get_logs_from_node(node_ip, remote_path, remote_path.replace(remote_dir, local_dir), sftp)
            continue

        logging.info(f"Copying '{remote_path}' from node {node_ip} to '{local_path}' on localhost.")
        sftp.get(remote_path, local_path)


def get_logs_from_sc(source_dir: str, dest_dir: str) -> None:
    """ Collect logs from source directory to a target directory on SC.

    :param source_dir: Directory to copy nodes from.
    :param dest_dir: Directory to copy nodes to.
    """
    for root, directories, files in os.walk(source_dir):
        for directory in directories:
            # Create any subdirectories at destination.
            dirpath = os.path.join(root, directory)
            os.makedirs(dirpath.replace(source_dir, dest_dir))
        for filename in files:
            # Join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            logging.info(f"Copying '{filepath}' to '{filepath.replace(source_dir, dest_dir)}'.")
            shutil.copyfile(filepath, filepath.replace(source_dir, dest_dir))


if __name__ == "__main__":
    args = parse_args()
    set_root_logger(level=logging.DEBUG if args.verbose else logging.INFO)

    exit_code = 0
    try:
        configure_jfrog()
        install_prerequisites()

        # importing installed prerequisites which are being used later in the one_click
        import bs4
        import paramiko
        logging.getLogger("paramiko").setLevel(logging.CRITICAL)
        from importlib_metadata import version

        if args.deployment:
            install_sit_bdd_deployment(args.sit_bdd_version)
        else:
            install_sit_bdd_development()
        # needs to be executed after sitbdd installation
        run_bdd_script("closeapps", unattended_mode=args.unattended_mode)

        enable_bdd_config(args, args.unattended_mode)

        # Create staging sitbdd folder
        os.makedirs(config["staging"], exist_ok=True)

        # Fuel package requires this environment variable for logging.
        temp = "TEMP"
        if os.getenv(temp) is None:
            os.environ[temp] = "./"

        install_bdd_packages()
        download_files_from_jfrog()

        run_enable_automation_script(args.unattended_mode)
        run_bddservices_on_jag()
        update_jaglessjag()
        run_sims_on_pos()
        reboot_nodes()

        check_radio_versions()

        logging.info("-----------------------------------------------")
        logging.info("SIT BDD provisioning was successfully completed.")
        logging.info("-----------------------------------------------")

        run_bdd_script("startapps", unattended_mode=args.unattended_mode)

        run_behave = args.run_behave
        if not args.unattended_mode and not args.run_behave:
            user_input = input("Would you like to run SIT BDD tests? ([y]/n): ")
            run_behave = False if user_input == "n" else True
        return_code = 0
        if run_behave:
            if args.part:
                logging.info(f"Runnning behave (part {args.part})")
            else:
                logging.info("Runnning behave (" + (args.feature if args.feature else "whole suite") + ")")
            return_code = run_bdd_script("behave", feature=args.feature, part=args.part)

        logging.debug(f"One_click returns code {return_code}")
        exit_code = return_code

    except Exception as exception:
        logging.error("An error occurred. One_click exiting with code 1")
        logging.error("One_click failed with exception:")
        logging.exception(exception)
        logging.debug(f"One_click returns code 1")
        exit_code = 1

    save_log_file()
    if args.collect_logs:
        get_logs_from_nodes()

    sys.exit(exit_code)
