package main

import (
	"context"
	"fmt"
	"github.com/crunchycookie/openstack-gc/gc-controller/api"
)

func main() {
	service := api.New()

	err := service.Start(context.TODO())
	if err != nil {
		fmt.Println("Error while starting the controller service")
	}
}
