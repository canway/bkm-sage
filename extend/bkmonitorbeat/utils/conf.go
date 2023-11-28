package utils

import (
	"bkmonitorbeat/define"
	"io"
	"os"
	"path/filepath"
	"strings"

	"github.com/fatih/color"
	"github.com/spf13/viper"
)

// GetViper 根据提供的路径获取 viper 对象, path 配置文件路径，cType 配置文件类型
func GetViper(path, cType string) *viper.Viper {
	c := "yaml"
	if cType != "" {
		c = cType
	}
	v := viper.New()
	v.SetConfigFile(path)
	v.SetConfigType(c)
	if err := v.ReadInConfig(); err != nil {
		color.Red("unable to read config file path: %s, error: %s\n", path, err)
		return nil
	}
	return v
}

// GenCopyFilePath 生成备份的文件路径 (兼容生成文件夹的备份路径)
func GenCopyFilePath(path string) string {
	base := filepath.Base(path)
	ext := filepath.Ext(path)
	dir := filepath.Dir(path)
	// 文件夹
	if ext == "" {
		return dir + "/" + base + "_copy"
	} else {
		fileName := base[:len(base)-len(ext)]
		return dir + "/" + fileName + "_copy" + ext
	}

}

const defaultJoinValue = "test"
const nativeTaskType = "nativeTask"
const customTaskType = "customTask"

// CreateCfgCopy 生成现网配置文件副本
func CreateCfgCopy(cfg, copyPath, taskType, taskName string) ([]string, bool) {
	var dataIds []string
	var sourceViper, destViper *viper.Viper
	var cfgFilterKeys = []string{"_task", "bkmonitorbeat.include", "output.bkpipe"}
	var cfgOutPutKeys = "logging.path,path.logs,path.pid,path.data"
	// 获取源配置文件viper
	if sourceViper = GetViper(cfg, ""); sourceViper == nil {
		color.Red("sourceViper is nil\n")
		return nil, false
	}
	// 过滤测试类型不符合预期的情况
	if taskType != nativeTaskType && taskType != customTaskType {
		color.Red("task_type does not meet expectations\n")
		return nil, false
	}
	// 创建配置文件空副本
	if _, err := os.Create(copyPath); err != nil {
		color.Red("unable to create copy file: %s, error: %s\n", copyPath, err)
		return nil, false
	}
	// 获取副本配置文件viper
	if destViper = GetViper(copyPath, ""); destViper == nil {
		color.Red("destViper is nil\n")
		return nil, false
	}
	// 先获取基础配置
	for _, key := range sourceViper.AllKeys() {
		var matched bool
		for _, filter := range cfgFilterKeys {
			if strings.Contains(key, filter) {
				matched = true
				break
			}
		}
		if !matched {
			// 修改作用于输出内容的 key
			if strings.Contains(cfgOutPutKeys, key) {
				destViper.Set(key, filepath.Join(sourceViper.GetString(key), defaultJoinValue))
			} else {
				destViper.Set(key, sourceViper.Get(key))
			}

		}
	}
	// 修改日志等级
	destViper.Set("logging.level", "debug")
	// 开始判定测试任务类型属于 nativeTask 还是 customTask
	if taskType == nativeTaskType {
		for _, key := range sourceViper.AllKeys() {
			if strings.Contains(key, taskName) {
				// key 组成格式  xxx.xxx
				// 修改检测周期为2秒，缩短任务执行时间
				t := strings.Split(key, ".")
				if t[len(t)-1] == "period" {
					destViper.Set(key, "2s")
				} else {
					destViper.Set(key, sourceViper.Get(key))
				}
				// 提取需要捕获的 dataid
				if strings.Contains(key, "dataid") {
					dataIds = append(dataIds, sourceViper.GetString(key))
				}
			}
		}
	}
	// 测试自定义任务的情况
	if taskType == customTaskType {
		// 测试类型 原生任务 自定义任务 二选一
		// 走到这里发现不存在自定义任务文件夹 则直接返回
		oriSubTaskDir := sourceViper.GetString(define.CfgKeySubTask)
		if oriSubTaskDir == "" {
			color.Yellow("unable to get custom task dir path!\n")
			return nil, false
		}
		copySubTaskDir := GenCopyFilePath(oriSubTaskDir)
		if copySubTaskDir == "" {
			color.Red("unable to generate copy custom dir path!\n")
			return nil, false
		}
		if err := os.Mkdir(copySubTaskDir, os.ModePerm); err != nil {
			color.Red("unable to create copy custom dir: %s, error: %s\n", copySubTaskDir, err)
			return nil, false
		}
		destViper.Set(define.CfgKeySubTask, copySubTaskDir)
		// 拷贝源自定义任务文件到副本文件夹中
		fileArry, err := os.ReadDir(oriSubTaskDir)
		if err != nil {
			color.Red("unable to read dir:%s, error: %s\n", oriSubTaskDir, err)
			return nil, false
		}
		var fNames []string
		for _, file := range fileArry {
			info, err := file.Info()
			if err != nil {
				color.Red("unable to get file info, name: %s, error: %s\n", file.Name(), err)
				continue
			}
			if !info.IsDir() {
				fNames = append(fNames, info.Name())
			}
		}
		for _, name := range fNames {
			source := filepath.Join(oriSubTaskDir, name)
			if v := GetViper(source, ""); v != nil && v.GetString("name") == taskName {
				dest := filepath.Join(copySubTaskDir, name)
				if CopyFile(source, dest) {
					dataIds = append(dataIds, v.GetString("dataid"))
				}
			}
		}
	}
	// 跟进 dataIds 判断是否正确生成了配置副本
	if len(dataIds) == 0 {
		return nil, false
	}
	// 对主配置文件进行保存
	err := destViper.WriteConfigAs(copyPath + ".yaml")
	if err != nil {
		color.Red("Error writing config file: %s", err)
		return nil, false
	}
	err = os.Rename(copyPath+".yaml", copyPath)
	if err != nil {
		color.Red("rename config file error: %s\n", err)
		return nil, false
	}
	// 弥补 Viper 无法仅设置 key 不设置 value 的情况
	f, err := os.OpenFile(copyPath, os.O_APPEND|os.O_WRONLY, 0666)
	if err != nil {
		color.Red("unable to open file")
		return nil, false
	}
	defer f.Close()
	_, err = f.WriteString("output.console:\n")
	if err != nil {
		color.Red("unable to write output.console, error:%s\n", err)
		return nil, false
	}
	// 对需要捕获的 dataIds 进行去重
	if len(dataIds) > 1 {
		dataIds = RemoveDuplicates(dataIds)
	}
	color.Green("Config file generate successfully")
	return dataIds, true
}

// CopyFile 将源文件拷贝到目标地址中
func CopyFile(source, dest string) bool {
	sourceFile, err := os.Open(source)
	if err != nil {
		color.Red("unable to open source file:%s, error:%s\n", source, err)
		return false
	}
	defer sourceFile.Close()

	destFile, err := os.Create(dest)
	if err != nil {
		color.Red("unable to create dest file:%s, error:%s\n", dest, err)
		return false
	}
	defer destFile.Close()
	_, err = io.Copy(destFile, sourceFile)
	if err != nil {
		color.Red("unable to copy file, source: %s, dest: %s, error: %s\n", sourceFile, destFile, err)
		return false
	}
	err = destFile.Sync()
	if err != nil {
		color.Red("unable to sync content to destFile, error: %s\n", err)
		return false
	}
	return true
}

func RemoveDuplicates(strs []string) []string {
	uniqueMap := make(map[string]interface{})
	var uniqueStrs []string

	for _, str := range strs {
		if _, ok := uniqueMap[str]; !ok {
			uniqueMap[str] = struct{}{}
			uniqueStrs = append(uniqueStrs, str)
		}
	}
	return uniqueStrs
}
