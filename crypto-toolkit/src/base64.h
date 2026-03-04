#ifndef BASE64_H
#define BASE64_H

#include <stddef.h>
#include <stdint.h>

/* Returns malloc'd NUL-terminated base64 string; caller free()s.
   Returns NULL on allocation failure. */
char *base64_encode(const uint8_t *data, size_t len);

/* Decodes base64 string into out.  *out_len set to decoded byte count.
   out must be at least (strlen(b64) * 3/4) bytes.
   Returns 0 on success, -1 on invalid input. */
int   base64_decode(const char *b64, uint8_t *out, size_t *out_len);

#endif /* BASE64_H */
