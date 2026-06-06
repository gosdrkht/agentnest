# Landing Page Deployment Guide

## 🚀 Deploy to Production (Free Options)

Your landing page is ready to deploy to the internet. Choose one of these free/cheap options:

### Option 1: Netlify (Easiest - Recommended)

```bash
# 1. Create Netlify account: https://app.netlify.com

# 2. Install Netlify CLI
npm install -g netlify-cli

# 3. Deploy
cd landing
netlify deploy --prod

# 4. Choose folder: landing/
# Done! Your site is live at [randomname].netlify.app

# 5. Add custom domain
# Settings > Domain Management > Custom Domain
# Add: agentnest.io
```

**Cost: $0 (free tier) to $15/month (pro)**

### Option 2: Vercel (Fast CDN)

```bash
# 1. Create Vercel account: https://vercel.com

# 2. Connect your GitHub repo (automatic deploys)
# 3. Deploy with one click
# Done! Your site is live at [project].vercel.app

# 4. Add custom domain in Vercel dashboard
```

**Cost: $0 (free tier) to $20/month (pro)**

### Option 3: GitHub Pages (Simplest)

```bash
# 1. Rename landing/ to docs/
mv landing docs

# 2. Push to GitHub
git add .
git commit -m "Add landing page"
git push

# 3. Go to Settings > Pages
# Select Source: main branch /docs folder
# Done! Your site is live at gosdrkht.github.io/agentnest

# 4. Point custom domain to GitHub Pages
# In your DNS settings:
# A record: 185.199.108.153
# CNAME: agentnest.io -> gosdrkht.github.io
```

**Cost: $0 (free tier)**

### Option 4: AWS S3 + CloudFront (Most Control)

```bash
# 1. Create S3 bucket
aws s3 mb s3://agentnest.io --region us-east-1

# 2. Enable static website hosting
aws s3 website s3://agentnest.io \
  --index-document index.html \
  --error-document index.html

# 3. Upload files
aws s3 sync landing/ s3://agentnest.io/ \
  --delete \
  --exclude '.DS_Store'

# 4. Create CloudFront distribution (CDN)
# AWS Console > CloudFront > Create Distribution
# Origin: agentnest.io.s3.amazonaws.com
# Add SSL certificate

# 5. Point domain to CloudFront
# Route 53 > Create A record
# Alias: CloudFront distribution
```

**Cost: $0.50-2/month (S3 + CloudFront)**

---

## 🎯 Quick Start (Netlify - Recommended)

### Step 1: Prepare Files

```bash
cd landing
ls -la
# Should see: index.html, styles.css, script.js
```

### Step 2: Create Netlify Account

Visit: https://app.netlify.com/signup

### Step 3: Deploy

**Option A: Drag & Drop (Easiest)**
1. Go to https://app.netlify.com
2. Drag the `landing/` folder onto the page
3. Done! Your site is live

**Option B: CLI (Recommended)**

```bash
# Install CLI
npm install -g netlify-cli

# Login
netlify login

# Deploy
cd landing
netlify deploy --prod

# Output:
# ✔ Site created
# ✔ Published to [yoursite].netlify.app
```

### Step 4: Add Custom Domain

1. Netlify Dashboard > Site Settings > Domain Management
2. Click "Add custom domain"
3. Enter: `agentnest.io`
4. Follow DNS setup instructions

---

## 📊 Setup Analytics

### Google Analytics

```bash
# 1. Create account: https://analytics.google.com

# 2. Get measurement ID (looks like: G-XXXXXXXXXX)

# 3. Add to script.js:
# Replace GA_MEASUREMENT_ID with your ID

# 4. Add tracking to landing/script.js (already done!)
```

### Netlify Analytics (Built-in)

```bash
# Enable in Netlify dashboard
# Settings > Analytics
# $9/month for detailed analytics
```

---

## 🔍 SEO Optimization

Your landing page already includes:
- ✅ Meta descriptions
- ✅ Open Graph tags (social sharing)
- ✅ Twitter cards
- ✅ Canonical URLs
- ✅ Mobile responsive
- ✅ Fast loading (< 2s)

### Further Optimization:

```bash
# 1. Submit to Google Search Console
https://search.google.com/search-console

# 2. Add sitemap
# Create landing/sitemap.xml

# 3. Add robots.txt
# Create landing/robots.txt

# 4. Monitor search performance
# Check Google Analytics + Search Console
```

---

## 🔗 Point Your Domain

### If you already have agentnest.io:

**Using Netlify:**
```
# DNS Settings (GoDaddy, Namecheap, etc.):
Add CNAME record:
Name: www
Value: agentnest.io (your Netlify domain)

Add A record for @:
Value: Netlify IP (they'll provide)
```

**Using AWS Route 53:**
```bash
# Create hosted zone for agentnest.io
aws route53 create-hosted-zone \
  --name agentnest.io \
  --caller-reference $(date +%s)

# Get nameservers and update registrar

# Create A record pointing to CloudFront
aws route53 change-resource-record-sets \
  --hosted-zone-id ZONE_ID \
  --change-batch file://route53-change-batch.json
```

---

## ✅ Pre-Launch Checklist

- [ ] Landing page deployed (check at yoursite.netlify.app)
- [ ] Custom domain working (agentnest.io)
- [ ] SSL certificate valid (HTTPS)
- [ ] Mobile responsive (test on phone)
- [ ] All links working
- [ ] CTA buttons point to app.agentnest.io
- [ ] Email signup working
- [ ] Analytics setup
- [ ] Social media images ready
- [ ] Tested in Chrome, Safari, Firefox

---

## 📱 Update Links in Landing Page

Before deploying, update these:

```html
<!-- In index.html, replace these URLs: -->

<!-- Change these:
  https://app.agentnest.io/signup
  https://app.agentnest.io/login
-->

<!-- To your actual backend URL once deployed to AWS:
  https://app.agentnest.io/signup  (keep as is, or change if different)
-->
```

---

## 🚀 Launch Checklist

### Week 1: Deploy & Setup
- [ ] Landing page live at agentnest.io
- [ ] Backend live at api.agentnest.io
- [ ] App live at app.agentnest.io
- [ ] Email signup working
- [ ] Analytics tracking

### Week 2: Get First Users
- [ ] Post to Hacker News (https://news.ycombinator.com/submit)
- [ ] Submit to Product Hunt (https://www.producthunt.com)
- [ ] Tweet about launch
- [ ] Share on Reddit (r/webdev, r/devops, r/python)
- [ ] Email your network

### Week 3: Optimize & Convert
- [ ] Track signup conversion rate
- [ ] Optimize based on analytics
- [ ] Gather user feedback
- [ ] Fix bugs reported
- [ ] Plan next features

---

## 💡 Marketing Tips

1. **Social Media**
   - Screenshot the dashboard
   - Make a 30-second demo video
   - Share on Twitter, LinkedIn, Reddit

2. **Content**
   - Write blog post: "How to Deploy Docker Containers in 30 Seconds"
   - Create comparison: "AgentNest vs Heroku vs Railway"

3. **Community**
   - Join AI/DevOps Slack communities
   - Answer questions on Stack Overflow
   - Contribute to open source

---

## 🎉 You're Ready to Launch!

Your landing page is production-ready. Choose your deployment method and go live!

**Questions?**
- Email: hello@agentnest.io
- GitHub Issues: https://github.com/gosdrkht/agentnest/issues
