package org.uranus.model;

import lombok.Builder;

@Builder
public class TextEncryptionModel {
    public String plaintext;
    public String algorithm;
    public String key;
    public String cipherText;
}
