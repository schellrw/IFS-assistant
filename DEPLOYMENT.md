# IFS Assistant Deployment Guide

This guide outlines the steps to deploy the IFS Assistant application to Digital Ocean using the App Platform, with Supabase for authentication and database.

## Prerequisites

- GitHub account with your IFS Assistant repository
- Digital Ocean account
- Supabase account

## Part 1: Supabase Setup

### 1. Create a Supabase Project

1. Log in to [Supabase](https://app.supabase.com/)
2. Click "New Project"
3. Enter project details:
   - Name: `ifs-assistant` (or your preferred name)
   - Database Password: (create a secure password)
   - Region: (choose closest to your users)
4. Click "Create new project"

### 2. Set Up Database Schema

1. Once your project is created, go to the SQL Editor
2. Run the schema setup script:
   ```
   FLASK_ENV=staging python setup_supabase_schema.py
   ```
3. Copy the generated SQL statements from the output
4. Paste them into the Supabase SQL Editor and run them

### 3. Enable Row Level Security

1. Run the RLS setup script:
   ```
   FLASK_ENV=staging python setup_supabase_rls.py
   ```
2. Copy the generated SQL statements from the output
3. Paste them into the Supabase SQL Editor and run them

### 4. Configure Authentication

1. Go to Authentication > Settings
2. Under Email Auth, make sure Email Confirmations are enabled
3. Set up your Site URL (this will be your Digital Ocean app URL once deployed)
4. Add any additional providers (Google, GitHub, etc.) if desired

### 5. Get Supabase Credentials

1. Go to Project Settings > API
2. Note down the following:
   - Project URL (e.g., `https://abcdefghijklm.supabase.co`)
   - `anon` public API key

## Part 2: Digital Ocean Setup

### 1. Prepare Your Repository

1. Make sure your code is in a GitHub repository
2. Update the `digitalocean.yaml` file with your GitHub username in the `repo` field

### 2. Create a New App on Digital Ocean

1. Log in to [Digital Ocean](https://cloud.digitalocean.com/)
2. Go to Apps > Create App
3. Select GitHub as the source
4. Authorize Digital Ocean to access your GitHub account
5. Select your IFS Assistant repository
6. Select the branch to deploy (usually `main`)
7. Click "Next"

### 3. Configure the App

1. Select "Use App Spec from Source Code"
2. This will use the `digitalocean.yaml` file from your repository
3. Click "Next"

### 4. Add Environment Variables

The required environment variables are already defined in the `digitalocean.yaml` file, but you'll need to set the values for the secrets:

1. Set `JWT_SECRET_KEY` and `SECRET_KEY` to secure random strings
   - You can generate these with: `python -c "import secrets; print(secrets.token_hex(32))"`
2. Set `SUPABASE_URL` to your Supabase Project URL
3. Set `SUPABASE_KEY` to your Supabase `anon` public API key
4. Add any other environment-specific variables

### 5. Configure Resources

1. Select the plan that suits your needs
2. For development and testing, the Basic plan should be sufficient
3. Click "Next"

### 6. Review and Launch

1. Review your app configuration
2. Click "Create Resources"
3. Wait for the deployment to complete

## Part 3: Post-Deployment Setup

### 1. Update Supabase Configuration

1. Once your app is deployed, note the URL
2. Go back to Supabase > Authentication > Settings
3. Update the Site URL to your Digital Ocean app URL
4. Add your app URL to the allowed CORS origins

### 2. Testing the Deployment

1. Visit your app URL
2. Try registering a new account
3. Test the login functionality
4. Test creating and managing parts, conversations, etc.

### 3. Monitoring and Maintenance

1. Set up monitoring in Digital Ocean (Metrics, Logs)
2. Monitor database usage in Supabase
3. Regularly backup your data from Supabase

## Troubleshooting

### Common Issues

1. **CORS Errors**: Make sure the `CORS_ORIGINS` environment variable in the Digital Ocean app includes your frontend URL

2. **Authentication Issues**: Check that the Supabase URL and key are correctly set

3. **Database Connection Problems**: Verify that the Supabase database is accessible from your Digital Ocean app

4. **Build Failures**: Check the build logs in Digital Ocean for specific errors

### Getting Help

If you encounter issues, check:
- Digital Ocean app logs
- Supabase database logs
- Application error messages

## Scaling Considerations

### Digital Ocean

- Upgrade your app resources (CPU, memory) as needed
- Add multiple instances for high availability

### Supabase

- Monitor database size and performance
- Upgrade to a larger plan if needed
- Set up database optimization (indexes, caching)

## Security Best Practices

1. Regularly rotate your JWT and secret keys
2. Keep Supabase API keys secure
3. Implement rate limiting for API endpoints
4. Set up alerts for unusual activity
5. Keep all dependencies updated

---

## Next Steps

After successful deployment, consider:

1. Setting up a CI/CD pipeline for automated testing and deployment
2. Adding monitoring and alerting
3. Implementing user feedback mechanisms
4. Planning for regular updates and maintenance 