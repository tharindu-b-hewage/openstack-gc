package main

import (
	"fmt"
	"github.com/gin-gonic/gin"
	"github.com/openstack-gc/extensions/gc-emulator-service/internal"
	"log"
	"os"
)

func main() {

	err := configureLogFile()
	if err != nil {
		fmt.Println("Unable to setup log file", err)
		return
	}

	configs, err := internal.NewConfigParser(os.Args[1])
	if err != nil {
		fmt.Println("Unable to start the gc-emulator service", err)
		return
	}

	manager := internal.NewGreenCoreMgt(configs)

	router := gin.Default()
	router.POST("/gc/begin", manager.Begin)
	router.GET("/gc/is-asleep", manager.IsAsleep)
	router.GET("/gc/core-usage", manager.GetCoreUsage)
	router.POST("/gc/dev/switch", manager.Switch)

	err = router.Run(configs.HostIP + ":" + configs.HostPort)
	if err != nil {
		fmt.Println("Unable to start the gc-emulator service", err)
		return
	}

	manager.Status = false
}

func configureLogFile() error {
	// O_APPEND = Append data to the file when writing.
	// O_CREATE = Create a new file if none exists.
	// O_WRONLY = Open the file write-only.
	flags := os.O_APPEND | os.O_CREATE | os.O_WRONLY
	file, err := os.OpenFile("gc-emulation-service.log", flags, 0666)
	if err != nil {
		log.Fatal(err)
	}
	// Redirecting logs to the file
	log.SetOutput(file)
	return err
}
