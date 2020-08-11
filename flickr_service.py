import flickr_api

API_KEY =  '6c7a35c6bb4aef2571d9d6feb21d08be'
API_SECRET = 'c13eb85d12c7ae95'


class FlickrService(object):

    def __init__(self):
        super(FlickrService, self).__init__()
        flickr_api.set_keys(api_key = API_KEY, api_secret = API_SECRET)

    async def getImagesList(self, pageIndex):
        flickrImages = flickr_api.Photo.getRecent(api_key = API_KEY, per_page=10, page=pageIndex)

        # Returning images ids cause i couldn't do serialization to the Photo object returning from flickr
        userImagesIds = [o.id for o in flickrImages.data]
        return userImagesIds

    async def getImagesBySearchTerm(self, searchTerm):
        # in flickr api wiki the saying the the field text is matching to Photo object - title , description, tags
        # https://www.flickr.com/services/api/flickr.photos.search.html
        flickrImages = flickr_api.Photo.search(api_key = API_KEY, per_page = 10, text = searchTerm)
        # Returning images ids cause i couldn't do serialization to the Photo object returning from flickr
        userImagesIds = [o['id'] for o in flickrImages.data]
        return userImagesIds

    async def getImageInfo(self, image_id):
        imageInfo =flickr_api.Photo(id= image_id).getInfo(api_key=API_KEY, photo_id = image_id, secret=API_SECRET)
        return imageInfo