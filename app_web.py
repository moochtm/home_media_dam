from flask import Flask, render_template
import os
import settings
import urlparse

my_path, _ = os.path.split(os.path.realpath(__file__))
static_path = os.path.join(my_path, 'web/static')
templates_path = os.path.join(my_path, 'web/templates')
print static_path

class CustomFlask(Flask):
  jinja_options = Flask.jinja_options.copy()
  jinja_options.update(dict(
    block_start_string='(%',
    block_end_string='%)',
    variable_start_string='((',
    variable_end_string='))',
    comment_start_string='(#',
    comment_end_string='#)',
  ))


app = CustomFlask(__name__, static_folder=static_path, template_folder=templates_path)

scheme = 'http'
netloc = '%s:%s' % (settings.API_FLASK_SERVER_HOST, settings.API_FLASK_SERVER_PORT)
path = settings.API_INITIAL_RESOURCE
query = settings.API_INITIAL_QUERY
api_endpoint_url = urlparse.urlunsplit((scheme, netloc, path, query, ''))

print api_endpoint_url

@app.route('/')
def root():
    return render_template('index.html', jinja_var_api_endpoint=api_endpoint_url)

if __name__ == "__main__":
    app.run(host=settings.API_FLASK_SERVER_HOST, port=6502)