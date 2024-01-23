package internal

import (
	"fmt"
	"slices"
	"strconv"
	"strings"
)

func (o *GreenCoreMgt) obtainCoreUsage() ([]HostCoreUsage, error) {

	var hostCoreUsages []HostCoreUsage
	for _, host := range o.conf.ComputeHosts {
		var hostCoreUsage HostCoreUsage
		hostCoreUsage.Ip = host.Ip

		var usedDynamicCores []int
		var usedStableCores []int

		var domains []domainsVirshModel
		err := RunThirdPartyClient[domainsVirshModel](&domains, "virsh-list-domains.sh", host.User, host.Ip)
		if err != nil {
			return nil, err
		}
		for _, domain := range domains {
			var cpuAffinities []emulatorPinVirshModel
			err := RunThirdPartyClient[emulatorPinVirshModel](&cpuAffinities, "virsh-domain-get-pinned-cpu-core.sh", host.User, host.Ip, domain.Name)
			if err != nil {
				return nil, err
			}
			for _, cpuAffinity := range cpuAffinities {
				pinnedCore, _ := strconv.Atoi(strings.Split(cpuAffinity.EmulatorCPUAffinity, "*: ")[1])
				if slices.Contains(host.DynamicCoreIds, pinnedCore) {
					usedDynamicCores = append(usedDynamicCores, pinnedCore)
				}
				if slices.Contains(host.StableCoreIds, pinnedCore) {
					usedStableCores = append(usedStableCores, pinnedCore)
				}
			}
		}

		hostCoreUsage.RegCoresAvl = len(host.StableCoreIds)
		hostCoreUsage.RegCoresUsg = len(usedStableCores)
		if o.IsGreenCoreAwake {
			hostCoreUsage.GreenCoresAvl = len(host.DynamicCoreIds)
			hostCoreUsage.GreenCoresUsg = len(usedDynamicCores)
		} else {
			hostCoreUsage.GreenCoresAvl = 0
			hostCoreUsage.GreenCoresUsg = 0
		}
		hostCoreUsages = append(hostCoreUsages, hostCoreUsage)

		fmt.Printf("core usage for %s is %+v\\n\n", host.Ip, hostCoreUsage)
	}
	return hostCoreUsages, nil
}
