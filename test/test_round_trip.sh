#!/bin/sh

set -u

# Exit with the first argument after printing the rest of the args as a message
#  to STDERR.
die() {
	status="$1"
	shift
	printf "%s\n" "$*" >&2
	exit "${status}"
}

# Find the first argument that is usable as a temporary directory, that is
#  it exists and is writable.
first_usable_tmpdir() {
	for dir in "$@"; do
		if [ -d "${dir}" ] && [ -w "${dir}" ]; then
			printf '%s' "${dir}"
			return 0
		fi
	done

	return 1
}

# Check that the argument (the file to load) exists.
if [ "$#" -ne 1 ]; then
        printf 'Test that an USeg file, when loaded and saved, round-trips.\nUsage: %s FILE.useg\n\n' "$0" >&2
        die 1 'Error: Missing or wrong arguments given.'
fi

useg_file="$(realpath -e "$1")"

if ! [ -r "${useg_file}" ]; then
	die 1 'Error: The specified input file is not readable or does not exist.'
fi

# Set a temporary directory.
if [ -n "${TMPDIR:+x}" ]; then
	# The temp dir is already set and not an empty string.
	# If it were an empty string, `mktemp` would substitute /tmp automatically,
	#  which we want to prevent, because we check its usability below and want
	#  to die if it is not usable.
	:
else
	# The temp dir is not set yet or empty, try several common possibilities.
	TMPDIR="$(first_usable_tmpdir '/COMP.TMP' '/var/tmp' '/tmp')" || die 1 'No usable temporary directory found, please enter one as TMPDIR in env.'
fi

# Change to the directory with the script; all paths here are relative to it.
mydir="$(dirname "$0")"
cd "${mydir}" || die 1 "Directory ${mydir} not found; maybe \$0 was not set?"

# Create a temporary file and set it up so that it is removed when the
#  script exits.
mytmp="$(mktemp --tmpdir="${TMPDIR}" 'roundtrip.useg.XXXXXXXXXX')" || die 1 "Couldn't create a temporary file in ${TMPDIR}."
printf 'Using temporary file "%s".\n\n' "${mytmp}" >&2
trap 'printf '"'"'\nRemoving temporary file "%s".\n'"'"' "${mytmp}" >&2
      rm -f "${mytmp}"' EXIT

PYTHONPATH=../src python3 ./test_round_trip.py < "${useg_file}" > "${mytmp}" && diff -u0 "${useg_file}" "${mytmp}" && echo OK >&2 || die 1 FAIL
