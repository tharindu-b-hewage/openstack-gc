package internal

type osServerModel struct {
	Id   string `json:"ID"`
	Name string `json:"Name"`
}

type domainsVirshModel struct {
	Name string `json:"Name"`
}
type emulatorPinVirshModel struct {
	EmulatorCPUAffinity string `json:"emulator: CPU Affinity"`
}

type GcStatus struct {
	IsAwake bool `json:"is-awake"`
}

type HostCoreUsage struct {
	Ip            string `json:"host-ip"`
	RegCoresAvl   int    `json:"reg-cores-avl"`
	RegCoresUsg   int    `json:"reg-cores-usg"`
	GreenCoresAvl int    `json:"green-cores-avl"`
	GreenCoresUsg int    `json:"green-cores-usg"`
}
