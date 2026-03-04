#include "base64.h"
#include <stdlib.h>
#include <string.h>

static const char B64_TABLE[] =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

char *base64_encode(const uint8_t *data, size_t len)
{
    size_t out_len = 4 * ((len + 2) / 3);
    char  *out = malloc(out_len + 1);
    if (!out) return NULL;

    size_t i = 0, j = 0;
    while (i < len) {
        int bytes = 1;
        uint32_t triple = (uint32_t)data[i++] << 16;
        if (i < len) { triple |= (uint32_t)data[i++] << 8;  bytes++; }
        if (i < len) { triple |= (uint32_t)data[i++];       bytes++; }

        out[j++] = B64_TABLE[(triple >> 18) & 0x3F];
        out[j++] = B64_TABLE[(triple >> 12) & 0x3F];
        out[j++] = (bytes >= 2) ? B64_TABLE[(triple >> 6) & 0x3F] : '=';
        out[j++] = (bytes >= 3) ? B64_TABLE[(triple >> 0) & 0x3F] : '=';
    }
    out[j] = '\0';
    return out;
}

static int b64_val(char c)
{
    if (c >= 'A' && c <= 'Z') return c - 'A';
    if (c >= 'a' && c <= 'z') return c - 'a' + 26;
    if (c >= '0' && c <= '9') return c - '0' + 52;
    if (c == '+')             return 62;
    if (c == '/')             return 63;
    return -1;
}

int base64_decode(const char *b64, uint8_t *out, size_t *out_len)
{
    size_t in_len = strlen(b64);
    if (in_len % 4 != 0) return -1;

    *out_len = (in_len / 4) * 3;
    if (in_len >= 1 && b64[in_len-1] == '=') (*out_len)--;
    if (in_len >= 2 && b64[in_len-2] == '=') (*out_len)--;

    size_t j = 0;
    for (size_t i = 0; i < in_len; i += 4) {
        int  v0 = b64_val(b64[i]),   v1 = b64_val(b64[i+1]);
        int  v2 = b64[i+2]=='=' ? 0 : b64_val(b64[i+2]);
        int  v3 = b64[i+3]=='=' ? 0 : b64_val(b64[i+3]);
        if (v0 < 0 || v1 < 0 || v2 < 0 || v3 < 0) return -1;

        uint32_t triple = ((uint32_t)v0 << 18) | ((uint32_t)v1 << 12)
                        | ((uint32_t)v2 <<  6) | (uint32_t)v3;
        out[j++] = (uint8_t)((triple >> 16) & 0xFF);
        if (b64[i+2] != '=') out[j++] = (uint8_t)((triple >> 8) & 0xFF);
        if (b64[i+3] != '=') out[j++] = (uint8_t)( triple       & 0xFF);
    }
    return 0;
}
