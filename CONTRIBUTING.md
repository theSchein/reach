**Contributing to Reach**
=================

Thanks again for your time and interest in this project!

The following document is a set of guidelines to streamline the contribution process for our contributors. Please feel free to suggest changes to this document in a pull request!

Things to know before getting started
-------------------------------------
#### Code of Conduct
Please try to keep discussions respectful and follow the [Apache Software Foundation Code of Conduct](https://www.apache.org/foundation/policies/conduct.html) when interacting with others.

How to Contribute
-------------------------------------

We love pull requests! We simply don't have the time or resources to add every feature, fix every bug and support every platform. If you have improvements (enhancements or bug fixes) for Reach, start by creating a [Github issue](https://github.com/mikeghen/reach/issues) and discussing it with us first on the [admin@reachtechnology.net](mailto:admin@reachtechnology.net) mailing list. We might already be working on it, or there might be an existing way to do it.

#### Design Decisions

##### Discussion Email
When we need to make changes to the project, we first discuss it on the [admin@reachtechnology.net](mailto:admin@reachtechnology.net) mailing list. Use your best judgement here. Small changes (i.e. bug fixes or small improvements) may not warrant an email discussion. However, larger changes (i.e. new features or changes to existing functionality) should be discussed on the email list prior to development.

#### Pull Requests
Once your issue has been approved you're ready to start slinging code, we have a few [guidelines](https://github.com/mikeghen/reach/blob/master/CONTRIBUTING.md#guidelines) to help maintain code quality and ensure the pull request process goes smoothly.


Guidelines
----------
Following the project conventions will make the pull request process go faster and smoother.

#### Create an issue

If you want to add a new feature, make a [GitHub issue](https://github.com/mikeghen/reach/issues) discuss it with us first on the [admin@reachtechnology.net](mailto:admin@reachtechnology.net) mailing list. We might already be working on it, or there might be an existing way to do it.

If it's a bug fix, make a [GitHub issue](https://github.com/mikeghen/reach/issues) and optionally discuss it with us first on the [admin@reachtechnology.net](mailto:admin@reachtechnology.net) mailing list.
 
#### Code formatting

Keep functions small. Big functions are hard to read, and hard to review. Try to make your changes look like the surrounding code, and follow language conventions. Follow PEP-8 guidelines for Python. 

#### One pull request per feature

Like big functions, big pull requests are just hard to review. Make each pull request as small as possible. For example, if you're adding ten independent API endpoints, make each a separate pull request. If you're adding interdependent functions or endpoints to multiple components, make a pull request for each, starting at the lowest level.

#### Tests

Make sure all existing tests pass. If you change the way something works, be sure to update tests to reflect the change. Add unit tests for new functions, and add integration tests for new interfaces.

Tests that fail if your feature doesn't work are much more useful than tests which only validate best-case scenarios.

We're in the process of adding more tests and testing frameworks, so if a testing framework doesn't exist for the component you're changing, don't worry about it.

#### Commit messages

Try to make your commit messages follow [git best practices](http://chris.beams.io/posts/git-commit/).
1. Separate subject from body with a blank line
2. Limit the subject line to 50 characters
3. Capitalize the subject line
4. Do not end the subject line with a period
5. Use the imperative mood in the subject line
6. Wrap the body at 72 characters
7. Use the body to explain what and why vs. how

This makes it easier for people to read and understand what each commit does, on both the command line interface and Github.com.

---
These guidelines were adapted from [Apache Traffic Control](https://github.com/apache/trafficcontrol)

Don't let all these guidelines discourage you, we're more interested in community involvement than perfection.

What are you waiting for? Get hacking!
