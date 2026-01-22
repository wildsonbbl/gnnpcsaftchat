"Django admin module."

from django.contrib import admin


class TablesAdmin(admin.ModelAdmin):
    "DB table row look at admin page."

    list_display = ["smiles", "inchi"]
