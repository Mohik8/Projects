#ifndef VISUALS_H
#define VISUALS_H

#include <stdint.h>
#include <stddef.h>

/* Visual step-by-step demos — each prints a rich terminal display */
void vis_caesar   (const char *plaintext, int shift);
void vis_vigenere (const char *plaintext, const char *key);
void vis_xor      (const char *plaintext, const char *key_hex);
void vis_base64   (const char *plaintext);
void vis_aes      (const char *plaintext, const uint8_t key[16], const uint8_t iv[16]);
void vis_bruteforce(const char *ciphertext, int answer_shift);

#endif
