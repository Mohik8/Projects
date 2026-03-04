package io.uranus.ucrypt.services.support.encryption.impl;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.security.InvalidAlgorithmParameterException;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.util.Base64;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.KeyGenerator;
import javax.crypto.NoSuchPaddingException;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;

import org.springframework.core.io.InputStreamResource;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;

import io.uranus.ucrypt.api.v1.resources.GenerateEncryptionKeyResponseResource;
import io.uranus.ucrypt.data.dtos.encryption.DecryptFileRequestDto;
import io.uranus.ucrypt.data.dtos.encryption.DecryptTextRequestDto;
import io.uranus.ucrypt.data.dtos.encryption.EncryptFileRequestDto;
import io.uranus.ucrypt.data.dtos.encryption.EncryptTextRequestDto;
import io.uranus.ucrypt.services.exceptions.BusinessException;
import io.uranus.ucrypt.services.support.encryption.EncryptionKeyHandler;
import io.uranus.ucrypt.services.support.encryption.FileEncryptionHandler;
import io.uranus.ucrypt.services.support.encryption.TextEncryptionHandler;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Service
@RequiredArgsConstructor
@Slf4j
public class TripleDesEncryptionHandler implements EncryptionKeyHandler, FileEncryptionHandler, TextEncryptionHandler {

    private static final int KEY_SIZE = 256; 
    private static final String ALGORITHM_NAME = "AES";
    private static final String ALTERNATIVE_ALGORITHM_NAME = "TripleDES";
    private static final String TRANSFORMATION = "AES/GCM/NoPadding";
    private static final int GCM_IV_LENGTH = 12; // GCM recommended IV length
    private static final int GCM_TAG_LENGTH = 16; // GCM tag length in bytes

    @Override
    public GenerateEncryptionKeyResponseResource generateEncryptionKey() {
        try {
            final KeyGenerator keyGenerator = KeyGenerator.getInstance(ALGORITHM_NAME);
            keyGenerator.init(KEY_SIZE);
            final SecretKey key = keyGenerator.generateKey();
            return new GenerateEncryptionKeyResponseResource()
                    .key(Base64.getEncoder().encodeToString(key.getEncoded()));
        } catch (final NoSuchAlgorithmException e) {
            log.error(e.getMessage(), e);
            throw new BusinessException(HttpStatus.INTERNAL_SERVER_ERROR,
                    String.format("Error in generating encryption key for %s algorithm", ALTERNATIVE_ALGORITHM_NAME));
        }
    }

    @Override
    public boolean isValidEncryptionKey(final String encodedKey) {
        try {
            final byte[] keyData = Base64.getDecoder().decode(encodedKey);
            final int keyBitLength = keyData.length * Byte.SIZE;
            // Validate AES key sizes: 128, 192, or 256 bits
            return keyBitLength == 128 || keyBitLength == 192 || keyBitLength == 256;
        } catch (final IllegalArgumentException e) {
            return false;
        }
    }

    @Override
    public Resource encryptFile(final EncryptFileRequestDto encryptFileRequest) {
        final var key = encryptFileRequest.getKey();
        final var file = encryptFileRequest.getFile();

        validateKeyIsCorrect(key);

        return encryptOrDecryptFile(key, file, Cipher.ENCRYPT_MODE);
    }

    @Override
    public Resource decryptFile(final DecryptFileRequestDto decryptFileRequest) {
        final var key = decryptFileRequest.getKey();
        final var encryptedFile = decryptFileRequest.getEncryptedFile();

        validateKeyIsCorrect(key);

        return encryptOrDecryptFile(key, encryptedFile, Cipher.DECRYPT_MODE);
    }

    private Resource encryptOrDecryptFile(final String encodedKey, final byte[] file, final int encryptionMode) {
        final var encryptionModeInString = encryptionMode == Cipher.ENCRYPT_MODE ? "Encrypting" : "Decrypting";
        final var secretKey = generateEncryptionSecretKey(encodedKey);

        try {
            final Cipher cipher = Cipher.getInstance(TRANSFORMATION);
            final ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
            
            if (encryptionMode == Cipher.ENCRYPT_MODE) {
                // Generate and write IV first
                final byte[] iv = new byte[GCM_IV_LENGTH];
                new SecureRandom().nextBytes(iv);
                outputStream.write(iv);
                
                // Initialize cipher and encrypt
                cipher.init(encryptionMode, secretKey, new GCMParameterSpec(GCM_TAG_LENGTH * 8, iv));
                outputStream.write(cipher.doFinal(file));
            } else {
                // Validate file length and extract IV
                if (file.length < GCM_IV_LENGTH) {
                    throw new IllegalArgumentException("File too short for decryption");
                }
                
                final byte[] iv = new byte[GCM_IV_LENGTH];
                final byte[] encryptedData = new byte[file.length - GCM_IV_LENGTH];
                System.arraycopy(file, 0, iv, 0, GCM_IV_LENGTH);
                System.arraycopy(file, GCM_IV_LENGTH, encryptedData, 0, encryptedData.length);
                
                // Initialize cipher and decrypt
                cipher.init(encryptionMode, secretKey, new GCMParameterSpec(GCM_TAG_LENGTH * 8, iv));
                outputStream.write(cipher.doFinal(encryptedData));
            }
            
            return new InputStreamResource(new ByteArrayInputStream(outputStream.toByteArray()));
            
        } catch (final NoSuchAlgorithmException | NoSuchPaddingException e) {
            log.error(e.getMessage(), e);
            throw new BusinessException(HttpStatus.INTERNAL_SERVER_ERROR,
                    String.format("Error in %s file for %s algorithm please contact the admin for more information!",
                            encryptionModeInString, ALTERNATIVE_ALGORITHM_NAME));
        } catch (final InvalidKeyException | BadPaddingException | 
                       IllegalBlockSizeException | InvalidAlgorithmParameterException e) {
            log.info(e.getMessage(), e);
            throw new BusinessException(HttpStatus.BAD_REQUEST,
                    String.format("Error in %s file for %s algorithm please verify your key is correct",
                            encryptionModeInString, ALTERNATIVE_ALGORITHM_NAME));
        } catch (final IOException e) {
            log.error(e.getMessage(), e);
            throw new BusinessException(HttpStatus.BAD_REQUEST,
                    String.format("Error in %s file for %s algorithm please verify your file can be encrypted",
                            encryptionModeInString, ALTERNATIVE_ALGORITHM_NAME));
        }
    }

    @Override
    public String encryptText(final EncryptTextRequestDto encryptTextRequest) {
        final var encodedKey = encryptTextRequest.getKey();
        final var textToBeEncrypted = encryptTextRequest.getText();

        validateKeyIsCorrect(encodedKey);

        return encryptOrDecryptText(encodedKey, textToBeEncrypted.getBytes(), Cipher.ENCRYPT_MODE);
    }

    private void validateKeyIsCorrect(final String encodedKey) {
        if (!isValidEncryptionKey(encodedKey)) {
            throw new BusinessException(HttpStatus.BAD_REQUEST, String.format("Encryption key for Algorithm %s is not a valid key!", ALTERNATIVE_ALGORITHM_NAME));
        }
    }

    @Override
    public String decryptText(final DecryptTextRequestDto decryptTextRequest) {
        final var encodedKey = decryptTextRequest.getKey();
        final var encodedEncryptedText = decryptTextRequest.getEncryptedText();
        final var textToBeEncrypted = getDecodedText(encodedEncryptedText);

        validateKeyIsCorrect(encodedKey);

        return encryptOrDecryptText(encodedKey, textToBeEncrypted, Cipher.DECRYPT_MODE);
    }

    private byte[] getDecodedText(final String encodedEncryptedText) {
        try {
            return Base64.getDecoder().decode(encodedEncryptedText);
        } catch (final IllegalArgumentException e) {
            log.error(e.getMessage(), e);
            throw new BusinessException(HttpStatus.BAD_REQUEST, "Text to be decrypted must be in base64 format");
        }
    }

    private String encryptOrDecryptText(final String encodedKey, final byte[] textInBytes, final int encryptionMode) {
        final var encryptionModeInString = encryptionMode == Cipher.ENCRYPT_MODE ? "Encrypting" : "Decrypting";

        try {
            final var secretKey = generateEncryptionSecretKey(encodedKey);
            final Cipher cipher = Cipher.getInstance(TRANSFORMATION);
            
            byte[] result;
            
            if (encryptionMode == Cipher.ENCRYPT_MODE) {
                // Generate IV and encrypt
                final byte[] iv = new byte[GCM_IV_LENGTH];
                new SecureRandom().nextBytes(iv);
                cipher.init(encryptionMode, secretKey, new GCMParameterSpec(GCM_TAG_LENGTH * 8, iv));
                
                final byte[] encrypted = cipher.doFinal(textInBytes);
                result = new byte[GCM_IV_LENGTH + encrypted.length];
                System.arraycopy(iv, 0, result, 0, GCM_IV_LENGTH);
                System.arraycopy(encrypted, 0, result, GCM_IV_LENGTH, encrypted.length);
                
                return Base64.getEncoder().encodeToString(result);
            } else {
                // Extract IV and decrypt
                if (textInBytes.length < GCM_IV_LENGTH) {
                    throw new IllegalArgumentException("Invalid encrypted text length");
                }
                
                final byte[] iv = new byte[GCM_IV_LENGTH];
                final byte[] encrypted = new byte[textInBytes.length - GCM_IV_LENGTH];
                System.arraycopy(textInBytes, 0, iv, 0, GCM_IV_LENGTH);
                System.arraycopy(textInBytes, GCM_IV_LENGTH, encrypted, 0, encrypted.length);
                
                cipher.init(encryptionMode, secretKey, new GCMParameterSpec(GCM_TAG_LENGTH * 8, iv));
                result = cipher.doFinal(encrypted);
                
                return new String(result);
            }
        } catch (final NoSuchAlgorithmException | NoSuchPaddingException e) {
            log.error(e.getMessage(), e);
            throw new BusinessException(HttpStatus.INTERNAL_SERVER_ERROR,
                    String.format("Error in %s text for %s algorithm please contact the admin for more information!",
                            encryptionModeInString, ALTERNATIVE_ALGORITHM_NAME));
        } catch (final InvalidKeyException | BadPaddingException | 
                       IllegalBlockSizeException | InvalidAlgorithmParameterException e) {
            throw new BusinessException(HttpStatus.BAD_REQUEST,
                    String.format("Error in %s text for %s algorithm please verify your key is correct",
                            encryptionModeInString, ALTERNATIVE_ALGORITHM_NAME));
        }
    }

    private SecretKey generateEncryptionSecretKey(final String encodedKey) {
        try {
            final byte[] decodedKey = Base64.getDecoder().decode(encodedKey);
            return new SecretKeySpec(decodedKey, 0, decodedKey.length, ALGORITHM_NAME);
        } catch (final IllegalArgumentException | ArrayIndexOutOfBoundsException e) {
            log.error(e.getMessage(), e);
            throw new BusinessException(HttpStatus.INTERNAL_SERVER_ERROR,
                    String.format("Error in generating encryption key for %s algorithm", ALTERNATIVE_ALGORITHM_NAME));
        }
    }
}
