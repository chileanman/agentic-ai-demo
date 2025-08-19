# Streamlit Cloud Deployment Guide for Agentic AI Demo

This guide provides step-by-step instructions for deploying your Agentic AI Demo application to Streamlit Cloud.

## Prerequisites
- GitHub account (already set up with repository: https://github.com/chileanman/agentic-ai-demo)
- Streamlit Cloud account (sign up at https://streamlit.io/cloud if you don't have one)

## Deployment Steps

### 1. Log in to Streamlit Cloud
- Visit https://streamlit.io/cloud
- Sign in with your credentials or create a new account

### 2. Create a New App
- Click on the "New app" button in the dashboard
- You'll be prompted to connect your GitHub account if you haven't already

### 3. Connect to Your GitHub Repository
- Select your repository: `chileanman/agentic-ai-demo`
- For the main file path, enter: `app.py`
- For the branch, select: `main`

### 4. Configure Custom URL
- In the app settings, look for "Custom subdomain" or "App URL" option
- Enter: `agentic-file-process`
- This will make your app available at: https://agentic-file-process.streamlit.app

### 5. Advanced Settings
- Set Python version to 3.9 (to match your local environment)
- Streamlit will automatically detect and install packages from your requirements.txt file

### 6. Deploy
- Click "Deploy" or "Create app" button
- Wait for the deployment process to complete (this may take a few minutes)

## Troubleshooting

### Common Issues:
1. **Custom URL already taken**: If "agentic-file-process" is already taken, try an alternative like "agentic-ai-file-process"
2. **Deployment failures**: Check the logs in Streamlit Cloud for specific error messages
3. **Package installation issues**: Ensure all dependencies in requirements.txt are compatible with Python 3.9

### Checking Deployment Status:
- After deployment starts, Streamlit Cloud provides a progress indicator
- You can view build logs by clicking on your app in the dashboard

## Alternative Deployment Options

### Option 1: Local Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### Option 2: Docker Deployment
Create a Dockerfile in your project root:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
```

Build and run:
```bash
docker build -t agentic-ai-demo .
docker run -p 8501:8501 agentic-ai-demo
```

## Post-Deployment

After successful deployment, your app will be accessible at:
https://agentic-file-process.streamlit.app

You can share this URL with others to showcase your Agentic AI Demo application.
