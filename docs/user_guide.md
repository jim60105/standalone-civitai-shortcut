# Civitai Shortcut User Guide

This guide provides end-user instructions for configuring and troubleshooting the Civitai Shortcut extension.

## Network Configuration and Troubleshooting

### API Key Setup
1. Visit the Civitai API settings page: https://civitai.com/user/account
2. Generate a new API key.
3. Enter the API key in the Civitai Shortcut settings.

### Timeout and Retry Settings
- **Default timeout**: 20 seconds
- **Recommended timeouts**:
  - Fast network: 15–20 seconds
  - Average network: 30–45 seconds
  - Slow network: 60–90 seconds
- **Default retry attempts**: 3
- **Recommended retry attempts**:
  - Stable network: 3
  - Unstable network: 5–7

## Common Issues and Solutions

### Network Connection Error
**Possible causes**:
- Connection interruption
- Firewall or proxy blocking access
- DNS resolution failure

**Solutions**:
1. Check your internet connection.
2. Restart your router or modem.
3. Try using a VPN or different network.
4. Verify firewall/proxy settings.

### Request Timeout Error
**Possible causes**:
- Slow network or server congestion
- Timeout setting too short

**Solutions**:
1. Increase the timeout setting in `setting.py`.
2. Retry after a short interval.
3. Check network speed and stability.

### Invalid API Key Error
**Possible causes**:
- Incorrect or expired API key
- API usage quota exceeded

**Solutions**:
1. Re-enter or generate a new API key.
2. Check your API usage and quota on the Civitai dashboard.

### Download Failure
**Possible causes**:
- Insufficient disk space
- Write permission denied
- Connection interruption

**Solutions**:
1. Free up disk space.
2. Verify folder permissions.
3. Retry the download.

## Performance Optimization Recommendations

### Download Settings
- **Concurrent downloads**: 2–3
- **Chunk size**: 1 MB
- **Enable resume support**: Recommended

### Caching Settings
- **Enable caching**: Recommended
- **Cache size**: 100–200 MB
- **Cache expiration**: 1 hour

### Memory Usage
- **Memory limit**: 200 MB
- **Large file mode**: Use chunked downloads for large files

## Monitoring and Diagnostics (Optional)

If performance monitoring is enabled, refer to the HTTP Client Guide for collecting request statistics and error metrics.
