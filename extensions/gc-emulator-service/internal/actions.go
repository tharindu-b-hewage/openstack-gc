package internal

import (
	"fmt"
	"slices"
	"strconv"
	"strings"
)

func (o *GreenCoreMgt) evictVMsOnGreenCores() error {
	for _, host := range o.conf.ComputeHosts {
		// Evicting VMs pinned to green cores.
		var domains []domainsVirshModel
		err := RunThirdPartyClient[domainsVirshModel](&domains, "virsh-list-domains.sh", host.User, host.Ip)
		if err != nil {
			return err
		}
		for _, domain := range domains {
			var cpuAffinities []emulatorPinVirshModel
			err := RunThirdPartyClient[emulatorPinVirshModel](&cpuAffinities, "virsh-domain-get-pinned-cpu-core.sh", host.User, host.Ip, domain.Name)
			if err != nil {
				return err
			}
			isShelve := false
			for _, cpuAffinity := range cpuAffinities {
				pinnedCore, _ := strconv.Atoi(strings.Split(cpuAffinity.EmulatorCPUAffinity, "*: ")[1])
				if slices.Contains(host.DynamicCoreIds, pinnedCore) {
					isShelve = true
				}
			}
			if isShelve {
				var servers []osServerModel
				err := RunThirdPartyClient[osServerModel](&servers, "openstack-get-server-by-domain.sh", domain.Name)
				if err != nil {
					return err
				}
				for _, server := range servers {
					err := RunThirdPartyClient[any](nil, "openstack-shelve-offload-server.sh", server.Id)
					if err != nil {
						return err
					}
				}
			}
		}

		// Putting green cores to sleep.
		fmt.Printf("gc-sleep: calling external power apis: %s...", host.Ip)
		err = RunThirdPartyClient[any](nil, "gc-controller-sleep.sh", host.Ip)
		if err != nil {
			fmt.Printf("failed to call external power api %s to wake...", host.Ip)
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
	err := o.evictVMsOnGreenCores()
	if err != nil {
		return fmt.Errorf("failed at shelving possible instances using green core: %w", err)
	}
	//o.putGcToSleepInHost()
	return nil
}

func (o *GreenCoreMgt) setPollingEndpointToAwake() {
	o.IsGreenCoreAwake = true
	// need to wait until os is properly updated. since this service serves multiple worker node, its not scalable to implement synchrounous check.
	//fmt.Println("waiting to allow openstack to update...")
	//time.Sleep(10 * time.Second)
	//fmt.Println("waited. assume openstack is updated...")
}

func (o *GreenCoreMgt) setPollingEndpointToSleep() {
	// Expects openstack to omit green core from pCPU list, through polling api.
	o.IsGreenCoreAwake = false
	// need to wait until os is properly updated. since this service serves multiple worker node, its not scalable to implement synchrounous check.
	//fmt.Println("waiting to allow openstack to update...")
	//time.Sleep(10 * time.Second)
	//fmt.Println("waited. assume openstack is updated...")
}
