Introduction
============

Nextcloud

Changelog

  # 2020.11.06
    - Initial

Environment Variables
=====================

- `DEFAULT_PAPERSIZE` - LDAP server hostname(s) (default: "ldap1.example.com ldap2.example.com")
- `AUTH_LDAP_SERVER` - LDAP ip address eg. 10.0.0.1
- `AUTH_LDAP_PORT` - LDAP server port (default: "389")
- `AUTH_LDAP_ADMIN` - LDAP server user (default: "cn=admin,dc=example,dc=com")
- `AUTH_LDAP_PASSWORD` - LDAP server password (default: "password")
- `AUTH_LDAP_BASEDN` - LDAP server Base DN (default: "dc=example,dc=com")
- `AUTH_METHOD` - none, unix, ldap
- `AUTH_LDAP_SCHEMA_TYPE` - ACTIVE_DIRECTORY or NOVELL_EDIRECTORY

- 




Example Docker Compose Configuration
====================================


# nextcloud_docker_cluster
