django-cache-by-user
====================

Make your django site share a cache for all anonymous users, increasing cache
hits, increasing page load time, reducing CPU load.

When using [Django's per view cache](), the session middleware will add ``Vary:
Cookie`` so that cached pages will not be shared between users. Nearly all the
time this is what you want. However if you have a popular webpage that is often
visited by non-logged in users, and you want to cache it, you have a problem.
Every different anonymous user will cause a cache hit.

By using ``django-cache-by-user``, you can share the cache for a page between anonymous users.

Installation
============

    pip install django-cache-by-user

Add it as a middleware:

    MIDDLEWARE_CLASSES = ( 
        ….
        'cache_by_user.middleware.AddUserIDHashMiddleware',
        …
    )

Usage
=====

Every response will now have a ``X-UserIDHash``
header. All anonymous users will have the same value, all logged in users will
have a different value based on their userid.

The value is hashed and based on the userid and your ``SECRET_KEY`` setting.
Neither your ``SECRET_KEY`` nor user ids are revealed though.

It adds ``X-UserIDHash`` to the ``Vary`` header of the response. To get the real benefit you need to use [django-dont-vary-on](https://github.com/rory/django-dont-vary-on) to remove ``Cookie`` from the Vary header.

    @dont_vary_on("Cookie")
    def my_view_with_anonymous(request):
        ...

