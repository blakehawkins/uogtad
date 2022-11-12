#!/usr/bin/env bash
set -euxo pipefail

conda env export > .conda_env.yaml
