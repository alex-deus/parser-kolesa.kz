#!/usr/bin/env bash

args=("$@")

case "${1}" in
    "bash")
        shift
        exec bash -c "${args[@]:1}"
        ;;
    "wait")
        exec bash -c "while true; do sleep 20; done"
        ;;
esac
