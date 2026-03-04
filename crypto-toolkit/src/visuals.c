/*
 * visuals.c — Rich terminal animations and step-by-step displays
 *
 * Renders Caesar wheel, Vigenere grid, XOR bit rows,
 * Base64 byte grouping, AES round-state matrix, brute-force scanner.
 */
#include "visuals.h"
#include "utils.h"
#include "ciphers.h"
#include "base64.h"
#include "aes.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#ifdef _WIN32
#  include <windows.h>
#  define SLEEP_MS(ms) Sleep(ms)
#else
#  include <unistd.h>
#  define SLEEP_MS(ms) usleep((ms)*1000)
#endif

/* ── helpers ─────────────────────────────────────────────────────────── */

static void section_header(const char *title)
{
    int pad = (52 - (int)strlen(title)) / 2;
    printf("\n" COL_YELLOW);
    printf("  ┌────────────────────────────────────────────────────┐\n");
    printf("  │%*s%s%*s│\n", pad, "", title, 52 - pad - (int)strlen(title), "");
    printf("  └────────────────────────────────────────────────────┘\n\n"
           COL_RESET);
}

static void step_label(const char *s)
{
    printf("  " COL_DIM "► " COL_CYAN "%s" COL_RESET "\n", s);
}

static void divider(void)
{
    printf("  " COL_DIM "────────────────────────────────────────────────────\n" COL_RESET);
}

/* ── 1.  CAESAR WHEEL ────────────────────────────────────────────────── */

void vis_caesar(const char *plaintext, int shift)
{
    section_header("  CAESAR CIPHER  —  VISUAL");

    shift = ((shift % 26) + 26) % 26;

    /* Draw the two alphabet rows */
    step_label("Alphabet wheel (plain → cipher)");
    printf("\n  " COL_WHITE "  Plain : ");
    for (int i = 0; i < 26; i++) printf(COL_DIM "%c " COL_RESET, 'A' + i);
    printf("\n");

    printf("  " COL_WHITE "  Cipher: ");
    for (int i = 0; i < 26; i++) {
        char c = (char)(((i + shift) % 26) + 'A');
        printf(COL_RED "%c " COL_RESET, c);
    }
    printf("\n\n");

    /* Show each character transforming */
    step_label("Character-by-character transformation");
    printf("\n  %-12s  %-8s  %-3s  %s\n",
           COL_DIM "Char" COL_RESET,
           COL_DIM "→" COL_RESET,
           COL_DIM "Result" COL_RESET,
           COL_DIM "Shift applied" COL_RESET);
    divider();

    char enc[256];
    strncpy(enc, plaintext, 255); enc[255] = '\0';

    for (const char *p = plaintext; *p; p++) {
        if (isalpha((unsigned char)*p)) {
            char base  = isupper((unsigned char)*p) ? 'A' : 'a';
            char after = (char)((*p - base + shift) % 26 + base);
            printf("  " COL_WHITE "'%c'" COL_RESET
                   "   →   "
                   COL_RED "'%c'" COL_RESET
                   "   (%c + %d = pos %d)\n",
                   *p, after, *p, shift, (*p - base + shift) % 26);
        } else {
            printf("  " COL_DIM "'%c'  →  '%c'  (unchanged)\n" COL_RESET, *p, *p);
        }
    }

    caesar_encrypt(enc, shift);
    printf("\n  " COL_DIM "Plaintext : " COL_WHITE  "%s\n" COL_RESET, plaintext);
    printf("  " COL_DIM "Ciphertext: " COL_RED    "%s\n\n" COL_RESET, enc);
    caesar_decrypt(enc, shift);
    printf("  " COL_DIM "Decrypted : " COL_GREEN  "%s\n\n" COL_RESET, enc);
}

/* ── 2.  VIGENERE GRID ───────────────────────────────────────────────── */

void vis_vigenere(const char *plaintext, const char *key)
{
    section_header("  VIGENÈRE CIPHER  —  VISUAL");

    size_t klen = strlen(key);
    size_t tlen = strlen(plaintext);

    step_label("Key stream (key repeating over plaintext)");
    printf("\n  " COL_DIM "Plain : " COL_RESET);
    for (size_t i = 0; i < tlen; i++) printf(COL_WHITE "%c " COL_RESET, plaintext[i]);
    printf("\n");

    printf("  " COL_DIM "Key   : " COL_RESET);
    size_t ki = 0;
    for (size_t i = 0; i < tlen; i++) {
        if (isalpha((unsigned char)plaintext[i])) {
            printf(COL_CYAN "%c " COL_RESET, toupper((unsigned char)key[ki % klen]));
            ki++;
        } else {
            printf(COL_DIM "  " COL_RESET);
        }
    }
    printf("\n\n");

    step_label("Letter-by-letter: plain + key (mod 26) = cipher");
    divider();
    printf("  %-6s  %-6s  %-6s  %s\n",
           COL_DIM "Plain" COL_RESET, COL_DIM "+Key" COL_RESET,
           COL_DIM "=Ciph" COL_RESET, COL_DIM "Formula" COL_RESET);
    divider();

    ki = 0;
    for (size_t i = 0; i < tlen; i++) {
        char c = plaintext[i];
        if (isalpha((unsigned char)c)) {
            int p = tolower((unsigned char)c) - 'a';
            int k = tolower((unsigned char)key[ki % klen]) - 'a';
            int r = (p + k) % 26;
            char enc_c = (isupper((unsigned char)c) ? 'A' : 'a') + r;
            printf("  " COL_WHITE "%-5c" COL_RESET
                   "   " COL_CYAN "+%-4c" COL_RESET
                   "  " COL_RED "=%-5c" COL_RESET
                   "  (%d + %d) mod 26 = %d\n",
                   c, toupper((unsigned char)key[ki % klen]), enc_c, p, k, r);
            ki++;
        } else {
            printf("  " COL_DIM "%-5c   (space/punct — unchanged)\n" COL_RESET, c);
        }
    }

    char enc[256];
    strncpy(enc, plaintext, 255); enc[255] = '\0';
    vigenere_encrypt(enc, key);
    printf("\n  " COL_DIM "Plaintext : " COL_WHITE "%s\n" COL_RESET, plaintext);
    printf("  " COL_DIM "Ciphertext: " COL_RED   "%s\n" COL_RESET, enc);
    vigenere_decrypt(enc, key);
    printf("  " COL_DIM "Decrypted : " COL_GREEN "%s\n\n" COL_RESET, enc);
}

/* ── 3.  XOR BIT DISPLAY ─────────────────────────────────────────────── */

static void print_bits(uint8_t byte, const char *col)
{
    for (int i = 7; i >= 0; i--)
        printf("%s%c" COL_RESET, col, (byte >> i & 1) ? '1' : '0');
    printf(" ");
}

void vis_xor(const char *plaintext, const char *key_hex)
{
    section_header("  XOR STREAM CIPHER  —  VISUAL");

    uint8_t key[64]; size_t klen = 0;
    if (hex_to_bytes(key_hex, key, &klen) != 0) {
        printf(COL_RED "  Bad hex key.\n" COL_RESET); return;
    }

    size_t show = strlen(plaintext);
    if (show > 6) show = 6;   /* show first 6 bytes of bits */

    step_label("Bit-level XOR (showing first 6 bytes)");
    printf("\n");

    /* Plain bits */
    printf("  " COL_DIM "Plain  " COL_RESET);
    for (size_t i = 0; i < show; i++)
        printf(COL_DIM "  '%c'='%02x'" COL_RESET "  ", (unsigned char)plaintext[i], (unsigned char)plaintext[i]);
    printf("\n");

    printf("  " COL_WHITE "       ");
    for (size_t i = 0; i < show; i++) print_bits((uint8_t)plaintext[i], COL_WHITE);
    printf(COL_RESET "\n");

    /* Key bits */
    printf("  " COL_DIM "Key    ");
    for (size_t i = 0; i < show; i++)
        printf("  key[%zu]='%02x'  ", i % klen, key[i % klen]);
    printf(COL_RESET "\n");

    printf("  " COL_CYAN "       ");
    for (size_t i = 0; i < show; i++) print_bits(key[i % klen], COL_CYAN);
    printf(COL_RESET "\n");

    /* XOR separator */
    printf("  " COL_DIM "       ");
    for (size_t i = 0; i < show; i++) printf("───────── ");
    printf(COL_RESET "\n");

    /* Result bits */
    printf("  " COL_DIM "Result ");
    for (size_t i = 0; i < show; i++) {
        uint8_t r = (uint8_t)plaintext[i] ^ key[i % klen];
        printf("  '%02x'       " , r);
    }
    printf(COL_RESET "\n");

    printf("  " COL_RED "       ");
    for (size_t i = 0; i < show; i++) {
        uint8_t r = (uint8_t)plaintext[i] ^ key[i % klen];
        print_bits(r, COL_RED);
    }
    printf(COL_RESET "\n\n");

    step_label("Full ciphertext (hex)");
    size_t len = strlen(plaintext);
    uint8_t out[512];
    xor_crypt((const uint8_t*)plaintext, len, key_hex, out);
    char *h = bytes_to_hex(out, len);
    printf("\n  " COL_DIM "Plain     : " COL_WHITE  "%s\n" COL_RESET, plaintext);
    printf("  " COL_DIM "Ciphertext: " COL_RED    "%s\n" COL_RESET, h);
    free(h);
    xor_crypt(out, len, key_hex, out);
    out[len] = '\0';
    printf("  " COL_DIM "Decrypted : " COL_GREEN  "%s\n\n" COL_RESET, (char*)out);
}

/* ── 4.  BASE64 BYTE GROUPING ────────────────────────────────────────── */

static const char *B64_COLS[] = { COL_RED, COL_CYAN, COL_YELLOW, COL_MAGENTA };

void vis_base64(const char *plaintext)
{
    section_header("  BASE64 ENCODING  —  VISUAL");

    const uint8_t *in  = (const uint8_t*)plaintext;
    size_t         len = strlen(plaintext);

    size_t show_groups = len / 3;
    if (show_groups > 4) show_groups = 4;   /* show up to 4 groups */
    size_t show_bytes  = show_groups * 3;

    step_label("Bytes grouped into 3s → split into 4×6-bit chunks → Base64 char");
    printf("\n");

    /* Byte hex row */
    printf("  " COL_DIM "Bytes   " COL_RESET);
    for (size_t i = 0; i < show_bytes; i++) {
        const char *col = B64_COLS[(i / 3) % 4];
        printf("%s %02x " COL_RESET, col, in[i]);
    }
    printf(COL_DIM " ...\n" COL_RESET);

    /* 24-bit group labels */
    printf("  " COL_DIM "Group   " COL_RESET);
    for (size_t g = 0; g < show_groups; g++) {
        const char *col = B64_COLS[g % 4];
        printf("%s├──── group %zu ────┤" COL_RESET " ", col, g + 1);
    }
    printf("\n");

    /* 6-bit chunks */
    printf("  " COL_DIM "6-bits  " COL_RESET);
    static const char *B64T = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    for (size_t g = 0; g < show_groups; g++) {
        const char *col = B64_COLS[g % 4];
        uint32_t triple = ((uint32_t)in[g*3] << 16)
                        | ((uint32_t)in[g*3+1] << 8)
                        |  (uint32_t)in[g*3+2];
        uint8_t c0 = (triple >> 18) & 0x3F;
        uint8_t c1 = (triple >> 12) & 0x3F;
        uint8_t c2 = (triple >>  6) & 0x3F;
        uint8_t c3 =  triple        & 0x3F;
        printf("%s[%2d]%c [%2d]%c [%2d]%c [%2d]%c" COL_RESET "  ",
               col,
               c0, B64T[c0], c1, B64T[c1],
               c2, B64T[c2], c3, B64T[c3]);
    }
    printf("\n\n");

    step_label("6-bit value → Base64 character mapping");
    /* Show a mini lookup excerpt for chars used */
    for (size_t g = 0; g < show_groups; g++) {
        uint32_t triple = ((uint32_t)in[g*3] << 16)
                        | ((uint32_t)in[g*3+1] << 8)
                        |  (uint32_t)in[g*3+2];
        for (int k = 3; k >= 0; k--) {
            uint8_t idx = (triple >> (k * 6)) & 0x3F;
            printf("  %sidx %-2d" COL_RESET " → " COL_WHITE "'%c'" COL_RESET "\n",
                   B64_COLS[g % 4], idx, B64T[idx]);
        }
        divider();
    }

    char *enc = base64_encode(in, len);
    printf("\n  " COL_DIM "Plaintext : " COL_WHITE  "%s\n" COL_RESET, plaintext);
    printf("  " COL_DIM "Base64    : " COL_RED    "%s\n" COL_RESET, enc);

    uint8_t dec[512]; size_t dlen = 0;
    base64_decode(enc, dec, &dlen);
    dec[dlen] = '\0';
    printf("  " COL_DIM "Decoded   : " COL_GREEN  "%s\n\n" COL_RESET, (char*)dec);
    free(enc);
}

/* ── 5.  AES STATE MATRIX ────────────────────────────────────────────── */

/* We re-implement the AES steps here with print calls between each */

static const uint8_t VIS_SBOX[256] = {
    0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76,
    0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0,
    0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15,
    0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75,
    0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84,
    0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf,
    0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8,
    0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2,
    0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73,
    0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb,
    0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79,
    0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08,
    0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a,
    0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e,
    0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf,
    0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16
};

#define VS(r,c) state[(c)*4+(r)]

static void vis_print_state(const uint8_t state[16],
                            const char *changed_col,   /* colour for changed cells */
                            const uint8_t *prev)       /* NULL = no highlight */
{
    printf("        ┌────┬────┬────┬────┐\n");
    for (int r = 0; r < 4; r++) {
        printf("        │");
        for (int c = 0; c < 4; c++) {
            uint8_t v = VS(r,c);
            int changed = prev && (v != prev[(c)*4+(r)]);
            if (changed)
                printf("%s%02x" COL_RESET "│", changed_col, v);
            else
                printf(COL_DIM "%02x" COL_RESET "│", v);
        }
        printf("\n");
        if (r < 3) printf("        ├────┼────┼────┼────┤\n");
    }
    printf("        └────┴────┴────┴────┘\n\n");
}

/* highlight which row was shifted */
static void vis_print_state_shifted(const uint8_t state[16], const uint8_t *prev)
{
    static const char *row_cols[4] = { COL_DIM, COL_CYAN, COL_YELLOW, COL_MAGENTA };
    printf("        ┌────┬────┬────┬────┐  ← row 0: no shift\n");
    for (int r = 0; r < 4; r++) {
        printf("        │");
        for (int c = 0; c < 4; c++) {
            uint8_t v = VS(r,c);
            int changed = prev && (v != prev[(c)*4+(r)]);
            if (changed)
                printf("%s%02x" COL_RESET "│", row_cols[r], v);
            else
                printf(COL_DIM "%02x" COL_RESET "│", v);
        }
        if (r == 1) printf("  ← row 1: rotated left 1");
        if (r == 2) printf("  ← row 2: rotated left 2");
        if (r == 3) printf("  ← row 3: rotated left 3");
        printf("\n");
        if (r < 3) printf("        ├────┼────┼────┼────┤\n");
    }
    printf("        └────┴────┴────┴────┘\n\n");
}

/* perform the operations on a local state copy and print at each step */
static void vis_sub_bytes(uint8_t s[16], const uint8_t *prev) {
    printf("  " COL_CYAN "  SubBytes (S-box substitution):\n" COL_RESET);
    uint8_t tmp[16]; memcpy(tmp,s,16);
    for (int i=0;i<16;i++) s[i]=VIS_SBOX[s[i]];
    vis_print_state(s, COL_GREEN, tmp);
}

static void vis_shift_rows(uint8_t state[16], const uint8_t *prev) {
    printf("  " COL_YELLOW "  ShiftRows (cyclic row rotation):\n" COL_RESET);
    uint8_t tmp[16]; memcpy(tmp,state,16);
    uint8_t t;
    t=VS(1,0); VS(1,0)=VS(1,1); VS(1,1)=VS(1,2); VS(1,2)=VS(1,3); VS(1,3)=t;
    t=VS(2,0); VS(2,0)=VS(2,2); VS(2,2)=t;
    t=VS(2,1); VS(2,1)=VS(2,3); VS(2,3)=t;
    t=VS(3,3); VS(3,3)=VS(3,2); VS(3,2)=VS(3,1); VS(3,1)=VS(3,0); VS(3,0)=t;
    vis_print_state_shifted(state, tmp);
}

static uint8_t vg(uint8_t a, uint8_t b) {
    uint8_t p=0;
    for(int i=0;i<8;i++){if(b&1)p^=a;uint8_t h=a&0x80;a<<=1;if(h)a^=0x1b;b>>=1;}
    return p;
}

static void _mix_cols_silent(uint8_t state[16]) {
    for(int c=0;c<4;c++){
        uint8_t s0=VS(0,c),s1=VS(1,c),s2=VS(2,c),s3=VS(3,c);
        VS(0,c)=vg(2,s0)^vg(3,s1)^s2^s3;
        VS(1,c)=s0^vg(2,s1)^vg(3,s2)^s3;
        VS(2,c)=s0^s1^vg(2,s2)^vg(3,s3);
        VS(3,c)=vg(3,s0)^s1^s2^vg(2,s3);
    }
}

static void vis_mix_columns(uint8_t state[16]) {
    printf("  " COL_MAGENTA "  MixColumns (GF(2\u2078) matrix multiply):\n" COL_RESET);
    uint8_t tmp[16]; memcpy(tmp,state,16);
    for(int c=0;c<4;c++){
        uint8_t s0=VS(0,c),s1=VS(1,c),s2=VS(2,c),s3=VS(3,c);
        VS(0,c)=vg(2,s0)^vg(3,s1)^s2^s3;
        VS(1,c)=s0^vg(2,s1)^vg(3,s2)^s3;
        VS(2,c)=s0^s1^vg(2,s2)^vg(3,s3);
        VS(3,c)=vg(3,s0)^s1^s2^vg(2,s3);
    }
    vis_print_state(state, COL_RED, tmp);
}

static void vis_add_round_key(uint8_t s[16], const uint8_t *rk, int round) {
    printf("  " COL_BLUE "  AddRoundKey (XOR with round key %d):\n" COL_RESET, round);
    uint8_t tmp[16]; memcpy(tmp,s,16);
    for(int i=0;i<16;i++) s[i]^=rk[i];
    vis_print_state(s, COL_WHITE, tmp);
}

void vis_aes(const char *plaintext, const uint8_t key[16], const uint8_t iv[16])
{
    section_header("  AES-128 CBC  —  ROUND-BY-ROUND STATE MATRIX");

    AES128_CTX ctx;
    aes128_init(&ctx, key);

    uint8_t state[16], prev[16];
    /* copy plaintext padded to 16 bytes */
    memset(state, 0x10, 16);   /* PKCS#7 pad value */
    size_t plen = strlen(plaintext);
    if (plen > 16) plen = 16;
    memcpy(state, plaintext, plen);

    /* XOR with IV (CBC) */
    for (int i = 0; i < 16; i++) state[i] ^= iv[i];

    printf("  " COL_DIM "Key   : " COL_RESET);
    for (int i=0;i<16;i++) printf(COL_CYAN "%02x " COL_RESET, key[i]);
    printf("\n");
    printf("  " COL_DIM "IV    : " COL_RESET);
    for (int i=0;i<16;i++) printf(COL_MAGENTA "%02x " COL_RESET, iv[i]);
    printf("\n");
    printf("  " COL_DIM "Input : " COL_RESET COL_WHITE);
    for (int i=0;i<16;i++) printf("%02x ", state[i]);
    printf(COL_RESET "\n\n");

    printf(COL_YELLOW "  ── Initial State ──\n" COL_RESET);
    vis_print_state(state, COL_WHITE, NULL);

    /* Round 0: AddRoundKey */
    vis_add_round_key(state, ctx.rk, 0);

    /* Rounds 1-3 full, then skip to 10 */
    for (int r = 1; r <= 3; r++) {
        printf(COL_YELLOW "  ══ Round %d ══\n" COL_RESET, r);
        memcpy(prev, state, 16);
        vis_sub_bytes(state, prev);
        memcpy(prev, state, 16);
        vis_shift_rows(state, prev);
        vis_mix_columns(state);
        vis_add_round_key(state, ctx.rk + r*16, r);
    }

    printf(COL_DIM "  · · · rounds 4–9 omitted for brevity · · ·\n\n" COL_RESET);

    /* Run rounds 4-9 silently */
    for (int r = 4; r <= 9; r++) {
        for(int i=0;i<16;i++) state[i]=VIS_SBOX[state[i]]; /* SubBytes */
        uint8_t t; /* ShiftRows */
        t=VS(1,0);VS(1,0)=VS(1,1);VS(1,1)=VS(1,2);VS(1,2)=VS(1,3);VS(1,3)=t;
        t=VS(2,0);VS(2,0)=VS(2,2);VS(2,2)=t; t=VS(2,1);VS(2,1)=VS(2,3);VS(2,3)=t;
        t=VS(3,3);VS(3,3)=VS(3,2);VS(3,2)=VS(3,1);VS(3,1)=VS(3,0);VS(3,0)=t;
        _mix_cols_silent(state);  /* MixColumns silent */
        for(int i=0;i<16;i++) state[i]^=ctx.rk[r*16+i]; /* AddRoundKey */
    }

    printf(COL_YELLOW "  ══ Final Round (Round 10) ══\n" COL_RESET);
    memcpy(prev, state, 16);
    for(int i=0;i<16;i++) state[i]=VIS_SBOX[state[i]];
    printf("  " COL_CYAN "  SubBytes:\n" COL_RESET);
    vis_print_state(state, COL_GREEN, prev);
    memcpy(prev, state, 16);
    uint8_t tt;
    tt=VS(1,0);VS(1,0)=VS(1,1);VS(1,1)=VS(1,2);VS(1,2)=VS(1,3);VS(1,3)=tt;
    tt=VS(2,0);VS(2,0)=VS(2,2);VS(2,2)=tt; tt=VS(2,1);VS(2,1)=VS(2,3);VS(2,3)=tt;
    tt=VS(3,3);VS(3,3)=VS(3,2);VS(3,2)=VS(3,1);VS(3,1)=VS(3,0);VS(3,0)=tt;
    printf("  " COL_YELLOW "  ShiftRows:\n" COL_RESET);
    vis_print_state_shifted(state, prev);
    vis_add_round_key(state, ctx.rk + 160, 10);

    printf("  " COL_DIM "Ciphertext: " COL_RED);
    for (int i=0;i<16;i++) printf("%02x ", state[i]);
    printf(COL_RESET "\n\n");

    /* decrypt and show it matches */
    uint8_t dec[16];
    aes128_cbc_decrypt(&ctx, iv, state, dec, 16);
    size_t pl = pkcs7_unpad(dec, 16);
    dec[pl] = '\0';
    printf("  " COL_DIM "Decrypted : " COL_GREEN "%s\n\n" COL_RESET, (char*)dec);
}

/* ── 6.  BRUTE-FORCE SCANNER ─────────────────────────────────────────── */

void vis_bruteforce(const char *ciphertext, int answer_shift)
{
    section_header("  CAESAR BRUTE-FORCE ATTACK  —  VISUAL");

    printf("  " COL_DIM "Target ciphertext: " COL_RED "%s\n\n" COL_RESET, ciphertext);
    step_label("Trying all 25 possible shifts...");
    printf("\n");

    char buf[256];
    int found = -1;

    for (int s = 1; s <= 25; s++) {
        strncpy(buf, ciphertext, 255); buf[255] = '\0';
        /* visual progress bar */
        int filled = (s * 20) / 25;
        printf("  " COL_DIM "[" COL_RESET);
        for (int i = 0; i < filled; i++)  printf(COL_GREEN "█" COL_RESET);
        for (int i = filled; i < 20; i++) printf(COL_DIM "░" COL_RESET);
        printf(COL_DIM "] " COL_RESET "shift=%-3d  ", s);

        caesar_decrypt(buf, s);

        if (s == answer_shift) {
            printf(COL_GREEN "✓  %s" COL_RESET " ← MATCH!\n", buf);
            found = s;
        } else {
            printf(COL_DIM "%s\n" COL_RESET, buf);
        }
        SLEEP_MS(40);
    }

    if (found > 0) {
        strncpy(buf, ciphertext, 255); buf[255]='\0';
        caesar_decrypt(buf, found);
        printf("\n  " COL_GREEN "Cracked! Shift = %d  →  \"%s\"\n\n" COL_RESET, found, buf);
    } else {
        printf("\n  " COL_RED "Not found.\n\n" COL_RESET);
    }
}
