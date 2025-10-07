#!/bin/bash

# Script para ver costos de Google Cloud Platform

echo "📊 COSTOS DE GOOGLE CLOUD - PRENSAI"
echo "===================================="
echo ""

# Requiere gcloud CLI instalado y autenticado
# gcloud auth login

PROJECT_ID="prensai-442915"

echo "🔍 Costo del mes actual:"
gcloud billing accounts list --format="table(displayName, open)" 2>/dev/null

echo ""
echo "📈 Uso de Cloud Run (últimas 24 horas):"
gcloud run services list --platform=managed --region=us-central1 --format="table(SERVICE,REGION,URL,LAST_MODIFIER_EMAIL)" 2>/dev/null

echo ""
echo "📦 Imágenes en Container Registry:"
gcloud container images list --format="table(name)" 2>/dev/null

echo ""
echo "🏗️ Builds recientes:"
gcloud builds list --limit=5 --format="table(id,createTime,duration,status)" 2>/dev/null

echo ""
echo "💡 Para ver costos detallados, visita:"
echo "   https://console.cloud.google.com/billing"
echo ""

