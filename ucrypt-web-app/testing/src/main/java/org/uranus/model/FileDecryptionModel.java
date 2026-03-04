package org.uranus.model;

import lombok.Builder;

@Builder
public class FileDecryptionModel {
    public String filePath;
    public String algorithm;
    public String keyType;
    public String key;
}
