from bkm_sage.actuator import registry

help = """
从目前环境信息检查 bkmonitorbeat 运行情况
"""

registry.new_actuator(
    registry.with_option(name="bkmonitorbeat-check_overall", help=help),
)
