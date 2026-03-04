#include "vault.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <time.h>

/*
 * File layout:
 *  [4]  magic "SVLT"
 *  [2]  version (uint16_t LE)
 *  [32] salt
 *  [12] IV
 *  [16] GCM tag
 *  [4]  ciphertext_len (uint32_t LE)
 *  [N]  ciphertext  (AES-256-GCM of serialized entries)
 *
 * The plaintext blob is: [4] entry_count + entry_count * sizeof(VaultEntry)
 */

#define HDR_MAGIC_OFF   0
#define HDR_VER_OFF     4
#define HDR_SALT_OFF    6
#define HDR_IV_OFF      (HDR_SALT_OFF + SALT_LEN)
#define HDR_TAG_OFF     (HDR_IV_OFF   + IV_LEN)
#define HDR_CTLEN_OFF   (HDR_TAG_OFF  + TAG_LEN)
#define HDR_DATA_OFF    (HDR_CTLEN_OFF + 4)

/* ─────────────────────────────────────────────────────── helpers ── */
static void secure_zero(void *ptr, size_t len)
{
    volatile uint8_t *p = (volatile uint8_t *)ptr;
    while (len--) *p++ = 0;
}

static int write_all(FILE *f, const void *buf, size_t n)
{
    return fwrite(buf, 1, n, f) == n ? 0 : -1;
}

static int read_all(FILE *f, void *buf, size_t n)
{
    return fread(buf, 1, n, f) == n ? 0 : -1;
}

/* ─────────────────────────────────────────────── vault_create ── */
int vault_create(Vault *v, const char *path, const char *master_password)
{
    memset(v, 0, sizeof(*v));
    strncpy(v->filepath, path, sizeof(v->filepath) - 1);
    v->count = 0;

    if (random_bytes(v->salt, SALT_LEN) != 0) return -1;
    if (derive_key(master_password, v->salt, v->key) != 0) return -1;
    v->unlocked = 1;

    return vault_save(v);
}

/* ─────────────────────────────────────────────── vault_open ── */
int vault_open(Vault *v, const char *path, const char *master_password)
{
    FILE *f = fopen(path, "rb");
    if (!f) { perror("[vault] fopen"); return -1; }

    char magic[4];
    uint16_t version;
    uint8_t  salt[SALT_LEN];
    uint8_t  iv[IV_LEN];
    uint8_t  tag[TAG_LEN];
    uint32_t ct_len;

    if (read_all(f, magic,   4)          != 0) goto err;
    if (memcmp(magic, VAULT_MAGIC, 4)    != 0) { fprintf(stderr, "[vault] Bad magic\n"); goto err; }
    if (read_all(f, &version, 2)         != 0) goto err;
    if (read_all(f, salt,  SALT_LEN)     != 0) goto err;
    if (read_all(f, iv,    IV_LEN)       != 0) goto err;
    if (read_all(f, tag,   TAG_LEN)      != 0) goto err;
    if (read_all(f, &ct_len, 4)          != 0) goto err;

    uint8_t *ciphertext = malloc(ct_len);
    if (!ciphertext) { goto err; }
    if ((uint32_t)fread(ciphertext, 1, ct_len, f) != ct_len) { free(ciphertext); goto err; }
    fclose(f); f = NULL;

    /* Derive key */
    memcpy(v->salt, salt, SALT_LEN);
    if (derive_key(master_password, salt, v->key) != 0) { free(ciphertext); return -1; }

    /* Decrypt */
    size_t pt_max = ct_len + 16;
    uint8_t *plaintext = malloc(pt_max);
    if (!plaintext) { free(ciphertext); return -1; }

    int pt_len = aes_gcm_decrypt(v->key, iv, ciphertext, ct_len, tag, plaintext);
    free(ciphertext);
    if (pt_len < 0) { free(plaintext); secure_zero(v->key, KEY_LEN); return -1; }

    /* Deserialize */
    uint32_t count;
    memcpy(&count, plaintext, 4);
    if (count > MAX_ENTRIES) { free(plaintext); return -1; }
    v->count = (int)count;
    memcpy(v->entries, plaintext + 4, count * sizeof(VaultEntry));
    free(plaintext);

    strncpy(v->filepath, path, sizeof(v->filepath) - 1);
    v->unlocked = 1;
    return 0;

err:
    if (f) fclose(f);
    return -1;
}

/* ─────────────────────────────────────────────── vault_save ── */
int vault_save(Vault *v)
{
    if (!v->unlocked) { fprintf(stderr, "[vault] Vault is locked\n"); return -1; }

    /* Serialize entries into plaintext blob */
    uint32_t count = (uint32_t)v->count;
    size_t pt_len = 4 + count * sizeof(VaultEntry);
    uint8_t *plaintext = malloc(pt_len);
    if (!plaintext) return -1;
    memcpy(plaintext, &count, 4);
    memcpy(plaintext + 4, v->entries, count * sizeof(VaultEntry));

    /* Encrypt */
    uint8_t iv[IV_LEN], tag[TAG_LEN];
    uint8_t *ciphertext = malloc(pt_len);
    if (!ciphertext) { free(plaintext); return -1; }

    int ct_len = aes_gcm_encrypt(v->key, iv, plaintext, pt_len, ciphertext, tag);
    secure_zero(plaintext, pt_len);
    free(plaintext);
    if (ct_len < 0) { free(ciphertext); return -1; }

    /* Write file */
    FILE *f = fopen(v->filepath, "wb");
    if (!f) { perror("[vault] fopen write"); free(ciphertext); return -1; }

    uint16_t version = VAULT_VERSION;
    uint32_t ct_len32 = (uint32_t)ct_len;

    write_all(f, VAULT_MAGIC,   4);
    write_all(f, &version,      2);
    write_all(f, v->salt,       SALT_LEN);
    write_all(f, iv,            IV_LEN);
    write_all(f, tag,           TAG_LEN);
    write_all(f, &ct_len32,     4);
    write_all(f, ciphertext,    ct_len);

    fclose(f);
    free(ciphertext);
    return 0;
}

/* ─────────────────────────────────────────────── vault_lock ── */
void vault_lock(Vault *v)
{
    secure_zero(v->key,     KEY_LEN);
    secure_zero(v->entries, sizeof(v->entries));
    v->unlocked = 0;
    v->count    = 0;
}

/* ─────────────────────────────────────────────── vault_add ── */
int vault_add(Vault *v, const VaultEntry *e)
{
    if (v->count >= MAX_ENTRIES) { fprintf(stderr, "[vault] Vault is full\n"); return -1; }
    v->entries[v->count++] = *e;
    return 0;
}

/* ─────────────────────────────────────────────── vault_find ── */
int vault_find(Vault *v, const char *label)
{
    for (int i = 0; i < v->count; i++) {
        /* case-insensitive compare */
        const char *a = v->entries[i].label, *b = label;
        int match = 1;
        while (*a && *b) {
            if (tolower((unsigned char)*a) != tolower((unsigned char)*b)) { match = 0; break; }
            a++; b++;
        }
        if (match && *a == '\0' && *b == '\0') return i;
    }
    return -1;
}

/* ─────────────────────────────────────────────── vault_delete ── */
int vault_delete(Vault *v, int index)
{
    if (index < 0 || index >= v->count) return -1;
    secure_zero(&v->entries[index], sizeof(VaultEntry));
    /* Shift remaining entries down */
    for (int i = index; i < v->count - 1; i++)
        v->entries[i] = v->entries[i + 1];
    secure_zero(&v->entries[v->count - 1], sizeof(VaultEntry));
    v->count--;
    return 0;
}

/* ─────────────────────────────────────────────── vault_list ── */
void vault_list(Vault *v, int show_passwords)
{
    if (v->count == 0) { printf("  (no entries)\n"); return; }
    printf("  %-4s %-25s %-25s %-35s\n", "#", "Label", "Username", "URL");
    printf("  %-4s %-25s %-25s %-35s\n", "---", "-------------------------",
           "-------------------------", "-----------------------------------");
    for (int i = 0; i < v->count; i++) {
        printf("  %-4d %-25s %-25s %-35s\n",
               i + 1,
               v->entries[i].label,
               v->entries[i].username,
               v->entries[i].url);
        if (show_passwords)
            printf("       Password : %s\n", v->entries[i].password);
        if (v->entries[i].notes[0])
            printf("       Notes    : %s\n", v->entries[i].notes);
    }
}

/* ─────────────────────────────────────── vault_generate_password ── */
void vault_generate_password(char *buf, size_t len)
{
    static const char charset[] =
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        "0123456789!@#$%^&*()-_=+[]{}|;:,.<>?";
    uint8_t rnd[256];
    if (len > sizeof(rnd) - 1) len = sizeof(rnd) - 1;
    random_bytes(rnd, len);
    for (size_t i = 0; i < len; i++)
        buf[i] = charset[rnd[i] % (sizeof(charset) - 1)];
    buf[len] = '\0';
}
