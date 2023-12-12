#!/bin/sh

if [ $1 = "-kube" ];then
  pod_name=$(kubectl get pods -n blueking | grep monitor-alarm-access | awk '$3 ~ /Running/ {print $1}' | head -1)
  kubectl exec -it $pod_name -n blueking -- /app/venv/bin/python manage.py healthz $2 $3 $4 $5
else
  source /root/.bkrc
  source /data/install/utils.fc
  workon bkmonitorv3-monitor
  ./bin/manage.sh healthz $1 $2 $3 $4
fi