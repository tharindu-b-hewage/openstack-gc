package internal

type osServerModel struct {
	Id string `json:"ID"`
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
