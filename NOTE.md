# DEVELOPER NOTE

sudo ln -s "$HOME/.docker/run/docker.sock" /var/run/docker.sock

Commands you can use next
=========================

[*] Validate SAM template: sam validate
[*] Invoke Function: sam local invoke
[*] Test Function in the Cloud: sam sync --stack-name {{stack-name}} --watch
[*] Deploy: sam deploy --guided

/Users/tangross/.ollama
/usr/share/ollama/.ollama

```shell
curl http://localhost:11434/api/generate -d '{"model": "deepseek-r1:1.5B","prompt": "Why is the sky blue?"}'
curl -X POST http://localhost:3000/api/generate -H "Content-Type: application/json" -d '{"model": "deepseek-r1:1.5B","prompt": "Why is the sky blue?"}'
curl http://localhost:3000/api/version
curl http://localhost:11434/api/chat -d '{"model": "deepseek-r1:1.5B","messages": [{"role":"user","content":"Why is the sky blue?"}]}'
curl http://localhost:8000/api/chat -d '{"model": "deepseek-r1:1.5B","messages": [{"role":"user","content":"Why is the sky blue?","stream":false}]}'
```

```shell
docker pull public.ecr.aws/docker/library/python:3.12-slim
# Clean up Docker system
docker system prune -f 
```
find / \( -path /proc -prune -a -path /dev -prune \) -o -type f -size +30M -exec ls -s1 {} \;  2>/dev/null| sort -n -r | head -n 20
