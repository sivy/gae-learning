## Google AppEngine Learnination

* Learn the basics of writing for AppEngine using python
* Figure out how to do unit testing on AppEngine
    - Figure out how to load data fixtures for consistent testing.

### Unit Testing AppEngine apps:

Severalin important links:

* [Local Unit Testing](https://developers.google.com/appengine/docs/python/tools/localunittesting) from the GAE docs
* [Unit testing for Google App Engine with Python](http://digitalflapjack.com/blog/2011/jun/14/gaetesting/)] - describes almost exactly the setup I'm using (which I worked out independently)

### Data Fixtures

A number of testing solutions offer the ability to load specific test data into a database before running your tests, so that you can design your test data to test various features and error conditions.

The quick-and-dirty FixureLoader I've written loads data from JSON files into the Google datastore during testing. With the [Testbed](https://developers.google.com/appengine/docs/python/tools/localunittesting#Introducing_the_Python_Testing_Utilities) loaded, this happens without ever touching the network, which means that tests can be run self-contained.