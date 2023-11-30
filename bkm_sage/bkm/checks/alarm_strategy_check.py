import os
import subprocess
import sys

from bkm_sage.actuator import ActuatorContext, registry


def alarm_strategy_check(context: ActuatorContext):
    args = []
    for k, v in context.params.items():
        if v == "False":
            continue
        if v is not None:
            args.extend([f"-{k}", str(v)])
    cmd = (f"sh ./extend_tools/alarm_strategy_check.sh {' '.join(args)}",)
    print(f"Exec cmd: {cmd}")
    process = subprocess.Popen(cmd, shell=True, env={**dict(os.environ)})
    process.wait()

    exit_code = process.returncode
    print("Exit code:", exit_code)
    sys.exit(exit_code)


help = """
\b
### 1.1 容器化版本
```shell
# 1.找出能执行命令的 pod
kubectl get pods -n blueking | grep monitor-alarm
# 2.进入 pod，执行命令，其中 strategy_id 为实际的策略 id
/app/venv/bin/python manage.py strategy_check -s strategy_id --from=start_time --until=end_time --filter=filter_args 
```
### 1.2 二进制版本
```shell
# 1.进入监控后台
ssh $BK_MONITORV3_MONITOR_IP
workon bkmonitorv3-monitor
# 2.执行命令
./bin/manage.sh strategy_check -s strategy_id --from=start_time --until=end_time --filter=filter_args
```

\b
返回数据分为以下几类：
    - Basic info on strategy
    - access pull
    - access handle
    - detect pull
    - detect handle
Basic info on strategy
    - 展示策略的基本信息，包括该策略当前的 group_key，拉取数据执行的查询语句
access pull
    - 经过传参的 filter 过滤维度数据之后，拉取的总数据，以及其中的一条示例
access handle
    - 对拉取的数据进行丰富和过滤，展示过滤后保留的数据记录，其中展示的示例是处理过后的数据内容
detect pull
    - 检测数据的拉取，数据与 access 输出的相似
detect handle
    - 检测出的异常点数量，注意的是，在 detect pull 和 detect handle 之间输出的是检测异常点过程中输出的内容
"""

registry.new_proxy_actuator(
    registry.with_proxy_option(
        name="alarm-strategy-check",
        help=help,
        params=[
            registry.with_param(name="s", type="string", help="需要检查的策略 ID"),
        ],
        exec=alarm_strategy_check,
        short_help="策略告警排障工具",
    )
)
