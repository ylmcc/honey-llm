LLM Honey is a SSH honeypot that uses LLMs to respond to commands.

Works with Ollama only currently, will add support for ChatGPT, etc in the future


Example session from Client POV

```
 ssh localhost -p2222
kyle@localhost's password:


 _______          _                 _            _       ____
/ ____(_) ___  __| |_ _ __ ___  ___| |_ _ __   (_) ___ _ __
| (___| |/ _ \/ _` | || '__/ _ \/ _ \ | || '_ \  | |/ _ \ '__|
 \___ \| |  __/ _,_| || | |  __/  __/ |_| | |_) | | |  __/ |
|_____/|_|\___|\__,_|___|_|\___|\___|\__, | .__/|_|_|\___|_|
                                    |___/|_|

                               CentOS Server
                      Transport-Staging.wheels.ride
                          _______
                         / ____(_) ___
                        | (___| |/ _ \
                        \___ \| |  __/
                         |_____|_|\___|

                    [Industry]: Transportation


kyle@transport-staging.wheels.ride:/home/kyle$ cd /var
/var
kyle@transport-staging.wheels.ride:/var$ ls -l
kyle@transport-staging.wheels.ride:/var$
 drwxr-xr-x 2 root root 4096 Jun 15 17:34 /var
kyle@transport-staging.wheels.ride:/var$ ls -l /var/
kyle@transport-staging.wheels.ride:/var$
 -drwxr-xr-x. 2 root root 4096 Oct 23 17:48 /var/
   -drwxr-xr-x. 12 root adm   4096 Nov  5 11:22 /var/adm
   drwxr-xr-x. 2 root mail  4096 Oct 23 17:48 /var/lib
   -rw-r--r--. 1 root root   110 Nov 15 11:16 /var/log/lastlog
   drwxr-xr-x. 2 root message 4096 Oct 23 17:48 /var/log
   -rw-r--r--. 1 root adm    15 Nov 15 11:17 /var/run/auditd/auditd.pid
   -rw-------. 1 root root   912 Nov 16 09:43 /var/spool/cron/crontabs/kyle
   drwxr-xr-x. 2 root mail  4096 Oct 23 17:48 /var/spool/mail
   drwxrwxrwt. 15 root syslog 4096 Nov 15 11:18 /var/syslog
   -rw-r--r--. 1 root root   213 Oct 23 17:48 /var/tmp/anaconda-ks.cfg
   drwxr-xr-x. 6 root postfix 4096 Nov 15 11:17 /var/spool/postfix
   -rw-------. 1 root mail   32 Nov 15 11:18 /var/spool/postfix/info/master.pid
   drwxr-xr-x. 2 root postfix 4096 Oct 23 17:48 /var/spool/postfix/queue
   -rw-------. 1 root mail    0 Nov 15 11:17 /var/spool/postfix/queue.db
   drwxr-xr-x. 6 root postfix 4096 Oct 23 17:48 /var/spool/postfix/sendmail.stuff
   drwxr-xr-x. 2 root postfix 4096 Oct 23 17:48 /var/spool/postfix/starttls
   -rw-------. 1 root mail   15 Nov 15 11:17 /var/spool/postfix/sync
   drwxr-xr-x. 2 root postfix 4096 Oct 23 17:48 /var/spool/postfix/tls
   -rw-------. 1 root mail    0 Nov 15 11:17 /var/spool/postfix/unknown
   drwxr-xr-x. 2 root postfix 4096 Oct 23 17:48 /var/spool/postmap
   -rw-------. 1 root mail    0 Nov 15 11:17 /var/spool/postmark
   drwxr-xr-x. 2 root postfix 4096 Oct 23 17:48 /var/spool/bind
   drwxr-xr-x. 2 root bind   4096 Nov 15 11:16 /var/named
   -rw-------. 1 root bind    64 Nov 15 11:17 /var/named/data/cache_dump.db
   drwxr-xr-x. 2 root bind   4096 Oct 23 17:48 /var/named/dynamic
   -rw-------. 1 root bind    0 Nov 15 11:17 /var/named/empty
   drwxr-xr-x. 2 root bind   4096 Oct 23 17:48 /var/named/master
   drwxr-xr-x. 2 root bind   4096 Nov 15 11:16 /var/named/slaves
   -rw-------. 1 root bind    0 Nov 15 11:17 /var/named/zone.db.junk
   drwxr-xr-x. 2 root named   4096 Oct 23 17:48 /var/named/zones
   drwxr-xr-x. 2 root sshd    4096 Nov 15 11:17 /var/lock
   -rw-r--r--. 1 root adm     371 Oct 23 17:48 /var/log/sshd_keys
   drwxr-xr-x. 2 root sshd    4096 Nov 15 11:17 /var/run
   -rw-------. 1 root sshd    301 Oct 23 17:48 /var/run/sshd.pid
   drwxr-xr-x. 2 root sshd    4096 Nov 15 11:17 /var/tmp
kyle@transport-staging.wheels.ride:/var$ 
Connection to localhost closed.
```

Same session from server POV:
```
2024-12-09 02:30:37,251 - INFO - Starting LLM Honey on 0.0.0.0:2222
Saving details to sqlite
2024-12-09 02:30:38,443 - INFO - Connection from ('127.0.0.1', 33558)
2024-12-09 02:30:38,444 - INFO - Connected (version 2.0, client OpenSSH_8.9p1)
2024-12-09 02:30:38,453 - INFO - Auth rejected (none).
2024-12-09 02:30:39,367 - INFO - Authentication attempt: username=kyle, password=test
2024-12-09 02:30:39,376 - INFO - Saved credentials to DB
2024-12-09 02:30:39,377 - INFO - Auth granted (password).
2024-12-09 02:30:39,378 - INFO - password:
2024-12-09 02:30:39,378 - INFO - Industry is set to Transportation
2024-12-09 02:30:39,660 - INFO - HTTP Request: POST /api/chat "HTTP/1.1 200 OK"
2024-12-09 02:30:39,660 - INFO - Domain is set to transport-staging.wheels.ride
2024-12-09 02:30:39,660 - INFO - Banner generated will be CentOS for transport-staging.wheels.ride
2024-12-09 02:30:41,671 - INFO - HTTP Request: POST /api/chat "HTTP/1.1 200 OK"
2024-12-09 02:30:50,464 - INFO - Received command: cd /var
2024-12-09 02:30:51,473 - INFO - Received command: ls -l
2024-12-09 02:30:51,473 - INFO - Command: ls -l /var
2024-12-09 02:30:51,964 - INFO - HTTP Request: POST /api/chat "HTTP/1.1 200 OK"
2024-12-09 02:30:59,969 - INFO - Received command: ls -l /var/
2024-12-09 02:31:15,823 - INFO - HTTP Request: POST /api/chat "HTTP/1.1 200 OK"
^C2024-12-09 02:32:01,074 - INFO - Connection closed.
```
