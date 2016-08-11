#!/usr/bin/python3

import sys
import subprocess
import time
import logging

os_package_managers = {}


def init_package_managers():
    os_package_managers["debian"] = ["sudo apt-get update",
                                     "sudo apt-get upgrade -y",
                                     "sudo apt-get autoremove -y",
                                     "sudo apt-get dist-upgrade -y",
                                     "sudo rpi-update"]
    os_package_managers["arch"] = ["pacman -Syu"]


def execute_cmd(cmds, logger):
    success = True
    for cmd in cmds:
        print(cmd)
        try:
            process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
            if error:
                logger.error("Update FAIL {}".format(error.decode('ascii')))
                success = False
                break
        except OSError as e:
            logger.error("OSError - {}".format(e))
            success = False
            break
    if success is True:
        logger.info("UPDATE SUCCESS")


def main():
    if len(sys.argv) != 1:
        raise Exception("Syntax: ./update.py")

    formatter = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(format=formatter, filename='/var/log/update_daemon',
                        level=logging.DEBUG)
    logger = logging.getLogger('UpdateDaemonLogger')
    init_package_managers()

    while True:
        execute_cmd(os_package_managers["debian"], logger)
        time.sleep(86400)


if __name__ == "__main__":
    main()
