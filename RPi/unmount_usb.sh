#!/bin/bash
#decription     	: Unmount the device upon a UDEV event
#author		 				: Niklas Adolfsson
#date            	: 2016-07-30
#version         	: 1.0   
#usage		 				: bash "<path>"
#notes           	: N/A 
#arguments	    	: Path to the device e.g. /dev/sda1
#==============================================================================#!/bin/sh

logger "UNMOUNT USB"
umount $1
