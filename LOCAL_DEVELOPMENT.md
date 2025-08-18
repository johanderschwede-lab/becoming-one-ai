# Local Development Guide for Becoming One™ AI

## Quick Start

1. **Verify Environment**
   ```bash
   python scripts/dev_env.py --verify
   ```
   This checks your Python version, virtual environment, dependencies, and configuration.

2. **Test Sacred Library**
   ```bash
   python scripts/dev_env.py --test-library
   ```
   Tests the Sacred Library integration with sample queries.

3. **Test Personality Analysis**
   ```bash
   python scripts/dev_env.py --test-analysis
   ```
   Tests the personality analysis system with a sample message.

4. **Run Bot Locally**
   ```bash
   python scripts/dev_env.py --bot
   ```
   Runs the bot locally for testing before deployment.

## Development Workflow

1. **Before Making Changes**
   - Run environment verification
   - Test the specific component you'll be modifying
   - Create a new branch for your changes

2. **During Development**
   - Use local bot testing to verify changes
   - Check logs in `logs/dev_*.log`
   - Run specific component tests as needed

3. **Before Deploying**
   - Run all tests
   - Verify environment again
   - Test bot locally
   - Review changes

## Debugging Tips

1. **Common Issues**
   - Missing environment variables
   - Database connection issues
   - API rate limits
   - Token validation errors

2. **Useful Commands**
   ```bash
   # Check all components
   python scripts/dev_env.py --verify

   # Test specific feature
   python scripts/dev_env.py --test-library
   python scripts/dev_env.py --test-analysis

   # Run bot locally
   python scripts/dev_env.py --bot
   ```

3. **Log Locations**
   - Development logs: `logs/dev_*.log`
   - Bot logs: `logs/bot_*.log`
   - Analysis logs: `logs/analysis_*.log`

## Best Practices

1. **Always Test Locally First**
   - Use `--verify` to check environment
   - Test specific components
   - Run bot locally
   - Review logs

2. **Debugging Process**
   - Check environment variables
   - Review recent logs
   - Test components in isolation
   - Verify database connections

3. **Code Changes**
   - Follow project style guide
   - Add appropriate logging
   - Update tests if needed
   - Document changes

## Railway Deployment

Only deploy to Railway after:
1. All local tests pass
2. Environment verification succeeds
3. Bot runs successfully locally
4. Changes are documented

## Getting Help

If you encounter issues:
1. Check the logs
2. Review common issues above
3. Test components individually
4. Document the exact error
5. Include relevant log snippets
