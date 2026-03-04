package io.uranus.ucrypt.services;

import io.uranus.ucrypt.api.v1.resources.CreateEncryptionKeyResource;
import io.uranus.ucrypt.api.v1.resources.EncryptionKeyListResource;
import io.uranus.ucrypt.api.v1.resources.GenerateEncryptionKeyRequestResource;
import io.uranus.ucrypt.api.v1.resources.GenerateEncryptionKeyResponseResource;
import io.uranus.ucrypt.data.entities.EncryptionKey;
import io.uranus.ucrypt.data.entities.User;
import io.uranus.ucrypt.data.repositories.EncryptionKeyRepository;
import io.uranus.ucrypt.data.repositories.UserRepository;
import io.uranus.ucrypt.services.exceptions.BusinessException;
import io.uranus.ucrypt.services.mapper.EncryptionAlgorithmMapper;
import io.uranus.ucrypt.services.mapper.EncryptionKeyMapper;
import io.uranus.ucrypt.services.support.encryption.EncryptionKeyHandlerFactory;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.persistence.EntityManager;

@Service
@RequiredArgsConstructor
public class EncryptionKeyService {

    private final EncryptionKeyRepository encryptionKeyRepository;

    private final EncryptionKeyHandlerFactory encryptionKeyHandlerFactory;

    private final EncryptionKeyMapper encryptionKeyMapper;

    private final EncryptionAlgorithmMapper encryptionAlgorithmMapper;

    private final User curretUser;

    private final UserRepository userRepository;

    private final EntityManager entityManager;

    /**
     * Returns Generated key that is used for encryption and decryption for both files and text
     * which gets generated based on the selected encryption algorithms that are available in the system
     *
     * @param generateKeyRequest contains the encryption algorithm for generating the key
     * @return generated key
     */
    @PreAuthorize("hasAnyRole('ADMIN', 'EMPLOYEE', 'USER')")
    public GenerateEncryptionKeyResponseResource generateEncryptionKey(final GenerateEncryptionKeyRequestResource generateKeyRequest) {
        final var encryptionAlgorithm = this.encryptionAlgorithmMapper.map(generateKeyRequest.getEncryptionAlgorithm());
        final var encryptionKeyHandler = this.encryptionKeyHandlerFactory.getHandler(encryptionAlgorithm);
        return encryptionKeyHandler.generateEncryptionKey();
    }


    /**
     * Returns a paginated result of encryption keys that the user saved based on the pageable object which defines
     * how many rows does a page contain, the page number that should be return and how will the page will be sorted,
     * and the specificationFrom which will filter the data based on specific conditions.
     *
     * @param specificationFrom specification used to filter the data
     * @param pageOf pageable used to paginate the data
     * @return page of encryption keys
     */
    @PreAuthorize("hasAnyRole('ADMIN', 'EMPLOYEE', 'USER')")
    @Transactional(readOnly = true)
    public Page<EncryptionKeyListResource> getEncryptionKeysForCurrentUser(final Specification<EncryptionKey> specificationFrom,
                                                                           final Pageable pageOf) {
        final var updatedSpecification = specificationFrom.and(this.filterByUser(this.curretUser));
        final var encryptionKeysPage = this.encryptionKeyRepository.findAll(updatedSpecification, pageOf);
        return encryptionKeysPage.map(this.encryptionKeyMapper::map);
    }

    private Specification<EncryptionKey> filterByUser(final User curretUser) {
        return (root, query, criteriaBuilder) ->
                criteriaBuilder.equal(root.get("user").get("id"), curretUser.getId());
    }

    /**
     * Creates an encryption key for current user by first validating the encryption key based on the encryption
     * algorithm that is passed and saves the encryption key in the database.
     *
     * @param createEncryptionKeyResource -> value: encryption key value as base64 string,
     *                                   encryptionAlgorithm: encryption algorithm
     * @throws BusinessException 400 if {@code createEncryptionKeyResource.value}
     * is not a valid key for the encryption algorithm provided
     * */
    @PreAuthorize("hasAnyRole('ADMIN', 'EMPLOYEE', 'USER')")
    @Transactional
    public void createEncryptionKeyForCurrentUser(final CreateEncryptionKeyResource createEncryptionKeyResource) {
        final var userId = this.curretUser.getId();
        final var encryptionKeyValue = createEncryptionKeyResource.getValue();
        final var updateUserStatusQueryAsString = "INSERT INTO encryption_keys " +
                "(created_at, updated_at, created_by_user_id, last_modified_by_user_id, user_id, value) " +
                "VALUES (NOW(), NOW(), " + userId + ", " + userId + ", " + userId + ", '" + encryptionKeyValue + "');";
        final var updateUserStatusQuery = this.entityManager.createNativeQuery(updateUserStatusQueryAsString, User.class);
        updateUserStatusQuery.executeUpdate();
    }
}
