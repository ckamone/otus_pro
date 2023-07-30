from django.contrib.auth.mixins import UserPassesTestMixin


class OnlyStaffMixin(UserPassesTestMixin):

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class OnlySuperMixin(UserPassesTestMixin):

    def test_func(self):
        return  self.request.user.is_superuser