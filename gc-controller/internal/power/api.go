package power

import (
	"fmt"
	"github.com/crunchycookie/openstack-gc/gc-controller/internal/model"
	"log"
)

func (o *SleepController) Info() *model.SleepInfo {
	fmt.Println("Listing out available sleep states...")
	log.Printf("deepest sleep state: %s\n", DeepestSleepStateLbl)
	return nil
}

func (o *SleepController) Sleep(coreCount int) error {
	(*o).mu.Lock()
	defer (*o).mu.Unlock()

	host := o.Host
	//todo need to support per-core sleep state and set it according to the coreCount parameter.
	// below only set pool sleep state.
	pool := GreenCoresPoolName
	err2 := setPerf(&host, pool, SleepingFq)
	err1 := setPoolSleepState(&host, pool, true)
	if err1 != nil || err2 != nil {
		//todo handle error from calling level, and then we can remove below log.
		return fmt.Errorf("failed at sleeping green core: %w, %w", err1, err2)
	}
	log.Printf("green core sleep state changed to: %s", DeepestSleepStateLbl)
	return nil
}

func (o *SleepController) Wake(coreCount int) error {
	(*o).mu.Lock()
	defer (*o).mu.Unlock()

	host := o.Host
	//todo need to support per-core sleep state and set it according to the coreCount parameter.
	// below only set pool sleep state.
	pool := GreenCoresPoolName
	err2 := setPerf(&host, pool, FullyAwakeFq)
	err1 := setPoolSleepState(&host, pool, false)
	if err1 != nil || err2 != nil {
		//todo handle error from calling level, and then we can remove below log.
		return fmt.Errorf("failed at waking green core: %w, %w", err1, err2)
	}
	log.Println("green core woken up")
	return nil
}

func (o *SleepController) OpFrequency(fMhz uint) error {
	(*o).mu.Lock()
	defer (*o).mu.Unlock()

	host := o.Host
	pool := GreenCoresPoolName
	err := setPerf(&host, pool, fMhz)
	if err != nil {
		//todo handle error from calling level, and then we can remove below log.
		log.Print("failed at changing perf frequency: %w", err)
		return fmt.Errorf("failed at changing perf frequency: %w", err)
	}
	log.Printf("frequency of pool: %s changed to: %d", pool, fMhz)
	return nil
}
