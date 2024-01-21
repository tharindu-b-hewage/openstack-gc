package org.crunchycookie.research.tracegen;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.crunchycookie.research.tracegen.clients.OpenstackComputeClient;

import java.io.FileInputStream;
import java.io.IOException;
import java.time.Duration;
import java.time.Instant;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.Properties;

public class Service {

    private static final Logger logger = LogManager.getLogger(Service.class);

    public static void main(String[] args) throws IOException {

        logger.atInfo().log("Loading properties...");
        var props = getProperties(args);

        long SYNC_INTERVAL_SECS = Long.parseLong(props.getProperty("SYNC_INTERVAL_SECS"));
        long EXPERIMENT_DURATION_SECS = Long.parseLong(props.getProperty("EXPERIMENT_DURATION_SECS"));

        logger.atInfo().log("Sync interval(s): " + SYNC_INTERVAL_SECS);
        logger.atInfo().log("Experiment duration(s): " + EXPERIMENT_DURATION_SECS);

        var client = getOpenstackClient(args);

        Map<String, Instant> hst = new HashMap<>();

        var start = Instant.now();
        var clk = Instant.from(start);
        var endAt = clk.plus(Duration.ofSeconds(EXPERIMENT_DURATION_SECS));
        while (clk.isBefore(endAt)) {
            cleanup(hst, clk, client);
            logger.atInfo().log("clk (s): " + (clk.toEpochMilli() - start.toEpochMilli()) / 1000.0);
            emulateTrace(client, hst, clk);
            clk = stayIdle(SYNC_INTERVAL_SECS, clk);
        }
        logger.atInfo().log("Deleting all VMs...");
        cleanup(hst, Instant.MAX, client);
    }

    private static void cleanup(Map<String, Instant> hst, Instant clk, OpenstackComputeClient client) {
        var iterator = hst.entrySet().iterator();
        while (iterator.hasNext()) {
            var e = iterator.next();
            if (e.getValue().isBefore(clk)) {
                logger.atInfo().log("Deleting VM: " + e.getKey());
                client.deleteVM(e.getKey());
                iterator.remove();
            }
        }
    }

    private static void emulateTrace(OpenstackComputeClient client, Map<String, Instant> hst, Instant clk) {

        System.out.println("Creating a VM...");
        String vmName = "vm-" + System.currentTimeMillis();
        double lifetime = 10.0;

        client.createVM(vmName);
        hst.put(vmName, clk.plus(Duration.ofSeconds((long) lifetime)));
    }

    private static Instant stayIdle(long SYNC_INTERVAL_SECS, Instant clk) {

        var wait = Duration.ofSeconds(SYNC_INTERVAL_SECS);
        await(wait);
        clk = clk.plus(wait);
        return clk;
    }

    private static OpenstackComputeClient getOpenstackClient(String[] args) {

        return new OpenstackComputeClient();
    }

    private static Properties getProperties(String[] args) throws IOException {

        var props = new Properties();
        props.load(new FileInputStream(args[0]));
        return props;
    }

    private static void await(Duration wait) {

        try {
            Thread.sleep(wait.toMillis());
        } catch (InterruptedException e) {
            throw new RuntimeException("failed to pause between requests", e);
        }
    }
}
