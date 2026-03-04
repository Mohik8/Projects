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

@Entity
@Table(name = "files")
@Getter
@Setter
@NoArgsConstructor
public class File extends AuditedEntity {

    @NotBlank
    @Length(min = AppConstants.MIN_FILE_NAME_LENGTH, max = AppConstants.MAX_FILE_NAME_LENGTH)
    @Column(nullable = false, unique = true)
    private String name;

    @NotBlank
    @Column(nullable = false, unique = true)
    private String path;

    @NotBlank
    @Column(nullable = false)
    private String contentType;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @Builder
    public File(final String name, final String path, final String contentType, final User user) {
        this.name = name;
        this.path = path;
        this.contentType = contentType;
        this.user = user;
    }
}
