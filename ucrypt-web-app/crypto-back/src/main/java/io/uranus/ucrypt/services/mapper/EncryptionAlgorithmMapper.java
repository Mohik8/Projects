package io.uranus.ucrypt.services.mapper;

import io.uranus.ucrypt.api.v1.resources.EncryptionAlgorithmEnumResource;
import io.uranus.ucrypt.data.entities.enums.EncryptionAlgorithm;
import org.mapstruct.Mapper;

@Mapper(componentModel = "spring")
public interface EncryptionAlgorithmMapper {

    EncryptionAlgorithm map(EncryptionAlgorithmEnumResource encryptionAlgorithmEnum);
}
