# Common Issues & Solutions

## Authentication Issues

### OpenAI API Key Invalid
**Error**: `Error code: 401 - {'error': {'message': 'Incorrect API key provided'`
**Cause**: API key expired, revoked, or incorrect
**Solution**: 
1. Check OpenAI dashboard for valid keys
2. Update Railway environment variables
3. Update local `.env` file
4. Test locally before deploying

### Telegram Bot Token Issues
**Error**: `telegram.error.InvalidToken`
**Cause**: Bot token expired or incorrect
**Solution**: 
1. Check with @BotFather on Telegram
2. Update Railway environment variables
3. Test locally with `python3 scripts/test_bot_offline.py`

## Database Issues

### Supabase Cloudflare Errors
**Error**: `Worker threw exception | Cloudflare`
**Cause**: Temporary Supabase service issues
**Solution**: 
1. Wait for Supabase to resolve
2. Check Supabase status page
3. Use offline fallback for testing
4. Implement retry logic

### Missing Database Tables
**Error**: `Could not find the table 'public.personality_profiles'`
**Cause**: Database schema not deployed
**Solution**: 
1. Run `python3 scripts/setup_database.py`
2. Verify tables exist in Supabase dashboard
3. Check service role key permissions

## Deployment Issues

### Railway Health Check Failures
**Error**: `Healthcheck failure`
**Cause**: App not responding on expected port
**Solution**: 
1. Ensure health server starts on port 8080
2. Check Railway logs for startup errors
3. Verify all environment variables set

### Import Errors on Railway
**Error**: `attempted relative import beyond top-level package`
**Cause**: Relative imports don't work in Railway
**Solution**: 
1. Convert to absolute imports: `from database.operations import db`
2. Add `sys.path.insert(0, 'src')` to launcher
3. Test locally first

## Async/Queue Issues

### Background Analysis Queue Errors
**Error**: `task_done() called too many times`
**Cause**: Improper async queue handling
**Solution**: 
1. Fix queue task lifecycle
2. Handle cancellation properly
3. Test async components locally

## Development Workflow

### Local Testing Best Practices
1. **Always test locally first**: `python3 scripts/dev_env.py --verify`
2. **Test components individually**: `python3 scripts/test_bot_offline.py`
3. **Check all connections**: Verify API keys, database, services
4. **Review logs**: Check `logs/` directory for detailed errors
5. **Fix locally, then deploy**: Never debug directly on Railway

### Debugging Process
1. Run environment verification
2. Test offline components
3. Check external service status
4. Review error logs
5. Fix issues locally
6. Test again
7. Deploy with confidence

## Prevention

### Environment Management
- Keep local `.env` in sync with Railway
- Test API keys regularly
- Monitor service status pages
- Use fallback mechanisms

### Code Quality
- Use absolute imports
- Handle async properly
- Add comprehensive error handling
- Test all components locally

### Deployment Safety
- Verify locally before deploying
- Use version control for all changes
- Monitor Railway logs after deployment
- Keep rollback procedures ready
