# Generated by Django 2.0.3 on 2018-03-13 17:05

from django.db import migrations, models

color_name_to_html = {
    "green": "#5cb85c",
    "pink": "pink",
    "purple": "purple",
    "gray": "#939393",
    "yellow": "#f0ad4e",
    "red": "#d9534f",
    "blue": "#372fc5",
}

tag_to_color_name = {
	"wbcreate-new": "green",
	"wbcreateredirect": "pink",
	"wbeditentity": "purple",
	"wbeditentity-create": "purple",
        "wbeditentity-update": "gray",
	"wbeditentity-override": "purple",
	"wbsetreference": "green",
	"wbsetreference-add": "green",
	"wbsetreference-set": "yellow",
	"wbsetlabel-add": "green",
	"wbsetlabel-set": "yellow",
	"wbsetlabel-remove": "red",
	"wbsetdescription-add": "green",
	"wbsetdescription-set": "yellow",
	"wbsetdescription-remove": "red",
	"wbsetaliases-set": "yellow",
	"wbsetaliases-add-remove": "red",
	"wbsetaliases-add": "green",
	"wbsetaliases-remove": "red",
	"wbsetaliases-update": "yellow",
	"wbsetlabeldescriptionaliases": "gray",
	"wbsetsitelink-add": "green",
	"wbsetsitelink-add-both": "green",
	"wbsetsitelink-set": "yellow",
	"wbsetsitelink-set-badges": "yellow",
	"wbsetsitelink-set-both": "yellow",
	"wbsetsitelink-remove": "red",
	"wblinktitles-create": "green",
	"wblinktitles-connect": "pink",
	"wbcreateclaim-value": "green",
	"wbcreateclaim-novalue": "green",
	"wbcreateclaim-somevalue": "green",
	"wbcreateclaim": "green",
	"wbsetclaimvalue": "yellow",
	"wbremoveclaims": "red",
	"wbremoveclaims-remove": "red",
	"wbremoveclaims-update": "yellow",
	"special-create-item": "purple",
	"wbcreateclaim-create": "green",
	"wbsetclaim-update": "yellow",
	"wbsetclaim-create": "green",
	"wbsetclaim-update-qualifiers": "yellow",
	"wbsetclaim-update-references": "yellow",
	"wbsetclaim-update-rank": "yellow",
	"clientsitelink-update": "yellow",
	"clientsitelink-remove": "red",
	"wbsetqualifier-add": "green",
	"wbsetqualifier-update": "yellow",
	"wbremovequalifiers-remove": "red",
	"wbremovereferences-remove": "red",
	"wbmergeitems-from": "pink",
	"wbmergeitems-to": "pink",
	"wbcreate-new": "purple",
	"wbeditentity-create": "purple",
	"wbeditentity-override": "purple",
	"wblinktitles-create": "purple",
	"wblinktitles-connect": "purple",
	"wbcreate-new": "purple",
	"wbeditentity-create": "purple",
	"wbeditentity-override": "purple",
	"special-create-property": "purple",
        "undo": "blue",
}


def set_colors(apps, schema_editor):
    Tag = apps.get_model('tagging', 'Tag')
    for tag_id, color in tag_to_color_name.items():
        html = color_name_to_html.get(color) or color
        tag, created = Tag.objects.get_or_create(id=tag_id, priority=10, defaults={'color':html})
        if not created:
            tag.color = html
            tag.save(update_fields=['color'])

def do_nothing(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('tagging', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='color',
            field=models.CharField(default='#939393', max_length=32),
        ),
        migrations.RunPython(
            set_colors, do_nothing
        ),
    ]
