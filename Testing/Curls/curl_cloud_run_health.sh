#!/bin/bash

# ==============================================================================
# HEALTH CHECK PARA GOOGLE CLOUD RUN
# ==============================================================================

CLOUD_RUN_URL="https://prensai-api-2857713417.us-central1.run.app"

echo ""
echo "🏥 HEALTH CHECK - GOOGLE CLOUD RUN"
echo "============================================================"
echo "🌐 URL: $CLOUD_RUN_URL/health"
echo "============================================================"
echo ""

curl -s $CLOUD_RUN_URL/health | jq '.'

echo ""
echo "============================================================"

