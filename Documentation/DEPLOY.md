# Melody Map - Deployment

## Auto-Deploy

Push to branch → automatic deployment to Cloud Run ✅

- **`develop`** → https://melody-map-dev-1011196950471.us-central1.run.app
- **`main`** → https://melody-map-1011196950471.us-central1.run.app

## Manual Deploy

```bash
# Dev
gcloud run deploy melody-map-dev --source . --region us-central1 --project melodymap-cs-3398

# Prod
gcloud run deploy melody-map --source . --region us-central1 --project melodymap-cs-3398
```

## View Logs

```bash
# Dev
gcloud run services logs tail melody-map-dev --region us-central1 --project melodymap-cs-3398

# Prod
gcloud run services logs tail melody-map --region us-central1 --project melodymap-cs-3398
```