package io.uranus.ucrypt.data.dtos.encryption;

import lombok.Builder;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@Builder
public class EncryptTextRequestDto {

    private String key;

    private String text;
}
