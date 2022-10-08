from application import app, greet

def test_quick():
  a = "jeff"
  greeting = greet(a)
  assert greeting == "Hi jeff"

from application import app
#test
def test_home_page():
    response = app.test_client().get('/')
    assert response.status_code == 200

def test_home_page():
    response = app.test_client().post('/')
    assert response.status_code == 405
