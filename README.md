<html>
<h2>RESTful API that is paired with the Photo-App</h2>
<div>See <a href="https://github.com/nburnet1/photo-app">Photo-app</a> for more front-end detail</div>
  <h3>How to install</h3>

  <h4>Virtual Environment</h4>
      <i>Create your virtual environment:</i>
      <div>
      <code>python3 -m venv env</code><br>
      <code>source env/bin/activate</code><br>
      <code>python -m pip install -r requirements.txt</code>
      </div>
  
  <h4>Database (PostgreSQL)</h4>
  <ul>
    <li>
      <i>Create the database:</i>
      <div>
      <code>CREATE DATABASE "photo-app";</code>
      </div>
    </li>
    <li>
      <i>Populate the database:</i>
      <div>
        <code>python3 populate.py</code>
      </div>
    </li>
  </ul>
  
  <h4>.env file</h4>
  <ul>
    <li><i>Create .env file</i></li>
    <li>
      <i>Add to .env file</i><br>
      <code>FLASK_APP=app.py</code><br>
      <code>DB_URL=postgresql://{user}:{password}@{host}/{database}</code>
    </li>
  </ul>

  <h4>Flask and Testing</h4>

  <ul>
    <li><code>flask run</code></li>
    <li>
      <code>cd tests</code><br>
      <code>python3 run_tests.py </code>
    </li>
  </ul>
</html>
