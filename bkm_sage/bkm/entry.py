import bkm_sage.bkm.checks.alarm_strategy_check  # noqa
import bkm_sage.bkm.checks.bkmonitorbeat_check_overall  # noqa
import bkm_sage.bkm.checks.bkmonitorbeat_check_task  # noqa
import bkm_sage.bkm.checks.web_healthz  # noqa
from bkm_sage.actuator import registry
from bkm_sage.actuator.click_adapter import ActuatorRegistryClickAdapter

help = """
BKMoniotor 蓝鲸监控运维工具指令入口函数，BKMonitor 指令格式内容满足以下协议，通过 --help 查看指令详情

\b
- 规范指令名称 {module}-{opertor}，比如 web-health
- 声明执行环境，远程执行/本地执行，远程执行需要申明在哪个环境下执行，比如需要在 bk-monitor-web 工程目录下执行
- 声明参数含义，列举指令涉及的参数，参数如何传值，分别对应什么效果
- 声明检查内容，列举检查明细，便于使用者初步判断执行后的效果
"""

bkm = ActuatorRegistryClickAdapter(registry).to_group("bkm", help)
