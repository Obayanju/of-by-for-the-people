# of-by-for-the-people 
### Resources
A sqlite3 database with a governors and user table.
The governors table consists of an id, a name, and duties.
The user table consists of an user_id, first name, last name, email, and password hash

### Schema
```sql
CREATE TABLE governors (
id INTEGER PRIMARY KEY,
name TEXT,
duties TEXT);

CREATE TABLE user(
user_id INTEGER PRIMARY KEY,
first_name text not null,
last_name text not null,
email text not null unique,
hash text not null);
```

### Password Hashing
[PassLib](https://passlib.readthedocs.io/en/stable/#) Library was used

### REST ENDPOINTS
|     Name | HTTP method |                                         Path |
| -------: | ----------: | -------------------------------------------: |
|     List |         GET |       http://localhost:port-number/governors |
| Retrieve |         GET | http://localhost:port-number/governors/${id} |
|   Create |        POST |       http://localhost:port-number/governors |
|  Replace |         PUT | http://localhost:port-number/governors/${id} |
|   Delete |      DELETE | http://localhost:port-number/governors/${id} |
|    Login |        POST |        http://localhost:port-number/sessions |
| Register |        POST |           http://localhost:port-number/users |

port-number is currently set to 8080
