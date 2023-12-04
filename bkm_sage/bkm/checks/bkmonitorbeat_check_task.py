import os
import subprocess
import sys

from bkm_sage.actuator import ActuatorContext, registry

help = """
运行 bkmonitorbeat-check_task 指令将会生成配置文件副本并且拉起现网 bkmonitorbeat 可执行二进制文件进行采集任务检测。

\b
使用例子:
    bkmonitorbeat-check_task --binary /usr/local/gse/plugings/bin/bkmonitorbeat --conf /usr/local/gse/plugings/etc/bkmonitorbeat.conf --task.type nativeTask --task.name basereport_task
    此命令指定了现网的可执行的 bkmonitorbeat 二进制文件以及现网配置文件，并且指定测试的任务类型为 bkmonitorbeat 原生任务测试类型（写在bkmonitorbeat.conf中的任务即为原生任务），并且指定测试任务名为 basereport_task
    （注：检测原生采集任务 task.type 需要置为 nativeTask）

\b
    bkmonitorbeat-check_task --binary /usr/local/gse/plugings/bin/bkmonitorbeat --conf /usr/local/gse/plugings/etc/bkmonitorbeat.conf --task.type customTask --task.name test_task
    大致内容同上，此命令指定了可执行文件位置以及配置文件位置，并且额外指明测试任务类型为自定义任务类型（自定义任务类型为配置文件下发在 bkmonitorbeat 配置文件夹中的任务），并且指明自定义任务名为 test_task
    (注：自定义任务名为下发在 bkmonitorbeat 子配置文件夹中的 具体的配置文件内部的 name 字段的值)
"""

binary_default = "/usr/local/gse2_paas3_dev/plugins/bin/bkmonitorbeat"
conf_default = "/usr/local/gse2_paas3_dev/plugins/etc/bkmonitorbeat.conf"

binary_help = """
现网机器 bkmonitorbeat 可执行文件的路径，默认为 '/usr/local/gse2_paas3_dev/plugins/bin/bkmonitorbeat'
"""
conf_help = """
现网机器 bkmonitorbeat 配置文件相对路径，默认为 '/usr/local/gse2_paas3_dev/plugins/etc/bkmonitorbeat.conf'
"""

task_type_help = """
测试类型，如果希望测试 bkmonitorbeat 原生任务，需要置为"nativeTask"，如果希望测试 bkmonitorbeat 自定义任务，需要置为"customTask"
(default "nativeTask")
"""
task_name_help = """
所需检测的任务的名称
"""


def check_task(context: ActuatorContext):
    args = []
    for k, v in context.params.items():
        if v is not None:
            args.extend([f"--{str(k)}", str(v)])
    cmd = (f"./extend_tools/bkmonitorbeat_tool bkmonitorbeat-check_task {' '.join(args)}",)
    process = subprocess.Popen(cmd, shell=True, env={**dict(os.environ)})
    process.wait()
    exit_code = process.returncode
    print("Exit code:", exit_code)
    sys.exit(exit_code)


registry.new_proxy_actuator(
    option=registry.with_proxy_option(
        name="bkmonitorbeat-check-task",
        help=help,
        params=[
            registry.with_param("--binary", type="string", default=binary_default, help=binary_help),
            registry.with_param("--conf", type="string", default=conf_default, help=conf_help),
            registry.with_param("--task_type", type="string", default="nativeTask", help=task_type_help),
            registry.with_param("--task_name", type="string", required=True, help=task_name_help),
        ],
        exec=check_task,
        short_help="对 bkmonitorbeat 指定的采集任务进行检测",
    )
)
