from bkm_sage.actuator import registry

help = """
调试 bkmonitorbeat 单个任务的运行情况
"""

registry.new_actuator(
    registry.with_option(name="bkmonitorbeat-check_task", help=help),
)
