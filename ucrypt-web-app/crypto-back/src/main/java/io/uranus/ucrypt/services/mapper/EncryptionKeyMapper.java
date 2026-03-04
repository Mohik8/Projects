package io.uranus.ucrypt.services.mapper;

import io.uranus.ucrypt.api.v1.resources.EncryptionKeyListResource;
import io.uranus.ucrypt.data.entities.EncryptionKey;
import org.mapstruct.Mapper;

@Mapper(componentModel = "spring")
public interface EncryptionKeyMapper {

    EncryptionKeyListResource map(EncryptionKey encryptionKey);
}
