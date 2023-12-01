package define

import "time"

const (
	CfgKeyPidDir     = "path.pid"               // cfg pid key
	CfgKeySocketFile = "output.bkpipe.endpoint" // cfg socket file key
	CfgKeyLogDir     = "path.logs"              // cfg log dir
	CfgKeySubTask    = "bkmonitorbeat.include"  // cfg subTask key

	PidFileName = "bkmonitorbeat.pid" // pid file name

	CmdKeyBinary     = "binary"
	CmdKeyConf       = "conf"
	CmdKeyFilter     = "filter"
	CmdKeyFilterType = "filter_type"
	CmdKeyTaskType   = "task_type"
	CmdKeyTaskName   = "task_name"
	CmdKeyLogCount   = "count"

	CmdKeyBinaryDefault  = "/usr/local/gse2_paas3_dev/plugins/bin/bkmonitorbeat"
	CmdConfDefault       = "/usr/local/gse2_paas3_dev/plugins/etc/bkmonitorbeat.conf"
	CmdFilterDefault     = "ERROR"
	CmdFilterTypeDefault = "or"
	CmdTaskTypeDefault   = "nativeTask"
	CmdTaskNameDefault   = ""
	CmdLogCount          = 3

	CmdBinaryUsage     = `现网机器可执行文件 bkmonitorbeat 路径`
	CmdConfUsage       = `现网机器 bkmonitorbeat 配置文件路径`
	CmdFilterUsage     = `用于过滤现网 bkmonitorbeat 日志的 key，支持多个用','进行分割，严格区分大小写`
	CmdFilterTypeUsage = `过滤类型，可选值为 and、or、not、close，分别代表与 或 非 以及 关闭过滤`
	CmdTaskTypeUsage   = `测试类型
如果希望测试 bkmonitorbeat 原生任务，需要置为"nativeTask"
如果希望测试 bkmonitorbeat 自定义任务，需要置为"customTask"`
	CmdTaskNameUsage = `任务名称`
	CmdLogCountUsage = `扫描的日志文件数量 1-7`
)

type FileInfo struct {
	Name    string
	ModTime time.Time
}
