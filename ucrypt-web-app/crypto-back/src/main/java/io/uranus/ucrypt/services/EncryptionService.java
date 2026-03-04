package io.uranus.ucrypt.services;

import io.uranus.ucrypt.api.v1.resources.*;
import io.uranus.ucrypt.data.dtos.encryption.DecryptFileRequestDto;
import io.uranus.ucrypt.data.dtos.encryption.EncryptFileRequestDto;
import io.uranus.ucrypt.services.exceptions.BusinessException;
import io.uranus.ucrypt.services.mapper.EncryptionAlgorithmMapper;
import io.uranus.ucrypt.services.mapper.EncryptionMapper;
import io.uranus.ucrypt.services.support.encryption.FileEncryptionHandlerFactory;
import io.uranus.ucrypt.services.support.encryption.TextEncryptionHandlerFactory;
import lombok.RequiredArgsConstructor;
import org.springframework.core.io.Resource;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class EncryptionService {

    private final FileEncryptionHandlerFactory fileEncryptionHandlerFactory;
    private final TextEncryptionHandlerFactory textEncryptionHandlerFactory;
    private final EncryptionAlgorithmMapper encryptionAlgorithmMapper;
    private final EncryptionMapper encryptionMapper;

    /**
     * Returns an encrypted file based on an encryption key which is in base64 string format
     * and one of the encryption algorithm that are available in the system.
     * both are used to encrypt the file in byte array format that is passed in the request
     * and return the encrypted resource.
     *
     * @param encryptFileRequestResource -> key: encryption key in base64 string format,
     *                                      file: file to be encrypted in byte array format,
     *                                      fileName: the name of the file that returned,
     *                                      fileType: the type of the file which will be returned,
     *                                      encryptionAlgorithm: the encryption algorithm that will be used.
     * @throws BusinessException 400 if {@code encryptFileRequestResource.key}
     * is not a valid key for the encryption algorithm provided;
     * or if {@code encryptFileRequestResource.encryptionAlgorithm}
     * is not a valid implemented algorithm by the system;
     * or if {@code encryptFileRequestResource.file}
     * is not a valid file and can't be encrypted (e.g: read-only file)
     * @return the encrypted file
     */
    @PreAuthorize("hasAnyRole('ADMIN', 'EMPLOYEE', 'USER')")
    public Resource encryptFile(final EncryptFileRequestResource encryptFileRequestResource) {
        final var encryptionAlgorithm = this.encryptionAlgorithmMapper.map(encryptFileRequestResource.getEncryptionAlgorithm());
        final var fileEncryptionHandler = this.fileEncryptionHandlerFactory.getHandler(encryptionAlgorithm);
        final var encryptFileRequestDto = EncryptFileRequestDto.builder()
                .key(encryptFileRequestResource.getKey())
                .file(encryptFileRequestResource.getFile())
                .build();
        return fileEncryptionHandler.encryptFile(encryptFileRequestDto);
    }

    /**
     * Returns a decrypted file based on an encryption key which is in base64 string format
     * and one of the encryption algorithm that are available in the system.
     * both are used to decrypt the encrypted file in byte array format that is passed in the request
     * and return the decrypted resource.
     *
     * @param decryptFileRequestResource -> key: encryption key in base64 string format,
     *                                      encryptedFile: file to be decrypted in byte array format,
     *                                      encryptedFileName: the name of the file which will be returned,
     *                                      encryptedFileType: the type of the file which will be returned,
     *                                      encryptionAlgorithm: the encryption algorithm that will be used.
     * @throws BusinessException 400 if {@code decryptFileRequestResource.key}
     * is not a valid key for the encryption algorithm provided;
     * or if the key wasn't the used key for encryption;
     * or if {@code decryptFileRequestResource.encryptionAlgorithm}
     * is not a valid implemented algorithm by the system;
     * or if {@code decryptFileRequestResource.encryptedFile}
     * is not a valid file and can't be decrypted (e.g: read-only file)
     * @return the encrypted file
     */
    @PreAuthorize("hasAnyRole('ADMIN', 'EMPLOYEE', 'USER')")
    public Resource decryptFile(final DecryptFileRequestResource decryptFileRequestResource) {
        final var encryptionAlgorithm = this.encryptionAlgorithmMapper.map(decryptFileRequestResource.getEncryptionAlgorithm());
        final var fileEncryptionHandler = this.fileEncryptionHandlerFactory.getHandler(encryptionAlgorithm);
        final var encryptFileRequestDto = DecryptFileRequestDto.builder()
                .key(decryptFileRequestResource.getKey())
                .encryptedFile(decryptFileRequestResource.getEncryptedFile())
                .build();
        return fileEncryptionHandler.decryptFile(encryptFileRequestDto);
    }

    /**
     * Returns an encrypted text based on an encryption key which is in base64 string format
     * and one of the encryption algorithm that are available in the system.
     * both are used to encrypt the text that is passed in the request
     * and return the encrypted text.
     *
     * @param encryptTextRequest -> key: encryption key in base64 string format,
     *                              text: text to be encrypted in string format,
     *                              encryptionAlgorithm: the encryption algorithm that will be used.
     * @throws BusinessException 400 if {@code encryptFileRequestResource.key}
     * is not a valid key for the encryption algorithm provided;
     * or if {@code encryptFileRequestResource.encryptionAlgorithm}
     * is not a valid implemented algorithm by the system;
     * @return the encrypted text
     */
    @PreAuthorize("hasAnyRole('ADMIN', 'EMPLOYEE', 'USER')")
    public EncryptTextResponseResource encryptText(final EncryptTextRequestResource encryptTextRequest) {
        final var encryptionAlgorithm = this.encryptionAlgorithmMapper.map(encryptTextRequest.getEncryptionAlgorithm());
        final var textEncryptionHandler = this.textEncryptionHandlerFactory.getHandler(encryptionAlgorithm);
        final var encryptedText = textEncryptionHandler.encryptText(this.encryptionMapper.map(encryptTextRequest));
        return new EncryptTextResponseResource().encryptedText(encryptedText);
    }

    /**
     * Returns a decrypted text based on an encryption key which is in base64 string format
     * and one of the encryption algorithm that are available in the system.
     * both are used to decrypt the text that is passed in the request
     * and returns the decrypted text.
     *
     * @param decryptTextRequest -> key: encryption key in base64 string format,
     *                              encryptedText: text to be decrypted in string format,
     *                              encryptionAlgorithm: the encryption algorithm that will be used.
     * @throws BusinessException 400 if {@code decryptTextRequest.key}
     * is not a valid key for the encryption algorithm provided;
     * or if {@code decryptTextRequest.encryptionAlgorithm}
     * is not a valid implemented algorithm by the system;
     * @return the decrypted text
     */
    @PreAuthorize("hasAnyRole('ADMIN', 'EMPLOYEE', 'USER')")
    public DecryptTextResponseResource decryptText(final DecryptTextRequestResource decryptTextRequest) {
        final var encryptionAlgorithm = this.encryptionAlgorithmMapper.map(decryptTextRequest.getEncryptionAlgorithm());
        final var textEncryptionHandler = this.textEncryptionHandlerFactory.getHandler(encryptionAlgorithm);
        final var decryptedText = textEncryptionHandler.decryptText(this.encryptionMapper.map(decryptTextRequest));
        return new DecryptTextResponseResource().decryptedText(decryptedText);
    }
}
