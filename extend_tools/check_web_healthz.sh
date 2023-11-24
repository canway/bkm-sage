#!/bin/sh
source /root/.bkrc
source /data/install/utils.fc
workon bkmonitorv3-monitor
./bin/manage.sh healthz $1 $2 $3 $4