#!/bin/sh
source /root/.bkrc
source /data/install/utils.fc
workon bkmonitorv3-monitor
./bin/manage.sh strategy_check $1 $2 $3 $4 $5 $6 $7 $8 $9 $10