# Security

## Exposed credential (action required)

While this repository was public, `literature_mining/3.run_breeding_evaluation.py`
contained a **hard-coded API key** together with an internal service
endpoint, for example:

```python
API_KEY = "sk-..."                     # hard-coded, now removed
URL = "http://<internal-host>/api/v1/run/<flow-id>"
```

Because the repository is public, that key must be treated as compromised.

### What to do

1. **Revoke / rotate the key** at the service that issued it. Assume it
   has already been scraped and is being abused.
2. Replace it with a new key and provide it via the environment only:
   ```bash
   export BREEDING_API_KEY="<new key>"
   export BREEDING_API_URL="https://<host>/api/v1/run/<flow-id>"
   ```
3. Never commit keys, tokens or internal endpoints. Use environment
   variables (as the scripts do now) or a secrets manager.

### Current handling

* The key and URL are read from the environment
  (`BREEDING_API_KEY`, `BREEDING_API_URL`); the script exits with a clear
  message if they are missing.
* No credentials are stored anywhere in this repository.

## Reporting

If you find a security issue, please contact the maintainer directly
rather than opening a public issue.

## General hygiene for contributors

* Keep `config/config.yaml` (machine-specific, may contain paths) out of
  version control — it is listed in `.gitignore`.
* Do not commit raw data, databases or large intermediate files.
