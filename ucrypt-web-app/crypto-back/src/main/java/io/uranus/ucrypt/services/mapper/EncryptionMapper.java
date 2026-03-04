package io.uranus.ucrypt.services.mapper;

import io.uranus.ucrypt.api.v1.resources.DecryptTextRequestResource;
import io.uranus.ucrypt.api.v1.resources.EncryptTextRequestResource;
import io.uranus.ucrypt.data.dtos.encryption.DecryptTextRequestDto;
import io.uranus.ucrypt.data.dtos.encryption.EncryptTextRequestDto;
import org.mapstruct.Mapper;

@Mapper(componentModel = "spring")
public interface EncryptionMapper {

    EncryptTextRequestDto map(EncryptTextRequestResource encryptTextRequestResource);

    DecryptTextRequestDto map(DecryptTextRequestResource decryptTextRequestResource);
}
