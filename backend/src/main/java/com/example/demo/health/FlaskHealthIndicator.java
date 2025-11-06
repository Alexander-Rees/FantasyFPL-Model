package com.example.demo.health;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.actuate.health.Health;
import org.springframework.boot.actuate.health.HealthIndicator;
import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import java.time.Duration;
import java.time.Instant;

@Component
@Profile("!test")
public class FlaskHealthIndicator implements HealthIndicator {

    @Value("${flask.api.url:http://localhost:5001}")
    private String flaskApiUrl;

    private final RestTemplate restTemplate;

    public FlaskHealthIndicator() {
        this.restTemplate = new RestTemplate();
    }

    @Override
    public Health health() {
        try {
            Instant start = Instant.now();
            String response = restTemplate.getForObject(flaskApiUrl + "/health", String.class);
            Duration duration = Duration.between(start, Instant.now());

            if (response != null && response.contains("ok")) {
                return Health.up()
                        .withDetail("flaskApiUrl", flaskApiUrl)
                        .withDetail("responseTime", duration.toMillis() + "ms")
                        .build();
            } else {
                // Flask is down but don't fail overall health - return unknown
                return Health.unknown()
                        .withDetail("flaskApiUrl", flaskApiUrl)
                        .withDetail("error", "Invalid response")
                        .build();
            }
        } catch (Exception e) {
            // Flask is down but don't fail overall health - return unknown
            return Health.unknown()
                    .withDetail("flaskApiUrl", flaskApiUrl)
                    .withDetail("error", e.getMessage())
                    .build();
        }
    }
}

