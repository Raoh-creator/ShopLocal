from django.contrib import admin

# Dashboard app has no models of its own; it provides the staff-facing
# management UI. Customize the standard Django admin branding here.
admin.site.site_header = 'LocalShop Admin'
admin.site.site_title = 'LocalShop Admin'
admin.site.index_title = 'LocalShop Management'