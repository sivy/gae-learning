# Google AppEngine Learnination

* Learn the basics of writing for AppEngine using python
* Figure out how to do unit testing on AppEngine
    - Figure out how to load data fixtures for consistent testing.

## Unit Testing with AppEngine:

Severalin important links:

* [Local Unit Testing](https://developers.google.com/appengine/docs/python/tools/localunittesting) from the GAE docs
* [Unit testing for Google App Engine with Python](http://digitalflapjack.com/blog/2011/jun/14/gaetesting/)] - describes almost exactly the setup I'm using (which I worked out independently)

## Data Fixtures

A number of testing solutions offer the ability to load specific test data into a database before running your tests, so that you can design your test data to test various features and error conditions.

The quick-and-dirty FixureLoader I've written loads data from JSON files into the Google datastore during testing. With the [Testbed](https://developers.google.com/appengine/docs/python/tools/localunittesting#Introducing_the_Python_Testing_Utilities) loaded, this happens without ever touching the network, which means that tests can be run self-contained.

A fixture is a JSON file containing and array of dicts that represent model instances, modeled on Django's fixture loader.

```javascript
[{
    "model": "greeting",
    "content": "hi",
    "author": "testuser@example.com",
    "date": "1971-06-29 04:13:01"
},
{
    "model": "greeting",
    "content": "bye",
    "author": "testuser@example.com",
    "date": "1971-06-29 04:13:00"
}]
```

The `model` property is a lowercase and underscore-delimited classname. "greeting" will get converted to "Greeting", while "foo_bar" will get converted to "FooBar". This model class will be imported and instances of the Model will be created from the JSON data.

When `FixtureLoader` is instantiated, it will look for a `fixtures` directory in the same directory as the current file. This is stupid and broken, and will be fixed.

### Usage

```python
from tests.loader import FixtureLoader
from nose.tools import ok_, eq_

class TestMyClass(object):
    def setUp(self):
        self.loader = FixtureLoader()  # finds the fixture driectory
        self.loader.load_data()  # loads fixtures into the testbed database

    def test_something(self):
        myobjects_query = SomeObject.gql('WHERE etc')
        myobjects = myobject_query.fetch(10)

        ok_(myobjects)  # not None
        eq_(type(myobjects), list)  # got a list back?

        # etc ...
```

### Followup Links:

Still need to grok how the testbad datastore handles indexes: >http://alex.cloudware.it/2012/02/app-engine-datastore-testbed-with.html>