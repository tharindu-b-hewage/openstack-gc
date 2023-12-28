package main

import (
	"fmt"
	"github.com/crunchycookie/openstack-gc/gc-controller/internal/configs"
	"github.com/crunchycookie/openstack-gc/gc-controller/internal/handler"
	"github.com/gin-gonic/gin"
	"os"
	"strconv"
)

func main() {

	conf := loadConfigs()

	router := gin.Default()
	router.GET("/gc-controller/sleep-info", handler.GetSleepInfo)
	router.GET("/gc-controller/sleep", handler.GetSleepOPs)
	router.PUT("/gc-controller/sleep", handler.PutSleepOP)

	err := router.Run(conf.Host + ":" + strconv.Itoa(conf.Port))
	if err != nil {
		fmt.Println("Unable to start the gc-controller", err)
		return
	}
}

func loadConfigs() *configs.GcControllerConfigs {
	path := ""
	if len(os.Args) > 1 {
		path = os.Args[1]
	}
	conf := configs.NewConfigs(path)
	return conf
}
