from flask import Flask, render_template

# Create a Flask application instance
app = Flask(__name__)

# Define a route for the home page ("/")
@app.route('/')
def hello_world():
    """Returns a simple greeting message."""
    return 'Hello, World!'

# Optional: define another route that uses an HTML template
# This requires a 'templates' folder in the same directory, 
# containing an 'index.html' file.
@app.route('/template')
def show_template():
    """Renders an HTML template."""
    # Example template content in templates/index.html: <h1>Hello, {{ name }}!</h1>
    return render_template('index.html', name='User')

# Run the application (only when executed directly)
if __name__ == '__main__':
    app.run(debug=True) # debug=True enables the debugger and auto-reloader
