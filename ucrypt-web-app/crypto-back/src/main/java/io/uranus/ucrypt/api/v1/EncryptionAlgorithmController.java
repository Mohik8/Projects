package io.uranus.ucrypt.api.v1;

import io.uranus.ucrypt.api.v1.resources.EncryptionAlgorithmResource;
import io.uranus.ucrypt.services.EncryptionAlgorithmService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequiredArgsConstructor
public class EncryptionAlgorithmController extends AbstractController implements EncryptionAlgorithmsApi {

    private final EncryptionAlgorithmService encryptionAlgorithmService;

    @Override
    public ResponseEntity<List<EncryptionAlgorithmResource>> getEncryptionAlgorithms() {
        return ResponseEntity.ok()
                .body(this.encryptionAlgorithmService.getEncryptionAlgorithms());
    }
}
