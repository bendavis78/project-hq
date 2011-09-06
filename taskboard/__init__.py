from . import listeners

# Add support for TagField
from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^tagging\.fields\.TagField"])
