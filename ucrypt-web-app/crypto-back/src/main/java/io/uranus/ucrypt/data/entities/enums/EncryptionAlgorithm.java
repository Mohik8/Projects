package io.uranus.ucrypt.data.entities.enums;

import lombok.AllArgsConstructor;
import lombok.Getter;

@AllArgsConstructor
@Getter
public enum EncryptionAlgorithm {

    AES("aes", "AES"),
    TRIPLE_DES("triple_des", "Triple Des"),
    BLOWFISH("blowfish", "Blowfish");

    private String name;

    private String displayName;

}
