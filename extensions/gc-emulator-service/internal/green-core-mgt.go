package internal

import (
	"github.com/gin-gonic/gin"
	"net/http"
	"sync"
)

type GreenCoreMgt struct {
	IsGreenCoreAwake bool
	IsAlive          bool
	mu               sync.Mutex
}

type GcStatus struct {
	IsAsleep bool `json:"is-asleep"`
}

func NewGreenCoreMgt() GreenCoreMgt {
	mgt := GreenCoreMgt{
		IsGreenCoreAwake: false,
		IsAlive:          true,
	}
	return mgt
}

func (o *GreenCoreMgt) Start() {
	for o.IsAlive {
		// read trace and interpret.
	}
}

func (o *GreenCoreMgt) Begin(c *gin.Context) {
	go o.Start()
	c.IndentedJSON(http.StatusAccepted, nil)
}

func (o *GreenCoreMgt) IsAsleep(c *gin.Context) {
	c.IndentedJSON(http.StatusOK, GcStatus{
		IsAsleep: o.IsGreenCoreAwake,
	})
}

func (o *GreenCoreMgt) Switch(c *gin.Context) {
	o.mu.Lock()
	defer o.mu.Unlock()
	o.IsGreenCoreAwake = !o.IsGreenCoreAwake
	c.IndentedJSON(http.StatusCreated, GcStatus{
		IsAsleep: o.IsGreenCoreAwake,
	})
}
