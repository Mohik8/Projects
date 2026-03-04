#include "crypto.h"
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <openssl/err.h>
#include <string.h>
#include <stdio.h>

/* ── PBKDF2 key derivation ─────────────────────────────────────────────── */
int derive_key(const char *password, const uint8_t *salt, uint8_t *key)
{
    if (!PKCS5_PBKDF2_HMAC(password, (int)strlen(password),
                            salt, SALT_LEN,
                            PBKDF2_ITER,
                            EVP_sha256(),
                            KEY_LEN, key)) {
        fprintf(stderr, "[crypto] PBKDF2 failed: %s\n",
                ERR_error_string(ERR_get_error(), NULL));
        return -1;
    }
    return 0;
}

/* ── AES-256-GCM encrypt ───────────────────────────────────────────────── */
int aes_gcm_encrypt(const uint8_t *key,
                    uint8_t *iv,
                    const uint8_t *plaintext, size_t plaintext_len,
                    uint8_t *ciphertext,
                    uint8_t *tag)
{
    EVP_CIPHER_CTX *ctx = NULL;
    int len = 0, ciphertext_len = 0;
    int ret = -1;

    if (random_bytes(iv, IV_LEN) != 0) goto cleanup;

    ctx = EVP_CIPHER_CTX_new();
    if (!ctx) goto cleanup;

    if (EVP_EncryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, NULL, NULL) != 1)
        goto cleanup;
    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, IV_LEN, NULL) != 1)
        goto cleanup;
    if (EVP_EncryptInit_ex(ctx, NULL, NULL, key, iv) != 1)
        goto cleanup;
    if (EVP_EncryptUpdate(ctx, ciphertext, &len, plaintext,
                          (int)plaintext_len) != 1)
        goto cleanup;
    ciphertext_len = len;
    if (EVP_EncryptFinal_ex(ctx, ciphertext + len, &len) != 1)
        goto cleanup;
    ciphertext_len += len;
    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_GET_TAG, TAG_LEN, tag) != 1)
        goto cleanup;
    ret = ciphertext_len;

cleanup:
    if (ctx) EVP_CIPHER_CTX_free(ctx);
    return ret;
}

/* ── AES-256-GCM decrypt ───────────────────────────────────────────────── */
int aes_gcm_decrypt(const uint8_t *key,
                    const uint8_t *iv,
                    const uint8_t *ciphertext, size_t ciphertext_len,
                    const uint8_t *tag,
                    uint8_t *plaintext)
{
    EVP_CIPHER_CTX *ctx = NULL;
    int len = 0, plaintext_len = 0;
    int ret = -1;

    ctx = EVP_CIPHER_CTX_new();
    if (!ctx) goto cleanup;

    if (EVP_DecryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, NULL, NULL) != 1)
        goto cleanup;
    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, IV_LEN, NULL) != 1)
        goto cleanup;
    if (EVP_DecryptInit_ex(ctx, NULL, NULL, key, iv) != 1)
        goto cleanup;
    if (EVP_DecryptUpdate(ctx, plaintext, &len, ciphertext,
                          (int)ciphertext_len) != 1)
        goto cleanup;
    plaintext_len = len;

    /* Set expected tag before finalization */
    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_TAG, TAG_LEN,
                             (void *)tag) != 1)
        goto cleanup;
    if (EVP_DecryptFinal_ex(ctx, plaintext + len, &len) <= 0) {
        fprintf(stderr, "[crypto] Authentication tag mismatch – vault may be corrupted or tampered.\n");
        goto cleanup;
    }
    plaintext_len += len;
    ret = plaintext_len;

cleanup:
    if (ctx) EVP_CIPHER_CTX_free(ctx);
    return ret;
}

/* ── Secure random bytes ───────────────────────────────────────────────── */
int random_bytes(uint8_t *buf, size_t len)
{
    if (RAND_bytes(buf, (int)len) != 1) {
        fprintf(stderr, "[crypto] RAND_bytes failed\n");
        return -1;
    }
    return 0;
}
