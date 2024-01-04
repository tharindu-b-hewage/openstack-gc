package org.crunchycookie.research.tracegen;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.io.FileInputStream;
import java.io.IOException;
import java.time.Duration;
import java.time.Instant;
import java.util.Properties;

public class Service {

    private static final Logger logger = LogManager.getLogger(Service.class);

    public static void main(String[] args) throws IOException {

        logger.atInfo().log("Loading properties...");
        var props = new Properties();
        props.load(new FileInputStream(args[0]));

        long SYNC_INTERVAL_SECS = Long.parseLong(props.getProperty("SYNC_INTERVAL_SECS"));
        long EXPERIMENT_DURATION_SECS = Long.parseLong(props.getProperty("EXPERIMENT_DURATION_SECS"));
        logger.atInfo().log("Sync interval(s): " + EXPERIMENT_DURATION_SECS);
        logger.atInfo().log("Experiment duration(s): " + EXPERIMENT_DURATION_SECS);

        var start = Instant.now();
        var clk = Instant.from(start);
        var endAt = clk.plus(Duration.ofSeconds(EXPERIMENT_DURATION_SECS));

        while (clk.isBefore(endAt)) {
            logger.atInfo().log("clk (s): " + (clk.toEpochMilli() - start.toEpochMilli()) / 1000.0);
            // do api call.
            System.out.println("dummu api call made!");

            var wait = Duration.ofSeconds(SYNC_INTERVAL_SECS);
            await(wait);
            clk = clk.plus(wait);
        }
    }

    private static void await(Duration wait) {
        try {
            Thread.sleep(wait.toMillis());
        } catch (InterruptedException e) {
            throw new RuntimeException("failed to pause between requests", e);
        }
    }
}
