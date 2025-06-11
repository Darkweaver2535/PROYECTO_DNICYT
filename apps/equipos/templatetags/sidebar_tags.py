from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def is_active_section(context, namespace, *url_names):
    """
    Determina si una sección del sidebar debe estar activa
    """
    request = context['request']
    current_namespace = getattr(request.resolver_match, 'namespace', None)
    current_url_name = getattr(request.resolver_match, 'url_name', None)
    
    if current_namespace == namespace:
        if url_names:
            return 'active' if current_url_name in url_names else ''
        return 'active'
    
    return ''

@register.simple_tag(takes_context=True)
def is_active_url(context, url_name, *related_urls):
    """
    Determina si una URL específica debe estar activa
    """
    request = context['request']
    current_url_name = getattr(request.resolver_match, 'url_name', None)
    
    if current_url_name == url_name:
        return 'active'
    
    # Verificar URLs relacionadas
    for related_url in related_urls:
        if current_url_name == related_url:
            return 'active'
    
    return ''