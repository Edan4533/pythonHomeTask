from flickr_service import FlickrService
from web_server import WebServer

def main():
    flickr_service = FlickrService()
    WebServer(flickr_service).run_web_server()


if __name__ == "__main__":
    # execute only if run as a script
    main()
