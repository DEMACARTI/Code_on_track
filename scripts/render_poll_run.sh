#!/bin/bash
set -e

RENDER_API_KEY=$1
RENDER_JOB_ID=$2

if [ -z "$RENDER_API_KEY" ] || [ -z "$RENDER_JOB_ID" ]; then
  echo "Usage: $0 <RENDER_API_KEY> <RENDER_JOB_ID>"
  exit 1
fi

echo "Triggering Render Job: $RENDER_JOB_ID"

RESPONSE=$(curl -s -f -X POST "https://api.render.com/v1/jobs/${RENDER_JOB_ID}/runs" \
  -H "Authorization: Bearer ${RENDER_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{}')

RUN_ID=$(echo "$RESPONSE" | jq -r .id)

if [ -z "$RUN_ID" ] || [ "$RUN_ID" == "null" ]; then
  echo "Failed to trigger job. Response: $RESPONSE"
  exit 1
fi

echo "Job triggered. Run ID: $RUN_ID"
echo "Polling status..."

for i in $(seq 1 120); do
  STATUS_RESPONSE=$(curl -s -f -H "Authorization: Bearer ${RENDER_API_KEY}" \
    "https://api.render.com/v1/job-runs/${RUN_ID}")
  
  STATUS=$(echo "$STATUS_RESPONSE" | jq -r .status)
  
  echo "Attempt $i: Status is $STATUS"
  
  if [ "$STATUS" == "succeeded" ]; then
    echo "Job completed successfully."
    exit 0
  fi
  
  if [ "$STATUS" == "failed" ] || [ "$STATUS" == "canceled" ]; then
    echo "Job failed or canceled."
    exit 2
  fi
  
  sleep 5
done

echo "Timeout waiting for job completion."
exit 2
