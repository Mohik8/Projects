package io.uranus.ucrypt.security;

import io.jsonwebtoken.ExpiredJwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.MalformedJwtException;
import io.jsonwebtoken.UnsupportedJwtException;
import io.jsonwebtoken.security.SignatureException;
import io.uranus.ucrypt.services.exceptions.BusinessException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.security.authentication.AuthenticationCredentialsNotFoundException;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.util.Date;
import java.util.stream.Collectors;

@Component
@RequiredArgsConstructor
@Slf4j
public class JwtGenerator {

    private final JwtConfig jwtConfig;

    private final SecretKey secretKey;

    public String generateToken(final Authentication authentication) {
        final var email = authentication.getName();
        final var currentDate = new Date();
        final var expirationDate = new Date(currentDate.getTime() + (this.jwtConfig.getExpirationInMinutes() * 60 * 1000));

        final var authority = authentication.getAuthorities().stream()
                .findFirst()
                .orElseThrow(() -> new BusinessException(HttpStatus.INTERNAL_SERVER_ERROR, "No role assigned to user!"));

        return Jwts.builder()
                .claim("role", authority.getAuthority().substring(5))
                .setSubject(email)
                .setIssuedAt(currentDate)
                .setExpiration(expirationDate)
                .signWith(this.secretKey)
                .compact();
    }

    public String getEmailFromJwt(final String token) {
        final var claims = Jwts.parserBuilder()
                .setSigningKey(this.secretKey)
                .build()
                .parseClaimsJws(token);

        return claims.getBody().getSubject();
    }

    public boolean validateToken(final String token) {
        try {
            Jwts.parserBuilder()
                    .setSigningKey(this.secretKey)
                    .build()
                    .parseClaimsJws(token);

            return true;
        } catch (final ExpiredJwtException | UnsupportedJwtException | MalformedJwtException |
                       SignatureException | IllegalArgumentException e) {
            log.error(e.getMessage(), e);
            throw new AuthenticationCredentialsNotFoundException("Jwt was expired or incorrect");
        }
    }

}
