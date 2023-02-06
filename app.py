# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

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
    genres = db.Column(db.String)
    website = db.Column(db.String)
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)
    shows = db.relationship('Show', backref='Venue', lazy=True);



class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    website = db.Column(db.String)
    seeking_description = db.Column(db.String)
    shows = db.relationship('Show', backref='Artist', lazy=True);


class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.String)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    outputData = [];
    inputData = Venue.query.all()
    for venue in inputData:
        city = venue.city
        allShows = Show.query.all()
        numUpcomingShows = 0
        for show in allShows:
            if(show.venue_id == venue.id):
                numUpcomingShows+=1
        # check if outputData is empty
        if outputData is None:
            outputData.append({
                "city": city,
                "state": venue.state,
                "venues": [{
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": numUpcomingShows
                }]
            })

        # check if area is already in outputData
        areaInOutput = False;
        for data in outputData:
            if city == data["city"]:
                areaInOutput = True
                data["venues"].append({
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_show": numUpcomingShows
                })

        # area is not in outputData
        if areaInOutput == False:
            outputData.append({
                "city": city,
                "state": venue.state,
                "venues": [{
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": numUpcomingShows,
                }]
            })
    return render_template('pages/venues.html', areas=outputData);


@app.route('/venues/search', methods=['POST'])
def search_venues():
    allVenues = Venue.query.all()
    search_query = request.form.get("search_term").lower()
    foundVenues = []
    for venue in allVenues:
        venueName = venue.name.lower()
        if search_query in venueName:
            shows = Show.query.filter(Show.venue_id==venue.id).all()
            foundVenues.append({
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(shows)
            })
    response = {
        "count": len(foundVenues),
        "data": foundVenues
    }
    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    allVenues = Venue.query.all()
    currentVenue = Venue()
    for venue in allVenues:
        if venue.id == venue_id:
            currentVenue = venue;

    allShows = Show.query.all()
    showsOfVenues = []
    for show in allShows:
        if show.venue_id == venue_id:
            showsOfVenues.append(show)

    pastShows = []
    upcomingShows = []
    date_format = '%Y-%m-%d %H:%M:%S'
    for show in showsOfVenues:
        date = datetime.strptime(show.start_time, date_format)
        if date < datetime.now():
            pastShows.append(show)
        else:
            upcomingShows.append(show)

    pastShowsCount = len(pastShows)
    upcomingShowsCount = len(upcomingShows)

    outputData = {
        "id": currentVenue.id,
        "name": currentVenue.name,
        "genres": currentVenue.genres,
        "address": currentVenue.address,
        "city": currentVenue.city,
        "state": currentVenue.state,
        "phone": currentVenue.phone,
        "website": currentVenue.website,
        "facebook_link": currentVenue.facebook_link,
        "seeking_talent": currentVenue.seeking_talent,
        "seeking_description": currentVenue.seeking_description,
        "image_link": currentVenue.image_link,
        "past_shows": pastShows,
        "upcoming_shows": upcomingShows,
        "past_shows_count": pastShowsCount,
        "upcoming_shows_count": upcomingShowsCount,
    }


    return render_template('pages/show_venue.html', venue=outputData)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    data = request.form
    try:
        newVenue = Venue()
        newVenue.name = data.get("name")
        newVenue.city = data.get("city")
        newVenue.state = data.get("state")
        newVenue.address = data.get("address")
        newVenue.phone = data.get("phone")
        newVenue.genres = data.get("genres")
        newVenue.facebook_link = data.get("facebook_link")
        newVenue.image_link = data.get("image_link")
        newVenue.website_link = data.get("website_link")
        seekingTalent = False
        if data.get("seeking_talent") == "y":
            seekingTalent = True
        newVenue.seeking_talent = seekingTalent
        newVenue.seeking_description = data.get("seeking_description")
        db.session.add(newVenue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' + data.get("name") + ' could not be listed.')
    finally:
        return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        Venue.query.filter(Venue.id == venue_id).delete
        print(Venue.query.filter(Venue.id == venue_id))
        db.session.commit()
    except:
        db.session.rollback()
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    data = []
    artists = Artist.query.all()
    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name
        })
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    allArtists = Artist.query.all()
    search_query = request.form.get("search_term").lower()
    foundArtists = []
    for artist in allArtists:
        artistName = artist.name.lower()
        if search_query in artistName:
            shows = Show.query.filter(Show.artist_id == artist.id).all()
            foundArtists.append({
                "id": artist.id,
                "name": artist.name,
                "num_upcoming_shows": len(shows)
            })
    response = {
        "count": len(foundArtists),
        "data": foundArtists
    }
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artists = Artist.query.all()
    currentArtist = Artist()
    for artist in artists:
        if artist.id == artist_id:
            currentArtist = artist

    allShows = Show.query.all()
    showsOfArtists = []
    for show in allShows:
        if show.artist_id == artist_id:
            showsOfArtists.append(show)

    pastShows = []
    upcomingShows = []
    date_format = '%Y-%m-%d %H:%M:%S'
    for show in showsOfArtists:
        date = datetime.strptime(show.start_time, date_format)
        if date < datetime.now():
            pastShows.append(show)
        else:
            upcomingShows.append(show)

    pastShowsCount = len(pastShows)
    upcomingShowsCount = len(upcomingShows)
    outputData = {
        "id": currentArtist.id,
        "name": currentArtist.name,
        "genres": currentArtist.genres,
        "city": currentArtist.city,
        "state": currentArtist.state,
        "phone": currentArtist.phone,
        "seeking_venue": currentArtist.seeking_venue,
        "image_link": currentArtist.image_link,
        "past_shows": pastShows,
        "upcoming_shows": upcomingShows,
        "past_shows_count": pastShowsCount,
        "upcoming_shows_count": upcomingShowsCount,
        "facebook_link": currentArtist.facebook_link,
        "website": currentArtist.website,
        "seeking_description": currentArtist.seeking_description
    }
    return render_template('pages/show_artist.html', artist=outputData)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.filter(Artist.id == artist_id).all()[0]
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    data = request.form

    try:
        editArtist = Artist.query.get(artist_id)
        editArtist.name = data.get("name")
        editArtist.city = data.get("city")
        editArtist.state = data.get("state")
        editArtist.phone = data.get("phone")
        editArtist.genres = data.get("genres")
        seeking_venue = False
        if data.get("seeking_venue") == "y":
            seeking_venue = True
        editArtist.seeking_venue = seeking_venue
        editArtist.image_link = data.get("image_link")
        editArtist.facebook_link = data.get("facebook_link")
        editArtist.seeking_description = data.get("seeking_description")
        editArtist.website = data.get("website_link")
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        return redirect(url_for('show_artist', artist_id=artist_id))



@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    data = request.form;

    try:
        editVenue = Venue.query.get(venue_id)
        editVenue.name = data.get("name")
        editVenue.city = data.get("city")
        editVenue.address = data.get("address")
        editVenue.state = data.get("state")
        editVenue.phone = data.get("phone")
        editVenue.genres = data.get("genres")
        editVenue.image_link = data.get("image_link")
        editVenue.facebook_link = data.get("facebook_link")
        editVenue.website = data.get("website_link")
        seekingTalent = False;
        if data.get("seeking_talent")=="y":
            seekingTalent = True
        editVenue.seeking_talent = seekingTalent
        editVenue.seeking_description = data.get("seeking_description")
        db.session.commit()
    except:
        db.session.rollback()
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    data = request.form
    try:
        newArtist = Artist()
        newArtist.name = data.get("name")
        newArtist.city = data.get("city")
        newArtist.state = data.get("state")
        newArtist.phone = data.get("phone")
        newArtist.genres = data.get("genres")
        seeking_venue = False
        if data.get("seeking_venue")=="y":
            seeking_venue = True
        newArtist.seeking_venue = seeking_venue
        newArtist.image_link = data.get("image_link")
        newArtist.facebook_link = data.get("facebook_link")
        newArtist.seeking_description = data.get("seeking_description")
        newArtist.website = data.get("website_link")
        db.session.add(newArtist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        flash('An error occurred. Artist ' + data.get("name") + ' could not be listed.')
        db.session.rollback()
    finally:
        return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows

    inputData = Show.query.all()
    outputData = []
    venues = Venue.query.all()
    artists = Artist.query.all()

    for show in inputData:
        for venue in venues:
            if venue.id == show.venue_id:
                showVenue = venue
        for artist in artists:
            if artist.id == show.artist_id:
                showArtist = artist
        outputData.append({
            "venue_id": show.venue_id,
            "venue_name": showVenue.name,
            "artist_id": show.artist_id,
            "artist_name": showArtist.name,
            "artist_image_link": showArtist.image_link,
            "start_time": show.start_time
        })
    return render_template('pages/shows.html', shows=outputData)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    data = request.form
    try:
        newShow = Show()
        newShow.artist_id = data['artist_id']
        newShow.venue_id = data['venue_id']
        newShow.start_time = data['start_time']
        db.session.add(newShow)
        db.session.commit()

        # on successful db insert, flash success
        flash('Show was successfully listed!')
    except:
        db.session.rollback()
        flash('Show could not be listed!')
    finally:
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

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
