#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
from datetime import datetime
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
        return f"""<Venue 
    id:{self.id}, 
    name:{self.name}, 
    city:{self.city}, 
    state:{self.state}, 
    address:{self.address}, 
    phone:{self.phone}, 
    genres:{self.genres}, 
    website:{self.website}, 
    image_link:{self.image_link}, 
    facebook_link:{self.facebook_link}, 
    seeking_talent:{self.seeking_talent}, 
    seeking_description:{self.seeking_description}
>"""


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
        return f"""<Artist
    id:{self.id},
    name:{self.name},
    city:{self.city},
    state:{self.state},
    phone:{self.phone},
    genres:{self.genres},
    website:{self.website},
    image_link:{self.image_link},
    facebook_link:{self.facebook_link},
    seeking_venue:{self.seeking_venue},
    seeking_description:{self.seeking_description}
>"""


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"""<Show
    id:{self.id},
    venue_id:{self.venue_id},
    artist_id:{self.artist_id},
    start_time:{self.start_time}
>"""
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  cities = [
    {
      "city": c[0], 
      "state": c[1], 
      "venues": [
        get_venue_dict(v)
        for v in Venue.query.filter(Venue.city==c[0], Venue.state==c[1]).all()
      ]
    } 
    for c in db.session.query(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  ]

  return render_template('pages/venues.html', areas=cities);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')

  venues = [
    get_venue_dict(v)
    for v in Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  ]

  response={
    "count": len(venues),
    "data": venues
  }

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

def get_venue_dict(v):
  return {
    "id": v.id, 
    "name": v.name,
    "num_upcoming_shows": len([s for s in v.shows if s.start_time > datetime.now()])
  }

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  v = Venue.query.get_or_404(venue_id)

  data={
    "id": v.id,
    "name": v.name,
    "address": v.address,
    "city": v.city,
    "state": v.state,
    "phone": v.phone,
    "website": v.website,
    "facebook_link": v.facebook_link,
    "seeking_talent": v.seeking_talent,
    "seeking_description": v.seeking_description,
    "image_link": v.image_link,
  }

  if v.genres != None:
    data["genres"] = [g.strip() for g in v.genres.split(",")]

  data["past_shows"] = [
    {
      "artist_id": s.artist_id,
      "artist_name": s.artist.name,
      "artist_image_link": s.artist.image_link,
      "start_time": s.start_time.isoformat()
    }
    for s in v.shows if s.start_time < datetime.now()
  ]
  data["past_shows_count"] = len(data["past_shows"])

  data["upcoming_shows"] = [
    {
      "artist_id": s.artist_id,
      "artist_name": s.artist.name,
      "artist_image_link": s.artist.image_link,
      "start_time": s.start_time.isoformat()
    }
    for s in v.shows if s.start_time > datetime.now()
  ]
  data["upcoming_shows_count"] = len(data["upcoming_shows"])

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)

  if not form.validate_on_submit():
    flash('Data submitted is not valid')
    return render_template('pages/home.html')

  try:
    venue = Venue(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      address = form.address.data,
      phone = form.name.data,
      genres = ",".join(form.genres.data),
      facebook_link = form.facebook_link.data
    )

    db.session.add(venue)
    db.session.commit()

    flash(f'Venue {form.name.data} was successfully listed!')
  
  except:
    flash(f'An error occurred. Venue {form.name.data} could not be listed.')
    db.session.rollback()

  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  return render_template('pages/artists.html', artists=Artist.query.all())

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term=request.form.get('search_term', '')

  artist = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()

  response={
    "count": len(artist),
    "data": [
      {
        "id": a.id,
        "name": a.name,
        "num_upcoming_shows": len([s for s in a.shows if s.start_time > datetime.now()]),
      }
      for a in artist
    ]
  }

  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  a = Artist.query.get_or_404(artist_id)
  data = {
    "id": a.id,
    "name": a.name,
    "city": a.city,
    "state": a.state,
    "phone": a.phone,
    "website": a.website,
    "seeking_venue": a.seeking_venue,
    "seeking_description": a.seeking_description,
    "image_link": a.image_link,
    "facebook_link": a.facebook_link
  }

  if a.genres != None:
    data['genres'] = [s.strip() for s in a.genres.split(",")]

  data["past_shows"] = [
    {
      "venue_id": s.venue_id,
      "venue_name": s.venue.name,
      "venue_image_link": s.venue.image_link,
      "start_time": s.start_time.isoformat()
    }
    for s in a.shows if s.start_time < datetime.now()
  ]
  data["past_shows_count"] = len(data["past_shows"])

  data["upcoming_shows"] = [
    {
      "venue_id": s.venue_id,
      "venue_name": s.venue.name,
      "venue_image_link": s.venue.image_link,
      "start_time": s.start_time.isoformat()
    }
    for s in a.shows if s.start_time > datetime.now()
  ]
  data["upcoming_shows_count"] = len(data["upcoming_shows"])

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get_or_404(artist_id)
  form = ArtistForm(obj=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form)

  if not form.validate_on_submit():
    flash(f'Data submitted is not valid')
    return redirect(url_for('show_artist', artist_id=artist_id))

  try:
    artist = Artist.query.get_or_404(artist_id)

    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.genres = ",".join(form.genres.data)
    artist.image_link = form.image_link.data
    artist.facebook_link = form.facebook_link.data

    db.session.commit()

    flash(f'Artist {form.name.data} was successfully updated!')

  except:
    flash(f'An error occurred. Artist {form.name.data} could not be updated.')
    db.session.rollback()

  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get_or_404(venue_id)
  form = VenueForm(obj=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form)

  if not form.validate_on_submit():
    flash('Data submitted is not valid')
    return redirect(url_for('show_venue', venue_id=venue_id))

  try:
    venue = Venue.query.get_or_404(venue_id)
    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    venue.genres = ",".join(form.genres.data)
    venue.image_link = form.image_link.data
    venue.facebook_link = form.facebook_link.data

    db.session.commit()

    flash(f'Venue {form.name.data} was successfully updated!')

  except:
    flash(f'An error occurred. Venue {form.name.data} could not be updated.')
    db.session.rollback()

  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)

  if not form.validate_on_submit():
    flash(f'Data submitted is not valid')
    return render_template('pages/home.html')

  try:
    artist = Artist(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      phone = form.phone.data,
      genres = ",".join(form.genres.data),
      image_link = form.image_link.data,
      facebook_link = form.facebook_link.data
    )
  
    db.session.add(artist)
    db.session.commit()

    flash(f'Artist {form.name.data} was successfully listed!')

  except:
    flash(f'An error occurred. Artist {form.name.data} could not be listed.')
    db.session.rollback()

  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
