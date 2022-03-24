# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Next
### Fixed
- Allow any IP to connect this admin instance. Useful in docker context.
- Don’t crash if the DKIM private key cannot be correctly read.

## 0.11.0
### Fixed
- Allow to edit dkim params of a domain
- Generate files for `rspamd-dkim` to allow signing outgoing mails

## 0.10.0
### Added
- Permissions
### Fixed
- Trying to sign-in with a user that has an empty or no password will not crash anymore
### Changed
- Bump deps versions
