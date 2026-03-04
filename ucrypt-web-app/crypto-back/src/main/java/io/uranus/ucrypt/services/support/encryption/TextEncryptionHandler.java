package io.uranus.ucrypt.services.support.encryption;

import io.uranus.ucrypt.data.dtos.encryption.DecryptTextRequestDto;
import io.uranus.ucrypt.data.dtos.encryption.EncryptTextRequestDto;

public interface TextEncryptionHandler {

    String encryptText(EncryptTextRequestDto encryptTextRequest);

    String decryptText(DecryptTextRequestDto decryptTextRequest);
}
