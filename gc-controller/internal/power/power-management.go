package power

import (
	"fmt"
	"github.com/crunchycookie/openstack-gc/gc-controller/internal/model"
	"github.com/intel/power-optimization-library/pkg/power"
	"sync"
)

type SleepController struct {
	Host power.Host
	mu   sync.Mutex
}

func NewSleepController() *SleepController {
	host, _ := power.CreateInstance("Name")
	return &SleepController{
		Host: host,
	}
}

func (o *SleepController) Info() *model.SleepInfo {
	fmt.Println("to be implemented")
	o.Host.GetFeaturesInfo()
	o.Host.GetAllCpus()
	return nil
}

func (o *SleepController) Sleep(coreCount int) {
	block(&o.mu)
	fmt.Println("to be implemented")
}

func (o *SleepController) Wake(coreCount int) {
	block(&o.mu)
	fmt.Println("to be implemented")
}

// Make sure the API call is blocking, such that no other sleep operation can occur.
func block(mu *sync.Mutex) {
	mu.Lock()
	defer mu.Unlock()
}
