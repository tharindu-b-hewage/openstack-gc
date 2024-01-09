package internal

import (
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
)

func RunThirdPartyClient[T any](script string, arg string, obj *[]T) error {
	cmd := exec.Command("sh", script, arg)
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
	fmt.Printf("gc-awake: calling external power apis...")
	//todo call core-power-mgt api
}

func (o *GreenCoreMgt) putGcToSleepInHost() {
	fmt.Printf("gc-sleep: calling external power apis...")
	//todo call core-power-mgt api
}
