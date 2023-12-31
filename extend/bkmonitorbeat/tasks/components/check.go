package components

import (
	"bkmonitorbeat/cmd"
	"bkmonitorbeat/define"
	"fmt"

	"github.com/spf13/cobra"
)

func init() {
	checkTaskCmd.Flags().String(define.CmdKeyBinary, define.CmdKeyBinaryDefault, define.CmdBinaryUsage)
	checkTaskCmd.Flags().String(define.CmdKeyConf, define.CmdConfDefault, define.CmdConfUsage)
	checkTaskCmd.Flags().String(define.CmdKeyTaskType, define.CmdTaskTypeDefault, define.CmdTaskTypeUsage)
	checkTaskCmd.Flags().String(define.CmdKeyTaskName, define.CmdTaskNameDefault, define.CmdTaskNameUsage)
	cmd.AddCommand(checkTaskCmd)
}

const (
	short = `运行 bkmonitorbeat-check_task 指令将会进入任务测试模式。`
	long  = `
该指令将会生成配置文件副本并且拉起现网 bkmonitorbeat 进程进行采集任务检测。

使用命令：
  bkmonitorbeat-check_task --binary /usr/local/gse/plugings/bin/bkmonitorbeat --conf /usr/local/gse/plugings/etc/bkmonitorbeat.conf --task_type nativeTask --task_name basereport_task
  此命令会测试现网的 bkmonitorbeat 的原生采集任务 basereport。（注：检测原生采集任务 task_type 需要置为 nativeTask）

  bkmonitorbeat-check_task --binary /usr/local/gse/plugings/bin/bkmonitorbeat --conf /usr/local/gse/plugings/etc/bkmonitorbeat.conf --task_type customTask --task_name script_name
  此命令会测试现网 bkmonitorbeat 的自定义采集任务。（注：task_type 此时应该置为 customTask，task_name 的值为自定义采集任务的配置文件中的 name 值）
`
)

var checkTaskCmd = &cobra.Command{
	Use:   "bkmonitorbeat-check_task",
	Short: short,
	Long:  long,
	Run: func(cmd *cobra.Command, args []string) {
		binary, err := cmd.Flags().GetString(define.CmdKeyBinary)
		if err != nil {
			fmt.Printf("unable to get param binary, error: %s\n", err)
			return
		}
		checkConf, err := cmd.Flags().GetString(define.CmdKeyConf)
		if err != nil {
			fmt.Printf("unable to get param conf, error: %s\n", err)
			return
		}
		taskType, err := cmd.Flags().GetString(define.CmdKeyTaskType)
		if err != nil {
			fmt.Printf("unable to get param task_type, error: %s\n", err)
			return
		}
		taskName, err := cmd.Flags().GetString(define.CmdKeyTaskName)
		if err != nil {
			fmt.Printf("unable to get param task_name, error: %s\n", err)
			return
		}
		fmt.Println(checkConf, taskType, taskName)
		// 执行组件测试
		Do(checkConf, taskType, taskName, binary)
	},
}
