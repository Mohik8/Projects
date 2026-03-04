package io.uranus.ucrypt.data.repositories;

import io.uranus.ucrypt.data.entities.EncryptionKey;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.stereotype.Repository;

@Repository
public interface EncryptionKeyRepository extends JpaRepository<EncryptionKey, Long>, JpaSpecificationExecutor<EncryptionKey> {
}
