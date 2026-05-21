# Email Notifications & User Engagement

## 📧 Email Events Configured

### User Events
- ✅ Welcome email (on signup)
- ✅ Password reset
- ✅ Account confirmation
- ✅ Profile updates

### Agent Events
- ✅ Agent deployed
- ✅ Agent crashed/restarted
- ✅ High resource usage alerts
- ✅ Agent deleted

### Billing Events
- ✅ Low balance warning (when < $10)
- ✅ Payment successful
- ✅ Payment failed (retry scheduled)
- ✅ Monthly invoice
- ✅ Usage alert (when > $50/month)

### Engagement Emails
- ✅ Tips & best practices (weekly)
- ✅ New feature announcements
- ✅ Security updates
- ✅ Community highlights

---

## 🔧 Setup Email Service

### Using Gmail (Development)

```bash
# 1. Create Gmail account
# 2. Enable 2FA
# 3. Create App Password:
#    - Gmail → Settings → Security
#    - App Passwords → Generate for "Mail" on "Other (custom name)"

# 4. Update .env
cat >> backend/.env << EOF
EMAIL_SERVICE=gmail
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_FROM=noreply@agentnest.io
EOF
```

### Using SendGrid (Production)

```bash
# 1. Create SendGrid account (free tier: 100 emails/day)
# 2. Get API key from https://app.sendgrid.com/settings/api_keys
# 3. Verify sender email

# 4. Update .env
cat >> backend/.env << EOF
EMAIL_SERVICE=sendgrid
SENDGRID_API_KEY=SG.xxxxx
EMAIL_FROM=noreply@agentnest.io
EOF

# 5. Update email_service.py:
import sendgrid
from sendgrid.helpers.mail import Mail

sg = sendgrid.SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
```

### Using AWS SES (Best for Scale)

```bash
# 1. Setup AWS SES:
#    - AWS Console → SES → Verified identities
#    - Add sender email (verify)
#    - Request production access (2 hour review)

# 2. Create IAM user with SES permissions
aws iam create-user --user-name agentnest-ses

aws iam attach-user-policy \
  --user-name agentnest-ses \
  --policy-arn arn:aws:iam::aws:policy/AmazonSESFullAccess

# 3. Create access key
aws iam create-access-key --user-name agentnest-ses

# 4. Update .env
cat >> backend/.env << EOF
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_SES_REGION=us-east-1
EMAIL_FROM=noreply@agentnest.io
EOF

# 5. Update email_service.py to use boto3/SES
```

---

## 🔔 Push Notifications (Optional)

### Browser Push Notifications

```typescript
// frontend/src/services/notifications.ts

export const requestNotificationPermission = async () => {
  if (!('Notification' in window)) {
    console.log('This browser does not support notifications');
    return;
  }

  if (Notification.permission === 'granted') {
    return;
  }

  if (Notification.permission !== 'denied') {
    await Notification.requestPermission();
  }
};

export const sendNotification = (title: string, options?: NotificationOptions) => {
  if (Notification.permission === 'granted') {
    new Notification(title, options);
  }
};
```

### In-App Toast Notifications

```typescript
// frontend/src/components/Toast.tsx

interface Toast {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
  duration?: number;
}

export const useToast = () => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = (message: string, type: Toast['type'] = 'info', duration = 5000) => {
    const id = Math.random().toString(36);
    setToasts(prev => [...prev, { id, message, type, duration }]);

    if (duration) {
      setTimeout(() => removeToast(id), duration);
    }
  };

  const removeToast = (id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  return { toasts, addToast, removeToast };
};
```

---

## 📱 Slack Notifications (Optional)

```python
# backend/app/services/slack_service.py

import requests
import os

class SlackService:
    def __init__(self):
        self.webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    
    def send_notification(self, message: str, severity: str = 'info'):
        if not self.webhook_url:
            return
        
        colors = {
            'info': '#0066ff',
            'warning': '#ff9900',
            'danger': '#ff4444',
            'success': '#00cc00',
        }
        
        payload = {
            'attachments': [{
                'color': colors.get(severity, '#0066ff'),
                'title': f'🤖 AgentNest {severity.upper()}',
                'text': message,
                'ts': int(time.time())
            }]
        }
        
        requests.post(self.webhook_url, json=payload)

# Usage:
slack = SlackService()
slack.send_notification('Agent deployed successfully', 'success')
```

---

## 📊 Email Analytics

Track email engagement:

```python
# backend/app/models.py - Add to User model

class EmailLog(Base):
    __tablename__ = "email_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    email_type = Column(String(50))  # welcome, agent_deployed, etc.
    sent_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    opened_at = Column(TIMESTAMP(timezone=True), nullable=True)
    clicked_at = Column(TIMESTAMP(timezone=True), nullable=True)
    bounce_status = Column(String(50))  # sent, bounce, complaint
```

---

## 🎯 Engagement Metrics

Track user engagement:

```python
# Goals to measure:
- Email open rate (target: > 25%)
- Click-through rate (target: > 5%)
- Unsubscribe rate (target: < 1%)
- Agent deployment rate (daily active users)
- Trial-to-paid conversion (target: > 10%)
- Customer lifetime value (target: > $500)
```

---

## ✉️ Email Templates by Use Case

### 1. Onboarding Sequence (3 emails, days 0-3)
- Day 0: Welcome + quick start guide
- Day 1: First agent deployment tips
- Day 3: Success story from another user

### 2. Agent Lifecycle
- Deployment successful
- High resource warning (threshold: 80% CPU or 90% memory)
- Agent crashed alert
- Agent updated

### 3. Billing Lifecycle
- Low balance warning (threshold: $10)
- Payment successful
- Payment failed (retry in 3 days)
- Monthly invoice summary

### 4. Re-engagement
- "We miss you" (30 days inactive)
- New feature announcement
- Success story from similar user
- Special offer/discount

---

## 🔐 Email Best Practices

✅ **Do:**
- Use transactional email service (SendGrid, AWS SES)
- Include unsubscribe link in every email
- Use clear, action-oriented subject lines
- Include user name personalization
- Send from recognizable sender address
- A/B test subject lines
- Track opens and clicks

❌ **Don't:**
- Send too frequently (max 2-3 per week)
- Use all caps or excessive punctuation
- Have broken links
- Send at odd hours (9-5 business hours best)
- Forget mobile optimization
- Include too much content

---

## 📈 Expected Results

With proper email engagement:
- **+20-30%** signup completion rate
- **+15-25%** first agent deployment rate
- **+5-10%** trial-to-paid conversion
- **+10-15%** customer retention
- **+$50-100** average customer lifetime value

