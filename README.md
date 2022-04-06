### Save private information and share it with one-time links 

#### Info

Sending passwords, certificates, keys, etc. via emails, instant messengers and others method is a common practice. This is also bad practice. Save your information encrypted on the server and get a one-time link. You can safely send this link in your favorite way. The information will not be available in the correspondence. After clicking on this link, the information will be displayed on the screen and permanently deleted from the server.

Encryption is done with AES 128 in CBC mode.

The decryption key is not stored on the server. The key is only available in the link. The key cannot be restored.

#### Automation

For automation tasks, you can create one-time link by token from JSON format by result:  

```
http://server:port/make_url?secret=some_private_unformation
```

#### Docker

Available at the link:

[https://hub.docker.com/r/silyashevich/secret_service](https://hub.docker.com/r/silyashevich/secret_service)


```
docker pull silyashevich/secret_service
```

If you want to persist the data in sqlite:

```console
docker run -d -p 5000:5000 -v /host/db/local-db:/code/db silyashevich/secret_service:latest
```

