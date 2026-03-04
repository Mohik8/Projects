#ifndef AES_H
#define AES_H

#include <stdint.h>
#include <stddef.h>

#define AES_BLOCK  16   /* bytes */
#define AES128_KEY 16   /* bytes */
#define AES128_RKS 176  /* 11 round keys * 16 bytes */

typedef struct { uint8_t rk[AES128_RKS]; } AES128_CTX;

/* Key schedule */
void aes128_init(AES128_CTX *ctx, const uint8_t key[AES128_KEY]);

/* Single-block (raw) */
void aes128_encrypt_block(const AES128_CTX *ctx,
                          const uint8_t in[AES_BLOCK],
                          uint8_t out[AES_BLOCK]);
void aes128_decrypt_block(const AES128_CTX *ctx,
                          const uint8_t in[AES_BLOCK],
                          uint8_t out[AES_BLOCK]);

/* ECB mode — len must be a multiple of AES_BLOCK */
void aes128_ecb_encrypt(const AES128_CTX *ctx,
                        const uint8_t *in, uint8_t *out, size_t len);
void aes128_ecb_decrypt(const AES128_CTX *ctx,
                        const uint8_t *in, uint8_t *out, size_t len);

/* CBC mode — len must be a multiple of AES_BLOCK */
void aes128_cbc_encrypt(const AES128_CTX *ctx, const uint8_t iv[AES_BLOCK],
                        const uint8_t *in, uint8_t *out, size_t len);
void aes128_cbc_decrypt(const AES128_CTX *ctx, const uint8_t iv[AES_BLOCK],
                        const uint8_t *in, uint8_t *out, size_t len);

#endif /* AES_H */
