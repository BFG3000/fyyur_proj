#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database #//Done

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
      return f'<Show {self.id}>'

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    #try this 
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    website = db.Column(db.String(120))
    #if true it should diplay the talent message
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    #relation with the show 
    #@ahmed
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    # this should be an array or a relation or maybe enum?
    #genres = db.Column(db.String(120)) 
    # i found this on sqlAlchemy docs
    #Column("genres", ARRAY(Integer))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

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

  # TODO: replace with real venues data.
  tempData=[]
  all_venues = Venue.query.order_by(Venue.state, Venue.city).all()
  states = db.session.query(Venue.city, Venue.state).distinct()
  #@ahmed
  #
  for addr in states:
    venues=[]
    for venue in all_venues:
      if venue.city == addr.city and venue.state == addr.state:
        venues.append({"id": venue.id, "name":venue.name })
    tempData.append({ "city":addr.city, "state":addr.state, "venues":venues })
  #print(tempData)

  #todo num_upcoming_shows
  data=[{
    "city": "San Francisco",
    "state": "CA",
    "venues": [{
      "id": 1,
      "name": "The Musical Hop",
      "num_upcoming_shows": 0,
    }, {
      "id": 3,
      "name": "Park Square Live Music & Coffee",
      "num_upcoming_shows": 1,
    }]
  }, {
    "city": "New York",
    "state": "NY",
    "venues": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }]
  return render_template('pages/venues.html', areas=tempData);
#@ahmed
@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  results = Venue.query.filter(Venue.name.ilike('%{}%'.format(request.form['search_term']))).all()
  response={
    "count": len(results),
    "data": []
  }
  for venue in results:
    response["data"].append({
      "id": venue.id,
      "name": venue.name,
    })

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))
#@ahmed
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  #get past and future shows
  shows = Show.query.filter_by(venue_id=venue_id).all()
  upcomingShows = []
  pastShows = []
  #past
  for show in shows:
    if show.start_time < datetime.now():
      pastShows.append({
        "artist_id": show.artist_id,
        "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
        "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
        "start_time": format_datetime(str(show.start_time))
        })
  #----------------------------------------------------------
  #upcoming
  for show in shows:
    if show.start_time > datetime.now():
      upcomingShows.append({
        "artist_id": show.artist_id,
        "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
        "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
        "start_time": format_datetime(str(show.start_time))
      })
  venue = Venue.query.get(venue_id)
  
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    "past_shows": pastShows,
    "upcoming_shows":upcomingShows,
    "past_shows_count": len(pastShows),
    "upcoming_shows_count": len(upcomingShows),
  }
 
  #its working but genere array is not working? i will fix it later or convert it to a string 
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  entry= Venue()
  #data
  entry.name = request.form['name']
  entry.city = request.form['city']
  entry.state = request.form['state']
  entry.phone = request.form['phone']
  entry.genres = request.form['genres']
  entry.image_link = request.form['image_link']
  entry.facebook_link = request.form['facebook_link']
  entry.website = request.form['website']
  # entry.seeking_talent = request.form['seeking_talent'] #soo buggy so i will remove it for now
  # entry.seeking_description = request.form['seeking_description']
  
  # this 
  # if form.validate():
  #   pass
  # else:
  #   flash('error in form validation!')
  #   return redirect(url_for('index'))
  # now we insert data 
  try:
    db.session.add(entry);
    db.session.commit()
  except expression as identifier:
    print('error couldnt insert data '+ identifier )
    flash('Error couldnt add Venue ' + request.form['name'] + 'pls refresh the page and try again!')
    db.session.rollback()
  finally:
    db.session.close()
  # on successful db insert, flash success
  flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead done.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    query = Venue.query.get(venue_id)
    db.session.delete(query)
    db.session.commit()
  except expression as err:
    flash('error cant delete the current venue')
    print('error: '+err)
    db.session.rollback()
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  #later
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  all_artist= Artist.query.all()
  data=[]
  for artist in all_artist:
    data.append({ "id":artist.id, "name":artist.name })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  results = Artist.query.filter(Artist.name.ilike('%{}%'.format(request.form['search_term']))).all()
  dummy=[]
  for artist in results:
    dummy.append({"id":artist.id, "name":artist.name })
  response={
    "count": len(dummy),
    "data": dummy
    }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  shows = Show.query.filter_by(artist_id=artist_id).all()
  upcomingShows = []
  pastShows = []
  #past
  for show in shows:
    if show.start_time < datetime.now():
      pastShows.append({
        "artist_id": show.artist_id,
        "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
        "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
        "start_time": format_datetime(str(show.start_time))
        })
  #----------------------------------------------------------
  #upcoming
  for show in shows:
    if show.start_time > datetime.now():
      upcomingShows.append({
        "artist_id": show.artist_id,
        "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
        "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
        "start_time": format_datetime(str(show.start_time))
      })
  # TODO: replace with real venue data from the venues table, using venue_id
  artist=Artist.query.get(artist_id)
  
  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": pastShows,
    "upcoming_shows": upcomingShows,
    "past_shows_count": len(pastShows),
    "upcoming_shows_count": len(upcomingShows),
  }
 
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  q = Artist.query.get(artist_id)
  artist={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.split(','),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    #"seeking_venue": artist.seeking_venue,
    #"seeking_description": artist.seeking_description,
    "image_link": artist.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)
  artist.name=request.form['name']
  artist.genres = request.form['name']
  artist.city = artist.city = request.form['city']
  artist.state = artist.state = request.form['state']
  artist.phone = request.form['phone']
  artist.website = request.form['website']
  artist.facebook_link = request.form['facebook_link']
  #artist.seeking_description = request.form['seeking_description']
  #artist.seeking_venue = request.form['seeking_venue']
  artist.image_link = request.form['image_link']
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    b.session.commit()
    flash("artist has beenn updated successfully")
  except expression as e:
    flash("Error couldnt update the artist"+e)
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  v= Venue.query.get(venue_id)
  venue={
    "id": v.id,
    "name": v.name,
    "address": v.address,
    "city": v.city,
    "state": venue.state,
    "genres": v.genres.split(','),
    "phone": v.phone,
    "website": v.website,
    "image_link": v.image_link,
    "facebook_link": v.facebook_link,

    #"seeking_talent": v.seeking_talent,
    #"seeking_description": v.seeking_description,
  }

  try:
    db.session.commit()
    flash("updated successfully !")
  except expression as identifier:
    flash("error couldnt update the current venue")
    db.session.rollback()
  finally:
    db.session.close()
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)
  venue.name = request.form['name']
  venue.city = request.form['city']
  venue.state = request.form['state']
  venue.address = request.form['address']
  venue.phone = request.form['phone']
  venue.genres = request.form['genres']
  venue.facebook_link = request.form['facebook_link']
  venue.image_link = request.form['image_link']
  venue.website = request.form['website']

  try:
    db.session.commit()
    flash("updated successfully !")
  except expression as identifier:
    flash("error couldnt update the current venue")
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
  # called upon submitting the new artist listing form
  entry= Artist()
  #data
  entry.name = request.form['name']
  entry.city = request.form['city']
  entry.state = request.form['state']
  entry.phone = request.form['phone']
  entry.genres = request.form['genres']
  entry.image_link = request.form['image_link']
  entry.facebook_link = request.form['facebook_link']
  entry.website = request.form['website']
  try:
    db.session.add(entry);
    db.session.commit()
  except expression as identifier:
    print('error couldnt insert data '+ identifier )
    flash('Error couldnt add Artist ' + request.form['name'] + 'pls refresh the page and try again!')
    db.session.rollback()
  finally:
    db.session.close()
  # on successful db insert, flash success
  flash('Artist was successfully listed!')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows= Show.query.all()
  data=[]
  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": db.session.query(Venue.name).filter_by(id=show.venue_id).first()[0],
      "artist_id": show.artist_id,
      "artist_name": db.session.query(Artist.name).filter_by(id=show.artist_id).first()[0],
      "artist_image_link": db.session.query(Artist.image_link).filter_by(id=show.artist_id).first()[0],
      "start_time": str(show.start_time)
    })
    
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
  entry= Show()
  #data
  entry.artist_id = request.form['artist_id']
  entry.venue_id = request.form['venue_id']
  entry.start_time = request.form['start_time']
  try:
    db.session.add(entry);
    db.session.commit()
  except expression as identifier:
    print('error couldnt insert data '+ identifier )
    flash('Error couldnt add Show. please try again!')
    db.session.rollback()
  finally:
    db.session.close()
  # on successful db insert, flash success
  flash('Show was successfully listed!')
  
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
