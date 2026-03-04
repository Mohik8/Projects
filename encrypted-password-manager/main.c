/*
 * SecureVault – CLI password manager
 *
 * Usage:
 *   securevault new    <vault_file>          – create a new vault
 *   securevault add    <vault_file>          – add an entry
 *   securevault get    <vault_file> <label>  – retrieve an entry (shows password)
 *   securevault list   <vault_file>          – list all entries
 *   securevault delete <vault_file> <label>  – delete an entry
 *   securevault gen    <length>              – generate a random password
 *
 * The master password is read from the terminal (no echo).
 */

#include "vault.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32
#  include <windows.h>
static void set_echo(int enable)
{
    HANDLE h = GetStdHandle(STD_INPUT_HANDLE);
    DWORD mode;
    GetConsoleMode(h, &mode);
    if (enable) mode |=  ENABLE_ECHO_INPUT;
    else        mode &= ~ENABLE_ECHO_INPUT;
    SetConsoleMode(h, mode);
}
#else
#  include <termios.h>
#  include <unistd.h>
static void set_echo(int enable)
{
    struct termios t;
    tcgetattr(STDIN_FILENO, &t);
    if (enable) t.c_lflag |=  ECHO;
    else        t.c_lflag &= ~ECHO;
    tcsetattr(STDIN_FILENO, TCSANOW, &t);
}
#endif

static void read_password(const char *prompt, char *buf, size_t max)
{
    printf("%s", prompt);
    fflush(stdout);
    set_echo(0);
    if (fgets(buf, (int)max, stdin)) {
        size_t n = strlen(buf);
        if (n && buf[n-1] == '\n') buf[n-1] = '\0';
    }
    set_echo(1);
    printf("\n");
}

static void read_line(const char *prompt, char *buf, size_t max)
{
    printf("%s", prompt);
    fflush(stdout);
    if (fgets(buf, (int)max, stdin)) {
        size_t n = strlen(buf);
        if (n && buf[n-1] == '\n') buf[n-1] = '\0';
    }
}

/* ── Commands ──────────────────────────────────────────────────────────── */

static int cmd_new(const char *path)
{
    char pw1[256], pw2[256];
    read_password("New master password : ", pw1, sizeof(pw1));
    read_password("Confirm             : ", pw2, sizeof(pw2));
    if (strcmp(pw1, pw2) != 0) {
        fprintf(stderr, "Passwords do not match.\n");
        return 1;
    }
    Vault v;
    if (vault_create(&v, path, pw1) != 0) {
        fprintf(stderr, "Failed to create vault.\n");
        return 1;
    }
    vault_lock(&v);
    printf("Vault created: %s\n", path);
    return 0;
}

static int cmd_add(const char *path)
{
    char pw[256];
    read_password("Master password: ", pw, sizeof(pw));

    Vault v;
    if (vault_open(&v, path, pw) != 0) {
        fprintf(stderr, "Failed to open vault (wrong password?).\n");
        return 1;
    }

    VaultEntry e;
    memset(&e, 0, sizeof(e));
    read_line("Label    : ", e.label,    sizeof(e.label));
    read_line("Username : ", e.username, sizeof(e.username));

    printf("Generate a password? [y/N] ");
    fflush(stdout);
    char choice[4];
    fgets(choice, sizeof(choice), stdin);
    if (choice[0] == 'y' || choice[0] == 'Y') {
        char lenstr[8];
        read_line("Length (default 24): ", lenstr, sizeof(lenstr));
        int plen = lenstr[0] ? atoi(lenstr) : 24;
        if (plen < 8 || plen > 128) plen = 24;
        vault_generate_password(e.password, (size_t)plen);
        printf("Generated password: %s\n", e.password);
    } else {
        read_password("Password : ", e.password, sizeof(e.password));
    }

    read_line("URL      : ", e.url,   sizeof(e.url));
    read_line("Notes    : ", e.notes, sizeof(e.notes));

    if (vault_add(&v, &e) != 0) { vault_lock(&v); return 1; }
    if (vault_save(&v)    != 0) { vault_lock(&v); return 1; }
    vault_lock(&v);
    printf("Entry '%s' added.\n", e.label);
    return 0;
}

static int cmd_get(const char *path, const char *label)
{
    char pw[256];
    read_password("Master password: ", pw, sizeof(pw));

    Vault v;
    if (vault_open(&v, path, pw) != 0) {
        fprintf(stderr, "Failed to open vault.\n");
        return 1;
    }

    int idx = vault_find(&v, label);
    if (idx < 0) {
        fprintf(stderr, "No entry found for label '%s'.\n", label);
        vault_lock(&v); return 1;
    }

    VaultEntry *e = &v.entries[idx];
    printf("\n  Label    : %s\n", e->label);
    printf("  Username : %s\n", e->username);
    printf("  Password : %s\n", e->password);
    if (e->url[0])   printf("  URL      : %s\n", e->url);
    if (e->notes[0]) printf("  Notes    : %s\n", e->notes);
    printf("\n");

    vault_lock(&v);
    return 0;
}

static int cmd_list(const char *path)
{
    char pw[256];
    read_password("Master password: ", pw, sizeof(pw));

    Vault v;
    if (vault_open(&v, path, pw) != 0) {
        fprintf(stderr, "Failed to open vault.\n");
        return 1;
    }

    printf("\n  Vault: %s  (%d entries)\n\n", path, v.count);
    vault_list(&v, 0);
    printf("\n");
    vault_lock(&v);
    return 0;
}

static int cmd_delete(const char *path, const char *label)
{
    char pw[256];
    read_password("Master password: ", pw, sizeof(pw));

    Vault v;
    if (vault_open(&v, path, pw) != 0) {
        fprintf(stderr, "Failed to open vault.\n");
        return 1;
    }

    int idx = vault_find(&v, label);
    if (idx < 0) {
        fprintf(stderr, "No entry found for label '%s'.\n", label);
        vault_lock(&v); return 1;
    }

    printf("Delete entry '%s'? [y/N] ", label);
    fflush(stdout);
    char choice[4];
    fgets(choice, sizeof(choice), stdin);
    if (choice[0] != 'y' && choice[0] != 'Y') {
        printf("Aborted.\n"); vault_lock(&v); return 0;
    }

    vault_delete(&v, idx);
    vault_save(&v);
    vault_lock(&v);
    printf("Entry deleted.\n");
    return 0;
}

static int cmd_gen(const char *lenstr)
{
    int len = lenstr ? atoi(lenstr) : 24;
    if (len < 4 || len > 128) { fprintf(stderr, "Length must be 4–128.\n"); return 1; }
    char buf[129];
    vault_generate_password(buf, (size_t)len);
    printf("%s\n", buf);
    return 0;
}

/* ── main ──────────────────────────────────────────────────────────────── */
static void usage(void)
{
    fprintf(stderr,
        "Usage:\n"
        "  securevault new    <vault_file>\n"
        "  securevault add    <vault_file>\n"
        "  securevault get    <vault_file> <label>\n"
        "  securevault list   <vault_file>\n"
        "  securevault delete <vault_file> <label>\n"
        "  securevault gen    <length>\n");
}

int main(int argc, char *argv[])
{
    if (argc < 2) { usage(); return 1; }

    const char *cmd = argv[1];

    if (strcmp(cmd, "new") == 0 && argc == 3)
        return cmd_new(argv[2]);
    if (strcmp(cmd, "add") == 0 && argc == 3)
        return cmd_add(argv[2]);
    if (strcmp(cmd, "get") == 0 && argc == 4)
        return cmd_get(argv[2], argv[3]);
    if (strcmp(cmd, "list") == 0 && argc == 3)
        return cmd_list(argv[2]);
    if (strcmp(cmd, "delete") == 0 && argc == 4)
        return cmd_delete(argv[2], argv[3]);
    if (strcmp(cmd, "gen") == 0)
        return cmd_gen(argc >= 3 ? argv[2] : NULL);

    usage();
    return 1;
}
