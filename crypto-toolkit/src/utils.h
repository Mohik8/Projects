#ifndef UTILS_H
#define UTILS_H

#include <stdint.h>
#include <stddef.h>

/* ── ANSI colour helpers ─────────────────────────────────────────────── */
#define COL_RESET   "\033[0m"
#define COL_RED     "\033[1;31m"
#define COL_GREEN   "\033[1;32m"
#define COL_YELLOW  "\033[1;33m"
#define COL_CYAN    "\033[1;36m"
#define COL_MAGENTA "\033[1;35m"
#define COL_WHITE   "\033[1;37m"
#define COL_BLUE    "\033[1;34m"
#define COL_DIM     "\033[2m"

void  utils_init_console(void);          /* enable VT100 on Windows        */
void  hex_dump(const char *label, const uint8_t *data, size_t len);
void  print_banner(void);
void  print_menu(void);
char *bytes_to_hex(const uint8_t *data, size_t len); /* caller free()s    */
int   hex_to_bytes(const char *hex, uint8_t *out, size_t *out_len);

/* PKCS#7 padding (in-place, buf must have room for up to 16 extra bytes) */
size_t pkcs7_pad  (uint8_t *buf, size_t data_len, size_t block_size);
size_t pkcs7_unpad(uint8_t *buf, size_t data_len);

#endif /* UTILS_H */
