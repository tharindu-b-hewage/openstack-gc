package org.crunchycookie.research.tracegen.clients;

import java.io.File;
import java.io.IOException;

public class OpenstackComputeClient {


    public OpenstackComputeClient() {
    }

    private static void listImages() {
        runOpenstackOP("image-list.sh");
    }

    private static void runOpenstackOP(String opScript) {
        try {
            var process = new ProcessBuilder()
                    .directory(new File(System.getProperty("user.home") + "/trace-gen"))
                    .command("sh", "-c", "./" + opScript)
                    .inheritIO()
                    .start();
            var exitCode = process.waitFor();
        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        }
    }

    public Object createVM(String vmName) {

        runOpenstackOP("create-vm.sh " + vmName);
        return null;
    }

    public void deleteVM(String vmName) {
        runOpenstackOP("delete-vm.sh " + vmName);
    }
}
