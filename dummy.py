
  upcoming = db.session.query(Artist, Show).join(Show).join(Venue).filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id,
        Show.start_time > datetime.now()
    ).all()
  past = db.session.query(Artist, Show).join(Show).join(Venue).filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id,
        Show.start_time < datetime.now()
    ).all()
  #testing to see how the obj look like
  # for show in upcoming:
  #   print(show.Show.start_time)
  
  upcomingShows = []
  pastShows = []
  #past
  for show in past:
      pastShows.append({
        "artist_id": show.Artist.id,
        "artist_name": show.Artist.name,
        "artist_image_link": show.Artist.image_link,
        "start_time": format_datetime(str(show.Show.start_time))
        })
  #----------------------------------------------------------
  #upcoming
  for show in upcoming:
      upcomingShows.append({
        "artist_id": show.Artist.id,
        "artist_name": show.Artist.name,
        "artist_image_link": show.Artist.image_link,
        "start_time": format_datetime(str(show.Show.start_time))
      })