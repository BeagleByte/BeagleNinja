# bash
# 1) Inspect host paths
ls -la ./config || echo "directory ./config not found"
if [ -e ./config/privoxy.config ]; then
  echo "Host path ./config/privoxy.config exists:"
  file ./config/privoxy.config
  ls -ld ./config/privoxy.config
else
  echo "Host file ./config/privoxy.config does not exist"
fi

# 2) If ./config/privoxy.config is a directory, move it aside
if [ -d ./config/privoxy.config ]; then
  echo "Saving directory ./config/privoxy.config -> ./config/privoxy.config.bak and creating file"
  mv ./config/privoxy.config ./config/privoxy.config.bak
fi

# 3) Ensure directory exists and create an empty config file (or copy your real config into it)
mkdir -p ./config
touch ./config/privoxy.config
chmod 644 ./config/privoxy.config
echo "Created ./config/privoxy.config (regular file)"

# 4) Optional: if your files live in ./configs instead of ./config, show a hint
if [ -d ./configs ] && [ ! -d ./config ]; then
  echo "Found ./configs directory. Either rename it to ./config or update docker-compose.yml to use ./configs"
fi
