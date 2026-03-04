# Encrypted Password Manager

A command-line password manager written in **C** using **AES-256-GCM** authenticated encryption and **PBKDF2-HMAC-SHA256** key derivation.

## Why it exists

Most industry password managers are black boxes. SecureVault demonstrates the cryptographic primitives behind them — a common question in security-focused software engineering interviews.

## Features

| Feature | Detail |
|---|---|
| Encryption | AES-256-GCM (authenticated — detects tampering) |
| Key derivation | PBKDF2-HMAC-SHA256, 200 000 iterations |
| Salt | 32 random bytes, unique per vault |
| Password generator | Cryptographically random, configurable length |
| Storage | Single encrypted binary file — portable |
| Memory safety | Key material zeroed after use (`volatile` wipe) |

## Security design

```
master_password + random_salt  ──PBKDF2──►  256-bit key
                                                │
  plaintext entries  ──AES-256-GCM──►  ciphertext + 128-bit GCM tag
                                                │
                              [magic | version | salt | IV | tag | ciphertext]
                                          written to vault file
```

The GCM authentication tag ensures any modification to the ciphertext is detected before decryption. The IV is freshly generated on every save.

## Build

**Requirements:** OpenSSL ≥ 1.1 (`libssl-dev` on Debian/Ubuntu, `brew install openssl` on macOS)

```bash
make
```

Windows (with OpenSSL via vcpkg):
```powershell
make CC=gcc `
     CFLAGS="-Wall -O2 -I$env:VCPKG_ROOT/installed/x64-windows/include" `
     LDFLAGS="-L$env:VCPKG_ROOT/installed/x64-windows/lib -lssl -lcrypto"
```

## Usage

```bash
# Create a new vault
./securevault new my.vault

# Add an entry
./securevault add my.vault

# Retrieve a specific entry (shows password)
./securevault get my.vault github

# List all entries
./securevault list my.vault

# Delete an entry
./securevault delete my.vault github

# Generate a random password (no vault needed)
./securevault gen 32
```

## Project structure

```
securevault/
├── main.c      – CLI entry point, command dispatch
├── vault.c     – Vault CRUD, serialization/deserialization
├── vault.h
├── crypto.c    – AES-256-GCM, PBKDF2, CSPRNG wrappers
├── crypto.h
└── Makefile
```

## Extending

- Add clipboard support (`xclip`/`pbcopy`/`clip.exe`)
- Add TOTP seed storage for 2FA codes
- Add `import/export` for CSV interchange
- Replace flat array with sqlite3 backend for large vaults
