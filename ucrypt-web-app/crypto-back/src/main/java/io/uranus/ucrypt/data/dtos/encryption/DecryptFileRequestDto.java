package io.uranus.ucrypt.data.dtos.encryption;

import lombok.Builder;
import lombok.Getter;
import lombok.Setter;
import org.springframework.web.multipart.MultipartFile;

@Getter
@Setter
@Builder
public class DecryptFileRequestDto {

    private String key;

    private byte[] encryptedFile;
}
