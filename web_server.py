from flask_sqlalchemy import SQLAlchemy
import json
from quart import Quart, request
# quart build as flask and handling async await
# each page will return 10 images
PER_PAGE_INDEX = 10

app = Quart(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

FLICKER = None

# in project structure migration table will be in a different folder - model
class Users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    user_id = db.Column("user_id", db.Integer)
    image_id = db.Column("image_id", db.Integer)
    is_active = db.Column(db.Boolean, default=True)

    def __init__(self, user_id, image_id):
        self.user_id = user_id
        self.image_id = image_id


class WebServer(object):
    def __init__(self, flickr_service):
        global flickrService
        flickrService = flickr_service

    @staticmethod
    def run_web_server(debug=True):
        #  this command to clear the DB
        # db.drop_all()

        db.create_all()
        app.run(debug=debug)


    # http://localhost:5000/getImages/1 - url example
    @staticmethod
    @app.route('/getImages/<pageIndex>')
    async def list_view_items(pageIndex):
        if pageIndex is None:
            return 'require page index '

        images = await flickrService.getImagesList(pageIndex)
        return json.dumps(images)

    @staticmethod
    @app.route('/getImagesBySearchTerm/<searchTerm>')
    async def search_results_items(searchTerm):
        images = await flickrService.getImagesBySearchTerm(searchTerm)
        return json.dumps(images)

    @staticmethod
    @app.route('/getImageInfo/<image_id>')
    async def get_image_info(image_id):
        imageInfo = await flickrService.getImageInfo(image_id)

        # Returning image title  cause i couldn't do serialization to the Photo object returning from flickr
        return imageInfo['title']

    @staticmethod
    @app.route('/markImageAsFavorite', methods=["POST"])
    async def mark_image_as_favorite():
        image_id = request.args.get('image_id')
        if not image_id:
            return 'missing image_id in request params'
        user_id = request.args.get('user_id')
        if not user_id:
            return 'missing user_id in request params'

        user = Users.query.filter_by(user_id=user_id, image_id=image_id).first()

        # handling the case user unmark the image and want to mark it again - prevent double records
        if user is not None:
            user.is_active = True
            db.session.commit()
            return 'DONE MARKING AS FAVORITE'
        imageRow = Users(user_id, image_id)
        db.session.add(imageRow)
        db.session.commit()
        return 'DONE'


    # this function also handle the part of delete favorite item - i went in approch of not deleting, i use "is_active" column
    @staticmethod
    @app.route('/unmarkImageAsFavorite', methods=["POST"])
    async def unmark_image_as_favorite():
        image_id = request.args.get('image_id')
        if not image_id:
            return 'missing image_id in params'
        user_id =  request.args.get('user_id')
        if not user_id:
            return 'missing user_id in request params'

        user = Users.query.filter_by(user_id=user_id, image_id=image_id).first()
        if user is None :
            return 'YOU DIDNT MARK THIS IMAGE AS FAVORITE'
        user.is_active = False
        db.session.commit()
        return 'DONE'

    @staticmethod
    @app.route('/getUserFavoriteImages/<user_id>/<pageIndex>')
    async def get_users_favorite_images(user_id, pageIndex):
        userImages = Users.query.filter_by(user_id=user_id, is_active=True).limit(pageIndex * PER_PAGE_INDEX).all()

        # Returning images ids cause i couldn't do serialization to the Photo object returning from flickr
        userImagesIds = [o.image_id for o in userImages]

        return json.dumps(userImagesIds)

    @staticmethod
    @app.route('/getUserFavoriteImagesByFilters', methods=["POST"])
    async def get_users_favorite_images_by_filters():
        pageIndex = request.args.get('page_index')
        user_id =  request.args.get('user_id')
        filter_by = request.args.get('filter_by')
        userImages = Users.query.filter_by(user_id=user_id, is_active=True).limit(pageIndex * PER_PAGE_INDEX).all()
        userImagesIds = [o.image_id for o in userImages]

        favoriteImagesInfo = []
        for imageId in userImagesIds:
            favoriteImagesInfo.append(await  flickrService.getImageInfo(imageId))

        # here we can make switch  case to every attribute we went to filter in Photo object returning from flickr api
        if filter_by == "views":
            sortedFavoriteImagesInfo = sorted(favoriteImagesInfo, key=lambda x: int(x['views']), reverse=True)

        #  I'm not return the sortedFavoriteImagesInfo beacuse the same serialization issue
        return 'Done'

    @staticmethod
    @app.route('/getFavoriteImagesBySearchTerm', methods=["POST"])
    async def get_users_favorite_images_by_search_term():
        pageIndex = request.args.get('page_index')
        userId =  request.args.get('user_id')
        searchTerm = request.args.get('search_term')
        images = await flickrService.getImagesBySearchTerm(searchTerm)
        imagesIds = []
        for imageId in  images:
            # check if user favorite image is with the same search term
            isFavoriteImage = Users.query.filter_by(user_id=userId, image_id=imageId).first()
            if isFavoriteImage is not None:
                imagesIds.append(imageId)

        return 'DONE'


