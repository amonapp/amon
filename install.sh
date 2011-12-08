#!/bin/sh

python setup.py install
sudo rm -rf amon.egg-info dist build 
sudo invoke-rc.d amond restart
sudo invoke-rc.d amon restart


