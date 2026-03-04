package io.uranus.ucrypt.security;

import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

@Getter
@Setter
@NoArgsConstructor
@ConfigurationProperties(prefix = "jwt")
@Component
public class JwtConfig {
    private Long expirationInMinutes;

    private String secretKey;
}
