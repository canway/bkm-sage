#!/bin/sh
source /root/.bkrc
source /data/install/utils.fc
workon bkmonitorv3-monitor
./bin/manage.sh strategy_check $1 $2