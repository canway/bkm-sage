#!/bin/bash

# 为什么需要这个工具？
# 截止到 2024 年，celery 项目有个拖了6年多仍未解决的问题：https://github.com/celery/celery/issues/4185
# 分析的怀疑可能和某些内核特性相关，导致 IPC 通信异常，但是无法进一步修复，唯一可以确认的现象是，worker 卡死后不会消费队列
# 因此基于这个工具提供了一个规避的方案：
# 1. 通过 rabbitmq 的 api 获取特定的队列的消费者
# 2. 判断消费者的数量，如果数量降为 0，说明 worker 已经卡死
# 3. 通过 supervisorctl 重启 worker 对应的进程组
# 
# 为什么不使用 SIGHUP 来重启 worker？
# 曾经发现过一个现场无法通过发送 SIGHUP 来重启，所以使用 supervisorctl 来控制是最合适的方式

usage() {
    echo "Usage: $0 -h <host> -p <port> -u <username> -P <password> -g <groupname> -v <vhost> -q <queue> -S <supervisorctl> -c <config>" 1>&2;
    exit 1;
}

SCHEME=http
PORT=15672
USERNAME=admin
PID=1

while getopts ":h:p:u:P:g:v:q:s:S:c:" option
do
    case "${option}"
    in
        s)
            SCHEME=${OPTARG}
            ;;
        h)
            HOST=${OPTARG}
            ;;
        p)
            PORT=${OPTARG}
            ;;
        u)
            USERNAME=${OPTARG}
            ;;
        P) 
            PASSWORD=${OPTARG}
            ;;
        g)
            GROUP=${OPTARG}
            ;;
        v)
            VHOST=${OPTARG}
            ;;
        q)
            QUEUE=${OPTARG}
            ;;
        S)
            SUPERVISORCTL=${OPTARG}
            ;;
        c)
            CONFIG=${OPTARG}
            ;;
        *)
            usage
            ;;
    esac
done

is_queue_running() {
    set -e
    set -o pipefail

    # 使用 python 去除对 jq 的依赖
    consumers=$(curl --fail -s -u "${USERNAME}:${PASSWORD}" "${SCHEME}://${HOST}:${PORT}/api/queues/${VHOST}/${QUEUE}" | python -c "import json; print(json.loads(input())['consumers'])" 2>/dev/null)
    if [ "${consumers}" = 0 ]; then
        echo "ERROR: Queue ${QUEUE} in ${VHOST} has no consumers"
        return 2
    elif [ "${consumers}" = "" ]; then
        echo "CRITICAL: Cannot requet the api for ${QUEUE} in ${VHOST}"
        return 1
    else
        return 0
    fi
}

is_process_running() {
    if ${SUPERVISORCTL} -c "${CONFIG}" status "${GROUP}:*" | grep "RUNNING"; then
        return 0
    else
        return 1
    fi
}

if [ -z "${HOST}" ]; then
    echo "Error: You must provide Host"
    exit 1
elif [ -z "${GROUP}" ]; then
    echo "Error: You must provide Name"
    exit 1
elif [ -z "${PASSWORD}" ]; then
    echo "Error: You must provide Password"
    exit 1
elif [ -z "${VHOST}" ]; then
    echo "Error: You must provide VHost"
    exit 1
elif [ -z "${QUEUE}" ]; then
    echo "Error: You must provide Queue"
    exit 1
elif [ -z "${SUPERVISORCTL}" ]; then
    echo "Error: You must provide Supervisorctl path"
    exit 1
elif [ -z "${CONFIG}" ]; then
    echo "Error: You must provide Config path"
    exit 1
fi

# 判断进程是否在运行
if ! is_process_running; then
    echo "Process ${GROUP} is not running, exiting"
    exit 0
fi

# 判断队列是否在运行
if is_queue_running; then
    echo "Queue ${QUEUE} in ${VHOST} is running, exiting"
    exit 0
fi

# 重启进程
echo "Restarting group ${GROUP}"
${SUPERVISORCTL} -c "${CONFIG}" restart "${GROUP}:*"