### Django Rest API comment microservice

#### Hack it locally
* `cd comments`
* `pip install -r requirements.txt`
* `python manage.py makemigrations`
* `python manage.py migrate`
* `python manage.py createsuperuser`

#### Endpoints: 
* `/api/comment/`
* `/api/comment/<comment_id>/`
* `/api/comment/<comment_id>/like/`
* `/api/reply/`
* `/api/reply/<reply_id>/`
* `/api/reply/<reply_id>/like/`
* `/api/swagger/`

#### Search and Ordering
* `/api/comments/?search=<username>/<comment_content>`
* `/api/comments/?ordering={created_at/-created_at/user}`

#### OpenAPI
* `.yml` spec can be found @ `OpenAPI/core.yml`

