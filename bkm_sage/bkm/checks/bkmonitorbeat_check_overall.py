import os
import subprocess
import sys

from bkm_sage.actuator import ActuatorContext, registry

help = """
该指令将会对现网的 bkmonitorbeat 进行快速检测。

检测内容包括进程、通信文件以及现网日志内容。

使用命令: 
  bkmonitorbeat-check_overall --conf ../etc/bkmonitorbeat.conf --filter "cpu"
  此命令将会对 bkmonitorbeat 进行快速检测，并且过滤日志，只输出有 cpu 的内容
"""
conf_help = """
现网机器 bkmonitorbeat 配置文件相对路径
"""
filter_help = """
用于过滤现网 bkmonitorbeat 日志的 key，支持多个用','进行分割，严格区分大小写
"""
filter_type_help = """
过滤类型，可选值为 and、or、not、close，分别代表与 或 非 以及 关闭过滤
"""


def check_overall(context: ActuatorContext):
    args = []
    for k, v in context.params.items():
        if v is not None:
            args.extend([f"--{str(k).replace('_','.')}", str(v)])
    cmd = (f"./extend_tools/bkmonitorbeat_tool bkmonitorbeat-check_overall {' '.join(args)}",)
    process = subprocess.Popen(cmd, shell=True, env={**dict(os.environ)})
    process.wait()
    exit_code = process.returncode
    print("Exit code:", exit_code)
    sys.exit(exit_code)


registry.new_proxy_actuator(
    option=registry.with_proxy_option(
        name="bkmonitorbeat-check_overall",
        help=help,
        params=[
            registry.with_param(name="conf", type="string", default="../etc/bkmonitorbeat.conf", help=conf_help),
            registry.with_param(name="filter", type="string", default="ERROR", help=filter_help),
            registry.with_param(name="filter_type", type="string", default="or", help=filter_type_help),
        ],
        exec=check_overall,
    )
)
