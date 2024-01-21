package internal

import (
	"gopkg.in/yaml.v3"
	"io/ioutil"
	"log"
)

type ComputeHost struct {
	Ip             string `yaml:"ip"`
	User           string `yaml:"user"`
	DynamicCoreIds []int  `yaml:"dynamic-core-ids"`
}

type ConfYaml struct {
	ComputeHosts []ComputeHost `yaml:"compute-hosts"`
}

func NewConfigParser(path string) (ConfYaml, error) {
	var result ConfYaml

	content, err := ioutil.ReadFile(path)
	if err != nil {
		log.Fatal(err.Error())
	}
	err = yaml.Unmarshal(content, &result)
	if err != nil {
		log.Fatal("Failed to parse file ", err)
	}

	return result, nil
}
