package io.uranus.ucrypt.config;

import io.uranus.ucrypt.data.entities.User;
import io.uranus.ucrypt.data.repositories.UserRepository;
import org.hibernate.FlushMode;
import org.hibernate.Session;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.AuditorAware;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;

import javax.persistence.EntityManager;
import java.util.Optional;

@Component
public class CustomAuditAware implements AuditorAware<User> {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private EntityManager entityManager;

    @Override
     public Optional<User> getCurrentAuditor() {
        if (SecurityContextHolder.getContext().getAuthentication() == null ||
                !(SecurityContextHolder.getContext().getAuthentication().getPrincipal() instanceof org.springframework.security.core.userdetails.User)
        ) {
            return Optional.empty();
        }

        final var applicationUser = (org.springframework.security.core.userdetails.User) SecurityContextHolder
                .getContext().getAuthentication().getPrincipal();
        final var userEmail = applicationUser.getUsername();
        if (userEmail == null) {
            return Optional.empty();
        }

        final var currentSession = this.entityManager.unwrap(Session.class);
        final var originalHibernateFlushMode = currentSession.getHibernateFlushMode();
        currentSession.setHibernateFlushMode(FlushMode.MANUAL);
        final var user = this.userRepository.findByEmail(userEmail).orElseThrow();
        currentSession.setHibernateFlushMode(originalHibernateFlushMode);
        return Optional.of(user);
    }
}