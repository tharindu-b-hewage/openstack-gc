package power

import (
	"fmt"
	"github.com/intel/power-optimization-library/pkg/power"
	"log"
	"sync"
)

const (
	RegularCoresPoolName           = "rc-pool"
	GreenCoresPoolName             = "gc-pool"
	MaxPerformancePowerProfileName = "maxPerfProf"
	CStatesFullyAwake              = "POLL"
	SleepingFq                     = 100
	FullyAwakeFq                   = 2600
)

var DeepestSleepStateLbl string

type SleepController struct {
	Host power.Host
	mu   sync.Mutex
}

// NewSleepController prepares host for green cores, and returns a controller for that. It assumes 4 physical cores cpu
// (preferably features such as hyper-threading disabled to achieve this) and the core configuration is hardcoded;
// 3 - regular cores and 1- green cores. This service must see on-node kernel, such that true control of the cores are
// provided (for example, running on a vm might only provide the vCPU abstract).
//
// Regular cores power profile is set at the high-performance (core clock set between 2.6-2.8 GHz), and its sleep state is set
// to POLL, which prevents the core from going into sleep states. This provides cpu cores that can cater workloads
// without compromise to service quality (instant execution at maximum performance).
//
// Green cores power profile is set at the same high-performance, but they are set at the deepest sleep state that the
// platform can offer. This provides minimum power draw, emulating fully asleep green cores; deepest the sleep state,
// core reaches perfect full asleep state.
func NewSleepController() (*SleepController, error) {
	log.Println("creating a power instance...")
	host, err := getPowerHost()
	if err != nil {
		return nil, err
	}

	log.Println("moving all cpu cores into the shared pool...")
	err = host.GetSharedPool().SetCpuIDs([]uint{0, 1, 2, 3})
	if err != nil {
		return nil, fmt.Errorf("failed at moving all cpu cores into the shared pool: %w", err)
	}

	log.Println("grouping cores into regular and green pools...")
	err1 := moveCoresToPool(&host, RegularCoresPoolName, []uint{0, 1, 2})
	err2 := moveCoresToPool(&host, GreenCoresPoolName, []uint{3})
	if err1 != nil || err2 != nil {
		return nil, fmt.Errorf("failed at grouping cores into pools: %w and %w", err1, err2)
	}

	log.Println("changing all cores to maximum performance profile...")
	err1 = setPerf(&host, RegularCoresPoolName, 2600)
	err2 = setPerf(&host, GreenCoresPoolName, 100) // CPU might stop at the lowest possible value, which might be higher that the provided.
	if err1 != nil || err2 != nil {
		return nil, fmt.Errorf("failed at setting cores to max performance: %w and %w", err1, err2)
	}

	log.Println("setting initial sleep levels: fully awake regulars and deep sleep greens...")
	//todo assumes an array with ordered list of c-states; most awake first. we might need to handle this properly.
	deepSleepLabel, err := evaluateReqSleepStates(&host)
	DeepestSleepStateLbl = deepSleepLabel
	if err != nil {
		return nil, err
	}
	err1 = setPoolSleepState(&host, RegularCoresPoolName, false)
	log.Printf("using deep sleep state: %s for green cores\n", DeepestSleepStateLbl)
	err2 = setPoolSleepState(&host, GreenCoresPoolName, true)
	if err1 != nil || err2 != nil {
		return nil, fmt.Errorf("failed setting pool sleep states: %w, %w", err1, err2)
	}

	return &SleepController{
		Host: host,
	}, nil
}

func evaluateReqSleepStates(host *power.Host) (deepSleepLabel string, err error) {
	availableCStates := (*host).AvailableCStates()
	if availableCStates[0] != CStatesFullyAwake {
		return "", fmt.Errorf("platform needs to support cores being fully awake (i.e. c-state = POLL)")
	}
	if len(availableCStates) < 2 {
		return "", fmt.Errorf("platform needs to support low-power c-states (provided: %x)", availableCStates)
	}
	deepSleepIdleStatus := availableCStates[len(availableCStates)-1]
	return deepSleepIdleStatus, nil
}

func setPoolSleepState(host *power.Host, poolName string, isSleep bool) error {
	err := (*host).GetExclusivePool(poolName).SetCStates(power.CStates{
		"POLL":    !isSleep,
		"C1_ACPI": false,
		"C2_ACPI": false,
		"C3_ACPI": isSleep,
	})
	if err != nil {
		return fmt.Errorf("failed at setting %s pool to isSleep: %t", poolName, isSleep)
	}
	return nil
}

func setPerf(host *power.Host, poolName string, baseFMhz uint) error {
	maxFMhz := baseFMhz + 100
	maxPerfProf, err := power.NewPowerProfile(MaxPerformancePowerProfileName, baseFMhz, maxFMhz, "performance", "performance")
	if err != nil {
		return fmt.Errorf("failed at creating a power profile: %w", err)
	}
	err = (*host).GetExclusivePool(poolName).SetPowerProfile(maxPerfProf)
	if err != nil {
		return fmt.Errorf("failed at setting %s pool to max power profile: %w", poolName, err)
	}
	return nil
}

func getPowerHost() (power.Host, error) {
	host, allErrors := power.CreateInstance("gc-enabled-host")
	if host != nil {
		features := host.GetFeaturesInfo()
		var reqPowerOptmzFeatures error
		reqPowerOptmzFeatures = features[power.CStatesFeature].FeatureError()
		reqPowerOptmzFeatures = features[power.FreqencyScalingFeature].FeatureError()
		if reqPowerOptmzFeatures != nil {
			return nil, fmt.Errorf("failed at creating a power instance: %w", allErrors)
		}
	}
	return host, nil
}

func moveCoresToPool(host *power.Host, poolName string, coreIDs []uint) error {
	gcPool, err := (*host).AddExclusivePool(poolName)
	if err != nil {
		return fmt.Errorf("failed at creating exclusive pool for %s: %w", poolName, err)
	}
	err = gcPool.MoveCpuIDs(coreIDs)
	if err != nil {
		return fmt.Errorf("failed at moving cpu core to the %s pool: %w", poolName, err)
	}
	return nil
}
