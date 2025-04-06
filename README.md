# Restaurant App - System Operations

## PythonAnywhere Deployment

### Setting up the Restart Server Feature

To enable the "Restart Server" functionality on PythonAnywhere, you need to set up the API credentials:

1. Log in to your PythonAnywhere account.
2. Go to Account settings and create an API token.
3. Add the following environment variables to your PythonAnywhere web app:
   - `PYTHONANYWHERE_USERNAME`: Your PythonAnywhere username
   - `PYTHONANYWHERE_API_TOKEN`: Your API token created in step 2

### Setting Environment Variables in PythonAnywhere

1. Go to the Web tab in your PythonAnywhere dashboard.
2. Scroll down to the "Environment variables" section.
3. Add the two environment variables mentioned above.
4. Click the "Save" button.
5. Reload your web app for the changes to take effect.

Once these environment variables are set, the "Restart Server" button in the System Operations page will be able to automatically reload your web application using the PythonAnywhere API.

## Requirements

This project requires the following Python packages:
- Django
- requests (for the PythonAnywhere API integration)
- Other dependencies listed in requirements.txt

Run `pip install -r requirements.txt` to install all dependencies. 