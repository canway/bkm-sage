package overall

import (
	"bkmonitorbeat/define"
	"bkmonitorbeat/utils"

	"net"
	"os"
	"path/filepath"
	"sort"
	"strconv"
	"strings"

	"github.com/fatih/color"
	"github.com/shirou/gopsutil/v3/process"
	"github.com/spf13/viper"
)

func Do(cfg, filter, filterKey string) {
	var v *viper.Viper
	if v = utils.GetViper(cfg, ""); v == nil {
		return
	}
	// 检查现网 bkmonitorbeat 进程是否存在
	pidDir := v.GetString(define.CfgKeyPidDir)
	if pidDir != "" {
		pidFile := filepath.Join(pidDir, define.PidFileName)
		if f, err := os.ReadFile(pidFile); err == nil {
			pid := strings.TrimRight(string(f), "\n")
			checkPidProcess(pid)
		}
	} else {
		color.Red("unable to check bkmonitorbeat process is exists\n")
	}
	// 检查现网 bkmonitorbeat socketFile
	socketFile := v.GetString(define.CfgKeySocketFile)
	if socketFile != "" {
		checkDomainSocket(socketFile)
	} else {
		color.Red("unable to check bkmonitorbeat socket file\n")
	}
	// 进行日志检测
	logDir := v.GetString(define.CfgKeyLogDir)
	if logDir != "" {
		checkLog(logDir, filter, filterKey)
	} else {
		color.Red("unable to check bkmonitorbeat log file\n")
	}
}

// checkPidProcess 检查 pid 进程是否存在
func checkPidProcess(pid string) {
	// pid 为空的情况
	if pid == "" {
		color.Red("pid is empty, unable to check bkmonitorbeat process\n")
		return
	}
	// 尝试捕获特定 pid 的进程
	pid32, err := strconv.ParseInt(pid, 10, 32)
	if err != nil {
		color.Red("transform string pid to int32 error:%s \n", err)
		return
	}
	p, err := process.NewProcess(int32(pid32))
	if err != nil {
		color.Red("unable to newProcess, pid: %+v, error: %s\n", pid32, err)
		return
	}
	running, err := p.IsRunning()
	if err != nil {
		color.Red("unable to check process is running! error: %s\n", err)
		return
	}
	if running {
		color.Green("bkmonitorbeat process status is ok!")
		return
	} else {
		color.Yellow("bkmonitorbeat process may not running!")
		return
	}
}

// checkDomainSocket 尝试与给定的 socketFile 进行连接确保文件可用
func checkDomainSocket(socketFile string) {
	// 当 err != nil  的时候说明 DomainSocket 文件夹不存在或其他错误
	_, err := os.Stat(socketFile)
	if err != nil {
		color.Red("unable to get socket file:%s error: %s\n", socketFile, err)
		return
	}
	// 尝试通过 DomainSocket 文件建立连接
	conn, err := net.Dial("unix", socketFile)
	if err != nil {
		color.Red("unable to connect unix socket, error: %s\n", err)
		return
	}
	// 仅仅是尝试与 unix domain socket 文件建立连接测试，不进行读写操作
	defer conn.Close()
	color.Green("bkmonitorbeat unix domain socket status is ok!\n")
}

// checkLog 尝试扫描日志文件夹最近的文件的数据
func checkLog(logDir, filter, filterKey string) {
	files, err := os.ReadDir(logDir)
	// 无法读取文件夹的情况
	if err != nil {
		color.Red("unable to open log dir: %s, error: %s\n", logDir, err)
		return
	}

	logs := make([]define.FileInfo, 0)
	for _, file := range files {
		// 尝试获取所有 bkmonitorbeat 的日志文件
		if strings.Contains(file.Name(), "bkmonitorbeat") {
			fileInfo, err := file.Info()
			if err != nil {
				color.Yellow("unable to get file modify time: %s, error: %s\n", file.Name(), err)
				continue
			}
			logs = append(logs, define.FileInfo{
				Name:    fileInfo.Name(),
				ModTime: fileInfo.ModTime(),
			})
		}
	}
	// 日志文件不存在则不继续
	if len(logs) == 0 {
		color.Red("logDir: %s is empty\n", logDir)
		return
	}

	sort.Slice(logs, func(i, j int) bool {
		return logs[i].ModTime.After(logs[j].ModTime)
	})

	// 仅取最近的三份日志数据
	for i := 0; i < 3 && i < len(logs); i++ {
		logPath := filepath.Join(logDir, logs[i].Name)
		utils.ScanLogFile(logPath, filter, filterKey)
	}
}
