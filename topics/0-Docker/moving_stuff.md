
## Short reference to Docker/Rancher linux/unix-extension commands

#### Provided your container name is AAbbCCddEEff to copy file from CONTAINER-to-HOST

```
docker cp AAbbCCddEEff:/path/container-file.txt ~/whatever.txt
```

#### To copy file from HOST-to-CONTAINER

```
docker cp ~/MyDir/my-host-file.txt AAbbCCddEEff:/db/container-file.txt
```

