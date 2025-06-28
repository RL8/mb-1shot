# Vercel + GitHub Actions Deployment Setup

## Step 1: Complete Vercel Project Setup

If you haven't finished the `vercel link` command, you'll need to:

1. **Choose "Set up new project"** when prompted
2. **Project name**: `mb-1shot` (or your preferred name)
3. **Framework preset**: Should auto-detect as "Vite"
4. **Root directory**: `.` (current directory)
5. **Build settings**: Should auto-detect from `vercel.json`

## Step 2: Get Your Vercel Token

Run this command to get your Vercel token:
```bash
vercel whoami --token
```

Or get it from the Vercel dashboard:
1. Go to https://vercel.com/account/tokens
2. Click "Create Token"
3. Name it "GitHub Actions"
4. Copy the token (keep it secure!)

## Step 3: Set up GitHub Repository Secrets

Add these secrets to your GitHub repository:

### Via GitHub Web Interface:
1. Go to https://github.com/RL8/mb-1shot/settings/secrets/actions
2. Click "New repository secret"
3. Add these secrets:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `VERCEL_TOKEN` | `your_vercel_token_here` | Token from Step 2 |
| `VERCEL_ORG_ID` | `your_org_id` | From `.vercel/project.json` |
| `VERCEL_PROJECT_ID` | `your_project_id` | From `.vercel/project.json` |

### Via GitHub CLI (Alternative):
```bash
# Set Vercel token
gh secret set VERCEL_TOKEN --body "your_vercel_token_here"

# Set org and project IDs (after vercel link completes)
gh secret set VERCEL_ORG_ID --body "$(cat .vercel/project.json | jq -r '.orgId')"
gh secret set VERCEL_PROJECT_ID --body "$(cat .vercel/project.json | jq -r '.projectId')"
```

## Step 4: Update GitHub Actions Workflow

The workflow needs the additional secrets, so let me update it for you.

## Step 5: Test Deployment

Once secrets are set:
1. Push any change to master branch
2. GitHub Actions will automatically deploy to Vercel
3. Check the Actions tab for deployment status
4. Your app will be live at your Vercel URL

## Manual Deployment (Alternative)

You can also deploy manually anytime:
```bash
vercel --prod
```

## Vercel Project URLs

After setup, you'll have:
- **Preview URL**: Auto-generated for each deployment
- **Production URL**: Your main app URL (custom domain possible)
- **Dashboard**: https://vercel.com/dashboard

## Benefits of Vercel vs GitHub Pages

✅ **Faster builds** (30s vs 2-3min)  
✅ **Better performance** (Edge CDN)  
✅ **Custom domains** (free SSL)  
✅ **Analytics** (web vitals)  
✅ **Preview deployments** (for PRs)  
✅ **Serverless functions** (if needed later)

## Troubleshooting

### Common Issues:
1. **Token error**: Make sure VERCEL_TOKEN is correct
2. **Build fails**: Check package.json scripts
3. **404 errors**: Ensure vercel.json rewrites are set
4. **Secrets missing**: Verify all 3 secrets are set in GitHub

### Debug Commands:
```bash
# Test local build
npm run build

# Test Vercel config
vercel build

# Check secrets (GitHub CLI)
gh secret list
``` 