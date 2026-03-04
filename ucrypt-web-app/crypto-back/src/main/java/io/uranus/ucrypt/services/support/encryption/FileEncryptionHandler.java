package io.uranus.ucrypt.services.support.encryption;

import io.uranus.ucrypt.data.dtos.encryption.DecryptFileRequestDto;
import io.uranus.ucrypt.data.dtos.encryption.EncryptFileRequestDto;
import org.springframework.core.io.Resource;

public interface FileEncryptionHandler {

    Resource encryptFile(EncryptFileRequestDto encryptFileRequest);

    Resource decryptFile(DecryptFileRequestDto decryptFileRequest);
}
