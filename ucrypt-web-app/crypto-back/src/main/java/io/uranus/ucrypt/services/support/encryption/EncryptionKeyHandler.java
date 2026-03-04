package io.uranus.ucrypt.services.support.encryption;

import io.uranus.ucrypt.api.v1.resources.GenerateEncryptionKeyResponseResource;

public interface EncryptionKeyHandler {

    GenerateEncryptionKeyResponseResource generateEncryptionKey();

    boolean isValidEncryptionKey(String encodedKey);
}
