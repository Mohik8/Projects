#include "ciphers.h"
#include "utils.h"
#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <stdint.h>
#include <stdlib.h>

/* ── Caesar ──────────────────────────────────────────────────────────── */

void caesar_encrypt(char *text, int shift)
{
    shift = ((shift % 26) + 26) % 26;
    for (char *p = text; *p; p++) {
        if (isupper((unsigned char)*p))
            *p = (char)((*p - 'A' + shift) % 26 + 'A');
        else if (islower((unsigned char)*p))
            *p = (char)((*p - 'a' + shift) % 26 + 'a');
    }
}

void caesar_decrypt(char *text, int shift)
{
    caesar_encrypt(text, 26 - ((shift % 26 + 26) % 26));
}

void caesar_bruteforce(const char *ciphertext)
{
    printf(COL_CYAN "  Brute-force (all 25 shifts):\n" COL_RESET);
    for (int s = 1; s <= 25; s++) {
        char buf[512];
        strncpy(buf, ciphertext, sizeof(buf) - 1);
        buf[sizeof(buf) - 1] = '\0';
        caesar_decrypt(buf, s);
        printf("  " COL_DIM "shift=%-3d" COL_RESET "  %s\n", s, buf);
    }
}

/* ── Vigenere ────────────────────────────────────────────────────────── */

void vigenere_encrypt(char *text, const char *key)
{
    size_t klen = strlen(key);
    size_t ki = 0;
    for (char *p = text; *p; p++) {
        if (isalpha((unsigned char)*p)) {
            int k = tolower((unsigned char)key[ki % klen]) - 'a';
            if (isupper((unsigned char)*p))
                *p = (char)((*p - 'A' + k) % 26 + 'A');
            else
                *p = (char)((*p - 'a' + k) % 26 + 'a');
            ki++;
        }
    }
}

void vigenere_decrypt(char *text, const char *key)
{
    size_t klen = strlen(key);
    size_t ki = 0;
    for (char *p = text; *p; p++) {
        if (isalpha((unsigned char)*p)) {
            int k = tolower((unsigned char)key[ki % klen]) - 'a';
            if (isupper((unsigned char)*p))
                *p = (char)((*p - 'A' - k + 26) % 26 + 'A');
            else
                *p = (char)((*p - 'a' - k + 26) % 26 + 'a');
            ki++;
        }
    }
}

/* ── XOR ─────────────────────────────────────────────────────────────── */

int xor_crypt(const uint8_t *in, size_t len, const char *key_hex, uint8_t *out)
{
    uint8_t key[256];
    size_t  klen = 0;

    if (hex_to_bytes(key_hex, key, &klen) != 0 || klen == 0)
        return -1;

    for (size_t i = 0; i < len; i++)
        out[i] = in[i] ^ key[i % klen];

    return 0;
}
