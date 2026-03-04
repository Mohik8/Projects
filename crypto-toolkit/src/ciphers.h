#ifndef CIPHERS_H
#define CIPHERS_H

#include <stddef.h>
#include <stdint.h>

/* ── Caesar cipher ───────────────────────────────────────────────────── */
/* Encrypt / decrypt in-place (alpha chars only, preserves case).
   shift: 0–25 for encrypt, (26 - shift) for decrypt, or just pass -shift */
void caesar_encrypt(char *text, int shift);
void caesar_decrypt(char *text, int shift);
void caesar_bruteforce(const char *ciphertext); /* prints all 25 candidates */

/* ── Vigenere cipher ─────────────────────────────────────────────────── */
/* key: alpha string (any case).  text: alpha + spaces (non-alpha passed) */
void vigenere_encrypt(char *text, const char *key);
void vigenere_decrypt(char *text, const char *key);

/* ── XOR stream cipher ───────────────────────────────────────────────── */
/* key_hex: hex string like "DEADBEEF".
   out must be at least len bytes.  Returns 0 on success, -1 on bad key. */
int xor_crypt(const uint8_t *in, size_t len, const char *key_hex, uint8_t *out);

#endif /* CIPHERS_H */
