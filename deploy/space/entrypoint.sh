#!/bin/sh
# Space entrypoint (live-demo-deployment D6, D8): start IRIS on localhost, set its password, then the demo API on :7860.
set -eu
for v in IRIS_PASSWORD SESSION_SECRET APP_MASTER_KEY DEMO_PASSWORDS; do  # names only, never values
  eval "[ -n \"\${$v:-}\" ]" || { echo "entrypoint: $v is not set; refusing to start" >&2; exit 1; }
done

# The web gateway signs in to IRIS as CSPSystem with the [LOCAL] password in CSP.ini, and CSPSystem can read FHIR data,
# so it gets a fresh random password on every boot (written before IRIS starts the gateway), never the default SYS.
gw=$(python -c 'import secrets; print(secrets.token_hex(24))')
sed -i "/^\[LOCAL\]/,/^\[/ s/^Password=.*/Password=$gw/" /usr/irissys/csp/bin/CSP.ini

echo "entrypoint: starting IRIS"
iris start IRIS quietly
/usr/irissys/dev/Container/waitReady.sh >/dev/null
iris session IRIS -U %SYS < /app/setup.script  # DEMO namespace and FHIR endpoint (fresh disk on every Space start)

# Replace SYS on the login accounts with IRIS_PASSWORD and on CSPSystem with the gateway's. Read from env inside IRIS,
# not from a command line. Not changePassword.sh: on this image it fails (looks for CSPpwd in the wrong directory) and
# leaves CSP.ini stale.
GW_PASSWORD=$gw iris session IRIS -U %SYS <<'OS'
set p("Password")=$System.Util.GetEnviron("IRIS_PASSWORD"),g("Password")=$System.Util.GetEnviron("GW_PASSWORD")
for u="_SYSTEM","SuperUser","Admin" { set sc=##class(Security.Users).Modify(u,.p) if 'sc { write !,"entrypoint: IRIS password change failed for ",u,! do $System.Process.Terminate(,1) } }
set sc=##class(Security.Users).Modify("CSPSystem",.g) if 'sc { write !,"entrypoint: IRIS password change failed for CSPSystem",! do $System.Process.Terminate(,1) }
halt
OS
unset gw

export FHIR_USER=_SYSTEM FHIR_PASS="$IRIS_PASSWORD"
unset IRIS_PASSWORD
echo "entrypoint: starting the demo API on :7860"
exec uvicorn main:app --host 0.0.0.0 --port 7860 --no-access-log  # no access log: patient data never reaches logs
