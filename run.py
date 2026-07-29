import os
from app import create_app

# Instantiate the application with the target environment config
app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    # Run the development server
    app.run(host='0.0.0.0', port=5000)
