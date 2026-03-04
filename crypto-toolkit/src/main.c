/*
 * main.c  — CryptKit: C Cryptography Toolkit
 *
 * Usage (interactive):   cryptkit
 * Usage (one-shot):
 *   cryptkit caesar   <enc|dec|bf>   "<text>"  -k <shift>
 *   cryptkit vigenere <enc|dec>      "<text>"  -k <keyword>
 *   cryptkit xor      <enc|dec>      "<text>"  -k <hex_key>
 *   cryptkit aes      <enc|dec>      "<text>"  -k <32-hex-key>  [-m ecb|cbc]
 *   cryptkit base64   <enc|dec>      "<text>"
 *   cryptkit demo
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "utils.h"
#include "ciphers.h"
#include "base64.h"
#include "aes.h"
#include "visuals.h"

/* ── Visual demo ─────────────────────────────────────────────────────── */

static void run_visual_demo(void)
{
    const uint8_t key[16] = {
        0x2b,0x7e,0x15,0x16,0x28,0xae,0xd2,0xa6,
        0xab,0xf7,0x15,0x88,0x09,0xcf,0x4f,0x3c
    };
    const uint8_t iv[16] = {
        0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,
        0x08,0x09,0x0a,0x0b,0x0c,0x0d,0x0e,0x0f
    };
    vis_caesar   ("Hello World",      13);
    vis_vigenere ("Hello World",      "CRYPTO");
    vis_xor      ("SecretMsg",        "DEADBEEF");
    vis_base64   ("Man landed on Moon");
    vis_aes      ("AES-128 in C!!!",  key, iv);
    vis_bruteforce("Khoor, Zruog!",   3);
}

/* ── Demo ────────────────────────────────────────────────────────────── */

static void run_demo(void)
{
    printf(COL_MAGENTA "\n  ╔══════════════════════════════════════════════════╗\n");
    printf(           "  ║            FULL CRYPTOGRAPHY DEMO                ║\n");
    printf(           "  ╚══════════════════════════════════════════════════╝\n\n" COL_RESET);

    /* ── 1. Caesar ─────────────────────────────────────────────────── */
    printf(COL_YELLOW "  ━━━  [1] CAESAR CIPHER  ━━━\n" COL_RESET);
    {
        const char *original = "Attack at dawn!";
        char plain[64], enc[64];
        strcpy(plain, original); strcpy(enc, original);
        caesar_encrypt(enc, 13);
        printf("  Plaintext  : " COL_WHITE "%s\n" COL_RESET, plain);
        printf("  Shift      : " COL_GREEN "13\n" COL_RESET);
        printf("  Ciphertext : " COL_RED   "%s\n" COL_RESET, enc);
        caesar_decrypt(enc, 13);
        printf("  Decrypted  : " COL_GREEN "%s\n\n" COL_RESET, enc);
    }

    /* ── 2. Vigenere ───────────────────────────────────────────────── */
    printf(COL_YELLOW "  ━━━  [2] VIGENERE CIPHER  ━━━\n" COL_RESET);
    {
        const char *key  = "CRYPTO";
        char plain[64]   = "Hello World From C";
        char enc[64];
        strcpy(enc, plain);
        vigenere_encrypt(enc, key);
        printf("  Plaintext  : " COL_WHITE "%s\n" COL_RESET, plain);
        printf("  Key        : " COL_GREEN "%s\n" COL_RESET, key);
        printf("  Ciphertext : " COL_RED   "%s\n" COL_RESET, enc);
        vigenere_decrypt(enc, key);
        printf("  Decrypted  : " COL_GREEN "%s\n\n" COL_RESET, enc);
    }

    /* ── 3. XOR ────────────────────────────────────────────────────── */
    printf(COL_YELLOW "  ━━━  [3] XOR STREAM CIPHER  ━━━\n" COL_RESET);
    {
        const char    *msg    = "SecretMessage";
        const char    *kh     = "DEADBEEF";
        size_t         len    = strlen(msg);
        uint8_t        enc[64], dec[64];

        xor_crypt((const uint8_t*)msg, len, kh, enc);
        char *hex = bytes_to_hex(enc, len);
        printf("  Plaintext  : " COL_WHITE "%s\n" COL_RESET, msg);
        printf("  Key (hex)  : " COL_GREEN "%s\n" COL_RESET, kh);
        printf("  Ciphertext : " COL_RED   "%s\n" COL_RESET, hex);
        free(hex);

        xor_crypt(enc, len, kh, dec);
        dec[len] = '\0';
        printf("  Decrypted  : " COL_GREEN "%s\n\n" COL_RESET, (char*)dec);
    }

    /* ── 4. AES-128 CBC ─────────────────────────────────────────────── */
    printf(COL_YELLOW "  ━━━  [4] AES-128 (CBC MODE)  ━━━\n" COL_RESET);
    {
        /* 16-byte key + IV */
        const uint8_t key[16] = { 0x2b,0x7e,0x15,0x16,0x28,0xae,0xd2,0xa6,
                                   0xab,0xf7,0x15,0x88,0x09,0xcf,0x4f,0x3c };
        const uint8_t iv [16] = { 0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,
                                   0x08,0x09,0x0a,0x0b,0x0c,0x0d,0x0e,0x0f };

        char msg[] = "AES-128 in C!!! ";   /* exactly 16 bytes */
        uint8_t buf[64], dec[64];
        size_t  padded_len;

        /* pad to block boundary */
        memcpy(buf, msg, 16);
        padded_len = pkcs7_pad(buf, 16, AES_BLOCK);

        AES128_CTX ctx;
        aes128_init(&ctx, key);
        aes128_cbc_encrypt(&ctx, iv, buf, buf, padded_len);

        char *hex = bytes_to_hex(buf, padded_len);
        printf("  Plaintext  : " COL_WHITE "%s\n" COL_RESET, msg);
        printf("  Key  (hex) : " COL_GREEN "2b7e151628aed2a6abf7158809cf4f3c\n" COL_RESET);
        printf("  IV   (hex) : " COL_GREEN "000102030405060708090a0b0c0d0e0f\n" COL_RESET);
        hex_dump("Ciphertext", buf, padded_len);

        /* decrypt */
        memcpy(dec, buf, padded_len);
        aes128_cbc_decrypt(&ctx, iv, dec, dec, padded_len);
        size_t plain_len = pkcs7_unpad(dec, padded_len);
        dec[plain_len] = '\0';
        printf("  Decrypted  : " COL_GREEN "%s\n\n" COL_RESET, (char*)dec);
        free(hex);
    }

    /* ── 5. Base64 ──────────────────────────────────────────────────── */
    printf(COL_YELLOW "  ━━━  [5] BASE64  ━━━\n" COL_RESET);
    {
        const char *msg = "Man landed on the Moon in 1969.";
        char *enc = base64_encode((const uint8_t*)msg, strlen(msg));
        printf("  Original   : " COL_WHITE "%s\n" COL_RESET, msg);
        printf("  Base64     : " COL_RED   "%s\n" COL_RESET, enc);

        uint8_t dec[256];
        size_t  dec_len;
        base64_decode(enc, dec, &dec_len);
        dec[dec_len] = '\0';
        printf("  Decoded    : " COL_GREEN "%s\n\n" COL_RESET, (char*)dec);
        free(enc);
    }

    /* ── 6. Caesar brute-force ──────────────────────────────────────── */
    printf(COL_YELLOW "  ━━━  [6] CAESAR BRUTE-FORCE ATTACK  ━━━\n" COL_RESET);
    {
        char cipher[64] = "Khoor, Zruog!";
        printf("  Ciphertext : " COL_RED "%s\n" COL_RESET, cipher);
        caesar_bruteforce(cipher);
    }

    printf(COL_MAGENTA "\n  ══ Demo complete ══\n\n" COL_RESET);
}

/* ── Interactive mode helpers ────────────────────────────────────────── */

static void do_caesar(void)
{
    int shift;
    char text[512], mode[8];
    printf("\n  " COL_DIM "Mode [enc/dec/bf]: " COL_RESET); scanf("%7s", mode);
    if (strcmp(mode,"bf") == 0) {
        printf("  " COL_DIM "Ciphertext: " COL_RESET); scanf(" %511[^\n]", text);
        caesar_bruteforce(text); return;
    }
    printf("  " COL_DIM "Text : " COL_RESET); scanf(" %511[^\n]", text);
    printf("  " COL_DIM "Shift: " COL_RESET); scanf("%d", &shift);
    if (strcmp(mode,"enc")==0) caesar_encrypt(text, shift);
    else                       caesar_decrypt(text, shift);
    printf(COL_GREEN "  Result: %s\n\n" COL_RESET, text);
}

static void do_vigenere(void)
{
    char text[512], key[64], mode[8];
    printf("\n  " COL_DIM "Mode [enc/dec]: " COL_RESET); scanf("%7s", mode);
    printf("  " COL_DIM "Text : " COL_RESET); scanf(" %511[^\n]", text);
    printf("  " COL_DIM "Key  : " COL_RESET); scanf("%63s", key);
    if (strcmp(mode,"enc")==0) vigenere_encrypt(text, key);
    else                       vigenere_decrypt(text, key);
    printf(COL_GREEN "  Result: %s\n\n" COL_RESET, text);
}

static void do_xor(void)
{
    char text[512], key_hex[128], mode[8];
    printf("\n  " COL_DIM "Mode [enc/dec]: " COL_RESET); scanf("%7s", mode);
    printf("  " COL_DIM "Text    : " COL_RESET); scanf(" %511[^\n]", text);
    printf("  " COL_DIM "Key hex : " COL_RESET); scanf("%127s", key_hex);

    size_t len = strlen(text);
    uint8_t out[512];
    if (xor_crypt((const uint8_t*)text, len, key_hex, out) != 0) {
        printf(COL_RED "  Bad hex key.\n" COL_RESET); return;
    }
    if (strcmp(mode,"enc")==0) {
        char *h = bytes_to_hex(out, len);
        printf(COL_GREEN "  Ciphertext (hex): %s\n\n" COL_RESET, h); free(h);
    } else {
        out[len] = '\0';
        printf(COL_GREEN "  Plaintext: %s\n\n" COL_RESET, (char*)out);
    }
}

static void do_aes(void)
{
    char mode[8], aes_mode[8], key_hex[64], text[512];
    printf("\n  " COL_DIM "Mode    [enc/dec]: " COL_RESET); scanf("%7s", mode);
    printf("  " COL_DIM "AES mode [ecb/cbc]: " COL_RESET); scanf("%7s", aes_mode);
    printf("  " COL_DIM "Text (max 480 B) : " COL_RESET); scanf(" %511[^\n]", text);
    printf("  " COL_DIM "Key (32 hex chars): " COL_RESET); scanf("%63s", key_hex);

    uint8_t key_bytes[16];
    size_t  klen = 0;
    if (hex_to_bytes(key_hex, key_bytes, &klen) != 0 || klen != 16) {
        printf(COL_RED "  Key must be exactly 32 hex chars (16 bytes).\n\n" COL_RESET); return;
    }

    AES128_CTX ctx;
    aes128_init(&ctx, key_bytes);

    /* use a fixed zero IV for interactive simplicity */
    uint8_t iv[16] = {0};

    size_t  text_len = strlen(text);
    uint8_t buf[512 + 16];
    memcpy(buf, text, text_len);
    size_t padded = pkcs7_pad(buf, text_len, AES_BLOCK);

    if (strcmp(mode,"enc")==0) {
        if (strcmp(aes_mode,"cbc")==0)
            aes128_cbc_encrypt(&ctx, iv, buf, buf, padded);
        else
            aes128_ecb_encrypt(&ctx, buf, buf, padded);
        char *h = bytes_to_hex(buf, padded);
        printf(COL_GREEN "  Ciphertext (hex): %s\n\n" COL_RESET, h); free(h);
    } else {
        /* expect hex input for decrypt */
        uint8_t ct[512]; size_t ct_len = 0;
        if (hex_to_bytes(text, ct, &ct_len) != 0) {
            printf(COL_RED "  For decryption, supply ciphertext as hex.\n\n" COL_RESET); return;
        }
        if (strcmp(aes_mode,"cbc")==0)
            aes128_cbc_decrypt(&ctx, iv, ct, ct, ct_len);
        else
            aes128_ecb_decrypt(&ctx, ct, ct, ct_len);
        size_t plain = pkcs7_unpad(ct, ct_len);
        ct[plain] = '\0';
        printf(COL_GREEN "  Plaintext: %s\n\n" COL_RESET, (char*)ct);
    }
}

static void do_base64(void)
{
    char mode[8], text[512];
    printf("\n  " COL_DIM "Mode [enc/dec]: " COL_RESET); scanf("%7s", mode);
    printf("  " COL_DIM "Text: " COL_RESET); scanf(" %511[^\n]", text);

    if (strcmp(mode,"enc")==0) {
        char *r = base64_encode((const uint8_t*)text, strlen(text));
        printf(COL_GREEN "  Base64: %s\n\n" COL_RESET, r); free(r);
    } else {
        uint8_t out[512]; size_t len = 0;
        if (base64_decode(text, out, &len) != 0) {
            printf(COL_RED "  Invalid base64.\n\n" COL_RESET); return;
        }
        out[len] = '\0';
        printf(COL_GREEN "  Decoded: %s\n\n" COL_RESET, (char*)out);
    }
}

/* ── Entry point ─────────────────────────────────────────────────────── */

int main(int argc, char *argv[])
{
    utils_init_console();
    print_banner();

    /* one-shot CLI usage */
    if (argc >= 2) {
        if (strcmp(argv[1], "demo")   == 0) { run_demo();         return 0; }
        if (strcmp(argv[1], "visual") == 0) { run_visual_demo();  return 0; }
    }

    /* interactive loop */
    char choice[8];
    for (;;) {
        print_menu();
        if (scanf("%7s", choice) != 1) break;

        if      (strcmp(choice,"1")==0) do_caesar();
        else if (strcmp(choice,"2")==0) do_vigenere();
        else if (strcmp(choice,"3")==0) do_xor();
        else if (strcmp(choice,"4")==0) do_aes();
        else if (strcmp(choice,"5")==0) do_base64();
        else if (strcmp(choice,"v")==0 ||
                 strcmp(choice,"V")==0) run_visual_demo();
        else if (strcmp(choice,"d")==0 ||
                 strcmp(choice,"D")==0) run_demo();
        else if (strcmp(choice,"0")==0) {
            printf(COL_DIM "  Goodbye.\n\n" COL_RESET);
            break;
        } else {
            printf(COL_RED "  Invalid choice.\n\n" COL_RESET);
        }
    }
    return 0;
}
