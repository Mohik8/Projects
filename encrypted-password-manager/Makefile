CC      = gcc
CFLAGS  = -Wall -Wextra -O2 -std=c11 -pedantic
LDFLAGS = -lssl -lcrypto
TARGET  = securevault
SRCS    = main.c vault.c crypto.c
OBJS    = $(SRCS:.c=.o)

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

clean:
	rm -f $(OBJS) $(TARGET)

# On Windows with vcpkg or pre-built OpenSSL:
#   make CC=gcc CFLAGS="-Wall -O2 -I/path/to/openssl/include" LDFLAGS="-L/path/to/openssl/lib -lssl -lcrypto"
