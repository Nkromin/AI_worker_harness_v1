# Windows equivalent of run_proxy.sh — loads .env then starts the LiteLLM proxy on :4000
Get-Content .env | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]*)=(.*)$') {
        [System.Environment]::SetEnvironmentVariable($Matches[1].Trim(), $Matches[2].Trim())
    }
}
# LiteLLM's banner crashes on cp1252 consoles without UTF-8 mode
$env:PYTHONUTF8 = "1"
litellm --config harness/litellm_config.yaml --port 4000
