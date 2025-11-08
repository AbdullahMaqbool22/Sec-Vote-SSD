# Contributing to Sec-Vote

Thank you for your interest in contributing to Sec-Vote!

## How to Contribute

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest tests/`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Development Setup

1. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Sec-Vote-SSD.git
   cd Sec-Vote-SSD
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy environment template:
   ```bash
   cp .env.example .env
   ```

4. Start services:
   ```bash
   docker-compose up --build
   ```

## Code Style

- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to functions
- Keep functions small and focused
- Write tests for new features

## Testing

- Write unit tests for new features
- Ensure all tests pass before submitting PR
- Aim for high code coverage

## Pull Request Guidelines

- Include a clear description of changes
- Reference any related issues
- Update documentation if needed
- Ensure tests pass
- Keep PRs focused on a single feature/fix

## Security

If you discover a security vulnerability, please email the maintainers directly rather than opening a public issue.

## Questions?

Feel free to open an issue for any questions or discussions.
