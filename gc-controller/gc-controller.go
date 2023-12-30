package main

import (
	"fmt"
	"github.com/crunchycookie/openstack-gc/gc-controller/internal/configs"
	"github.com/crunchycookie/openstack-gc/gc-controller/internal/handler"
	"github.com/crunchycookie/openstack-gc/gc-controller/internal/power"
	"github.com/gin-gonic/gin"
	"log"
	"os"
	"strconv"
)

func main() {

	log.Println("loading service configurations...")
	conf := loadConfigs()

	log.Println("creating an api handler...")
	apiHandler, err := getAPIHandler()
	if err != nil {
		fmt.Println("Failed to create an API handler", err)
		return
	}

	log.Println("configuring api routing...")
	router := gin.Default()
	router.GET("/gc-controller/sleep-info", apiHandler.GetSleepInfo)
	router.PUT("/gc-controller/sleep", apiHandler.PutSleepOP)
	router.PUT("/gc-controller/wake", apiHandler.PutAwakeOP)
	router.PUT("/gc-controller/perf", apiHandler.PutPoolFreq)

	log.Println("begin serving...")
	err = router.Run(conf.Host + ":" + strconv.Itoa(conf.Port))
	if err != nil {
		fmt.Println("Unable to start the gc-controller", err)
		return
	}
}

func getAPIHandler() (*handler.SleepAPIHandler, error) {
	controller, err := power.NewSleepController()
	if err != nil {
		return nil, fmt.Errorf("failed to initialize sleep controller: %w", err)
	}
	sleepHandler := handler.SleepAPIHandler{
		Controller: controller,
	}
	return &sleepHandler, nil
}

func loadConfigs() *configs.GcControllerConfigs {
	path := ""
	if len(os.Args) > 1 {
		path = os.Args[1]
	}
	conf := configs.NewConfigs(path)
	return conf
}
