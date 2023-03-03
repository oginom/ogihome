set -eux

HOSTNAME=rasp2
HOST_OGIHOME_PATH=ogihome

# for my environment
rsync -C --exclude="/.git" --filter=":- .gitignore" -acvz --delete . $HOSTNAME:$HOST_OGIHOME_PATH
