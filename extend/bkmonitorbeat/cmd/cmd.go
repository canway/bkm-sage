package cmd

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"
)

var RootCmd = &cobra.Command{
	Short: "bkmonitorbeat 排障工具",
	Long: `
bkmonitorbeat 排障工具主要用于 bkmonitorbeat 问题快速诊断、采集任务测试。`,
}

func Execute() {
	if err := RootCmd.Execute(); err != nil {
		fmt.Printf("start bkmonitor-datalink tool error: %s\n", err)
		os.Exit(1)
	}
}

func AddCommand(cmd *cobra.Command) {
	RootCmd.AddCommand(cmd)
}
