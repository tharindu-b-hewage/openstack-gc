package internal

import (
	"fmt"
	"log"
	"regexp"
	"strconv"
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
				// Note that below parsing works when consecutive cores are pinned for a VM. Eg: 1-4, 5-9, etc.
				// Other permutations are not tested.
				pinnedCores := extractPinnedCores(cpuAffinity.EmulatorCPUAffinity)
				if isIntersecting(host.DynamicCoreIds, pinnedCores) {
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
					log.Printf("vm evicted: %s\n", server.Name)
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

func isIntersecting(arr1, arr2 []int) bool {
	// Create a map to store elements of the first array
	valueMap := make(map[int]bool)

	// Populate the map with elements from the first array
	for _, value := range arr1 {
		valueMap[value] = true
	}

	// Check if any element in the second array exists in the map
	for _, value := range arr2 {
		if valueMap[value] {
			return true
		}
	}

	return false
}

func extractPinnedCores(s string) []int {
	// Define the regular expression to match the pattern "*: number(-number)?"
	re := regexp.MustCompile(`\*: (\d+)(-(\d+))?`)
	matches := re.FindStringSubmatch(s)

	if len(matches) == 0 {
		return nil // Or handle the error as needed
	}

	start, err := strconv.Atoi(matches[1])
	if err != nil {
		return nil // Or handle the error as needed
	}

	if matches[3] == "" {
		// Return a slice with the single value
		return []int{start}
	}

	end, err := strconv.Atoi(matches[3])
	if err != nil {
		return nil // Or handle the error as needed
	}

	// Return a slice with the range of values
	result := make([]int, end-start+1)
	for i := start; i <= end; i++ {
		result[i-start] = i
	}

	return result
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
