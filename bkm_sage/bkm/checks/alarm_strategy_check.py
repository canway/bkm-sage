import os
import subprocess
import sys

from bkm_sage.actuator import ActuatorContext, registry


def alarm_strategy_check(context: ActuatorContext):
    args = []
    is_kube = False
    for k, v in context.params.items():
        if v is None:
            continue
        if k == "kube":
            is_kube = True
            continue
        if k == "s":
            args.extend([f"-{k}", str(v)])
        else:
            args.extend([f"--{k}", str(v)])
    cmd = (f"sh ./extend_tools/alarm_strategy_check.sh {'-kube' if is_kube else ''} {' '.join(args)}",)
    print(f"Exec cmd: {cmd}")
    process = subprocess.Popen(cmd, shell=True, env={**dict(os.environ)})
    process.wait()

    exit_code = process.returncode
    print("Exit code:", exit_code)
    sys.exit(exit_code)


help = """
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
    
\b
使用例子:
    ./bkm-sage alarm-strategy-check -s=123 --from=1653056280 --until=1653056280 --filter=bk_host_id:2,bk_cloud_id=0 --max=5
"""

registry.new_proxy_actuator(
    registry.with_proxy_option(
        name="alarm-strategy-check",
        help=help,
        params=[
            registry.with_param("-kube", type="string", is_flag=True, help="是否为 kubernetes 环境"),
            registry.with_param("-s", type="string", help="需要检查的策略ID", required=True),
            registry.with_param("--from", type="string", help="数据拉取时间范围起始点，不填默认最近五分钟，例子：1653056040"),
            registry.with_param("--until", type="string", help="数据拉取时间范围结束点，不填默认最近五分钟，例子：1653056280"),
            registry.with_param("--filter", type="string", help="输入过滤数据条件格式： k:v,k1:v1, 暂不支持过滤值中带有逗号的情况"),
            registry.with_param("--max", type="int", help="最大显示 detect debug 数据的数量，不填默认显示 10条"),
        ],
        exec=alarm_strategy_check,
        short_help="对策略无告警进行检测",
    )
)
