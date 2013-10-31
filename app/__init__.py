from flask import Flask
import os

# sets the root-directory of the application to be the parent of the actual root. This is because strangely this application's root is in the app folder, not the actual root. Workaround, should be fixed properly.
root_dir = os.path.dirname(os.path.abspath(os.path.join(__file__, os.pardir)))

app = Flask(__name__)
app.config.from_object('config_default')
app.config.from_pyfile(os.path.join(root_dir, 'config_instance.py'))
from app import views

