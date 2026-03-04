package io.uranus.ucrypt.services.support.encryption.impl;

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
import org.springframework.core.io.InputStreamResource;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;

import javax.crypto.*;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.security.InvalidAlgorithmParameterException;
import java.security.InvalidKeyException;
import java.security.InvalidParameterException;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.util.Base64;

@Service
@RequiredArgsConstructor
@Slf4j
public class BlowfishEncryptionHandler implements EncryptionKeyHandler, FileEncryptionHandler, TextEncryptionHandler {

    private static final int KEY_SIZE = 256;
    private static final String ALGORITHM_NAME = "AES";
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
        } catch (final NoSuchAlgorithmException | InvalidParameterException e) {
            log.error(e.getMessage(), e);
            throw new BusinessException(HttpStatus.INTERNAL_SERVER_ERROR, "Error in generating encryption key for AES algorithm");
        }
    }

    @Override
    public boolean isValidEncryptionKey(final String encodedKey) {
        try {
            // throws IllegalArgumentException - if src is not in valid Base64
            final byte[] keyData = Base64.getDecoder().decode(encodedKey);
            final int encodedKeySize = keyData.length * Byte.SIZE;

            if (encodedKeySize == 128 || encodedKeySize == 192 || encodedKeySize == 256) {
                return true;
            }
        } catch (final IllegalArgumentException e) {
            return false;
        }

        return false;
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
            
            if (encryptionMode == Cipher.ENCRYPT_MODE) {
                return encryptFileData(cipher, secretKey, file);
            } else {
                return decryptFileData(cipher, secretKey, file);
            }
        } catch (final NoSuchAlgorithmException |
                       NoSuchPaddingException e) {
            log.error(e.getMessage(), e);
            throw new BusinessException(HttpStatus.INTERNAL_SERVER_ERROR,
                    String.format("Error in %s file for %s algorithm please contact the admin for more information!",
                            encryptionModeInString, ALGORITHM_NAME));
        } catch (final InvalidKeyException |
                       InvalidAlgorithmParameterException |
                       BadPaddingException |
                       IllegalBlockSizeException e) {
            log.info(e.getMessage(), e);
            throw new BusinessException(HttpStatus.BAD_REQUEST,
                    String.format("Error in %s file for %s algorithm please verify your key is correct",
                            encryptionModeInString, ALGORITHM_NAME));
        } catch (final IOException e) {
            log.error(e.getMessage(), e);
            throw new BusinessException(HttpStatus.BAD_REQUEST,
                    String.format("Error in %s file for %s algorithm please verify your file can be encrypted",
                            encryptionModeInString, ALGORITHM_NAME));
        }
    }

    private Resource encryptFileData(final Cipher cipher, final SecretKey secretKey, final byte[] file) 
            throws InvalidKeyException, InvalidAlgorithmParameterException, IOException, 
                   BadPaddingException, IllegalBlockSizeException {
        final byte[] iv = new byte[GCM_IV_LENGTH];
        new SecureRandom().nextBytes(iv);
        cipher.init(Cipher.ENCRYPT_MODE, secretKey, new GCMParameterSpec(GCM_TAG_LENGTH * 8, iv));
        
        final var outputStream = new ByteArrayOutputStream();
        outputStream.write(iv);
        outputStream.write(cipher.doFinal(file));
        outputStream.close();
        
        return new InputStreamResource(new ByteArrayInputStream(outputStream.toByteArray()));
    }

    private Resource decryptFileData(final Cipher cipher, final SecretKey secretKey, final byte[] file) 
            throws InvalidKeyException, InvalidAlgorithmParameterException, IOException, 
                   BadPaddingException, IllegalBlockSizeException {
        if (file.length < GCM_IV_LENGTH) {
            throw new IllegalArgumentException("Encrypted data is too short to contain IV");
        }
        
        final byte[] iv = new byte[GCM_IV_LENGTH];
        System.arraycopy(file, 0, iv, 0, GCM_IV_LENGTH);
        cipher.init(Cipher.DECRYPT_MODE, secretKey, new GCMParameterSpec(GCM_TAG_LENGTH * 8, iv));
        
        final byte[] encryptedData = new byte[file.length - GCM_IV_LENGTH];
        System.arraycopy(file, GCM_IV_LENGTH, encryptedData, 0, encryptedData.length);
        
        final byte[] decryptedData = cipher.doFinal(encryptedData);
        return new InputStreamResource(new ByteArrayInputStream(decryptedData));
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
            throw new BusinessException(HttpStatus.BAD_REQUEST, String.format("Encryption key for Algorithm %s is not a valid key!", ALGORITHM_NAME));
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
            
            if (encryptionMode == Cipher.ENCRYPT_MODE) {
                return performTextEncryption(cipher, secretKey, textInBytes);
            } else {
                return performTextDecryption(cipher, secretKey, textInBytes);
            }
        } catch (final NoSuchAlgorithmException |
                       NoSuchPaddingException e) {
            log.error(e.getMessage(), e);
            throw new BusinessException(HttpStatus.INTERNAL_SERVER_ERROR,
                    String.format("Error in %s text for %s algorithm please contact the admin for more information!",
                            encryptionModeInString, ALGORITHM_NAME));
        } catch (final InvalidKeyException |
                       InvalidAlgorithmParameterException |
                       BadPaddingException |
                       IllegalBlockSizeException e) {
            throw new BusinessException(HttpStatus.BAD_REQUEST,
                    String.format("Error in %s text for %s algorithm please verify your key is correct",
                            encryptionModeInString, ALGORITHM_NAME));
        }
    }

    private String performTextEncryption(final Cipher cipher, final SecretKey secretKey, final byte[] textInBytes) 
            throws InvalidKeyException, InvalidAlgorithmParameterException, 
                   BadPaddingException, IllegalBlockSizeException {
        final byte[] iv = new byte[GCM_IV_LENGTH];
        new SecureRandom().nextBytes(iv);
        cipher.init(Cipher.ENCRYPT_MODE, secretKey, new GCMParameterSpec(GCM_TAG_LENGTH * 8, iv));
        
        final byte[] cipherText = cipher.doFinal(textInBytes);
        final byte[] result = new byte[GCM_IV_LENGTH + cipherText.length];
        System.arraycopy(iv, 0, result, 0, GCM_IV_LENGTH);
        System.arraycopy(cipherText, 0, result, GCM_IV_LENGTH, cipherText.length);
        
        return Base64.getEncoder().encodeToString(result);
    }

    private String performTextDecryption(final Cipher cipher, final SecretKey secretKey, final byte[] textInBytes) 
            throws InvalidKeyException, InvalidAlgorithmParameterException, 
                   BadPaddingException, IllegalBlockSizeException {
        if (textInBytes.length < GCM_IV_LENGTH) {
            throw new IllegalArgumentException("Encrypted text too short");
        }
        
        final byte[] iv = new byte[GCM_IV_LENGTH];
        final byte[] cipherText = new byte[textInBytes.length - GCM_IV_LENGTH];
        System.arraycopy(textInBytes, 0, iv, 0, GCM_IV_LENGTH);
        System.arraycopy(textInBytes, GCM_IV_LENGTH, cipherText, 0, cipherText.length);
        
        cipher.init(Cipher.DECRYPT_MODE, secretKey, new GCMParameterSpec(GCM_TAG_LENGTH * 8, iv));
        return new String(cipher.doFinal(cipherText));
    }

    private SecretKey generateEncryptionSecretKey(final String encodedKey) {
        try {
            final byte[] decodedKey = Base64.getDecoder().decode(encodedKey);
            return new SecretKeySpec(decodedKey, 0, decodedKey.length, ALGORITHM_NAME);
        } catch (final IllegalArgumentException | ArrayIndexOutOfBoundsException e) {
            log.error(e.getMessage(), e);
            throw new BusinessException(HttpStatus.INTERNAL_SERVER_ERROR,
                    String.format("Error in generating encryption key for %s algorithm", ALGORITHM_NAME));
        }
    }
}
