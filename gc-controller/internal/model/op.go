package model

type SleepOp struct {
	Kind  string `json:"kind"`
	Count int    `json:"count"`
}

type FqOp struct {
	FMhz uint `json:"f-mhz"`
}
