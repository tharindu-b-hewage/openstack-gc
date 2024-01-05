package org.crunchycookie.research.tracegen.clients;

import java.io.File;
import java.io.IOException;

public class OpenstackComputeClient {


    public OpenstackComputeClient() {
    }

    private static void listImages() {
        try {
            var process = new ProcessBuilder()
                    .directory(new File(System.getProperty("user.home") + "/trace-gen"))
                    .command("sh", "-c", "./image-list.sh")
                    .inheritIO()
                    .start();
            var exitCode = process.waitFor();
        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        }
    }

    public Object createVM(String vmName) {

        listImages();
        return null;
    }

    public void deleteVM(Object server) {

    }
}
