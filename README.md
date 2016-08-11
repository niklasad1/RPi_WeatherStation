# Raspberry Pi 3 Weatherstation
This is project that uses a Raspberry Pi 3 with a SenseHat I/O card to measure
temperature, humidity and pressure every minute. It is written in python and
uses Mongo databases.

Every minute the temperature, humidity and pressure is written to a local
database which "volatile" and removed every day. Before the daily database is
removed every day the average temperature, humidity and pressure is calculated
and stored to another local database "non_volatile".
After average measurements have been stored these are transmitted to a third
database online that the website is using to report the measurements daily.

Also, the application also supports read out average temperatures via USB just
plug in a flash drive and it writes out the temperature in CSV file.

## Hardware Requirements
* Raspberry Pi 3
* Raspberry Pi Sense Hat  

## Software Requirements
* OS: RASPBIAN JESSIE Version: May 2016
* python2
* python3

## Installation Guides
See respective subfolders:
* RPi
* Website
