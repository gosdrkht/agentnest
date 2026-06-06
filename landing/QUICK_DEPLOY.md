# 🚀 Deploy AgentNest Landing Page in 5 Minutes

## ⚡ FASTEST WAY (Recommended)

### Option 1: Netlify (Most Popular)

```bash
# Step 1: Install CLI
npm install -g netlify-cli

# Step 2: Login
netlify login
# Opens browser → Click authorize → Done

# Step 3: Deploy
cd landing
netlify deploy --prod

# Wait 30 seconds...
# ✅ Your site is LIVE!
# Output shows your URL
```

**What happens:**
- CLI uploads files to Netlify
- Netlify creates HTTPS certificate (auto)
- DNS propagates (< 1 min)
- Site live at `https://[yourname].netlify.app`

---

### Option 2: GitHub Pages (Instant - No Setup)

```bash
# Already pushed to GitHub!
# Just 2 clicks:

# 1. Go to:
https://github.com/gosdrkht/agentnest/settings/pages

# 2. Select:
# Source: Deploy from a branch
# Branch: main
# Folder: /landing

# 3. Click Save
# ✅ Live in 1 minute!
# URL: https://gosdrkht.github.io/agentnest/landing
```

---

### Option 3: Vercel (Best Performance)

```bash
# 1. Visit: https://vercel.com/new

# 2. Select: Import Git Repository
# → Choose: gosdrkht/agentnest

# 3. Configure:
# Framework Preset: Other (static)
# Root Directory: landing

# 4. Click Deploy
# ✅ Live instantly!
```

---

## 📊 Comparison

| Platform | Time | Cost | SSL | Custom Domain | CDN | Performance |
|----------|------|------|-----|---|---|---|
| **Netlify** | 1 min | Free | ✅ | ✅ | ✅ | ⭐⭐⭐⭐ |
| **Vercel** | 1 min | Free | ✅ | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| **GitHub Pages** | 2 min | Free | ✅ | ✅ | ✅ | ⭐⭐⭐ |

---

## 🎯 RECOMMENDED: Netlify

### Why?
- ✅ Easiest setup
- ✅ Free tier generous
- ✅ Great support
- ✅ Perfect for startups
- ✅ Auto-deploys from GitHub

### Quick Command (Copy & Paste)

```bash
npm install -g netlify-cli && netlify login && cd landing && netlify deploy --prod
```

---

## 🔧 AFTER DEPLOYMENT

### Step 1: Get Your URL
The deploy command shows:
```
✅ Site published at https://agentnest-12345.netlify.app
```

### Step 2: Add Custom Domain

**If you own agentnest.io:**

```bash
# In Netlify Dashboard:
# 1. Settings > Domain Management
# 2. Add custom domain: agentnest.io
# 3. Update DNS at your registrar (GoDaddy, Namecheap, etc.)

# Add CNAME record:
# Host: agentnest.io
# Value: agentnest-12345.netlify.app

# Netlify auto-provisions SSL (5 min)
```

### Step 3: Verify

```bash
# In terminal:
curl -I https://agentnest.io

# Should show:
# HTTP/2 200
# X-Frame-Options: DENY
# Cache-Control: max-age=3600
```

---

## 📈 VERIFY DEPLOYMENT

### Check it's working:

```bash
# 1. Open in browser
https://agentnest.io  (or your Netlify URL)

# 2. Check in DevTools (F12):
# Network tab → All files load
# Console → No errors
# Mobile tab → Responsive

# 3. Test features:
# - Click navigation links
# - Open FAQ items
# - Toggle pricing (monthly/annual)
# - Click CTA buttons
```

### Browser testing:

```bash
# Test on:
☑ Chrome/Edge (Windows)
☑ Safari (Mac/iPhone)
☑ Firefox
☑ Mobile Safari
```

---

## 🚨 TROUBLESHOOTING

### "Site not found" error

**Solution:**
```bash
# Make sure you're in landing folder
cd landing
ls -la
# Should see: index.html, styles.css, script.js

# Deploy again
netlify deploy --prod
```

### "netlify: command not found"

**Solution:**
```bash
# Install CLI
npm install -g netlify-cli

# Verify
netlify --version
```

### "Auth failed"

**Solution:**
```bash
# Clear cached auth
netlify logout
netlify login
```

---

## ⏱️ Timeline

```
Right Now:
  npm install -g netlify-cli          ← 1 min
  
In 1 min:
  netlify login                        ← Opens browser
  
In 2 min:
  cd landing                           ← Change directory
  netlify deploy --prod                ← Upload files
  
In 3 min:
  ✅ DEPLOYED! Site is LIVE
  
Optional (add custom domain):
  Update DNS records                   ← 5 min setup
  Wait for propagation                 ← 5-30 min
  ✅ agentnest.io is LIVE
```

---

## 🎉 NEXT STEPS

1. ✅ Landing page live
2. ⏳ Deploy backend to AWS (30 min)
3. ⏳ Setup Stripe billing (1 day)
4. ⏳ Launch marketing (1 day)
5. 💰 Get first customers

---

## 📞 SUPPORT

**Netlify Docs:** https://docs.netlify.com
**Netlify Status:** https://www.netlifystatus.com
**GitHub Issues:** https://github.com/gosdrkht/agentnest/issues

---

**You're ready to go live! Choose your platform and deploy now.** 🚀
