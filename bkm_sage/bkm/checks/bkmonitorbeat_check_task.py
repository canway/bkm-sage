import os
import subprocess
import sys

from bkm_sage.actuator import ActuatorContext, registry

help = """

该指令将会生成配置文件副本并且拉起现网 bkmonitorbeat 进程进行采集任务检测。

使用命令：
  bkmonitorbeat-check_task --conf ../etc/bkmonitorbeat.conf --task.type nativeTask --task.name basereport_task
  此命令会测试现网的 bkmonitorbeat 的原生采集任务 basereport。（注：检测原生采集任务 task.type 需要置为 nativeTask）

  bkmonitorbeat-check_task --conf ../etc/bkmonitorbeat.conf --task.type customTask --task.name script_name
  此命令会测试现网 bkmonitorbeat 的自定义采集任务。（注：task.type 此时应该置为 customTask，task.name 的值为自定义采集任务的配置文件中的 name 值）
"""
binary_help = """
现网机器 bkmonitorbeat 可执行文件的路径，默认为 './bkmonitorbeat'
"""
conf_help = """
现网机器 bkmonitorbeat 配置文件相对路径，默认为 '../etc/bkmonitorbeat.conf'
"""
task_type_help = """
测试类型
如果希望测试 bkmonitorbeat 原生任务，需要置为"nativeTask"
如果希望测试 bkmonitorbeat 自定义任务，需要置为"customTask" (default "nativeTask")
"""
task_name_help = """
所需检测的任务的名称
"""


def check_task(context: ActuatorContext):
    args = []
    for k, v in context.params.items():
        if v is not None:
            args.extend([f"--{str(k).replace('_','.')}", str(v)])
    cmd = (f"./extend_tools/bkmonitorbeat_tool bkmonitorbeat-check_task {' '.join(args)}",)
    process = subprocess.Popen(cmd, shell=True, env={**dict(os.environ)})
    process.wait()
    exit_code = process.returncode
    print("Exit code:", exit_code)
    sys.exit(exit_code)


registry.new_proxy_actuator(
    option=registry.with_proxy_option(
        name="bkmonitorbeat-check_task",
        help=help,
        params=[
            registry.with_param(name="binary", type="string", default="./bkmonitorbeat", help=binary_help),
            registry.with_param(name="conf", type="string", default="../etc/bkmonitorbeat.conf", help=conf_help),
            registry.with_param(name="task_type", type="string", default="nativeTask", help=task_type_help),
            registry.with_param(name="task_name", type="string", default="", help=task_name_help),
        ],
        exec=check_task,
    )
)
