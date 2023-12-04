# bkm-sage
蓝鲸监控运维工具集合，辅助检测服务健康以及问题定位

## 构建工具支持的运行环境（已测试验证）

构建机：Linux master-node 3.10.107-1-tlinux2_kvm_guest-0056 #1 SMP Wed Dec 29 14:35:09 CST 2021 x86_64 x86_64 x86_64 GNU/Linux

|系统版本|测试镜像|是否支持|
|--|--|--|
|centos|centos:latest|√|
|ubuntu|ubuntu:latest|镜像下载报错，未测试通过|
|debian|debian:latest|√|
|alpine|alpine:latest|测试失败，提示文件不存在|
|fedora|fedora:latest|还未测试|
|archlinux|alpinux:base|还未测试|

## 配置环境

项目使用 poetry 进行环境管理，默认 python3.10，建议使用 `python venv` 激活独立的虚拟环境

安装 poetry
```
curl -sSL https://install.python-poetry.org | python3 -
```

初始化依赖包
```
poetry install -E toolkit
```

如果提交代码，需要配置 pre-commit 进行代码格式化
```
pip3 install pre-commit
pre-commit install --allow-missing-config
pre-commit install --hook-type commit-msg --allow-missing-config
```

## sdk 使用方式

bkm.actuator 目录为通用的检查框架，可以独立出包，在监控其他服务模块中使用，直接执行 `python -m bkm_sage.actuator.example` 测试 SDK 效果，以下是输出内容

```bash
Usage: python -m bkm_sage.actuator.example [OPTIONS] COMMAND [ARGS]...

  BKMonitor指令集合

Options:
  --help  Show this message and exit.

Commands:
  example-demo  这个是普通执行器样例指令
  example-tool  这个是代理执行器样例指令
```

`bkm_sage/actuator/exampel.py` 代码演示了两种执行器以及两种执行方式


## 如何在工具集添加检查指令

直接执行 `python main.py` 查看效果，以下是输出内容

```bash
Usage: main.py [OPTIONS] COMMAND [ARGS]...

  BKMoniotor 蓝鲸监控运维工具指令入口函数，BKMonitor 指令格式内容满足以下协议，通过 --help 查看指令详情

  - 规范指令名称 {module}-{opertor}，比如 web-health
  - 声明执行环境，远程执行/本地执行，远程执行需要申明在哪个环境下执行，比如需要在 bk-monitor-web 工程目录下执行
  - 声明参数含义，列举指令涉及的参数，参数如何传值，分别对应什么效果
  - 声明检查内容，列举检查明细，便于使用者初步判断执行后的效果

Options:
  --help  Show this message and exit.

Commands:
  alarm-strategy_check         策略告警排障工具
  bkmonitorbeat-check_overall  从目前环境信息检查 bkmonitorbeat 运行情况
  bkmonitorbeat-check_task     调试 bkmonitorbeat 单个任务的运行情况
  web-healthz                  远程执行(二进制环境） > # 连接监控后台服务器 > ssh...
```

在 bkm_sage.bkm.checks 增加文件，按照 {module}_{opertor}.py 格式命名文件

以 bkmonitorbeat-check_overall 为例，演示最基础的注册信息，具体检查内容请参看 `bkm_sage/actuator/exampel.py` 样例
```
from bkm_sage.actuator import registry

help = """
从目前环境信息检查 bkmonitorbeat 运行情况
"""

registry.new_actuator(
    registry.with_option(name="bkmonitorbeat-check_overall", help=help),
)
```

在 bkm_sage.bkm.entry 文件中增加一行引用即可
```
import bkm_sage.bkm.checks.bkmonitorbeat_check_overall  # noqa
```


## 构建工具以及使用方式

构建 SDK，仅包含 actuator 代码和依赖包，便于在监控其他服务模块进行安装使用，生成 dist/bkm_sage-0.1.0.tar.gz，可上传 pypi 安转使用
```
make build-sdk
```

构建整个工具集 toolkit，包含所有代码、依赖包和指令，生成 dist/bkm_sage_toolkit-0.1.0.tar.gz，上传服务器解压，配合服务器环境使用，便于边改代码，边验证服务
```
make build-toolkit
```

构建独立可执行的二进制文件，生成 dist/bkm_sage_bundle-0.1.0.tar.gz，直接上传服务器解压就可以执行
```
make build-bundle
```

bundle 包目录包含入口脚本 bkm-sage 以及其他依赖的脚本资源，可通过 `chmod +x bkm-sage; ./bkm-sage` 查看指令列表
```
dist/bkm_sage_bundle-0.1.0
├── bkm-sage
└── extend_tools
    └── example.sh
```
