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
import javax.validation.constraints.NotNull;

@Entity
@Table(name = "encryption_keys", indexes = {
        @Index(name = "idx_encryption_keys_user_id", columnList = "user_id")
})
@Getter
@Setter
@NoArgsConstructor
@Builder
public class EncryptionKey extends AuditedEntity {

    @NotBlank
    @Length(min = AppConstants.MIN_NAME_LENGTH, max = AppConstants.MAX_NAME_LENGTH)
    @Column(nullable = false)
    private String value;

    @NotNull
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    public EncryptionKey(final String value, final User user) {
        this.value = value;
        this.user = user;
    }
}
