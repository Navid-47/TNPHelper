# Resume Bank Management System
# Main Django project package

# Support running on dev environments with older MariaDB (< 10.5) such as standard XAMPP.
# CI and production use Oracle MySQL 8.4
try:
    from django.db.backends.base.base import BaseDatabaseWrapper
    from django.db.backends.mysql.features import DatabaseFeatures

    _orig_check = BaseDatabaseWrapper.check_database_version_supported
    def _relaxed_check(self):
        try:
            _orig_check(self)
        except Exception as e:
            if 'MariaDB' in str(e):
                pass
            else:
                raise
    BaseDatabaseWrapper.check_database_version_supported = _relaxed_check

    _orig_returning = DatabaseFeatures.can_return_columns_from_insert
    def _safe_can_return(self):
        if self.connection.mysql_is_mariadb and self.connection.mysql_version < (10, 5):
            return False
        return self.connection.mysql_is_mariadb
    DatabaseFeatures.can_return_columns_from_insert = property(_safe_can_return)
except ImportError:
    pass