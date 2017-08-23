# Change Log

## [Unreleased](https://github.com/melexis/warnings-plugin/tree/HEAD)

[Full Changelog](https://github.com/melexis/warnings-plugin/compare/0.0.9...HEAD)

**Merged pull requests:**

- Adding automated version from repo's git tags [\#44](https://github.com/melexis/warnings-plugin/pull/44) ([Letme](https://github.com/Letme))

## [0.0.9](https://github.com/melexis/warnings-plugin/tree/0.0.9) (2017-08-11)
[Full Changelog](https://github.com/melexis/warnings-plugin/compare/0.0.8...0.0.9)

**Fixed bugs:**

- broken functionality for python3 in 0.0.8 [\#42](https://github.com/melexis/warnings-plugin/issues/42)

**Merged pull requests:**

- Issue 42: convention about string format [\#43](https://github.com/melexis/warnings-plugin/pull/43) ([SteinHeselmans](https://github.com/SteinHeselmans))

## [0.0.8](https://github.com/melexis/warnings-plugin/tree/0.0.8) (2017-08-11)
[Full Changelog](https://github.com/melexis/warnings-plugin/compare/0.0.7...0.0.8)

**Implemented enhancements:**

- JUnit part should be using some junit parser [\#20](https://github.com/melexis/warnings-plugin/issues/20)
- Implicit members for name and pattern, can be overriden [\#39](https://github.com/melexis/warnings-plugin/pull/39) ([SteinHeselmans](https://github.com/SteinHeselmans))
- Add command to emulate windows wildcard \(no shell expansion\) [\#37](https://github.com/melexis/warnings-plugin/pull/37) ([SteinHeselmans](https://github.com/SteinHeselmans))
- Add option to print version and exit [\#35](https://github.com/melexis/warnings-plugin/pull/35) ([SteinHeselmans](https://github.com/SteinHeselmans))
- Allow for multiple log-files to be provided and fix \#33 [\#32](https://github.com/melexis/warnings-plugin/pull/32) ([SteinHeselmans](https://github.com/SteinHeselmans))
- fix \#20 use parser module for junit failures [\#29](https://github.com/melexis/warnings-plugin/pull/29) ([SteinHeselmans](https://github.com/SteinHeselmans))
- Fix issue \#23: return number of warnings counted when not within limits [\#28](https://github.com/melexis/warnings-plugin/pull/28) ([SteinHeselmans](https://github.com/SteinHeselmans))

**Fixed bugs:**

- issue with python3 and unicode [\#33](https://github.com/melexis/warnings-plugin/issues/33)

**Closed issues:**

- Return code of main\(\) could/should be number of warnings [\#23](https://github.com/melexis/warnings-plugin/issues/23)

**Merged pull requests:**

- Integration test start: JUnit [\#40](https://github.com/melexis/warnings-plugin/pull/40) ([SteinHeselmans](https://github.com/SteinHeselmans))
- Add verbose flag [\#36](https://github.com/melexis/warnings-plugin/pull/36) ([SteinHeselmans](https://github.com/SteinHeselmans))
- Added glob wildcard expansion [\#34](https://github.com/melexis/warnings-plugin/pull/34) ([bavovanachte](https://github.com/bavovanachte))
- Trying to output code coverage by CodeClimate plugin [\#31](https://github.com/melexis/warnings-plugin/pull/31) ([Letme](https://github.com/Letme))
- CodeClimate configuration needs to be adjusted [\#30](https://github.com/melexis/warnings-plugin/pull/30) ([Letme](https://github.com/Letme))
- Codeclimate integration [\#27](https://github.com/melexis/warnings-plugin/pull/27) ([Letme](https://github.com/Letme))

## [0.0.7](https://github.com/melexis/warnings-plugin/tree/0.0.7) (2017-06-27)
[Full Changelog](https://github.com/melexis/warnings-plugin/compare/0.0.6...0.0.7)

**Implemented enhancements:**

- Refactor to use more classes [\#19](https://github.com/melexis/warnings-plugin/issues/19)

**Fixed bugs:**

- python -m mlx.warnings   not working anymore in 0.0.6 [\#22](https://github.com/melexis/warnings-plugin/issues/22)

**Merged pull requests:**

- Fix \#22: different main approach [\#25](https://github.com/melexis/warnings-plugin/pull/25) ([SteinHeselmans](https://github.com/SteinHeselmans))
- Refactoring for the future [\#21](https://github.com/melexis/warnings-plugin/pull/21) ([Letme](https://github.com/Letme))

## [0.0.6](https://github.com/melexis/warnings-plugin/tree/0.0.6) (2017-06-23)
[Full Changelog](https://github.com/melexis/warnings-plugin/compare/0.0.5...0.0.6)

**Merged pull requests:**

- Minimum limit should be zero by default [\#18](https://github.com/melexis/warnings-plugin/pull/18) ([SteinHeselmans](https://github.com/SteinHeselmans))
- Adding requirements badge and a bit more installation information [\#17](https://github.com/melexis/warnings-plugin/pull/17) ([Letme](https://github.com/Letme))
- JUnit failures counter [\#16](https://github.com/melexis/warnings-plugin/pull/16) ([SteinHeselmans](https://github.com/SteinHeselmans))
- Adding some more content to README [\#15](https://github.com/melexis/warnings-plugin/pull/15) ([Letme](https://github.com/Letme))
- Create Contribution guide [\#14](https://github.com/melexis/warnings-plugin/pull/14) ([Letme](https://github.com/Letme))

## [0.0.5](https://github.com/melexis/warnings-plugin/tree/0.0.5) (2017-06-20)
[Full Changelog](https://github.com/melexis/warnings-plugin/compare/0.0.2...0.0.5)

**Implemented enhancements:**

- Missing argument --minwarnings [\#10](https://github.com/melexis/warnings-plugin/issues/10)
- Add unit tests into directory structure [\#4](https://github.com/melexis/warnings-plugin/issues/4)
- Adding unit tests and TOX test environment with directory structure change [\#5](https://github.com/melexis/warnings-plugin/pull/5) ([Letme](https://github.com/Letme))

**Fixed bugs:**

- Fixed regex to also accept warnings without a valid line number [\#9](https://github.com/melexis/warnings-plugin/pull/9) ([bavovanachte](https://github.com/bavovanachte))

**Closed issues:**

- Issue with license and pypi [\#12](https://github.com/melexis/warnings-plugin/issues/12)
- Some RST warnings are not recognized [\#8](https://github.com/melexis/warnings-plugin/issues/8)

**Merged pull requests:**

- Fix license in packaging [\#13](https://github.com/melexis/warnings-plugin/pull/13) ([SteinHeselmans](https://github.com/SteinHeselmans))
- Min threshold [\#11](https://github.com/melexis/warnings-plugin/pull/11) ([SteinHeselmans](https://github.com/SteinHeselmans))
- Adding license [\#1](https://github.com/melexis/warnings-plugin/pull/1) ([Letme](https://github.com/Letme))

## [0.0.2](https://github.com/melexis/warnings-plugin/tree/0.0.2) (2017-03-24)


\* *This Change Log was automatically generated by [github_changelog_generator](https://github.com/skywinder/Github-Changelog-Generator)*