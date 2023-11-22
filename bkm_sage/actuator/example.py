import os
import subprocess
import sys

from bkm_sage.actuator import ActionState, ActuatorContext, registry
from bkm_sage.actuator.click_adapter import ActuatorRegistryClickAdapter


def example_action01(state: ActionState, context: ActuatorContext):
    state.log("Start exec aciton01 in example, {}".format(context))


def example_action02(state: ActionState, context: ActuatorContext):
    state.log("Start exec aciton02 in example, {}".format(context))
    raise Exception("Unexpected error ...")


def example_tool(context: ActuatorContext):
    args = []
    for k, v in context.params.items():
        if v is not None:
            args.extend([f"-{k}", str(v)])
    cmd = (f"sh ./extend_tools/example.sh {' '.join(args)}",)
    print(f"Exec cmd: {cmd}")
    process = subprocess.Popen(cmd, shell=True, env={**dict(os.environ)})
    process.wait()

    exit_code = process.returncode
    print("Exit code:", exit_code)
    sys.exit(exit_code)


# 声明普通 actuator 执行器，串联检查步骤
registry.new_actuator(
    option=registry.with_option(
        name="example-demo",
        help="这个是普通执行器样例指令",
        params=[registry.with_param(name="aa", type="int", help="整型的测试参数")],
        actions=[
            registry.with_action(
                name="example-action01",
                exec=example_action01,
            ),
            registry.with_action(
                name="example-action02",
                exec=example_action02,
            ),
        ],
    )
)

# 声明代理 actuator 执行器，调用脚本函数
registry.new_proxy_actuator(
    option=registry.with_proxy_option(
        name="example-tool",
        help="这个是代理执行器样例指令",
        params=[registry.with_param(name="aa", type="int", help="整型的测试参数")],
        exec=example_tool,
    )
)


if __name__ == "__main__":
    # 将注册的指令转换为 click 脚本，进行选择执行功能
    click_group = ActuatorRegistryClickAdapter(registry).to_group("bkm", "BKMonitor指令集合")
    click_group()

    # 直接执行 actuator
    # registry["example-demo"](aa=11)
