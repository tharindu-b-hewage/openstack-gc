package handler

import (
	"github.com/crunchycookie/openstack-gc/gc-controller/internal/dummy"
	"github.com/crunchycookie/openstack-gc/gc-controller/internal/model"
	"github.com/crunchycookie/openstack-gc/gc-controller/internal/power"
	"github.com/gin-gonic/gin"
	"net/http"
)

type SleepAPIHandler struct {
	Controller power.SleepController
}

func (o *SleepAPIHandler) GetSleepInfo(c *gin.Context) {
	postBody := o.Controller.Info()
	c.IndentedJSON(http.StatusOK, postBody)
}

func (o *SleepAPIHandler) GetSleepOPs(c *gin.Context) {
	c.IndentedJSON(http.StatusOK, dummy.DummySleepOps)
}

func (o *SleepAPIHandler) PutSleepOP(c *gin.Context) {
	var newSleepOp model.SleepOp
	if err := c.BindJSON(&newSleepOp); err != nil {
		return
	}

	controller := o.Controller
	if newSleepOp.Kind == "sleep" {
		controller.Sleep(newSleepOp.Count)
	} else if newSleepOp.Kind == "wake" {
		controller.Wake(newSleepOp.Count)
	}

	dummy.DummySleepOps = append(dummy.DummySleepOps, newSleepOp)
	c.IndentedJSON(http.StatusCreated, newSleepOp)
}
