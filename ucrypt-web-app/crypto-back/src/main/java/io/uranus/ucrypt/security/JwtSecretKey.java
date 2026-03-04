package io.uranus.ucrypt.security;

import io.jsonwebtoken.security.Keys;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import javax.crypto.SecretKey;
import java.util.Base64;

@Configuration
@RequiredArgsConstructor
public class JwtSecretKey {
    private final JwtConfig jwtConfig;

    @Bean
    public SecretKey secretKey() {
        final var encodedSecretKey = Base64.getEncoder().encode(this.jwtConfig.getSecretKey().getBytes());
        return Keys.hmacShaKeyFor(encodedSecretKey);
    }
}
