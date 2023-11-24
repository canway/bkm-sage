package utils

import (
	"bufio"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"os"
	"strings"

	"github.com/fatih/color"
)

// ScanLogFile 全量扫描文件，去重输出，支持关键字查询
func ScanLogFile(path, filter, filterType string) {
	if path == "" {
		color.Red("unable to scan log file, path is empty!\n")
		return
	}
	color.Yellow("start to scan log file: %s\n", path)
	file, err := os.Open(path)
	if err != nil {
		color.Red("unable to open log file, error: %s\n", err)
		return
	}
	defer file.Close()
	scanner := bufio.NewScanner(file)
	lines := make([]string, 0)
	uniqueMap := make(map[string]bool)

	for scanner.Scan() {
		line := strings.Join(strings.Fields(scanner.Text()), " ")
		// 切分数据，仅获取 时间、日志级别、日志内容，然后根据日志内容进行去重
		content := strings.SplitN(line, " ", 3)
		if len(content) < 3 {
			continue
		}
		// 对日志内容进行 hash 获取唯一key
		hash := sha256.Sum256([]byte(content[2]))
		hashKey := hex.EncodeToString(hash[:])
		if uniqueMap[hashKey] {
			continue
		}

		// 关键词匹配
		if filter == "" {
			uniqueMap[hashKey] = true
			lines = append(lines, scanner.Text())
		} else {
			content := scanner.Text()
			if strFilter(content, filter, filterType) {
				uniqueMap[hashKey] = true
				lines = append(lines, content)
			}
		}
	}
	// 对于扫描的过程中产生了错误，则不对数据进行输出，直接返回
	if err = scanner.Err(); err != nil {
		color.Red("an error occurred while scanning the file, error: %s\n", err)
		return
	}
	for _, line := range lines {
		fmt.Println(line)
	}
}

// strFilter 对 content 的内容进行过滤
// filter 由多个关键词组成的字符串 example: "key1,key2,key3"
// filterType 过滤条件 and or not 以及关闭选项 close
func strFilter(content, filter, filterType string) bool {
	keywords := strings.Split(filter, ",")

	switch filterType {
	case "or":
		for _, keyword := range keywords {
			if strings.Contains(content, keyword) {
				return true
			}
		}
		return false
	case "and":
		for _, keyword := range keywords {
			if !strings.Contains(content, keyword) {
				return false
			}
		}
		return true
	case "not":
		for _, keyword := range keywords {
			if strings.Contains(content, keyword) {
				return false
			}
		}
		return true
	case "close":
		return true
	default:
		color.Red("filterType not in ['and','or','not']\n")
	}
	return false
}
