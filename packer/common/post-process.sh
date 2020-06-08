#!/bin/bash

if hash jq 2>/dev/null; then
  AMI_ID=$(jq ".builds[-1].artifact_id" manifest.json | cut -d: -f 2 | tr -d '"')
  # This runs on local, which may be mac or linux. Which is why we need both -i'' and -e
  sed -i'' -e "s/ami_id:.*$/ami_id: $AMI_ID/" ../config.yaml
else
  echo "Please manually modify the config.yaml file to set the following AMI ID";
  grep "artifact_id" manifest.json | tail -1 | cut -d: -f3 | tr -d '",'
fi
