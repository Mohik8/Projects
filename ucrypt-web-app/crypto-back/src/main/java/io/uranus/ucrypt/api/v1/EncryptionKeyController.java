package io.uranus.ucrypt.api.v1;

import io.uranus.ucrypt.api.v1.resources.GenerateEncryptionKeyRequestResource;
import io.uranus.ucrypt.api.v1.resources.GenerateEncryptionKeyResponseResource;
import io.uranus.ucrypt.services.EncryptionKeyService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequiredArgsConstructor
public class EncryptionKeyController extends AbstractController implements EncryptionKeysApi {

    private final EncryptionKeyService encryptionKeyService;

    @Override
    public ResponseEntity<GenerateEncryptionKeyResponseResource> generateEncryptionKey(final GenerateEncryptionKeyRequestResource generateKeyRequest) {
        return ResponseEntity.ok()
                .body(this.encryptionKeyService.generateEncryptionKey(generateKeyRequest));
    }
}
