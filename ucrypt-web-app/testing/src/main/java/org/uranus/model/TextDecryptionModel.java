package org.uranus.model;

import lombok.Builder;

@Builder
public class TextDecryptionModel {
    public String ciphertext;
    public String algorithm;
    public String keyType;
    public String key;
    public String plaintext;
}
