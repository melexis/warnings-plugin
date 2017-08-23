Contribution guide
==================
Anyone is more than welcome to contribute to the development of warnings-plugin,
no matter of your prorgamming skill level. It is reviewers obligation to help bring your
contribution to our desired quality level and you should do your best to help reviewer
understand your decisions. Standard GitHub flow is used https://guides.github.com/introduction/flow/
to start Pull Requests, which are then merged. We also prefer to make a Work In Progress
Merge request once you starting your work just in case someone else is not working on the
same issue.

Getting started
===============
There should always be few issues opened for new features, otherwise you are also
more than welcome to create some on your own suggestions. The `help wanted` label
indicates that it is easy enough task for anyone to start, so go and pick up the
feature you feel most excited by and start implementing it.

Quality of contribution
-----------------------
All new contributions need to be properly tested. We are not targeting some coverage
percentage, but rather focus on regression testing to confirm expected functionality
and border cases. This will help us keep existing features even after years of constant
development and it helps fixing regression bugs.

Documentation
-------------
Basic documentation is expected, but every bit of detail you can include will help in
the future. It might look obvious, but it will also help person reviewing the code to
correctly understand the intended functionality, so that he can focus more on implementation
aspect.

Code review
-----------
Anyone is more than welcome to check open Pull requests and make a code review. Everyone
benefits from fresh eyes looking at new features or bug fixes and it also improves
coding skills of all included. Remember to act politely. Since some people might not be
frequent contributors to various repositories, do not intimidate them, but rather
help them improve. We are all learning.

Changelog
---------
We have deployed automated CHANGELOG to the repository using: 
https://github.com/skywinder/github-changelog-generator . The update of CHANGELOG is simple
but it requires installation of Ruby. Then you install it via `gem install github_changelog_generator`
generate a personal token on GitHub (see https://github.com/skywinder/github-changelog-generator#github-token)
and afterwards generate an CHANGELOG with `github_changelog_generator --token=your-40-digit-token`

Reporting issues or requesting a new feature
============================================
Please open a new Issue if you have any problems with the usage plugin. We will be happy
to fix them as soon as possible. If you want some feature to be included, but do not know
where to start, you should also open an Issue with label `enhancement request` and we
can implement it when we have time if it fits in our view.
