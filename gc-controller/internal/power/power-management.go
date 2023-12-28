package power

import (
	"fmt"
	"github.com/crunchycookie/openstack-gc/gc-controller/internal/model"
)

type SleepController struct {
}

func NewSleepController() *SleepController {
	return &SleepController{}
}

func (o *SleepController) Info() *model.SleepInfo {
	fmt.Println("to be implemented")
	return nil
}

func (o *SleepController) Sleep(coreCount int) {
	fmt.Println("to be implemented")
}

func (o *SleepController) Wake(coreCount int) {
	fmt.Println("to be implemented")
}
