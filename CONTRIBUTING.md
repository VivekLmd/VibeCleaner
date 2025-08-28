# Contributing to VibeCleaner

Thank you for your interest in improving VibeCleaner and the broader vibe coding ecosystem!

## The Mission

Make agentic AI workflows actually work for real-world problems. VibeCleaner is a test case for vibe coding - if we can't organize a Downloads folder reliably with AI, how can we trust it with more complex tasks?

## Current State

This project is experimental and has known limitations:
- AI agents fail on large folders (1000+ files)
- Context window limitations cause attention drift
- Inconsistent results with same prompts
- Heavy reliance on fallback rules

Your contributions can help solve these fundamental challenges.

## Priority Areas

### 1. Context Management (CRITICAL)
- Implement chunking strategies for large folders
- Create checkpoint/resume systems
- Design context preservation mechanisms
- Test with folders of varying sizes (100, 1000, 10000 files)

### 2. Attention Systems
- Prevent AI from "forgetting" initial instructions
- Implement task focus mechanisms
- Create attention validation checks
- Document attention drift patterns

### 3. Provider Improvements
- Better error handling for Claude/Codex
- Add support for new AI providers (GPT-4, Gemini, etc.)
- Create provider abstraction layer
- Document provider-specific quirks

### 4. Cross-Provider Consistency (NEW CHALLENGE)
Based on our experiments:
- Claude and Codex approach problems fundamentally differently
- Codex tends toward ML/academic solutions
- Claude prefers pragmatic/rule-based approaches
- Need strategies to harmonize different AI philosophies
- Research: Can we predict which provider suits which task?

### 4. Real-World Testing
- Test on actual messy Downloads folders
- Document failure cases with reproducible examples
- Create test datasets of various folder types
- Share performance metrics

## How to Contribute

### For Developers

1. **Fork & Clone**
   ```bash
   git clone https://github.com/yourusername/VibeCleaner.git
   cd VibeCleaner
   pip install -e .
   ```

2. **Test on Your Downloads**
   ```bash
   vibecleaner clean --dry-run
   vibecleaner ask "organize my pdfs" --dry-run
   ```

3. **Document Issues**
   - What failed?
   - How many files?
   - What was the AI response?
   - Include logs/screenshots

4. **Submit Improvements**
   - Create focused PRs
   - Include test cases
   - Document your approach
   - Share performance impacts

### For AI/ML Researchers

We especially need help with:
- Attention mechanism improvements
- Context window optimization
- Prompt engineering strategies
- Multi-pass processing algorithms

### For Users

- Report edge cases
- Share your Downloads folder statistics (file count, types, age)
- Suggest natural language commands that should work
- Test and report AI comprehension issues

## Development Guidelines

### Code Style
- Python 3.9+ compatibility
- Type hints where helpful
- Clear docstrings
- Handle errors gracefully

### Testing Philosophy
- Test on real messy folders, not clean test data
- Document failure modes
- Prefer safety over functionality
- Always implement --dry-run

### Commit Messages
```
feat: add checkpoint system for large folders
fix: prevent context loss after 500 files  
docs: document Claude timeout issues
test: add 1000-file folder test case
```

## Sharing Knowledge

### Blog Posts / Research
If you write about your experience with VibeCleaner or vibe coding:
- Share what didn't work (as important as successes)
- Include metrics and reproducible examples
- Share via an issue linking to your post (no external handles required)

### Academic Research
Using VibeCleaner for research on agentic workflows? We'd love to:
- Include your findings in the documentation
- Implement your improvements
- Cite your work

## Communication

### Issues
- Check existing issues first
- Include system info (OS, Python version, AI provider)
- Provide minimal reproducible examples
- Be specific about expected vs actual behavior

### Discussions
- Share your vibe coding experiences
- Propose architectural changes
- Discuss attention/context solutions
- Brainstorm new approaches

## The Bigger Picture

VibeCleaner is more than a Downloads organizer - it's a testing ground for making AI agents useful in daily life. Every improvement here advances the entire field of practical agentic AI.

Your contribution, whether it's fixing a bug or sharing why something failed, helps build the infrastructure for reliable vibe coding.

## Recognition

All contributors will be acknowledged in:
- README.md contributors section
- Release notes
- Academic papers (if applicable)

## Questions?

Open an issue with the "question" label. For private matters, use the email listed in SECURITY.md.

---

**Remember**: Documenting failures is as valuable as implementing features. We're building something new here, and every lesson matters.
