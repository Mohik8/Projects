package io.uranus.ucrypt.api.v1;

import io.uranus.ucrypt.api.v1.resources.*;
import io.uranus.ucrypt.services.EncryptionService;
import lombok.RequiredArgsConstructor;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequiredArgsConstructor
public class EncryptionController extends AbstractController implements EncryptionApi {

    private final EncryptionService encryptionService;

    @Override
    public ResponseEntity<Resource> encryptFile(EncryptFileRequestResource encryptFileRequestResource) {
        return ResponseEntity
                .ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=" + encryptFileRequestResource.getFileName())
                .contentType(getMimeType(encryptFileRequestResource.getFileType()))
                .body(this.encryptionService.encryptFile(encryptFileRequestResource));
    }

    @Override
    public ResponseEntity<Resource> decryptFile(DecryptFileRequestResource decryptFileRequestResource) {
        return ResponseEntity
            .ok()
            .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=" + decryptFileRequestResource.getEncryptedFileName())
            .contentType(getMimeType(decryptFileRequestResource.getEncryptedFileType()))
            .body(this.encryptionService.decryptFile(decryptFileRequestResource));
    }

    @Override
    public ResponseEntity<EncryptTextResponseResource> encryptText(final EncryptTextRequestResource encryptTextRequestResource) {
        return ResponseEntity
                .ok()
                .body(this.encryptionService.encryptText(encryptTextRequestResource));
    }

    @Override
    public ResponseEntity<DecryptTextResponseResource> decryptText(final DecryptTextRequestResource decryptTextRequestResource) {
        return ResponseEntity
                .ok()
                .body(this.encryptionService.decryptText(decryptTextRequestResource));
    }
}
