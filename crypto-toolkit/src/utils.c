#include "utils.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#ifdef _WIN32
#  include <windows.h>
#endif

/* Enable ANSI escape codes on Windows 10+ */
void utils_init_console(void)
{
#ifdef _WIN32
    HANDLE h = GetStdHandle(STD_OUTPUT_HANDLE);
    DWORD  mode = 0;
    GetConsoleMode(h, &mode);
    SetConsoleMode(h, mode | ENABLE_VIRTUAL_TERMINAL_PROCESSING);
#endif
}

/* Pretty hex dump */
void hex_dump(const char *label, const uint8_t *data, size_t len)
{
    printf(COL_CYAN "  %-14s" COL_RESET " [%zu B]  ", label, len);
    for (size_t i = 0; i < len && i < 32; i++)
        printf("%02x ", data[i]);
    if (len > 32) printf("...");
    putchar('\n');
}

/* Allocated hex string — caller free()s */
char *bytes_to_hex(const uint8_t *data, size_t len)
{
    char *s = malloc(len * 2 + 1);
    if (!s) return NULL;
    for (size_t i = 0; i < len; i++)
        sprintf(s + i * 2, "%02x", data[i]);
    s[len * 2] = '\0';
    return s;
}

/* Returns 0 on success, -1 on bad input */
int hex_to_bytes(const char *hex, uint8_t *out, size_t *out_len)
{
    size_t hlen = strlen(hex);
    if (hlen % 2 != 0) return -1;
    *out_len = hlen / 2;
    for (size_t i = 0; i < *out_len; i++) {
        char byte[3] = { hex[i*2], hex[i*2+1], '\0' };
        for (int j = 0; j < 2; j++)
            if (!isxdigit((unsigned char)byte[j])) return -1;
        out[i] = (uint8_t)strtoul(byte, NULL, 16);
    }
    return 0;
}

/* PKCS#7 pad — returns new total length */
size_t pkcs7_pad(uint8_t *buf, size_t data_len, size_t block_size)
{
    size_t pad = block_size - (data_len % block_size);
    memset(buf + data_len, (uint8_t)pad, pad);
    return data_len + pad;
}

/* PKCS#7 unpad — returns unpadded length */
size_t pkcs7_unpad(uint8_t *buf, size_t data_len)
{
    if (data_len == 0) return 0;
    uint8_t pad = buf[data_len - 1];
    if (pad == 0 || pad > 16) return data_len;
    return data_len - pad;
}

void print_banner(void)
{
    printf(COL_RED
"  ██████╗██████╗ ██╗   ██╗██████╗ ████████╗██╗  ██╗██╗████████╗\n"
" ██╔════╝██╔══██╗╚██╗ ██╔╝██╔══██╗╚══██╔══╝██║ ██╔╝██║╚══██╔══╝\n"
" ██║     ██████╔╝ ╚████╔╝ ██████╔╝   ██║   █████╔╝ ██║   ██║   \n"
" ██║     ██╔══██╗  ╚██╔╝  ██╔═══╝    ██║   ██╔═██╗ ██║   ██║   \n"
" ╚██████╗██║  ██║   ██║   ██║        ██║   ██║  ██╗██║   ██║   \n"
"  ╚═════╝╚═╝  ╚═╝   ╚═╝   ╚═╝        ╚═╝   ╚═╝  ╚═╝╚═╝   ╚═╝   \n"
    COL_RESET);
    printf(COL_DIM "  C Cryptography Toolkit  |  Caesar · Vigenere · XOR · AES-128 · Base64\n\n" COL_RESET);
}

void print_menu(void)
{
    printf(COL_YELLOW "  ╔══════════════════════════════════╗\n" COL_RESET);
    printf(COL_YELLOW "  ║  " COL_WHITE "SELECT MODE" COL_YELLOW "                      ║\n" COL_RESET);
    printf(COL_YELLOW "  ╠══════════════════════════════════╣\n" COL_RESET);
    printf(COL_YELLOW "  ║  " COL_GREEN "[1]" COL_WHITE " Caesar Cipher            " COL_YELLOW "║\n" COL_RESET);
    printf(COL_YELLOW "  ║  " COL_GREEN "[2]" COL_WHITE " Vigenere Cipher          " COL_YELLOW "║\n" COL_RESET);
    printf(COL_YELLOW "  ║  " COL_GREEN "[3]" COL_WHITE " XOR Stream Cipher        " COL_YELLOW "║\n" COL_RESET);
    printf(COL_YELLOW "  ║  " COL_GREEN "[4]" COL_WHITE " AES-128  (ECB / CBC)     " COL_YELLOW "║\n" COL_RESET);
    printf(COL_YELLOW "  ║  " COL_GREEN "[5]" COL_WHITE " Base64   (enc / dec)     " COL_YELLOW "║\n" COL_RESET);
    printf(COL_YELLOW "  ╠══════════════════════════════════╣\n" COL_RESET);
    printf(COL_YELLOW "  ║  " COL_MAGENTA "[v]" COL_WHITE " Visual Demo              " COL_YELLOW "║\n" COL_RESET);
    printf(COL_YELLOW "  ║  " COL_MAGENTA "[d]" COL_WHITE " Quick Demo               " COL_YELLOW "║\n" COL_RESET);
    printf(COL_YELLOW "  ║  " COL_RED "[0]" COL_WHITE " Exit                     " COL_YELLOW "║\n" COL_RESET);
    printf(COL_YELLOW "  ╚══════════════════════════════════╝\n\n" COL_RESET);
    printf("  " COL_DIM "Choice: " COL_RESET);
}
