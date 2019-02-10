{%  if 'ictv_data_form' in chan.unavailablefields  %}
{{ ictv_data[chan.name]['control']|safe }}
{% endif %}

