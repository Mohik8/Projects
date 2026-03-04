CC     = gcc
CFLAGS = -Wall -Wextra -O2 -std=c11
SRC    = src/main.c src/aes.c src/ciphers.c src/base64.c src/utils.c src/visuals.c
TARGET = cryptkit

all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) $(SRC) -o $(TARGET)

clean:
	del /Q $(TARGET).exe 2>NUL || rm -f $(TARGET)

.PHONY: all clean
