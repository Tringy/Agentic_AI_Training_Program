# Training Slides - Agentic AI Program

Support slides for the 5-day Agentic AI Training Program.

## 📁 Contents

| File | Day | Topic | Slides |
|------|-----|-------|--------|
| `day1-foundations.md` | Day 1 | GenAI Foundations & Vibe Coding | ~30 |
| `day2-prompting.md` | Day 2 | Advanced Prompting + **Multimodal** | ~56 (+16) |
| `day3-agents.md` | Day 3 | Agent Architectures + **Context/Memory/Structured** | ~66 (+26) |
| `day4-rag-eval.md` | Day 4 | RAG & Evaluation + **Testing** | ~56 (+16) |
| `day5-production.md` | Day 5 | Production + **Cost Opt/Integration** | ~61 (+26) |

**Total: ~269 slides** (+84 new slides)

---

## 🎨 Format: Marp

These slides are written in [Marp](https://marp.app/) (Markdown Presentation Ecosystem), which allows:

- ✅ Writing slides in pure Markdown
- ✅ Version control friendly
- ✅ Syntax highlighting for code
- ✅ Export to HTML, PDF, PowerPoint

---

## 🚀 Quick Start

### Option 1: VS Code (Recommended)

1. **Install Marp extension:**
   - Open VS Code
   - Install "Marp for VS Code" extension
   - Open any `.md` file in `slides/`
   - Click "Open Preview to the Side" icon

2. **Present:**
   - Press `Ctrl/Cmd + Shift + P`
   - Type "Marp: Toggle Marp feature"
   - Use arrow keys to navigate slides

### Option 2: Marp CLI

```bash
# Install Marp CLI globally
npm install -g @marp-team/marp-cli

# Preview slides in browser
marp -s day1-foundations.md

# Navigate to: http://localhost:8080
```

---

## 📤 Exporting Slides

### Export to HTML

```bash
# Single file
marp day1-foundations.md -o day1-foundations.html

# All slides
marp *.md
```

**HTML slides are:**
- Portable (single file with embedded assets)
- Presentable in any browser
- Support speaker notes

### Export to PDF

```bash
# Install Chromium (required for PDF export)
npm install -g puppeteer

# Export to PDF
marp day1-foundations.md --pdf

# Or with custom size
marp day1-foundations.md --pdf --allow-local-files
```

### Export to PowerPoint (PPTX)

```bash
# Export to PPTX
marp day1-foundations.md --pptx

# All slides
for file in day*.md; do
  marp "$file" --pptx
done
```

---

## 🎯 Presenting Tips

### Navigation
- **Arrow keys**: Next/previous slide
- **Home/End**: First/last slide
- **Number + Enter**: Jump to slide number

### Presenter Mode
```bash
# Export with presenter notes
marp day1-foundations.md -o output.html --html

# Open in browser and press 'P' for presenter view
```

### Split View
Most slides are designed for 16:9 aspect ratio. To change:

```markdown
---
marp: true
size: 4:3  # or 16:9 (default)
---
```

---

## 📝 Slide Structure

Each slide deck follows this pattern:

```markdown
---
marp: true
theme: default
paginate: true
header: 'Agentic AI Training'
footer: 'Day X - Topic'
---

<!-- _class: lead -->
# Title Slide

---

# Regular Slide

Content here

---

# Code Slide

```python
# Code with syntax highlighting
```

---
```

---

## 🎨 Customization

### Themes

To change theme, edit the frontmatter:

```markdown
---
theme: default  # or gaia, uncover
---
```

Available themes:
- `default` - Clean, professional
- `gaia` - Colorful, modern
- `uncover` - Minimalist

### Custom Styles

Each slide deck includes custom CSS in the frontmatter:

```markdown
---
style: |
  section {
    background-color: #fff;
    font-family: 'Helvetica Neue', sans-serif;
  }
  code {
    background-color: #1e1e1e;
  }
---
```

---

## 📊 Slide Types Used

### 1. Title Slide
```markdown
<!-- _class: lead -->
# Day 1: Title
## Subtitle
```

### 2. Content Slide
```markdown
# Heading
- Bullet points
- More content
```

### 3. Code Slide
```markdown
# Code Example
```python
def hello():
    return "world"
```
```

### 4. Comparison Table
```markdown
| Feature | Option A | Option B |
|---------|----------|----------|
| Speed   | Fast     | Slow     |
```

### 5. Diagram Slide
```markdown
# Architecture
```
┌──────┐    ┌──────┐
│  A   │───▶│  B   │
└──────┘    └──────┘
```
```

---

## 🔧 Troubleshooting

### Slides not rendering
- Ensure Marp extension is installed
- Check for syntax errors in frontmatter
- Verify `---` separators between slides

### Code highlighting not working
- Ensure language is specified: \`\`\`python
- Check for proper closing \`\`\`

### PDF export fails
```bash
# Install chromium dependencies
npm install -g puppeteer
export PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=false
```

### PowerPoint export issues
```bash
# Ensure latest Marp CLI
npm update -g @marp-team/marp-cli

# Try with --allow-local-files flag
marp slides.md --pptx --allow-local-files
```

---

## 📚 Additional Resources

### Marp Documentation
- Official docs: https://marpit.marp.app/
- Marp CLI: https://github.com/marp-team/marp-cli
- VS Code extension: https://marketplace.visualstudio.com/items?itemName=marp-team.marp-vscode

### Markdown Guide
- Basic syntax: https://www.markdownguide.org/basic-syntax/
- Extended syntax: https://www.markdownguide.org/extended-syntax/

### Presentation Tips
- Keep slides concise (max 5-7 bullets)
- Use visuals when possible
- Code examples should be short and focused
- Practice timing (aim for 1-2 minutes per slide)

---

## 🎓 Usage in Training

### For Instructors

**Preparation:**
1. Review slides before each day
2. Customize examples for your audience
3. Prepare additional demos if needed
4. Test all code examples

**During Training:**
1. Use slides as visual support, not script
2. Pause for questions at "---" breaks
3. Live code instead of showing code slides when possible
4. Reference corresponding day materials (DAYx-*.md)

**After Each Day:**
1. Export slides to PDF for students
2. Share HTML version for interactive review
3. Collect feedback for improvements

### For Students

**During Training:**
1. Focus on instructor, not slides
2. Take notes on key concepts
3. Ask questions when confused
4. Follow along with labs

**After Training:**
1. Review slides for concepts
2. Reference code examples
3. Use as quick reference guide
4. Share with colleagues

---

## 🔄 Updating Slides

To update content:

1. Edit the `.md` file directly
2. Changes appear immediately in preview
3. Re-export to HTML/PDF/PPTX as needed
4. Commit changes to version control

```bash
# Example workflow
vim day1-foundations.md  # Make changes
marp day1-foundations.md --pdf  # Re-export
git add day1-foundations.md
git commit -m "Update Day 1 slides: Added example for X"
```

---

## 📋 Checklist for Instructors

Before Day 1:
- [ ] Test all slides render correctly
- [ ] Verify code examples work
- [ ] Export to PDF for distribution
- [ ] Set up presentation environment

For Each Day:
- [ ] Review slides 1 hour before
- [ ] Test live demos
- [ ] Prepare Q&A talking points
- [ ] Have backup examples ready

After Training:
- [ ] Collect slide feedback
- [ ] Note areas for improvement
- [ ] Update slides based on questions
- [ ] Share final versions with students

---

## 🤝 Contributing

Found issues or have improvements?

1. Edit the markdown files directly
2. Test changes with Marp preview
3. Submit improvements

**Common improvements:**
- Fix typos or unclear explanations
- Add more code examples
- Improve diagrams
- Add speaker notes

---

## 📄 License

These slides are part of the Agentic AI Training Program and follow the same license as the main repository.

---

## 💡 Tips for Creating New Slides

### Keep It Visual
```markdown
# ❌ Don't: Wall of text
This is a lot of text that explains everything in paragraph form...

# ✅ Do: Bullet points + visuals
Key Points:
- Point 1
- Point 2
- Point 3

[Diagram or code example]
```

### Use Progressive Disclosure
Split complex topics across multiple slides rather than cramming everything into one.

### Code Should Be Concise
```python
# ❌ Don't show entire file
[100 lines of code]

# ✅ Show key snippet
def key_function():
    """Focus on the important part."""
    return important_logic()
```

### Include Takeaways
End each section with:
```markdown
# Key Takeaways

1. Main point 1
2. Main point 2
3. Main point 3
```

---

**Happy Presenting! 🎉**
