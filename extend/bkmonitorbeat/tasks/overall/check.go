package overall

import (
	"bkmonitorbeat/cmd"
	"bkmonitorbeat/define"
	"fmt"

	"github.com/spf13/cobra"
)

func init() {
	// overall
	checkOverAllCmd.Flags().String(define.CmdKeyConf, define.CmdConfDefault, define.CmdConfUsage)                   // 配置文件地址
	checkOverAllCmd.Flags().String(define.CmdKeyFilter, define.CmdFilterDefault, define.CmdFilterUsage)             // 关键词过滤
	checkOverAllCmd.Flags().String(define.CmdKeyFilterType, define.CmdFilterTypeDefault, define.CmdFilterTypeUsage) // 关键词过滤关系
	checkOverAllCmd.Flags().Int(define.CmdKeyLogCount, define.CmdLogCount, define.CmdLogCountUsage)                 // 日志扫描的数量
	cmd.AddCommand(checkOverAllCmd)
}

const (
	short = `运行 bkmonitorbeat-check_overall 指令将会进入快速测试模式。`
	long  = `
bkmonitorbeat-check_overall 指令将会对现网的 bkmonitorbeat 进行快速检测。

检测内容包括进程、通信文件以及现网日志内容。

使用命令: 
  bkmonitorbeat-check_overall --conf /usr/local/gse/plugings/etc/bkmonitorbeat.conf --filter "cpu"
  此命令将会对 bkmonitorbeat 进行快速检测，并且过滤日志，只输出有 cpu 的内容

  bkmonitorbeat-check_overall --conf /usr/local/gse/plugings/etc/bkmonitorbeat.conf --filter "cpu,basereport"  --filter_type "and" 
  此命令将会对 bkmonitorbeat 进行快速检测，并且过滤日志，只输出既包含"cpu"又包含"basereport"的内容。
  `
)

var checkOverAllCmd = &cobra.Command{
	Use:   "bkmonitorbeat-check_overall",
	Short: short,
	Long:  long,
	Run: func(cmd *cobra.Command, args []string) {
		checkConf, err := cmd.Flags().GetString(define.CmdKeyConf)
		if err != nil {
			fmt.Printf("unable to get param conf, error: %s\n", err)
			return
		}
		filter, err := cmd.Flags().GetString(define.CmdKeyFilter)
		if err != nil {
			fmt.Printf("unable to get param filter, error: %s\n", err)
			return
		}
		filterType, err := cmd.Flags().GetString(define.CmdKeyFilterType)
		if err != nil {
			fmt.Printf("unable to get param filter.type, error: %s\n", err)
			return
		}
		logCount, err := cmd.Flags().GetInt(define.CmdKeyLogCount)
		if err != nil {
			fmt.Printf("unable to get param count, error: %s\n", err)
			return
		}
		Do(checkConf, filter, filterType, logCount)
	},
}
