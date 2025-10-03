# Deploying FIRM UI to Vercel

## Quick Deploy (3 minutes)

### Prerequisites
- GitHub account
- Vercel account (sign up free at https://vercel.com)

### Step 1: Push to GitHub

First, authenticate and push your repository:

```bash
# Authenticate GitHub CLI (one-time)
gh auth login

# Create repository and push
cd "/Users/fractlphoneroom1/Desktop/AnalogExNahilo 2"
gh repo create FIRM-ExNihilo --public --source=. --push --description="Theory-first framework for recursive emergence and consciousness bootstrapping"
```

### Step 2: Deploy to Vercel

**Option A: Via Vercel CLI (Recommended)**

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy (will prompt for login on first use)
cd "/Users/fractlphoneroom1/Desktop/AnalogExNahilo 2"
vercel --prod
```

**Option B: Via Vercel Dashboard**

1. Go to https://vercel.com/new
2. Click "Import Git Repository"
3. Select your `FIRM-ExNihilo` repository
4. Vercel will auto-detect settings from `vercel.json`
5. Click "Deploy"

### Step 3: Access Your Site

After deployment completes, Vercel will provide a URL like:
```
https://firm-exnihilo.vercel.app
```

The FIRM UI will be live at that URL!

## What Gets Deployed

✅ **Included**:
- Complete FIRM UI (index.html + all JavaScript modules)
- ZX evolution engine
- Sacred morphic system
- Theory validation tests
- WebGL visualization pipeline
- All required dependencies

❌ **Excluded** (via .gitignore):
- Debug scripts
- Test images
- Python backend
- Investigation directories

## Configuration Details

**`vercel.json` configures**:
- Static file serving from `FIRM-Core/FIRM_ui/`
- CORS headers for WebGL/Workers
- Route mapping for clean URLs

**Browser Requirements**:
- WebGL2 support
- ES6 modules support
- Modern browser (Chrome, Firefox, Safari, Edge)

## Verify Deployment

Once deployed, open DevTools Console and run:
```javascript
await window.runTheoryValidation();
```

Expected output: `5/5 tests passed` ✅

## Custom Domain (Optional)

To use your own domain:
1. Go to Vercel dashboard → Your project → Settings → Domains
2. Add your domain
3. Follow DNS configuration instructions
4. Vercel handles SSL automatically

## Environment Variables

The FIRM UI is fully static—no environment variables needed!

## Troubleshooting

**"Module not found" errors**:
- Vercel serves from `FIRM-Core/FIRM_ui/` root
- All import paths are relative and should work

**Black viewport**:
- Check browser console for errors
- Run `window.zxEvolutionEngine` to verify engine loaded
- May need to click "Enable Audio" button

**Validation fails**:
- Check `window.runTheoryValidation()` output
- Review `FIRM-Core/FIRM_ui/theory_validation_tests.js` for details

## Local Testing Before Deploy

```bash
cd FIRM-Core/FIRM_ui
python3 -m http.server 8000
# Visit http://localhost:8000
```

Confirms everything works before pushing to Vercel.

---

**Ready to deploy!** Follow Step 1 and Step 2 above.

