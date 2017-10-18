import mongoengine

class User(mongoengine.Document):
    email = mongoengine.StringField(required=True)
    first_name = mongoengine.StringField(max_length=50)
    last_name = mongoengine.StringField(max_length=50)

def main():
    mongoengine.connect("tumblelog")

def add_user(user, first_name, last_name):
    new_user = User(user, first_name, last_name).save()


if __name__ == "__main__":
    main()
