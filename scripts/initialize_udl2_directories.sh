#!/bin/sh

echo "make option directory"
sudo mkdir -p /opt/wgen/edware-udl/etc
# we need to fix permission later not to own by root by udl app user
sudo chmod 755 /opt/wgen
sudo chmod 755 /opt/wgen/edware-udl
sudo chmod 777 /opt/wgen/edware-udl/etc

echo "make log directory"
sudo mkdir -p /var/log/wgen/edware-udl/logs
# we need to fix permission later not to own by root by udl app user
sudo chmod 755 /var/log/
sudo chmod 755 /var/log/wgen
sudo chmod 755 /var/log/wgen/edware-udl/
sudo chmod 777 /var/log/wgen/edware-udl/logs

echo "make zones directory"
sudo mkdir -p /opt/wgen/edware-udl/zones/
sudo mkdir -p /opt/wgen/edware-udl/zones/landing
sudo mkdir -p /opt/wgen/edware-udl/zones/work
sudo mkdir -p /opt/wgen/edware-udl/zones/history
sudo mkdir -p /opt/wgen/edware-udl/zones/datafiles
# we need to fix permission later not to own by root by udl app user
sudo chmod 777 /opt/wgen/edware-udl/zones
sudo chmod 777 /opt/wgen/edware-udl/zones/landing
sudo chmod 777 /opt/wgen/edware-udl/zones/work
sudo chmod 777 /opt/wgen/edware-udl/zones/history
sudo chmod 777 /opt/wgen/edware-udl/zones/datafiles
