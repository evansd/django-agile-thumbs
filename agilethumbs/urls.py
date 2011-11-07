from django.conf.urls.defaults import patterns, url

regices = dict(
    (key, '(?P<%s>%s)' % (key, value)) for (key, value) in [
        ('file_id', r'[A-Za-z0-9_\-~/]+'),
        ('style', r'[a-z0-9_]+'),
        ('version', r'[0-9]+'),
        ('signature', r'[a-z0-9]+'),
        ('extension', r'[a-z0-9]+')
    ]
)

urlpatterns = patterns('',
    url(r'^%(file_id)s-%(style)s-%(version)s-%(signature)s\.%(extension)s$' %
            regices,
        'agilethumbs.views.agilethumbs_image',
        name='agilethumbs_image'),
)
