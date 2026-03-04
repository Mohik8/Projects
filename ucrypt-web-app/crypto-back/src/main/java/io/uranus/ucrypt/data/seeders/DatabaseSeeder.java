package io.uranus.ucrypt.data.seeders;

import io.uranus.ucrypt.data.entities.Role;
import io.uranus.ucrypt.data.entities.User;
import io.uranus.ucrypt.data.repositories.RoleRepository;
import io.uranus.ucrypt.data.repositories.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.event.ContextRefreshedEvent;
import org.springframework.context.event.EventListener;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import static io.uranus.ucrypt.data.entities.enums.UserStatus.ACTIVE;

@Component
@RequiredArgsConstructor
public class DatabaseSeeder {

    private final UserRepository userRepository;
    private final RoleRepository roleRepository;
    private final PasswordEncoder passwordEncoder;

    @Value("${main-account.email}")
    private String mainAccEmail;
    @Value("${main-account.password}")
    private String mainAccPassword;

    @EventListener
    @Transactional
    public void seed(final ContextRefreshedEvent event) {
        this.seedMainUsers();
    }

    private void seedMainUsers() {
        if(this.userRepository.existsByEmail(this.mainAccEmail)) {
            return;
        }

        final var adminRole = this.roleRepository.findByName(Role.RoleProperty.ADMIN.getName())
                .orElseThrow();

        final var employeeRole = this.roleRepository.findByName(Role.RoleProperty.EMPLOYEE.getName())
                .orElseThrow();

        final var encodedPassword= this.passwordEncoder.encode(this.mainAccPassword);
        this.userRepository.save(User.builder()
                .name("Admin")
                .email(this.mainAccEmail)
                .password(encodedPassword)
                .role(adminRole)
                .status(ACTIVE)
                .build());

        this.userRepository.save(User.builder()
                .name("Jeanne Lagasse – Founder & Chairman")
                .email("jeanne.lagasse@uranus.com")
                .password(this.passwordEncoder.encode("X#abcRT"))
                .role(employeeRole)
                .status(ACTIVE)
                .build());

        this.userRepository.save(User.builder()
                .name("Ayesha Al Chamy – CEO")
                .email("ayesha.alchamy@uranus.com")
                .password(this.passwordEncoder.encode("Oranus$%34"))
                .role(employeeRole)
                .status(ACTIVE)
                .build());

        this.userRepository.save(User.builder()
                .name("Amy Keita – CFO")
                .email("amy.keita@uranus.com")
                .password(this.passwordEncoder.encode("L@guna546"))
                .role(employeeRole)
                .status(ACTIVE)
                .build());
                
        this.userRepository.save(User.builder()
                .name("Kumar Viswanath - CTO")
                .email("kumar.viswanath@uranus.com")
                .password(this.passwordEncoder.encode("@lphaG@mma"))
                .role(employeeRole)
                .status(ACTIVE)
                .build());

        this.userRepository.save(User.builder()
                .name("Lin Zhang - SVP of Worldwide Sales")
                .email("lin.zhang@uranus.com")
                .password(this.passwordEncoder.encode("BetaW0rld56"))
                .role(employeeRole)
                .status(ACTIVE)
                .build());

        this.userRepository.save(User.builder()
                .name("Ahmad Alezani – VP of Engineering")
                .email("ahmad.alezani@uranus.com")
                .password(this.passwordEncoder.encode("tryABX90&"))
                .role(employeeRole)
                .status(ACTIVE)
                .build());

        this.userRepository.save(User.builder()
                .name("Wei Wang – Chief   Information Officer")
                .email("wei.wang@uranus.com")
                .password(this.passwordEncoder.encode("poiuytrew"))
                .role(employeeRole)
                .status(ACTIVE)
                .build());
    }
}
