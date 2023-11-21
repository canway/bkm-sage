from bkm_sage.actuator import registry

help = """
策略告警排障工具
"""

registry.new_actuator(
    registry.with_option(
        name="alarm-strategy_check",
        help=help,
    ),
)
