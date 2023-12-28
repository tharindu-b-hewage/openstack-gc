package configs

import (
	"github.com/crunchycookie/openstack-gc/gc-controller/internal/dummy"
	"log"

	"github.com/knadh/koanf/parsers/yaml"
	"github.com/knadh/koanf/providers/file"
	"github.com/knadh/koanf/providers/rawbytes"
	"github.com/knadh/koanf/v2"
)

type GcControllerConfigs struct {
	Host       string `json:"host-name"`
	Port       int    `json:"port"`
	GcPoolSize int    `json:"gc-pool-size"`
}

func NewConfigs(path string) *GcControllerConfigs {

	var k = koanf.New(".")
	loadConfigs(path, k)
	return &GcControllerConfigs{
		Host:       k.String("host.name"),
		Port:       k.Int("host.port"),
		GcPoolSize: k.Int("gc.pool-size"),
	}
}

func loadConfigs(path string, k *koanf.Koanf) {
	var err error
	if len(path) > 0 {
		err = k.Load(file.Provider(path), yaml.Parser())
	} else {
		err = k.Load(rawbytes.Provider(dummy.DefaultConfigsBytes), yaml.Parser())
	}
	if err != nil {
		log.Fatalf("error loading config: %v", err)
	}
}
