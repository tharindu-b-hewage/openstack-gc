package main

import (
	"fmt"
	"github.com/gin-gonic/gin"
	"github.com/openstack-gc/extensions/gc-emulator-service/internal"
)

func main() {

	manager := internal.NewGreenCoreMgt()

	router := gin.Default()
	router.POST("/gc/begin", manager.Begin)
	router.GET("/gc/is-asleep", manager.IsAsleep)
	router.POST("/gc/dev/switch", manager.Switch)

	err := router.Run("localhost:4000")
	if err != nil {
		fmt.Println("Unable to start the gc-emulator service", err)
		return
	}

	manager.IsAlive = false
}
