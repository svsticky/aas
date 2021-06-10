# This file provides a function that can return the dependencies for Aas given
# whether we're in development and a Python package set.
{ development }: ps: with ps; [
  flask
  flask-restful
  python-dotenv
  gunicorn
  requests
]
++ (
  if development 
  then [
    black
    pylint
  ] 
  else []
)
