package components

import (
	"bkmonitorbeat/define"
	"bkmonitorbeat/utils"
	"bufio"
	"fmt"
	"os"
	"os/exec"
	"strings"
	"syscall"
	"time"

	"github.com/fatih/color"
)

// Do 组件测试功能入口
// taskType: 测试的任务类型 原生任务、自定义任务
// taskName: 测试的任务名
func Do(cfg, taskType, taskName string) {
	var copyPath string
	if copyPath = utils.GenCopyFilePath(cfg); copyPath == "" {
		return
	}
	defer releaseResource(copyPath)
	dataIds, ok := utils.CreateCfgCopy(cfg, copyPath, taskType, taskName)
	if !ok {
		return
	}
	color.Green("component task dataid is %+v\n", dataIds)
	cmd := exec.Command("./bkmonitorbeat", "-c", copyPath)
	stdout, err := cmd.StdoutPipe()
	if err != nil {
		color.Red("unable to band stdoutPipe: %s\n", err)
		return
	}
	scanner := bufio.NewScanner(stdout)
	if err = cmd.Start(); err != nil {
		color.Red("unable to start bkmonitorbeat subprocess, error: %s\n", err)
		return
	}
	logDir := utils.GetViper(copyPath, "").GetString("logging.path")
	color.Green("start bkmonitorbeat component %s test, max time out is 2 minute", taskName)
	color.Yellow("for more detail, you can check component test log dir:%s\n", logDir)
	c := make(chan interface{}, 1)
	// 监听指标输出
	go func() {
		defer close(c)
		matchMap := make(map[string]interface{})
		for scanner.Scan() {
			text := scanner.Text()
			for _, id := range dataIds {
				if strings.Contains(text, id) {
					fmt.Println(text)
					matchMap[id] = struct{}{}
				}
			}
			if len(matchMap) == len(dataIds) {
				c <- struct{}{}
				_ = cmd.Process.Signal(syscall.SIGINT)
			}
		}
	}()
	// 超时机制最大时长 2 分钟
	select {
	case <-time.After(2 * time.Minute):
		color.Red("Max time out! stopping the subprocess\n")
		_ = cmd.Process.Kill()
	case <-c:
		color.Green("subprocess finished!")
	}
}

func releaseResource(cfg string) {
	v := utils.GetViper(cfg, "")
	if v == nil {
		return
	}
	dataDir := v.GetString("path.data")
	if dataDir != "" {
		// 删除产生的 data 文件
		if err := os.RemoveAll(dataDir); err != nil {
			color.Red("unable to remove dir:%s, error: %s\n", dataDir, err)
			return
		}
	}
	subTaskDir := v.GetString(define.CfgKeySubTask)
	if subTaskDir != "" {
		if err := os.RemoveAll(subTaskDir); err != nil {
			color.Red("unable to remove dir:%s, error: %s\n", dataDir, err)
			return
		}
	}
	// 删除配置文件副本
	if err := os.RemoveAll(cfg); err != nil {
		color.Red("unable to remove config: %s, error: %s\n", cfg, err)
		return
	}
}
