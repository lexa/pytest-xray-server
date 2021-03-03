What is that?
======================

This is a pytest plugin for reporting tests results to Xray *Server* . Xray
comes in two flavours [Xray Server and Xray Cloud](https://docs.getxray.app/display/XRAYCLOUD/Xray+Server+and+Xray+Cloud)
which are significantly different. They have incompatible APIs.

This plugin works with Xray *Server*. If you want to work with [Xray Cloud](https://xray.cloud.xpand-it.com), use [pytest-typhoon-xray](https://github.com/typhoon-hil/pytest-typhoon-xray)

If you are interested in improving the plugin, read [API documentation for Xray Server] (https://docs.getxray.app/display/XRAY/REST+API)

Plugin installation
======================

To install this library for use please enter the following command:

    $ pip install pytest_xray_server

How to use this plugin
======================

To start using the plugin, add it to the list [pytest_plugins in conftest.py](https://docs.pytest.org/en/stable/plugins.html).

    pytest_plugins = ["pytest_xray_server"]

And configure URL to your xray instance in pytest.ini:

    [pytest]
    xray_base_url = https://xray.example.com/rest/

In test cases use markers to associate a test function with a test key and test execution id:

    import pytest

    @pytest.mark.xray(test_key="PRDS-12345")
    def test_my_function():
        assert True == True

Enable the plugin by passing the extra options to the command line when invoking the pytest runner:

    $ pytest . --jira-xray --jira-xray-test-exec-key=PRDS-12121

where PRDS-12121 is Jira ticket ID of Test Execution ticket.

It is important that the environment variables **XRAY_API_CLIENT_ID** and **XRAY_API_CLIENT_SECRET** are set for pytest_xray_server to successfully post results to the Xray API.

    export XRAY_API_CLIENT_ID=user.name
    export XRAY_API_CLIENT_SECRET=password

Adding execution evidence.
======================

Xray allows attachiching execution evidence in form of text (Results) and binary
blobs (evidence). This plug-in lets you create both of the from tests using xray_result and xray_evidence fixtures

    def test_my_function(xray_evidence, xray_result):
        xray_evidence(filename="screenshot.png", data=open('screenshot.png').read())
        xray_result(name='text results', log='chunk of text', status='PASS')

The fixtures work by appending evidence and resutls to node.user_properties, you
could add evidence to it from pytest hooks. It is important to add a tuple of
two elements with first element 'xray_result' or 'xray_evidence' and appropriate
type of the second element.

    from pytest_xray_server import models

    item.user_properties.append(("xray_result", models.XrayResult(name='text results', log='chunk of text', outcome='passed')))


Maintenance notes
======================
Please make sure that any new releases of the library use an incremented version number from the last. The following guidance is used to properly version bump this library {major}.{minor}.{patch}.

Major versions are increased for any new overall library features or general API breaking changes.

Minor versions are increased for any new features added or implementation changes to existing APIs.

Patch versions are increased for any bug fixes and non-breaking changes.

To automatically bump versions, best to install bump2version, then enter either of the following on the command line:

    $ bump2version major

or

    $ bump2version minor

or

    $ bump2version patch

These commands automatically commits and tags a new version. Make sure to push tags to the server with 

    $ git push && git push --tags
