#Test ushapy

def try_photo():
	#fake up some data
	mapurl = "https://worldushahidis.crowdmap.com/";
	title = "this is my title";
	description = "this is my description";
	lat = 0;
	lon = 0;
	location = "Nairobi";
	categories = "unknown,tiny";
	photopath = "/";
	photoname = "test.jpg"; #NB jpgs only at mo - will need other type above (e.g. image/otherformat) if not
	r = push_report_to_ush(mapurl, title, description, lat, lon, location, categories, photopath, photoname);
	print(r.text);

