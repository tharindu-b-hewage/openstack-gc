package internal

import (
	"fmt"
	"github.com/gin-gonic/gin"
	"net/http"
)

type GreenCoreMgt struct {
	IsGreenCoreAwake bool
	Status           bool
	greenCoreId      uint
}

func NewGreenCoreMgt() GreenCoreMgt {

	mgt := GreenCoreMgt{
		IsGreenCoreAwake: false,
		Status:           true,
		greenCoreId:      3,
	}
	return mgt
}

func (o *GreenCoreMgt) Start() {
	for o.Status {
		//todo read trace and set state.
	}
}

func (o *GreenCoreMgt) Begin(c *gin.Context) {
	fmt.Printf("starting monitoring...")
	go o.Start()
	c.IndentedJSON(http.StatusAccepted, nil)
}

func (o *GreenCoreMgt) IsAsleep(c *gin.Context) {
	fmt.Printf("checking gc state...")
	c.IndentedJSON(http.StatusOK, GcStatus{
		IsAwake: o.IsGreenCoreAwake,
	})
}

func (o *GreenCoreMgt) Switch(c *gin.Context) {
	fmt.Printf("changing gc state from: %t, to: %t\n ...", o.IsGreenCoreAwake, !o.IsGreenCoreAwake)
	o.IsGreenCoreAwake = !o.IsGreenCoreAwake
	err := o.triggerTransition(!o.IsGreenCoreAwake)
	if err != nil {
		c.JSON(http.StatusInternalServerError, "Something went wrong. Check admin logs.")
		return
	}

	c.IndentedJSON(http.StatusCreated, GcStatus{
		IsAwake: o.IsGreenCoreAwake,
	})
}
