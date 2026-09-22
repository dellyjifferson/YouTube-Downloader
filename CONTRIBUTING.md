# Contributing to YouTube Downloader

Thank you for your interest in contributing to the YouTube Downloader project! We welcome contributions from everyone. This document provides guidelines and instructions for contributing.

## License

This project is licensed under the **GNU General Public License v3.0**. By contributing to this project, you agree that your contributions will be licensed under the same GPLv3.0 license. For more details, see the [LICENSE](LICENSE) file.

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please be respectful, professional, and considerate in all interactions.

## How to Contribute

### Reporting Bugs

Found a bug? We'd appreciate a report! Please include:

1. A clear, descriptive title
2. Steps to reproduce the issue
3. Expected behavior vs. actual behavior
4. Your environment (OS, Python version, etc.)
5. Screenshots or error messages if applicable

### Suggesting Enhancements

Have an idea for improvement? We'd love to hear it! Please provide:

1. A clear description of the feature or enhancement
2. Why this would be useful
3. Possible implementation approach (if you have one)

### Submitting Changes

#### Prerequisites

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/youtube_downloader.git
   cd youtube_downloader
   ```

3. **Create a virtual environment** and install dependencies:
   ```bash
   python -m venv .env
   source .env/bin/activate  # On Windows: .\.env\Scripts\activate
   pip install yt-dlp
   ```

#### Development Workflow

1. **Create a new branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```
   or for bug fixes:
   ```bash
   git checkout -b fix/bug-description
   ```

2. **Make your changes** following the guidelines below

3. **Test your changes**:
   - Run the application: `python "YouTube downloader.py"`
   - Test the specific functionality you modified
   - Verify no existing features are broken

4. **Commit your changes** with clear, descriptive messages:
   ```bash
   git add .
   git commit -m "Brief description of changes"
   ```
   
   Use the imperative mood ("Add feature" not "Added feature")

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Submit a Pull Request** on GitHub with:
   - A clear title and description of your changes
   - Reference to any related issues
   - Steps to test the changes (if applicable)

## Development Guidelines

### Code Style

- Follow PEP 8 conventions for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions focused and reasonably sized

### Commit Messages

- Use clear, descriptive commit messages
- Start with an imperative verb (Add, Fix, Update, Remove, etc.)
- Keep the first line under 72 characters
- Add more details in the message body if needed

Example:
```
Add audio quality selection option

Users can now choose from multiple audio bitrates when downloading
as MP3. This addresses feature request #123.
```

### Testing

- Test your changes thoroughly before submitting
- Verify downloads work for both single videos and playlists
- Test with different URL formats
- Check that the GUI remains responsive during downloads

### Documentation

- Update the [README.md](README.md) if you add new features
- Add docstrings to new functions
- Update this CONTRIBUTING.md if you add new processes

## Types of Contributions

### Bug Fixes
- Fix crashes or errors
- Improve error handling
- Fix UI/UX issues

### Features
- New download options or formats
- UI improvements
- Better error messages
- Performance enhancements

### Documentation
- Improve README or guides
- Add code comments
- Fix typos or unclear instructions

### Testing & Quality
- Identify edge cases
- Test on different platforms/Python versions
- Suggest optimizations

## Pull Request Process

1. **Update dependencies** if needed (update in pip install commands in docs)
2. **Add tests** for new functionality (if applicable)
3. **Update documentation** for user-facing changes
4. **Keep commits clean** - squash/rebase if needed
5. **Be responsive** to review feedback
6. **Follow the PR template** when submitting

## Questions?

- Check existing issues and discussions first
- Open a new issue with your question
- Be specific about what you're trying to do

## Recognition

Contributors will be recognized in the project. Thank you for helping make this project better!

## Getting Help

If you're stuck or have questions about the contribution process:

1. Check the [README.md](README.md) for project information
2. Review existing issues and pull requests
3. Open a new issue with your question
4. Reach out to the project maintainer

## Additional Resources

- [GitHub Flow Guide](https://guides.github.com/introduction/flow/)
- [How to Write Good Commit Messages](https://chris.beams.io/posts/git-commit/)
- [PEP 8 Style Guide](https://pep8.org/)
- [GNU GPLv3 License](https://www.gnu.org/licenses/gpl-3.0.html)

---

Thank you for contributing! Every improvement, no matter how small, helps make this project better for everyone. 🎉
