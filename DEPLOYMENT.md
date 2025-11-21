# Deploying PressCoach

The easiest way to host this application for your colleagues is using **Streamlit Community Cloud**. It is free and connects directly to your GitHub repository.

## Prerequisites

1.  A [GitHub](https://github.com/) account.
2.  A [Streamlit Community Cloud](https://share.streamlit.io/) account (you can sign up with GitHub).

## Steps

### 1. Push Code to GitHub

Create a new repository on GitHub and push your code there.

```bash
git init
git add .
git commit -m "Initial commit"
# Follow GitHub instructions to add remote and push
# git remote add origin https://github.com/yourusername/presscoach.git
# git push -u origin main
```

### 2. Deploy on Streamlit Cloud

1.  Go to [share.streamlit.io](https://share.streamlit.io/).
2.  Click **"New app"**.
3.  Select your repository (`presscoach`), branch (`main`), and main file path (`app.py`).
4.  Click **"Deploy!"**.

### 3. Configure Secrets

Your app needs the `GEMINI_API_KEY` to work. **Do not commit your `.env` file to GitHub.** Instead:

1.  On your deployed app dashboard in Streamlit Cloud, click the **Settings** (three dots) -> **Settings**.
2.  Go to the **Secrets** tab.
3.  Paste your API key in TOML format:

```toml
GEMINI_API_KEY = "your_actual_api_key_here"
```

4.  Save. The app will restart automatically.

## Other Options

-   **Hugging Face Spaces**: Create a new Space, select Streamlit SDK, and upload your files. Add the API key in the Space's "Settings" -> "Variables and secrets".
-   **Render / Railway / Heroku**: These require a `Dockerfile` or specific build configurations, which is slightly more complex but offers more control.
