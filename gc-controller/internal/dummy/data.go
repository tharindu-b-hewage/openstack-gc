package dummy

import (
	"github.com/crunchycookie/openstack-gc/gc-controller/internal/model"
	"gopkg.in/yaml.v3"
)

var DummyData = []model.SleepInfo{
	{GcPoolSize: 4, GcAsleep: 1, GcAwake: 3, HostInfo: model.HostInfo{
		CPU:            "corei7",
		SleepLevels:    []string{"c0", "c6"},
		MaxAwakePower:  12.1,
		MaxAsleepPower: 4.2,
	}},
}

var DummySleepOps = []model.SleepOp{
	{Kind: "sleep", Count: 2},
}

type Host struct {
	Name string `yaml:"name"`
	Port int    `yaml:"port"`
}

type Gc struct {
	PoolSize int `yaml:"pool-size"`
}

type dummyConfigYaml struct {
	Host Host `yaml:"host"`
	Gc   Gc   `yaml:"gc"`
}

var DefaultConfigsBytes, _ = yaml.Marshal(&dummyConfigYaml{
	Host: Host{
		Name: "localhost",
		Port: 3000,
	},
	Gc: Gc{
		PoolSize: 4,
	},
})
