package main

import (
	"fmt"
	"github.com/gin-gonic/gin"
	"github.com/openstack-gc/extensions/gc-emulator-service/internal"
	"os"
)

func main() {

	configs, err := internal.NewConfigParser(os.Args[1])
	if err != nil {
		fmt.Println("Unable to start the gc-emulator service", err)
		return
	}

	manager := internal.NewGreenCoreMgt(configs)

	router := gin.Default()
	router.POST("/gc/begin", manager.Begin)
	router.GET("/gc/is-asleep", manager.IsAsleep)
	router.POST("/gc/dev/switch", manager.Switch)

	err = router.Run("100.64.42.11:4000")
	if err != nil {
		fmt.Println("Unable to start the gc-emulator service", err)
		return
	}

	manager.Status = false
}
