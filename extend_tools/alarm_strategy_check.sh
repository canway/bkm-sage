#!/bin/sh

if [ $1 = "-kube" ];then
  pod_name=$(kubectl get pods -n blueking | grep monitor-alarm-access | awk '$3 ~ /Running/ {print $1}' | head -1)
  echo "pod name is: $pod_name"
  echo "command is: kubectl exec -it $pod_name -n blueking -- /app/venv/bin/python manage.py strategy_check $2 $3 $4 $5 $6 $7 $8 $9 ${10} ${11}"
  kubectl exec -it $pod_name -n blueking -- /app/venv/bin/python manage.py strategy_check $2 $3 $4 $5 $6 $7 $8 $9 ${10} ${11}
else
  source /root/.bkrc
  source /data/install/utils.fc
  workon bkmonitorv3-monitor
  echo "command is：./bin/manage.sh strategy_check $1 $2 $3 $4 $5 $6 $7 $8 $9 ${10} ${11}"
  ./bin/manage.sh strategy_check $1 $2 $3 $4 $5 $6 $7 $8 $9 ${10} ${11}
fi