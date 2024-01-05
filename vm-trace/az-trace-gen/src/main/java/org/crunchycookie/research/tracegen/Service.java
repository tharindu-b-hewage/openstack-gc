package org.crunchycookie.research.tracegen;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.crunchycookie.research.tracegen.clients.OpenstackComputeClient;

import java.io.FileInputStream;
import java.io.IOException;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
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

        var start = Instant.now();
        var clk = Instant.from(start);
        var endAt = clk.plus(Duration.ofSeconds(EXPERIMENT_DURATION_SECS));
        while (clk.isBefore(endAt)) {
            logger.atInfo().log("clk (s): " + (clk.toEpochMilli() - start.toEpochMilli()) / 1000.0);
            emulateTrace(client);
            clk = stayIdle(SYNC_INTERVAL_SECS, clk);
        }
        logger.atInfo().log("Deleting VMs...");
    }

    private static void emulateTrace(OpenstackComputeClient client) {

        System.out.println("Creating a VM...");
        String vmName = "vm-" + System.currentTimeMillis();
        client.createVM(vmName);
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
