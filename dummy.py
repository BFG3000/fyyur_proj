 # shows the venue page with the given venue_id
  #get past and future shows
  shows = Show.query.filter_by(venue_id=venue_id).all()
  upcomingShows = []
  pastShows = []
  #past
  for show in shows:
    if show.start_time < datetime.now():
      past.append({
        "artist_id": show.artist_id,
        "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
        "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
        "start_time": format_datetime(str(show.start_time))
        })
  #----------------------------------------------------------
  #upcoming
  for show in shows:
    if show.start_time > datetime.now():
      upcoming.append({
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