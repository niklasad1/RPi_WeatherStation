#!/bin/bash
#decription     	: Mount the insert flash drive at /media/pi/test and send UDP
#                   packet to localhost:50000
#author		 				: Niklas Adolfsson
#date            	: 2016-07-30
#version         	: 1.0   
#usage		 				: bash mount_usb_run.sh "<path>"
#notes           	: N/A
#arguments    	  : path to device </dev/sda1>
#==============================================================================

mountpoint=/media/pi/test
logger "MOUNT USB $1 and read.py"
mount $1 $mountpoint
echo -n "READ_DB_TO_USB $mountpoint" > /dev/udp/127.0.0.1/50000
