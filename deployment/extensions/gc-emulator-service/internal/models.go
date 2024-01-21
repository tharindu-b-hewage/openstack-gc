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
