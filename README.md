# CRUD Flask API with PostgreSQL database and JWT authentication
Originally a demo for Klinify candidacy. Now a general purpose portfolio project.

TODO
- Docker Image
- Security against JWT replay attacks
  - possibly via making each JWT only good for a single HTTP request
  - or by using flask_kvsession, though I am not certain if this would still be JWT
- CI/CL with Github actions

## Documentation

Preamble: Admins and Users. Admins can CRUD Users. Admins have to be manually added to the DB.
