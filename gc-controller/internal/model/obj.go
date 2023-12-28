package model

type HostInfo struct {
	CPU            string   `json:"cpu"`
	SleepLevels    []string `json:"sleep-levels"`
	MaxAwakePower  float32  `json:"max-awake-power"`
	MaxAsleepPower float32  `json:"max-asleep-power"`
}

type SleepInfo struct {
	GcPoolSize int      `json:"gc-pool-size"`
	GcAsleep   int      `json:"gc-asleep"`
	GcAwake    int      `json:"gc-awake"`
	HostInfo   HostInfo `json:"host-info"`
}
