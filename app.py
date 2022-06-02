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

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String())
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String())
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    shows = db.relationship("Show", backref="venues", lazy=True, cascade="all, delete-orphan")


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120)) 
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    shows = db.relationship("Show", backref="artists", lazy=True, cascade="all, delete-orphan")


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = "shows"

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey("artists.id"), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("venues.id"), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

# ---------------------------------------------------------------------------#
#  Venues  section
#  --------------------------------------------------------------------------#

# show all venues functionality
# ------------------------------------------
@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }]
  data = []
  venues = Venue.query.all()
  for venue in venues:
    grouped_venue = {
          "city": venue.city,
          "state": venue.state
      }
    filtered_venues = Venue.query.filter_by(city=venue.city, state=venue.state).all()

    filtered_venues_arr = []
    for filtered_venue in filtered_venues:
          num_upcoming_shows_count = db.session.query(Show).filter(Show.venue_id == venue.id).filter(
              Show.start_time > datetime.now()).join(Artist, Show.artist_id == Artist.id).count()
          filtered_venues_arr.append({
              "id": filtered_venue.id,
              "name": filtered_venue.name,
              "num_upcoming_shows": num_upcoming_shows_count,
          })
      
    grouped_venue["venues"] = filtered_venues_arr
    data.append(grouped_venue)
  #print(data)    
  return render_template('pages/venues.html', areas=data)



# searh venue functionality
# ----------------------------------------------------
@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get("search_term", "")
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  response={}
  venues = list(Venue.query.filter(
        Venue.name.ilike(f"%{search_term}%") |
        Venue.state.ilike(f"%{search_term}%") |
        Venue.city.ilike(f"%{search_term}%") 
    ).all())
  response["count"] = len(venues)
  response["data"] = []

  for venue in venues:
    searched_data = {
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": len(list(filter(lambda x: x.start_time > datetime.now(), venue.shows)))
    }
    response["data"].append(searched_data)
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

# venues details
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  venue = Venue.query.get(venue_id)

  setattr(venue, "genres", venue.genres.split(","))

  past_shows_query = db.session.query(Show).filter(Show.venue_id == venue_id).filter(
   Show.start_time < datetime.now()).join(Artist, Show.artist_id == Artist.id).add_columns(Artist.id, Artist.name,
   Artist.image_link, Show.start_time)

  past_shows = past_shows_query.all()

  past_shows_count = past_shows_query.count()

  past_shows_arr = []

  for past_show in past_shows:
    past_shows_dict = {}
    past_shows_dict['artist_name'] = past_show.name
    past_shows_dict['artist_id'] = past_show.id
    past_shows_dict['artist_image_link'] = past_show.image_link
    past_shows_dict['start_time'] = past_show.start_time.strftime("%m/%d/%Y, %H:%M:%S")

    past_shows_arr.append(past_shows_dict)

  #print(past_shows)
  setattr(venue, "past_shows", past_shows_arr)
  setattr(venue, "past_shows_count", past_shows_count)


  upcoming_shows_query = db.session.query(Show).filter(Show.venue_id == venue_id).filter(
   Show.start_time > datetime.now()).join(Artist, Show.artist_id == Artist.id).add_columns(Artist.id, Artist.name,
   Artist.image_link, Show.start_time)

  upcoming_shows = upcoming_shows_query.all()

  upcoming_shows_count = upcoming_shows_query.count()

  upcoming_shows_arr = []

  for upcoming_show in upcoming_shows:
    upcoming_shows_dict = {}
    upcoming_shows_dict['artist_name'] = upcoming_show.name
    upcoming_shows_dict['artist_id'] = upcoming_show.id
    upcoming_shows_dict['artist_image_link'] = upcoming_show.image_link
    upcoming_shows_dict['start_time'] = upcoming_show.start_time.strftime("%m/%d/%Y, %H:%M:%S")

    upcoming_shows_arr.append(upcoming_shows_dict)

  #print(past_shows)
  setattr(venue, "upcoming_shows", upcoming_shows_arr)
  setattr(venue, "upcoming_shows_count", upcoming_shows_count)

  #data = list(filter(lambda d: d['id'] == venue_id, [data]))[0]
  return render_template('pages/show_venue.html', venue=venue)


#  Create Venue
#  ---------------------------------------------------------------
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    body = {}

    form = VenueForm(request.form)

    if form.validate(): 
      try:
        name = form.name.data
        city = form.city.data
        state = form.state.data
        address = form.address.data
        phone = form.phone.data
        genres=",".join(form.genres.data)
        image_link = form.image_link.data
        facebook_link = form.facebook_link.data
        website_link = form.website_link.data
        seeking_talent = form.seeking_talent.data
        seeking_description = form.seeking_description.data

        new_venue = Venue(
          name=name, 
          city=city, 
          state=state,
          address=address,
          phone=phone,
          genres=genres,
          image_link=image_link,
          facebook_link=facebook_link,
          website_link=website_link,
          seeking_talent=seeking_talent,
          seeking_description=seeking_description
          )

        db.session.add(new_venue)
        db.session.commit()
        body['name'] = new_venue.name
        flash('Venue ' + request.form['name'] + ' was successfully listed!')

      except:
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        db.session.rollback()
        print(sys.exc_info())
        flash('Venue ' + request.form['name'] + ' could not be listed.')

      finally:
        db.session.close()

    else:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')

    return render_template('pages/home.html')





#  Delete venue
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>/del', methods=['DELETE','GET','POST'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
    try:
      venue = Venue.query.get(venue_id)
      db.session.delete(venue)
      db.session.commit()
      flash("Venue " + venue.name + " was deleted successfully!")
    except:
      db.session.rollback()
      print(sys.exc_info())
      flash("Venue was not deleted successfully.")
    finally:
      db.session.close()
    #return None
    #return jsonify('success', 200)
    return render_template('pages/home.html')


#  update venue
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # venue={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id)
  form.genres.data = venue.genres.split(",")
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  if form.validate():

    try:
      venue = Venue.query.get(venue_id)

      venue.name = form.name.data
      venue.city=form.city.data
      venue.state=form.state.data
      venue.address=form.address.data
      venue.phone=form.phone.data
      venue.genres=",".join(form.genres.data)
      venue.facebook_link=form.facebook_link.data
      venue.image_link=form.image_link.data
      venue.seeking_talent=form.seeking_talent.data
      venue.seeking_description=form.seeking_description.data
      venue.website_link=form.website_link.data

      db.session.add(venue)
      db.session.commit()

      flash("Venue " + form.name.data + " edited successfully")
        
    except Exception:
      db.session.rollback()
      print(sys.exc_info())
      flash("Venue was not edited successfully.")
    finally:
      db.session.close()
  else:
    flash("Venue was not edited successfully.")

  return redirect(url_for('show_venue', venue_id=venue_id))






# ----------------------------------------------------------------------------------------------------#
#                         artist section
# ----------------------------------------------------------------------------------------------------#


#  show all Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }]
  data = Artist.query.with_entities(Artist.id, Artist.name).all()
  #data = db.session.query(Artist.id, Artist.name).all() ------ working too
  return render_template('pages/artists.html', artists=data)


#  search artist
#  ----------------------------------------------------------------
@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(
    Artist.name.ilike(f"%{search_term}%") |
    Artist.city.ilike(f"%{search_term}%") |
    Artist.state.ilike(f"%{search_term}%")
  ).all()

  response = {
            "count": len(artists),
            "data": []
            }

  for artist in artists:
      searched_data = {}
      searched_data["name"] = artist.name
      searched_data["id"] = artist.id

      upcoming_shows = 0
      for show in artist.shows:
          if show.start_time > datetime.now():
              upcoming_shows = upcoming_shows + 1
      searched_data["upcoming_shows"] = upcoming_shows

      response["data"].append(searched_data)
  return render_template('pages/search_artists.html', results=response, search_term=search_term)


# show artist details
# ----------------------------------------
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  artist = Artist.query.get(artist_id)
  setattr(artist, 'genres', artist.genres.split(","))

  past_shows_query = db.session.query(Show).filter(Show.artist_id == artist_id).filter(
   Show.start_time < datetime.now()).join(Venue, Show.venue_id == Venue.id).add_columns(Venue.id, Venue.name,
   Venue.image_link, Show.start_time)


  past_shows = past_shows_query.all()
  past_shows_count = past_shows_query.count()

  past_shows_arr = []

  for past_show in past_shows:
    past_shows_dict = {}
    past_shows_dict['venue_name'] = past_show.name
    past_shows_dict['venue_id'] = past_show.id
    past_shows_dict['venue_image_link'] = past_show.image_link
    past_shows_dict['start_time'] = past_show.start_time.strftime("%m/%d/%Y, %H:%M:%S")

    past_shows_arr.append( past_shows_dict)

  #print(past_shows)
  setattr(artist, "past_shows", past_shows_arr)
  setattr(artist, "past_shows_count", past_shows_count)


  upcoming_shows_query = db.session.query(Show).filter(Show.artist_id == artist_id).filter(
   Show.start_time > datetime.now()).join(Venue, Show.venue_id == Venue.id).add_columns(Venue.id, Venue.name,
   Venue.image_link, Show.start_time)


  upcoming_shows = upcoming_shows_query.all()
  upcoming_shows_count = upcoming_shows_query.count()

  upcoming_shows_arr = []

  for upcoming_show in upcoming_shows:
    upcoming_shows_dict = {}
    upcoming_shows_dict['venue_name'] = upcoming_show.name
    upcoming_shows_dict['venue_id'] = upcoming_show.id
    upcoming_shows_dict['venue_image_link'] = upcoming_show.image_link
    upcoming_shows_dict['start_time'] = upcoming_show.start_time.strftime("%m/%d/%Y, %H:%M:%S")

    upcoming_shows_arr.append(upcoming_shows_dict)

  #print(past_shows)
  setattr(artist, "upcoming_shows", upcoming_shows_arr)
  setattr(artist, "upcoming_shows_count", upcoming_shows_count)

  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=artist)



#  Update artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }
  # TODO: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.get(artist_id)
  form.genres.data = artist.genres.split(",")
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)
  if form.validate:
    try:
      artist = Artist.query.get(artist_id)

      artist.name = form.name.data
      artist.city=form.city.data
      artist.state=form.state.data
      artist.phone=form.phone.data
      artist.genres=",".join(form.genres.data)
      artist.facebook_link=form.facebook_link.data
      artist.image_link=form.image_link.data
      artist.seeking_venue=form.seeking_venue.data
      artist.seeking_description=form.seeking_description.data
      artist.website_link=form.website_link.data

      db.session.add(artist)
      db.session.commit()
      flash("Artist " + artist.name + " was successfully edited!")
    except:
      db.session.rollback()
      print(sys.exc_info())
      flash("Artist was not edited successfully.")
    finally:
      db.session.close()
  else:
    flash("Artist was not edited successfully.")

  return redirect(url_for('show_artist', artist_id=artist_id))





#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)
  if form.validate:
    try:
      new_artist = Artist(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        genres=",".join(form.genres.data),
        image_link=form.image_link.data,
        facebook_link=form.facebook_link.data,
        website_link=form.website_link.data,
        seeking_venue=form.seeking_venue.data,
        seeking_description=form.seeking_description.data,
      )
      db.session.add(new_artist)
      db.session.commit()
      # on successful db insert, flash success
      flash("Artist " + request.form["name"] + " was successfully listed!")
    except Exception:
      db.session.rollback()
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
      flash("Artist was not successfully listed.")
    finally:
      db.session.close()
  else:
    flash("Artist was not successfully listed.")

  return render_template('pages/home.html')





# ----------------------------------------------------------------------------------------------------#
#                                   show section
# ----------------------------------------------------------------------------------------------------#


#  display all shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }]

  data = []

  shows = Show.query.all()
  for show in shows:
    shows_dict = {}
    shows_dict["venue_id"] = show.venues.id
    shows_dict["venue_name"] = show.venues.name
    shows_dict["artist_id"] = show.artists.id
    shows_dict["artist_name"] = show.artists.name
    shows_dict["artist_image_link"] = show.artists.image_link
    shows_dict["start_time"] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
      
    data.append(shows_dict)
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
  form = ShowForm(request.form)
  if form.validate():
    try:
      new_show = Show(
          artist_id=form.artist_id.data,
          venue_id=form.venue_id.data,
          start_time=form.start_time.data
      )
      db.session.add(new_show)
      db.session.commit()
      flash('Show was successfully listed!')
    except Exception:
      db.session.rollback()
      print(sys.exc_info())
      # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Show could not be listed.')
    finally:
      db.session.close()
  else:
    flash('An error occurred. Show could not be listed.')

  return render_template('pages/home.html')




# ----------------------------------------------------------------------------------------------------#
#                         error section
# ----------------------------------------------------------------------------------------------------#

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
