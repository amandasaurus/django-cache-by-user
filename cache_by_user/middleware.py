from django.conf import settings

class AddUserIDHashMiddleware(object):
    """
    Middleware that adds a HTTP header X-UserIDHash to request &
    responses, with a hash of the user id. All anonymous users (i.e. not
    logged in) will have the same value of this. This allows one to cache pages
    so that anonymous users can all get the same version of a page, even if
    they have session cookies
    """

    def _user_id_hash(self, request):
        """
        Given a request, try to figure out the UserIDHash
        """
        try:
            if request.user.is_authenticated():
                user_id_string = str(request.user.id)
            else:
                # Anonymous user
                user_id_string = "none"
        except Exception as ex:
            # Can happen if there is no request.session. This happened in some
            # unittests, /shouldn't/ happen in Real World™, but just in case...
            if not hasattr(request, 'session'):
                # No session, so this is equivalent to an anonymous user
                user_id_string = "none"
            else:
                # request.session exists, but we got an error doing request.user.is_authenticated()
                # WTF?!
                # TODO add some logging
                # default to something different
                user_id_string = "unknown"

        user_id_string = user_id_string.rjust(10)

        # add some salt to prevent guessing the user id
        user_id_string = "AddUserIDHashMiddleware(%s)(%s)" % (settings.SECRET_KEY, user_id_string)
        print user_id_string

        # Little bit of obfucation here, SHA1 hash the id string, so no-one will
        # be able to guess user id's, or know how many users we have
        user_id_string = hashlib.sha1(user_id_string).hexdigest()

        # This is a very stupid hack to prevent messages being displayed when the user has message to be shown
        # Append a random string to the user id string if there are any messages to be shown. It is *highly* unlikely
        # there'll be an overlap, so this will mean this request would not be cached.
        #
        # Initially, I tried to replace this middleware with a generic one that looks at the messages (as well as user id),
        # but if you iterate over the messages, it clears them in the request, so they aren't shown in the html (v. bad!), you can set the
        # message storage to not clear, but then they aren't cleared when they are shown, so they are shown every page!
        # If you clear the messages after the response, then if there is a 30X response, the messages are cleared on the 30X response
        # and not available to be shown in the html.
        if len(messages.get_messages(request)) > 0:
            user_id_string += '.' + str(random.randint(0, 1000000))

        return user_id_string

    def process_request(self, request):

        # Add request header.
        # When using this for caching, the FetchFromCacheMiddleware must be
        # below this middleware, and it needs the request to have a
        # X-UserIDHash request header so it can look up the cache to
        # see if it can return a cached response
        request.META['HTTP_X_USERIDHASH'] = self._user_id_hash(request)

    def process_response(self, request, response):

        # Add response header, based on request.
        # The UpdateCacheMiddleware must be above this middleware, so that if
        # it wants to store this response in the cache (for serving later),
        # then it'll know what key to use to store it under
        response['X-UserIDHash'] = self._user_id_hash(request)

        # Tell caches in future that this header is important
        patch_vary_headers(response, ['X-UserIDHash'])

        return response

