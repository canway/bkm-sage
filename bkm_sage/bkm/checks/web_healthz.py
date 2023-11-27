import os
import subprocess
import sys

from bkm_sage.actuator import ActuatorContext, registry


def web_healthz(context: ActuatorContext):
    args = []
    for k, v in context.params.items():
        if v == "False":
            continue
        if v is not None:
            args.extend([f"-{k}", str(v)])
    cmd = (f"sh ./extend_tools/check_web_healthz.sh {' '.join(args)}",)
    print(f"Exec cmd: {cmd}")
    process = subprocess.Popen(cmd, shell=True, env={**dict(os.environ)})
    process.wait()

    exit_code = process.returncode
    print("Exit code:", exit_code)
    sys.exit(exit_code)


help = """
\b
远程执行(二进制环境）
    > # 连接监控后台服务器
    > ssh $BK_MONITORV3_MONITOR_IP
    > # 切换python环境
    > workon bkmonitorv3-monitor
    > # 使用工具
    > cd /data/bkee/bkmonitorv3/monitor
    > ./bin/manage.sh healthz
远程执行(容器化环境）
    # 连接中控机，通过kubectl查找alarm-alert的pod
    kubectl get pods -n blueking | grep bk-monitor-alarm-alert
        bk-monitor-alarm-alert-cc4db6cc-85kgc
        bk-monitor-alarm-alert-worker-58c946699d-hslw9
    # 进入pod(bk-monitor-alarm-alert)
    kubectl -n blueking exec bk-monitor-alarm-alert-cc4db6cc-85kgc -it -- bash
    # 使用工具
    python manage.py healthz

\b
将对默认模块进行检查：
    - Mysql Healthz
    - RabbitMQ Healthz
    - Redis Healthz
    - Kernel Service Healthz
    - Version Requirements Healthz
    - ElasticSearch Healthz
    - Function Healthz
    - Mysql Healthz
Mysql Healthz Check
    - 检查mysql后台数据库中空间占用Top10的表，单表大于 100G 或自增ID 大于180,000,000 时进行预警
RabbitMQ Healthz Check
    - 检查RabbitMQ队列情况，队列中消息数大于 10,000 时预警，其中 celery_service 队列阈值为 20,000 及 策略数*15 中的较大者
Redis Healthz Check
    - 检测Redis中evicted key数量，若持续增加则表明redis可能内存不足，产生预警
    - 根据info/memory计算内存使用率，根据内存使用率和内存碎片率判断是否需要预警
Kernel Service Healthz Check
    - 核心服务的检测
    - 检测策略数量，待检测信号队列( detect )和 trigger 信号队列是否拥堵，与策略检测相关;
    - 检测基础告警 GSE EVENT kafka 队列拉取是否延迟；
    - 检测 AlertPoller 告警拉取是否延迟；
    - 检测 cmdb 缓存任务和策略相关定时任务是否正常运行；
    - 检测 api 服务 pending 时间，超过2s进行预警；
    - 检测 fat_action 的 redis 队列是否堵塞，阈值100；
Version Requirements Check
    - 检查saas和backend版本
ElasticSearch Healthz Check
    - 检查 es 集群可用性
    - 检查 es 索引状态
    - 检查无别名的无效索引
    - 检查 fta 相关的索引状态
Nodeman legacy and wild subscription Check
    - 检测 nodeman 的野订阅数量
Transfer Healthz Check
    - 检测transfer消费kafka的offset；
    - 检测transfer数据drop情况
Function Healthz Check
    - 检测下发到每台 ping server 机器的Ping目标数量是否超出限制；
    - 检测实时监控topic消息是否堆积；
"""

registry.new_proxy_actuator(
    registry.with_proxy_option(
        name="web-healthz",
        help=help,
        params=[
            registry.with_param(name="t", default="False", type="string", help="检查后尝试自动修复问题"),
            registry.with_param(name="es", default="False", type="string", help="运行 elasticsearch 深入检查"),
            registry.with_param(
                name="transfer", default="False", type="string", help="运行 transfer 检查, 注意: 此项检查将耗时1分钟以上"
            ),
            registry.with_param(name="wild", default="False", type="string", help="运行 nodeman wild subscription 检查"),
        ],
        exec=web_healthz,
    )
)
