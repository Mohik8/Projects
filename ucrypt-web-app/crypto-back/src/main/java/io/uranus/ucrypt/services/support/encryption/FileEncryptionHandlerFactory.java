package io.uranus.ucrypt.services.support.encryption;

import io.uranus.ucrypt.data.entities.enums.EncryptionAlgorithm;
import io.uranus.ucrypt.services.exceptions.BusinessException;
import io.uranus.ucrypt.services.support.encryption.impl.AesEncryptionHandler;
import io.uranus.ucrypt.services.support.encryption.impl.BlowfishEncryptionHandler;
import io.uranus.ucrypt.services.support.encryption.impl.TripleDesEncryptionHandler;
import org.springframework.context.ApplicationContext;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;

import java.util.EnumMap;
import java.util.Optional;

@Component
public class FileEncryptionHandlerFactory {

    private final EnumMap<EncryptionAlgorithm, Class> encryptionAlgorithmTypes = new EnumMap<>(EncryptionAlgorithm.class);
    private final ApplicationContext applicationContext;

    public FileEncryptionHandlerFactory(final ApplicationContext applicationContext) {
        this.applicationContext = applicationContext;
        initializeEncryptionAlgorithmTypesMap();
    }

    private void initializeEncryptionAlgorithmTypesMap() {
        this.encryptionAlgorithmTypes.put(EncryptionAlgorithm.AES, AesEncryptionHandler.class);
        this.encryptionAlgorithmTypes.put(EncryptionAlgorithm.TRIPLE_DES, TripleDesEncryptionHandler.class);
        this.encryptionAlgorithmTypes.put(EncryptionAlgorithm.BLOWFISH, BlowfishEncryptionHandler.class);
    }

    public FileEncryptionHandler getHandler(final EncryptionAlgorithm encryptionAlgorithm) {
        return (FileEncryptionHandler) Optional.of(this.applicationContext.getBean(this.encryptionAlgorithmTypes.get(encryptionAlgorithm)))
                .orElseThrow(() -> new BusinessException(HttpStatus.BAD_REQUEST, "invalid encryption algorithm"));
    }
}
