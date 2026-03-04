#ifndef VAULT_H
#define VAULT_H

#include "crypto.h"
#include <stdint.h>

#define MAX_LABEL_LEN    64
#define MAX_USERNAME_LEN 128
#define MAX_PASSWORD_LEN 256
#define MAX_URL_LEN      256
#define MAX_NOTES_LEN    512
#define MAX_ENTRIES      512
#define VAULT_MAGIC      "SVLT"
#define VAULT_VERSION    1

/* ── On-disk entry (plaintext representation, never written directly) ── */
typedef struct {
    char label[MAX_LABEL_LEN];
    char username[MAX_USERNAME_LEN];
    char password[MAX_PASSWORD_LEN];
    char url[MAX_URL_LEN];
    char notes[MAX_NOTES_LEN];
} VaultEntry;

/* ── In-memory vault ─────────────────────────────────────────────────── */
typedef struct {
    uint8_t      salt[SALT_LEN];
    uint8_t      key[KEY_LEN];    /* derived at unlock, zeroed at lock */
    VaultEntry   entries[MAX_ENTRIES];
    int          count;
    char         filepath[512];
    int          unlocked;
} Vault;

/*
 * Create a new vault file at 'path' protected by 'master_password'.
 * Returns 0 on success.
 */
int vault_create(Vault *v, const char *path, const char *master_password);

/*
 * Open an existing vault. Derives key; does NOT decrypt entries yet.
 * Returns 0 on success, -1 on bad password or I/O error.
 */
int vault_open(Vault *v, const char *path, const char *master_password);

/* Flush all entries (encrypted) back to disk. Returns 0 on success. */
int vault_save(Vault *v);

/* Zero-out the key material and mark vault locked. */
void vault_lock(Vault *v);

/* Add a new entry. Returns 0 on success, -1 if vault full. */
int vault_add(Vault *v, const VaultEntry *e);

/* Find entry by label (case-insensitive). Returns index or -1. */
int vault_find(Vault *v, const char *label);

/* Delete entry at index. Returns 0 on success. */
int vault_delete(Vault *v, int index);

/* Print all entries to stdout (password hidden unless show_passwords set). */
void vault_list(Vault *v, int show_passwords);

/* Generate a random printable password of given length. */
void vault_generate_password(char *buf, size_t len);

#endif /* VAULT_H */
