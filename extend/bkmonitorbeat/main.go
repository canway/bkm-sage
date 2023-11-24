package main

import (
	"bkmonitorbeat/cmd"
	_ "bkmonitorbeat/register"
)

func main() {
	cmd.Execute()
}
