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
		var usedTotalCores = 0

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
				pinnedCores, _ := parseCPUIds(strings.Split(cpuAffinity.EmulatorCPUAffinity, "*: ")[1])
				usedTotalCores = usedTotalCores + len(pinnedCores)

				pinnedCore, _ := strconv.Atoi(strings.Split(cpuAffinity.EmulatorCPUAffinity, "*: ")[1])
				if slices.Contains(host.DynamicCoreIds, pinnedCore) {
					usedDynamicCores = append(usedDynamicCores, pinnedCore)
				}
				if slices.Contains(host.StableCoreIds, pinnedCore) {
					usedStableCores = append(usedStableCores, pinnedCore)
				}
			}
		}

		// todo: harcoded fix for specific deployment.
		hostCoreUsage.RegCoresAvl = len(host.StableCoreIds)

		if o.IsGreenCoreAwake {
			hostCoreUsage.GreenCoresAvl = len(host.DynamicCoreIds)
		} else {
			hostCoreUsage.GreenCoresAvl = 0
		}
		// todo: hardcoded R as half of the CPU cores.
		var R = (len(host.StableCoreIds) + len(host.DynamicCoreIds)) / 2
		if usedTotalCores > R {
			hostCoreUsage.RegCoresUsg = R
			hostCoreUsage.GreenCoresUsg = usedTotalCores - R
		} else {
			hostCoreUsage.RegCoresUsg = usedTotalCores
			hostCoreUsage.GreenCoresUsg = 0
		}
		fmt.Printf("calculated green cores inventory")

		//hostCoreUsage.RegCoresAvl = len(host.StableCoreIds)
		//hostCoreUsage.RegCoresUsg = len(usedStableCores)
		//if o.IsGreenCoreAwake {
		//	hostCoreUsage.GreenCoresAvl = len(host.DynamicCoreIds)
		//	hostCoreUsage.GreenCoresUsg = len(usedDynamicCores)
		//} else {
		//	hostCoreUsage.GreenCoresAvl = 0
		//	hostCoreUsage.GreenCoresUsg = 0
		//}
		hostCoreUsages = append(hostCoreUsages, hostCoreUsage)

		fmt.Printf("core usage for %s is %+v\\n\n", host.Ip, hostCoreUsage)
	}
	return hostCoreUsages, nil
}

func parseCPUIds(input string) ([]int, error) {
	var cpus []int

	// Split the string by commas, e.g. "1-2,4,9-12" => ["1-2", "4", "9-12"]
	for _, part := range strings.Split(input, ",") {
		part = strings.TrimSpace(part)
		// Check if there's a dash indicating a range
		if strings.Contains(part, "-") {
			// Split by dash, e.g. "1-2" => ["1", "2"]
			rangeParts := strings.SplitN(part, "-", 2)
			if len(rangeParts) != 2 {
				return nil, fmt.Errorf("invalid range format: %s", part)
			}

			start, err := strconv.Atoi(strings.TrimSpace(rangeParts[0]))
			if err != nil {
				return nil, err
			}
			end, err := strconv.Atoi(strings.TrimSpace(rangeParts[1]))
			if err != nil {
				return nil, err
			}
			if start > end {
				return nil, fmt.Errorf("start of range is greater than end: %d-%d", start, end)
			}

			// Append all numbers in the range to the slice
			for i := start; i <= end; i++ {
				cpus = append(cpus, i)
			}
		} else {
			// It's a single CPU ID
			id, err := strconv.Atoi(part)
			if err != nil {
				return nil, err
			}
			cpus = append(cpus, id)
		}
	}

	return cpus, nil
}
