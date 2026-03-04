#ifndef CRYPTO_H
#define CRYPTO_H

#include <stdint.h>
#include <stddef.h>

#define KEY_LEN       32   /* AES-256 */
#define IV_LEN        12   /* GCM recommended */
#define TAG_LEN       16
#define SALT_LEN      32
#define PBKDF2_ITER   200000

/*
 * Derive a 256-bit key from a master password using PBKDF2-HMAC-SHA256.
 * salt  - SALT_LEN random bytes (caller provides)
 * key   - output buffer of KEY_LEN bytes
 * Returns 0 on success, -1 on failure.
 */
int derive_key(const char *password, const uint8_t *salt, uint8_t *key);

/*
 * Encrypt plaintext with AES-256-GCM.
 * iv       - IV_LEN random bytes written here by callee
 * tag      - TAG_LEN authentication tag written here by callee
 * ciphertext must be at least plaintext_len bytes.
 * Returns ciphertext_len on success, -1 on failure.
 */
int aes_gcm_encrypt(const uint8_t *key,
                    uint8_t *iv,
                    const uint8_t *plaintext, size_t plaintext_len,
                    uint8_t *ciphertext,
                    uint8_t *tag);

/*
 * Decrypt ciphertext with AES-256-GCM.
 * Returns plaintext_len on success, -1 on authentication failure.
 */
int aes_gcm_decrypt(const uint8_t *key,
                    const uint8_t *iv,
                    const uint8_t *ciphertext, size_t ciphertext_len,
                    const uint8_t *tag,
                    uint8_t *plaintext);

/* Fill buf with len cryptographically random bytes. Returns 0 on success. */
int random_bytes(uint8_t *buf, size_t len);

#endif /* CRYPTO_H */
