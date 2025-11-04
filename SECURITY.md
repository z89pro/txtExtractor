# Security Guidelines

## Environment Variables Required

This bot requires the following environment variables to be set for secure operation:

### Main Bot Configuration
- `BOT_TOKEN`: Your Telegram bot token from @BotFather
- `API_ID`: Your Telegram API ID from my.telegram.org
- `API_HASH`: Your Telegram API hash from my.telegram.org
- `AUTH_USERS`: Comma-separated list of authorized user IDs

### Secondary Bot Configuration (for lo.py)
- `BOT_TOKEN_CW`: Secondary bot token (if using lo.py)
- `API_ID_CW`: Secondary API ID (if using lo.py)  
- `API_HASH_CW`: Secondary API hash (if using lo.py)

## Security Improvements Made

### 🔒 Credential Security
- ✅ Removed all hardcoded bot tokens and API credentials
- ✅ Replaced with environment variable references
- ✅ Added validation for empty credentials

### 🛡️ Input Validation
- ✅ Added null checking for forwarded messages in forward.py
- ✅ Added proper error handling for authentication failures
- ✅ Added validation for user inputs (course IDs, tokens, etc.)

### 🔧 Error Handling
- ✅ Improved error messages with user-friendly feedback
- ✅ Added try-catch blocks for network requests
- ✅ Proper handling of JSON parsing errors

### 📦 Dependency Management
- ✅ Removed duplicate dependencies from requirements.txt
- ✅ Fixed version conflicts (websockets, pyaes, PySocks)
- ✅ Updated to compatible versions

### 🚫 Deprecated Code Removal
- ✅ Removed deprecated `filters.edited` usage across all plugins
- ✅ Updated to current Pyrogram API standards

## Best Practices

1. **Never commit credentials**: Always use environment variables
2. **Validate inputs**: Check user inputs before processing
3. **Handle errors gracefully**: Provide meaningful error messages
4. **Use HTTPS**: All API calls use secure connections
5. **Session management**: Proper handling of authentication tokens

## Setup Instructions

1. Copy `.env.example` to `.env` (create if doesn't exist)
2. Fill in all required environment variables
3. Never commit the `.env` file to version control
4. Use a process manager like PM2 or systemd for production

## Reporting Security Issues

If you discover a security vulnerability, please report it privately to the maintainers.
