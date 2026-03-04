package io.uranus.ucrypt.services;

import io.uranus.ucrypt.api.v1.resources.EncryptionAlgorithmResource;
import io.uranus.ucrypt.data.entities.enums.EncryptionAlgorithm;
import lombok.RequiredArgsConstructor;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Supplier;

@Service
@RequiredArgsConstructor
public class EncryptionAlgorithmService {

    /**
     * Returns a list of available encryption algorithms which are implemented and can be used in the system
     *
     * @return List of encryption algorithms
     */
    @PreAuthorize("hasAnyRole('ADMIN', 'EMPLOYEE', 'USER')")
    public List<EncryptionAlgorithmResource> getEncryptionAlgorithms() {
        final var encryptionAlgorithms = EncryptionAlgorithm.values();
        final var encryptionAlgorithmResources = new ArrayList<EncryptionAlgorithmResource>();
        for (final var encryptionAlgorithm : encryptionAlgorithms) {
            encryptionAlgorithmResources.add(constructEncryptionAlgorithmResource(encryptionAlgorithm));
        }

        return encryptionAlgorithmResources;
    }

    private EncryptionAlgorithmResource constructEncryptionAlgorithmResource(final EncryptionAlgorithm encryptionAlgorithm) {
        return new EncryptionAlgorithmResource()
                .name(encryptionAlgorithm.getName())
                .displayName(encryptionAlgorithm.getDisplayName());
    }
}
