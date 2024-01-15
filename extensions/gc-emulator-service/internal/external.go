package internal

import (
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
)

func RunThirdPartyClient[T any](obj *[]T, args ...string) error {
	cmd := exec.Command("sh", args...)
	cmd.Stderr = os.Stderr // or any other io.Writer
	out, err := cmd.Output()
	if err != nil {
		return fmt.Errorf("failed at running os command: %w", err)
	}
	if obj != nil {
		err = json.Unmarshal(out, &obj)
		if err != nil {
			fmt.Println(err.Error())
			return fmt.Errorf("failed at unmarshalling response: %w", err)
		}
	}
	return nil
}

func (o *GreenCoreMgt) putGcToAwakeInHost() {
	for _, host := range o.conf.ComputeHosts {
		fmt.Printf("gc-awake: calling external power apis: %s...", host.Ip)
		err := RunThirdPartyClient[any](nil, "gc-controller-wake.sh", host.Ip)
		if err != nil {
			fmt.Printf("failed to call external power api %s to wake...", host.Ip)
		}
	}
}

func (o *GreenCoreMgt) putGcToSleepInHost() {
	for _, host := range o.conf.ComputeHosts {
		fmt.Printf("gc-sleep: calling external power apis: %s...", host.Ip)
		err := RunThirdPartyClient[any](nil, "gc-controller-sleep.sh", host.Ip)
		if err != nil {
			fmt.Printf("failed to call external power api %s to wake...", host.Ip)
		}
	}
}
