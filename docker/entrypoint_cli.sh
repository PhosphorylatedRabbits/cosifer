#!/bin/bash

set -Eeuo pipefail

app_user=cosifer
# check if user is root
if [ "$(id -u)" = '0' ]; then
	# make sure we can write to stdout and stderr as $app_user
	chown --dereference $app_user "/proc/$$/fd/1" "/proc/$$/fd/2" || :
	exec gosu $app_user "$BASH_SOURCE" "$@"
    # below will never be called by root, but $app_user instead
fi

cosifer "$@"
