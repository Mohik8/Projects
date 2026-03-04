package io.uranus.ucrypt.data.entities;

import io.uranus.ucrypt.data.constants.AppConstants;
import io.uranus.ucrypt.data.entities.shared.AuditedEntity;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.hibernate.validator.constraints.Length;

import javax.persistence.*;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.Pattern;
import java.util.HashSet;
import java.util.Set;

@Entity
@Table(name = "roles")
@Getter
@Setter
@NoArgsConstructor
@Builder
public class Role extends AuditedEntity {

    @NotBlank
    @Pattern(regexp = AppConstants.NAME_REGEX, message = AppConstants.INVALID_NAME_REGEX_ERROR_MESSAGE)
    @Column(unique = true, nullable = false)
    private String name;

    @NotBlank
    @Length(min = AppConstants.MIN_NAME_LENGTH, max = AppConstants.MAX_NAME_LENGTH)
    @Pattern(regexp = AppConstants.NAME_REGEX, message = AppConstants.INVALID_NAME_REGEX_ERROR_MESSAGE)
    @Column(name = "display_name", unique = true, nullable = false)
    private String displayName;

    private String description;

    @OneToMany(mappedBy = "role")
    private Set<User> users = new HashSet<>();

    public Role(final String name, final String displayName, final String description, final Set<User> users) {
        this.name = name;
        this.displayName = displayName;
        this.description = description;
        this.users = users;
    }

    @Getter
    public enum RoleProperty {
        ADMIN(1L, "ADMIN", "Admin"),
        EMPLOYEE(2L, "EMPLOYEE", "Employee"),
        USER(3L, "USER", "User");

        private final long id;
        private final String name;
        private final String displayName;

        RoleProperty(final long id, final String name, final String displayName) {
            this.id = id;
            this.name = name;
            this.displayName = displayName;
        }
    }
}
