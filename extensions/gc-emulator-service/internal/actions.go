package internal

import (
	"fmt"
	"strconv"
	"strings"
)

func (o *GreenCoreMgt) shelveAllRunningInstancesOnGreenCore() error {
	var domains []domainsVirshModel
	err := RunThirdPartyClient[domainsVirshModel]("virsh-list-domains.sh", "", &domains)
	if err != nil {
		return err
	}
	for _, domain := range domains {
		var cpuAffinities []emulatorPinVirshModel
		err := RunThirdPartyClient[emulatorPinVirshModel]("virsh-domain-get-pinned-cpu-core.sh", domain.Name, &cpuAffinities)
		if err != nil {
			return err
		}
		isShelve := false
		for _, cpuAffinity := range cpuAffinities {
			pinnedCore, _ := strconv.Atoi(strings.Split(cpuAffinity.EmulatorCPUAffinity, "*: ")[1])
			if o.isGreenCore(pinnedCore) {
				isShelve = true
			}
		}
		if isShelve {
			var servers []osServerModel
			err := RunThirdPartyClient[osServerModel]("openstack-get-server-by-domain.sh", domain.Name, &servers)
			if err != nil {
				return err
			}
			for _, server := range servers {
				err := RunThirdPartyClient[any]("openstack-shelve-offload-server.sh", server.Id, nil)
				if err != nil {
					return err
				}
			}
		}
	}
	return nil
}

func (o *GreenCoreMgt) triggerTransition(isPutToSleep bool) error {

	if !isPutToSleep {
		fmt.Println("waking up gc...")
		// order matters: wake core physically and then set polling status.
		o.putGcToAwakeInHost()
		o.setPollingEndpointToAwake()
		return nil
	}

	fmt.Println("putting gc to sleep...")
	// order matters: omit core at the middleware layer and then physically change core power status.
	o.setPollingEndpointToSleep()
	err := o.shelveAllRunningInstancesOnGreenCore()
	if err != nil {
		return fmt.Errorf("failed at shelving possible instances using green core: %w", err)
	}
	o.putGcToSleepInHost()
	return nil
}

func (o *GreenCoreMgt) setPollingEndpointToAwake() {
	o.IsGreenCoreAwake = true
}

func (o *GreenCoreMgt) isGreenCore(pinnedCore int) bool {
	return uint(pinnedCore) == o.greenCoreId
}

func (o *GreenCoreMgt) setPollingEndpointToSleep() {
	// Expects openstack to omit green core from pCPU list, through polling api.
	o.IsGreenCoreAwake = false
}
