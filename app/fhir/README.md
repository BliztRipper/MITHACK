# IRIS for Health (FHIR R4 server)

Only the FHIR store runs in Docker; the API runs natively (design D1).

```
cd app/fhir && docker compose up -d
# wait ~1-2 min for IRIS, then create the DEMO namespace + FHIR endpoint (idempotent):
docker exec -i iris-fhir iris session IRIS -U %SYS < setup.script
curl http://localhost:32783/csp/healthshare/demo/fhir/r4/metadata
```

Bound to 127.0.0.1 only. No volume: `docker compose down` drops data (re-run setup and seed).

## Attribution
`docker-compose.yml` and `setup.script` are adapted from
[intersystems-community/FHIR-AI-Hackathon-Kit](https://github.com/intersystems-community/FHIR-AI-Hackathon-Kit)
(`docker-iris-fhir/`), MIT License, Copyright (c) 2025 Gabriel Ing.
Changes: stock image instead of a Dockerfile, port 32783 on 127.0.0.1, namespace `DEMO` with endpoint
`/csp/healthshare/demo/fhir/r4`, setup as an ObjectScript script run via `iris session`.

MIT License text: https://github.com/intersystems-community/FHIR-AI-Hackathon-Kit/blob/main/LICENSE

## API client login
The API client (`app/api/fhir/client.py`) reads the IRIS login from env `FHIR_USER` / `FHIR_PASS` and fails if unset
(the stock container's default login is in the Hackathon Kit linked above). Optional: `FHIR_BASE`.
