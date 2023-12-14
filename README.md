# bkm-sage
蓝鲸监控运维工具集合，辅助检测服务健康以及问题定位


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

导出帮助文档至 doc 目录
```
make dumps-wiki
```

bundle 包目录包含入口脚本 bkm-sage 以及其他依赖的脚本资源，可通过 `chmod +x bkm-sage; ./bkm-sage` 查看指令列表
```
dist/bkm_sage_bundle-0.1.0
├── bkm-sage
└── extend_tools
    └── example.sh
```

## 工具跨平台支持情况

工具是使用 [pyinstaller](https://github.com/pyinstaller/pyinstaller) 方案来编译生成 python 的可执行文件，pyinsataller 会读取用户编写的 python 代码，扫描发现所有依赖包，然后将这些源文件和 python 解释器一起打包成一个文件包或者一个可执行文件。

> PyInstaller is tested against Windows, macOS, and GNU/Linux. However, it is not a cross-compiler: to make a Windows app you run PyInstaller in Windows; to make a GNU/Linux app you run it in GNU/Linux, etc. PyInstaller has been used successfully with AIX, Solaris, FreeBSD and OpenBSD, but is not tested against them as part of the continuous integration tests.
> 
> Requirements and Tested Platforms
> 
> - Python:
>   - 3.8-3.12. Note that Python 3.10.0 contains a bug making it unsupportable by PyInstaller. PyInstaller will also not work with beta releases of Python 3.13.
> 
> - Windows (32bit/64bit/ARM64):
>   - PyInstaller should work on Windows 7 or newer, but we only officially support Windows 8+.
>   - Support for Python installed from the Windows store without using virtual environments requires PyInstaller 4.4 or later.
> 
> - Linux:
>   - GNU libc based distributions on architectures x86_64, aarch64, i686, ppc64le, s390x.
>   - musl libc based distributions on architectures x86_64, aarch64.
>   - ldd: Console application to print the shared libraries required by each program or shared library. This typically can be found in the distribution-package glibc or libc-bin.
>   - objdump: Console application to display information from object files. This typically can be found in the distribution-package binutils.
>   - objcopy: Console application to copy and translate object files. This typically can be found in the distribution-package binutils, too.
>   - Raspberry Pi users on armv5-armv7 should add piwheels as an extra index url then pip install pyinstaller as usual.
> 
> - macOS (x86_64 or arm64):
>   - macOS 10.15 (Catalina) or newer.
>   - Supports building universal2 applications provided that your installation of Python and all your dependencies are also compiled universal2.

`PyInstaller` 不支持跨平台编译构建，需要用户自行在目标架构建机上编译对应架构下的工具产物（可执行文件）。目前主流的平台组合方案基本都能测试覆盖，部分较为少见架构和系统未测试完全。
- Windows (32bit/64bit/ARM64)
- Linux (x86_64/aarch64/i686/ppc64le/s390x * GNUlibc/musllibc)
- macOS (x86_64/arm64)

那么如何判定构建的工具是否可以在目标平台上执行呢？只要保障构建平台与执行平台一致即可，可以从以下三个维度进行判定
- 操作系统是否一致（window/linux/macOS）
- 指令架构是否一致（以 linux 为例，x86_64, aarch64, i686, ppc64le, s390x）
- 核心C库是否一致（以 linux 为例，有 GNU libc, musl libc）

bkm-sage 以 `x86_64 GNU/Linux` 构建机（3.10.107-1-tlinux2_kvm_guest-0056）进行编译，交付工具，使用 `docker` 验证工具在统一架构平台不同发行商的操作系统下是否可正常执行，测试指令如下
```
# 启动不同版本的镜像进行测试
docker run -v ${PROJECT_ROOT}/dist:/dist -it auchida/centos:latest /bin/bash
docker run -v ${PROJECT_ROOT}/dist:/dist -it auchida/debian:latest /bin/bash
docker run -v ${PROJECT_ROOT}/dist:/dist -it auchida/alpine:latest /bin/sh

# 执行挂载的脚本
cd /dist/bkm_sage_bundle-0.1.0/
./bkm-sage
```

以下是测试结果

|操作系统|测试镜像|是否可执行|
|--|--|--|
|centos|centos:latest|√|
|debian|debian:latest|√|
|alpine|alpine:latest|出现 syntax error 语法报错|
