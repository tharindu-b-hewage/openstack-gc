package handler

import (
	"github.com/crunchycookie/openstack-gc/gc-controller/internal/dummy"
	"github.com/crunchycookie/openstack-gc/gc-controller/internal/model"
	"github.com/gin-gonic/gin"
	"net/http"
)

func GetSleepInfo(c *gin.Context) {
	c.IndentedJSON(http.StatusOK, dummy.DummyData)
}

func GetSleepOPs(c *gin.Context) {
	c.IndentedJSON(http.StatusOK, dummy.DummySleepOps)
}

func PutSleepOP(c *gin.Context) {
	var newSleepOp model.SleepOp

	if err := c.BindJSON(&newSleepOp); err != nil {
		return
	}

	dummy.DummySleepOps = append(dummy.DummySleepOps, newSleepOp)
	c.IndentedJSON(http.StatusCreated, newSleepOp)
}
