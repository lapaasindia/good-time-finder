import re

with open('life_predictor_ui.html', 'r', encoding='utf-8') as f:
    content = f.read()

# CSS adjustments for "too zoomed" and readability
new_css_adjustments = """
  /* Adjusting Typography & Spacing for Better Readability (Un-zoomed) */
  body {
    font-size: 0.95rem;
    line-height: 1.6;
  }
  
  .display-lg { font-size: 2.5rem; }
  
  header {
    padding: 20px 32px;
  }
  
  .header-left h1 {
    font-size: clamp(2rem, 4vw, 2.5rem);
  }
  
  .wrap {
    padding: 32px 24px 80px;
    max-width: 1100px;
  }
  
  .form-card, .narrative-box, .mini-card, .dosha-card {
    padding: 24px 32px;
    margin-bottom: 24px;
  }
  
  .form-card h2 {
    font-size: 1.5rem;
    margin-bottom: 24px;
  }
  
  .form-grid {
    gap: 20px;
  }
  
  input, select {
    padding: 12px 16px;
    font-size: 0.95rem;
  }
  
  .range-row {
    gap: 20px;
    margin-top: 24px;
    padding-top: 24px;
  }
  
  .pill {
    padding: 8px 16px;
    font-size: 0.85rem;
  }
  
  .narrative-box h3, .sec-head {
    font-size: 1.25rem;
    margin-bottom: 20px;
  }
  
  .section-nav {
    margin: 40px 0 32px;
    gap: 12px;
  }
  
  .tab-link {
    padding: 8px 16px;
    font-size: 0.9rem;
  }
  
  .timeline-item {
    padding: 20px 24px;
    gap: 24px;
  }
  
  .tl-date {
    font-size: 1.1rem;
    min-width: 120px;
  }
  
  .tl-content h4 {
    font-size: 1.15rem;
    margin-bottom: 8px;
  }
  
  .tl-content p {
    font-size: 0.95rem;
  }
  
  .tl-score {
    font-size: 4rem;
    bottom: -10px;
    right: -10px;
  }
  
  .two-col, .gochara-grid {
    gap: 24px;
  }
  
  th, td {
    padding: 12px 16px;
    font-size: 0.85rem;
  }
  
  /* Fix broken UI lists and grids */
  ul, ol { margin-left: 20px; }
  li { margin-bottom: 4px; }
  
  .score-tag {
    display: inline-block;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    background: var(--surface-container-high);
  }
  .score-tag.good { color: var(--primary); background: rgba(151, 217, 79, 0.1); }
  .score-tag.bad { color: #e05e5e; background: rgba(224, 94, 94, 0.1); }
  
  .yoga-chip {
    display: inline-flex;
    align-items: center;
    background: var(--surface-container-highest);
    padding: 6px 12px;
    border-radius: 20px;
    margin: 4px;
    font-size: 0.85rem;
  }
  .yoga-chip .dot {
    width: 8px; height: 8px; border-radius: 50%; margin-right: 8px;
  }
"""

content = content.replace("  /* Tables */", new_css_adjustments + "\n  /* Tables */")

with open('life_predictor_ui.html', 'w', encoding='utf-8') as f:
    f.write(content)
