# Installation Guide

## Install Binaries
```bash
$ sudo apt-get update
$ sudo apt-get install sense-hat mongodb
$ sudo reboot
```

## Install Python Packages
```bash
pip install -r requirements.txt --user
```

## Configure External MongoDB
# enter your MongoDB credentials
$ vim ws_config.json


## Install WeatherStation Application
``` bash
$ sudo cp weatherstation /etc/init.d
$ sudo cp weather_station.py /usr/local/bin
$ sudo cp ws_config.json /etc/weatherstation
$ sudo update-rc.d weatherstation defaults
```

## Install USB udev rules
``` bash
$ sudo cp mount_usb_run.sh /usr/local/bin
$ sudo cp unmount_usb_run.sh /usr/local/bin
$ sudo cp usb.rules /etc/udev/rules.d/
$ sudo udevadm control --reload-rules && udevadm trigger
```

## Install automatic update script
```bash
$ sudo cp update.py /usr/local/update.py
$ sudo cp update_damon /etc/init.d
$ sudo update-rc.d update_daemon defaults
```
