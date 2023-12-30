package main

import (
	"fmt"
	"github.com/crunchycookie/openstack-gc/gc-controller/internal/configs"
	"github.com/crunchycookie/openstack-gc/gc-controller/internal/handler"
	"github.com/crunchycookie/openstack-gc/gc-controller/internal/power"
	"github.com/gin-gonic/gin"
	"os"
	"strconv"
)

func main() {

	conf := loadConfigs()

	router := gin.Default()
	sleepHandler := handler.SleepAPIHandler{
		Controller: *power.NewSleepController(),
	}
	router.GET("/gc-controller/sleep-info", sleepHandler.GetSleepInfo)
	router.GET("/gc-controller/sleep", sleepHandler.GetSleepOPs)
	router.PUT("/gc-controller/sleep", sleepHandler.PutSleepOP)

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
