package io.uranus.ucrypt.security;

import io.uranus.ucrypt.data.entities.enums.UserStatus;
import io.uranus.ucrypt.data.repositories.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

import java.util.HashSet;
import java.util.Set;

@Service
@RequiredArgsConstructor
public class CustomUserDetailsService implements UserDetailsService {

    private final UserRepository userRepository;

    @Override
    public UserDetails loadUserByUsername(final String email) throws UsernameNotFoundException {
        final var user = this.userRepository.findByEmailAndStatus(email, UserStatus.ACTIVE)
                .orElseThrow(() -> new UsernameNotFoundException("user with this email not found!"));
        return new User(user.getEmail(), user.getPassword(), getAuthoritiesOfUser(user));
    }

    private Set<SimpleGrantedAuthority> getAuthoritiesOfUser(final io.uranus.ucrypt.data.entities.User user) {
        final var authorities = new HashSet<SimpleGrantedAuthority>();
        authorities.add(new SimpleGrantedAuthority("ROLE_" + user.getRole().getName()));

        return authorities;
    }
}
