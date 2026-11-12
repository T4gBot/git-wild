from datetime import datetime
from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///observations.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Observation(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  animal = db.Column(db.String(100), nullable=False)
  stream = db.Column(db.String(100), nullable=False)
  timestamp = db.Column(db.DateTime, default=datetime.utcnow)


with app.app_context():
  db.create_all()


@app.route('/', methods=['GET', 'POST'])
def index():
  if request.method == 'POST':
    animal = request.form.get('animal')
    stream = request.form.get('stream')
    if animal and stream:
      new_obs = Observation(animal=animal, stream=stream)
      db.session.add(new_obs)
      db.session.commit()
    return redirect(url_for('index'))

  observations = Observation.query.order_by(Observation.timestamp.desc()).all()
  return render_template('index.html', observations=observations)


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)