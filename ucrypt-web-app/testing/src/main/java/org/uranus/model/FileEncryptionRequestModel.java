package org.uranus.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.NoArgsConstructor;

@NoArgsConstructor
@AllArgsConstructor
@Builder
public class FileEncryptionRequestModel {
    public String filePath;
    public String algorithm;
    public String key;
}
