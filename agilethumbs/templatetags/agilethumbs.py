from django import template
from .. import image_url as get_image_url

register = template.Library()

@register.simple_tag
def image_url(image, style='default'):
	return get_image_url(image, style)
