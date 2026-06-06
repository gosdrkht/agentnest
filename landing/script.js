// Email signup form
function handleEmailSignup(event) {
  event.preventDefault();
  const email = event.target.querySelector('input[type="email"]').value;
  
  // Send to backend
  fetch('https://api.agentnest.io/api/email/subscribe', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email })
  })
  .then(response => response.json())
  .then(data => {
    alert('✅ Thanks for subscribing! Check your email for early access.');
    closeEmailModal();
  })
  .catch(error => {
    alert('❌ Something went wrong. Please try again.');
  });
}

function closeEmailModal() {
  document.getElementById('emailModal').classList.remove('active');
}

// FAQ Toggle
function toggleFAQ(element) {
  const parent = element.parentElement;
  parent.classList.toggle('active');
}

// Pricing Toggle
function togglePricing(period) {
  // Update button states
  document.querySelectorAll('.toggle-btn').forEach(btn => btn.classList.remove('active'));
  event.target.classList.add('active');
  
  // Update pricing display
  const cards = document.querySelectorAll('.pricing-card');
  cards.forEach(card => {
    const price = card.querySelector('.price');
    if (period === 'annual') {
      const monthlyPrice = parseInt(price.textContent);
      const annualPrice = Math.round(monthlyPrice * 12 * 0.9); // 10% discount
      price.textContent = `$${annualPrice}`;
      price.querySelector('span').textContent = '/year';
    } else {
      price.innerHTML = `$${period === 'monthly' ? price.dataset.monthly || 'Custom' : '0'}<span>/month</span>`;
    }
  });
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      target.scrollIntoView({ behavior: 'smooth' });
    }
  });
});

// CTA tracking
document.querySelectorAll('[href*="app.agentnest.io"]').forEach(link => {
  link.addEventListener('click', function() {
    // Track CTA clicks
    if (typeof gtag !== 'undefined') {
      gtag('event', 'cta_click', {
        'cta_text': this.textContent,
        'cta_location': this.closest('section').className
      });
    }
  });
});

// Animate elements on scroll
const observerOptions = {
  threshold: 0.1,
  rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver(function(entries) {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.animation = 'slideUp 0.6s ease-out forwards';
      observer.unobserve(entry.target);
    }
  });
}, observerOptions);

document.querySelectorAll('.feature-card, .pricing-card, .testimonial-card').forEach(el => {
  el.style.opacity = '0';
  observer.observe(el);
});

// Mobile menu toggle
function toggleMobileMenu() {
  const navLinks = document.querySelector('.nav-links');
  if (navLinks) {
    navLinks.style.display = navLinks.style.display === 'flex' ? 'none' : 'flex';
  }
}

// Prevent showing email modal on page load (optional)
window.addEventListener('load', function() {
  // Show modal after 30 seconds or on exit intent
  setTimeout(showEmailModalOnExit, 30000);
});

function showEmailModalOnExit() {
  document.addEventListener('mouseleave', function() {
    if (!document.getElementById('emailModal').classList.contains('active')) {
      // Commented out to not be intrusive on first load
      // document.getElementById('emailModal').classList.add('active');
    }
  }, { once: true });
}

// Analytics
if (window.location.hostname !== 'localhost') {
  // Add Google Analytics
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
}
