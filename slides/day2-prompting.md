---
marp: true
theme: default
paginate: true
header: 'Agentic AI Training'
footer: 'Day 2 - Advanced Prompting'
style: |
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Fira+Code&display=swap');

  section {
    font-family: 'Inter', -apple-system, sans-serif;
    font-size: 20px;
    background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
    color: #1a202c;
    padding: 45px 60px;
    line-height: 1.5;
  }

  h1 {
    color: #1a365d;
    font-size: 1.9em;
    font-weight: 700;
    border-bottom: 3px solid #3182ce;
    padding-bottom: 0.2em;
    margin-bottom: 0.5em;
    margin-top: 0;
  }

  h2 {
    color: #2c5282;
    font-size: 1.3em;
    font-weight: 600;
    margin: 0.6em 0 0.4em 0;
  }

  h3 {
    color: #2d3748;
    font-size: 1.1em;
    font-weight: 600;
    margin: 0.5em 0 0.3em 0;
  }

  code {
    background-color: #edf2f7;
    color: #2d3748;
    padding: 0.1em 0.3em;
    border-radius: 3px;
    font-family: 'Fira Code', Monaco, monospace;
    font-size: 0.85em;
  }

  pre {
    background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%) !important;
    padding: 0.9em !important;
    border-radius: 8px !important;
    border: 2px solid #4a5568 !important;
    overflow-x: auto !important;
    max-height: 320px !important;
    font-size: 0.62em !important;
    line-height: 1.4 !important;
    margin: 0.6em 0 !important;
  }

  pre code {
    background: transparent !important;
    color: #e2e8f0 !important;
    border: none !important;
    padding: 0 !important;
    font-size: 1em !important;
  }

  ul, ol {
    line-height: 1.6;
    margin: 0.5em 0;
  }

  li {
    margin-bottom: 0.3em;
  }

  p {
    margin: 0.5em 0;
  }

  strong {
    color: #2c5282;
    font-weight: 700;
  }

  table {
    border-collapse: collapse;
    width: 100%;
    font-size: 0.75em;
    margin: 0.5em 0;
  }

  th {
    background: linear-gradient(135deg, #3182ce 0%, #2c5282 100%);
    color: white;
    padding: 0.5em;
    font-weight: 600;
  }

  td {
    padding: 0.4em;
    border-bottom: 1px solid #e2e8f0;
    background-color: white;
  }

  tr:nth-child(even) td {
    background-color: #f7fafc;
  }

  section.lead {
    text-align: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
  }

  section.lead h1 {
    color: white;
    border-bottom: none;
    font-size: 2.5em;
    margin-bottom: 0.3em;
  }

  section.lead h2 {
    color: #e6fffa;
    font-weight: 500;
    font-size: 1.4em;
  }

  blockquote {
    border-left: 3px solid #3182ce;
    padding: 0.6em 1em;
    background-color: #ebf8ff;
    margin: 0.5em 0;
    border-radius: 5px;
    font-style: italic;
    color: #2c5282;
    font-size: 0.9em;
  }
---

<!-- _class: lead -->
# Day 2: Advanced Prompting

## Agentic AI Training

---

# Learning Objectives

- Write effective prompts using RCFG framework
- Apply advanced patterns (CoT, Few-Shot, Tree-of-Thought)
- Design system prompts and personas
- Create specialized prompts for code tasks
- Build migration and refactoring prompts

---

# RCFG Framework

| Component | Purpose | Example |
|-----------|---------|---------|
| **R**ole | Set expertise | "Security-focused reviewer" |
| **C**ontext | Background | "Migrating Django 2.x to 4.x" |
| **F**ormat | Output type | "JSON with issues/suggestions" |
| **G**oal | The task | "Identify breaking changes" |

**Before:** `Review this code for issues.`

**After:**
```
Role: Senior Python dev, clean code expert
Context: Financial lib (precision critical)
Goal: Review naming, readability, bugs
Format: ## Issues, ## Suggestions sections
```
