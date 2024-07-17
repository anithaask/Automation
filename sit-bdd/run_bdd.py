import argparse
import logging
import os
import subprocess
import sys
import time
import json
from win32.lib import win32serviceutil
from datetime import datetime
from typing import Union

from sitbdd.config import Config

config = Config()
logger = None

def parse_args() -> argparse.Namespace:
    """Parse arguments to file.

    :return: Arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--run",
        help="Defines what the program will do.",
        choices=['startapps', 'closeapps', 'restartapps', 'behave'],
        type=str,
        default=None
    )
    parser.add_argument(
        "-u",
        "--unattended-mode",
        help="Serves for the script to be able to run in unattended mode. True/False",
        action="store_true"
    )
    parser.add_argument(
        "--feature",
        help="Serves for run-behave, if we want to run some specific feature file only e.g. 'BasicTest.feature'. Runs all by default.",
        type=str,
        default=""
    )
    parser.add_argument(
        "--part",
        help="Serves for run-behave, if we want to run the suite in parts. A simple integer, works in cooperation with parts.json",
        choices=[1, 2, 3],
        type=int,
        default=None,
    )
    parser.add_argument(
        "-t",
        "--tags",
        help="Adds tags to existing tags. Use the tags without @, eg \"--tags fast custom_tag smoke\" ",
        nargs='*',
        default=[]
    )
    return parser.parse_args()


def set_module_logger(level: Union[int, str] = logging.DEBUG) -> None:
    """Set root logger.

    :param level: Log level. Default level is set to debug.
    """
    global logger
    formatter = logging.Formatter("[%(levelname)-8s] %(message)s")

    logger = logging.getLogger("run_bdd")
    logger.handlers.clear()
    logger.setLevel(level)

    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setLevel(level)
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)


def close_apps():
    """Closes running applications according to their window title names.
    """
    logger.info("Closing running applications...")
    for window_name in config['prereq_windowtitles']:
        subprocess.run(['taskkill', '/f', '/fi', f'WINDOWTITLE eq {window_name}'], stdout=subprocess.DEVNULL)
    logger.info("All applications have been closed, process can proceed")


def start_apps(unattended_mode: bool = False):
    """Runs prerequisite applications.

    :param unattended_mode: If the start_apps are running in unattended mode. True/False
    """
    user_input = ""
    if not unattended_mode:
        user_input = input("Would you like to start all SIT BDD prerequisites? ([y]/n): ")
    if user_input == "n":
        return

    logger.info("Starting apps...")
    os.chdir(config["staging"])

    # Start services if they are not already running.
    for service in config['prereq_services']:
        if win32serviceutil.QueryServiceStatus(service)[1] == 1:
            win32serviceutil.StartService(service)

    # Start up executables.
    for executable in config['executables']:
        logger.info(f'Starting executable: {os.path.join(config["staging"], executable)}')
        os.startfile(os.path.join(config["staging"], executable))

    # Start up python programs.
    logger.info("Giving prerequisites time to start...")
    time.sleep(5)
    logger.info("Prerequisites are ready!")
    if not unattended_mode:
        input("Press Enter to continue...")


def run_tests(feature: str = "", tags: list = [], part: int = 0) -> int:
    """ Run behave on not wip or manual scenarios and features.

    :param feature: Name of the feature what we want to run. If empty str is given, the whole suite is executed.
    :param tags: List of tags, which we want to append to existing ones.
    :param part: Part of suite which we want to run. If not zero, this will override feature paramater.
    :return: Return code of subprocess Popen
    """
    date_time = datetime.now().strftime("%m-%d-%Y-%H%M%S")
    if part:
        log_file_name = f'{date_time}_part_{part}.log'
    elif feature:
        feature_name = feature
        if feature.endswith(".feature"):
            feature_name = feature.split('.')[0]
        log_file_name = f'{date_time}_{feature_name}.log'
    else:
        log_file_name = f'{date_time}_behave_all.log'
    log_folder_log_file = os.path.join(config["staging"], config['log_folder'], log_file_name)

    junit_log = os.path.join(config['staging'], config['log_folder'], 'junit')
    behave_args = [
        'behave',
        '--tags=~@manual', '--tags=~@waitingforfix', '--tags=~@wip',
        '-k',  # skip output of skipped scenarios
        '--junit',
        '--junit-directory', junit_log
    ]
    if tags:
        for tag in tags:
            behave_args.append("--tags=@"+tag)
    if part:
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "parts.json"), "r") as file:
            parts = json.load(file)
            # Behave matches feature names against a regular expression pattern
            inclusion_pattern = "(" + "|".join(parts[part-1]) + ")"
            behave_args.append("-i")
            behave_args.append(f'{inclusion_pattern}')
    elif feature:
        behave_args.append('-i')
        behave_args.append(feature)
    import sitbdd
    cwd = os.path.dirname(sitbdd.__file__)
    logger.info("Running behave.")
    logger.info(f"-- \"{' '.join(behave_args)}\".")

    os.makedirs(os.path.join(config["staging"], config['log_folder']), exist_ok=True)
    with open(log_folder_log_file, "w+") as file_out:
        process = subprocess.Popen(
            behave_args,
            cwd = cwd,
            shell = False,
            text = True,
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT
        )
        for line in process.stdout:
            sys.stdout.write(line)
            file_out.write(line)
        return_code = process.wait()
    if return_code:
        logger.warning(f"Behave did not run successfully.\n"\
                        f"Please check behave log '{log_folder_log_file}' and junit logs '{junit_log}'")
    return return_code


def main():
    set_module_logger()
    args = parse_args()

    if args.run:
        match (args.run.lower()):
            case "startapps":
                start_apps(args.unattended_mode)
            case "closeapps":
                close_apps()
            case "restartapps":
                close_apps()
                start_apps(args.unattended_mode)
            case "behave":
                run_tests(feature=args.feature, tags=args.tags, part=args.part)

    else:
        # No args are provided which mean user double-clicked script, restart apps in unattended mode.
        close_apps()
        start_apps(True)

if __name__ == "__main__":
    main()
