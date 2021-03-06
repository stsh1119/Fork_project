# Forks
The project aims at people, who are into collecting forks.
Users can:
* Register,
* Log in,
* Create forks(if authorized)
* Delete forks(if authorized)
* View your own forks(if authorized)
* View forks others created(if authorized)
* Sign up for a certain category, to get email notification whenever new fork is added to a chosen category (if authorized)


### Tech stack:
 - Flask
 - Flask-JWT-Extended
 - Flask-SQLAlchemy
 - Flask-Marshmallow
 - Celery
 - Redis(message broker, backend)

## Endpoints usage:
#### Register
```
/register [POST]
```
Registration requires the following parameters in request body:
1. Login
2. Email
3. Password

Registration will return success provided that the email is valid and both login and email aren't taken by other users.

```
{
	"login": "user",
	"email": "john_doe@gmail.com",
	"password": "Password1234"
}
```
---

#### Login
```
/login [POST]
```
Login requires the following parameters in request body:
1. Login
3. Password

Login will return access and refresh tokens,
provided that user exists and password is matching.

```
{
	"login": "user",
	"password": "Password1234"
}
```
---

#### Refresh/Get new access token
```
/refresh [POST]
```
Refresh will give you new access token, which will expire in 15 minutes

Authorization: Bearer {valid_refresh_token} is reqired to get access token. 

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2MTM0MjM0NjUsIm5iZiI6MTYxMzQyMzQ2NSwianRpIjoiMmE5NWJmOGYtYmY1NS00MjZjLTlkY2ItZmQ3ODlhZjEwNTI2IiwiZXhwIjoxNjEzNTA5ODY1LCJpZGVudGl0eSI6InN0c2giLCJ0eXBlIjoyymVmcmVzaCJ9.jTv-zGqfkaeuPGm3oebUJ1OW0r9eweGj4r1SkdBrV44
```
---

#### Logout
```
/logout [DELETE]
```
Logout requires valid access token in header:

After request is sent, access token will be revoked and will no longer be valid

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2MTM0MjM0NjUsIm5iZiI6MTYxMzQyMzQ2NSwianRpIjoiMjE0MTViZGUtYWM1Yy00Njc2LThhZTgtMTA0NTg4ZjMzOWIyIiwiZXhwIjoxNjEzNDI0MzY1LCJpZGVudGl0eSI6InN0c2giLCJmcmVzaCI6ZmFsc2UsInR5cGUiOiJhY2Nlc3MifQ.rpFti_mQNEALSWpQZbPQJcTcvWwEx5O2Vfwx2w-yl7E
```
---

#### View all existing forks
```
/forks/all [GET]
```
Requires access token in header.

Will return all forks in descending order
page can be explicitly set to some value, in case no value is given, first page will be displayed.

```
/forks/all?page=2
```
---
#### View fork by id

```
/forks/<int:fork_id> [GET]
```
Requires access token in header.

Will return all info on a specific fork by given id.

```
/forks/3
```

---
#### View Categories

```
/forks/categories [GET]
```
Requires access token in header.

Will return a list of all existing categories with their descriptions.

Page can be explicitly set to some value, in case no value is given, first page will be displayed.

---

#### View forks from a specific category

```
/forks/category/<string:category_name> OR /forks/category/ [GET]
```
Requires access token in header.

Will return a list of all forks under given category.


Page and category can be explicitly set to some values, in case no values are given, first page will be displayed, 
with forks with 'Uncategorized' value in category.

```
/forks/category?page=1 OR /forks/category/Newer forks?page=1
```
---


#### Create a fork
```
/forks/create [POST]
```
Requires access token in header.

Creation of fork requires the following parameters in request body:
1. name
2. description
3. creation_date
4. category (**Optional**)

In case category is not present in the request, it will be set as 'Uncategorized'.

```
{
	"name": "Test Fork",
	"description": "Some description",
	"creation_date": 1000
}
```
---

#### Delete a fork
```
/forks/delete [DELETE]
```
Requires access token in header.

Accepts fork name in query parameters as a criteria for deletion.

```
/forks/delete?name=Fork Fork
```
---

#### View your forks
```
/forks/my_forks [GET]
```
Requires access token in header.

Will show all foks, that belowng to a current user.

---

#### Show other user's forks
```
/forks/<string:email> [GET]
```
Requires access token in header.

Will show all forks, that belong to a user, if the user exists.

```
/forks/john_doe@gmail.com
```
---

#### Sign up for notifications for a certain fork category
```
/forks/sign_up [POST]
```
Requires access token in header.

Accepts category name in query parameters as a criteria for subscription.

In case wrong/no category is given - will throw an error.

```
/forks/sign_up?category=Uncategorized
```
---

#### Sign up for notifications for a certain fork category
```
/forks/remove_subscription [DELETE]
```
Requires access token in header.

Accepts category name in query parameters as a criteria for deleting a subscription.

In case wrong/no category is given - will respond, that user is not signed up for {category_name}.

```
/forks/sign_up?category=Uncategorized
```
---

#### Sign up for notifications for a certain fork category
```
/forks/view_subscriptions [GET]
```
Requires access token in header.

Returns list of subscriptions for current user.

In case there are no subscriprions, the user will get a message, that he's not subscribed to any category.

---