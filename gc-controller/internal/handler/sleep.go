package handler

import (
	"github.com/crunchycookie/openstack-gc/gc-controller/internal/dummy"
	"github.com/crunchycookie/openstack-gc/gc-controller/internal/model"
	"github.com/crunchycookie/openstack-gc/gc-controller/internal/power"
	"github.com/gin-gonic/gin"
	"net/http"
)

type SleepAPIHandler struct {
	Controller *power.SleepController
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
	controller.Sleep(newSleepOp.Count)

	c.IndentedJSON(http.StatusCreated, newSleepOp)
}

func (o *SleepAPIHandler) PutAwakeOP(c *gin.Context) {
	var newSleepOp model.SleepOp
	if err := c.BindJSON(&newSleepOp); err != nil {
		return
	}

	controller := o.Controller
	controller.Wake(newSleepOp.Count)

	c.IndentedJSON(http.StatusCreated, newSleepOp)
}

func (o *SleepAPIHandler) PutPoolFreq(c *gin.Context) {
	var newFqOp model.FqOp
	if err := c.BindJSON(&newFqOp); err != nil {
		return
	}

	controller := o.Controller
	controller.OpFrequency(newFqOp.FMhz)

	c.IndentedJSON(http.StatusCreated, newFqOp)
}
