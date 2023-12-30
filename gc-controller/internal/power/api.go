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
	state := DeepestSleepStateLbl
	err := setPoolSleepState(&host, pool, true)
	if err != nil {
		//todo handle error from calling level, and then we can remove below log.
		log.Print("failed at changing pool sleep state: %w", err)
		return fmt.Errorf("failed at changing pool sleep state: %w", err)
	}
	log.Printf("sleep state of pool: %s changed to: %s", pool, state)
	return nil
}

func (o *SleepController) Wake(coreCount int) error {
	(*o).mu.Lock()
	defer (*o).mu.Unlock()

	host := o.Host
	//todo need to support per-core sleep state and set it according to the coreCount parameter.
	// below only set pool sleep state.
	pool := GreenCoresPoolName
	state := CStatesFullyAwake
	err := setPoolSleepState(&host, pool, false)
	if err != nil {
		//todo handle error from calling level, and then we can remove below log.
		log.Print("failed at changing pool sleep state: %w", err)
		return fmt.Errorf("failed at changing pool sleep state: %w", err)
	}
	log.Printf("sleep state of pool: %s changed to: %s", pool, state)
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
