# s19-resourceful-Obayanju
### Resources
A sqlite3 database with a governors and user table.
The governors table consists of an id, a name, and duties.
The user table consists of an user_id, first name, last name, email, and password hash

### Schema
```sql
CREATE TABLE governors (
id SERIAL PRIMARY KEY,
name TEXT,
duties TEXT);

CREATE TABLE user_account(
user_id SERIAL PRIMARY KEY,
first_name TEXT,
last_name TEXT,
email TEXT,
hash TEXT);
```

### Password Hashing
[PassLib](https://passlib.readthedocs.io/en/stable/#) Library was used

### Hosting
Heroku and Github Pages

### REST ENDPOINTS
BASE_URL="https://my-democracy-app.heroku.com/"

|     Name | HTTP method |                     Path |
| -------: | ----------: | -----------------------: |
|     List |         GET |       BASE_URL+governors |
| Retrieve |         GET | BASE_URL+governors/${id} |
|   Create |        POST |       BASE_URL+governors |
|  Replace |         PUT | BASE_URL+governors/${id} |
|   Delete |      DELETE | BASE_URL+governors/${id} |
|    Login |        POST |        BASE_URL+sessions |
| Register |        POST |           BASE_URL+users |

port-number is currently set to 8080