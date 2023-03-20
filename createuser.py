from django.contrib.auth.models import User
user = User.objects.create_user(username='admin', email='supriyom@theeolico.com', password='pa$$w0rd')
