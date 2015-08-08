__author__ = 'Art'
from django.dispatch import Signal

setAttValSignal = Signal()

#----------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------
#             Indexing signal receivers
#----------------------------------------------------------------------------------------------------------
# class ItemIndexSignal(BaseSignalProcessor):
#     """
#     Allows for observing when saves/deletes fire & automatically updates the
#     search engine appropriately.
#     """
#
#     def handle_delete(self, sender, instance, **kwargs):
#         """
#         Given an individual model instance, determine which backends the
#         delete should be sent to & delete the object on those backends.
#         """
#         initial_language = translation.get_language()[:2]
#
#         for language, __ in settings.LANGUAGES:
#
#             translation.activate(language)
#             using_backends = self.connection_router.for_write(instance=instance)
#
#             for using in using_backends:
#                 try:
#                     index = self.connections[using].get_unified_index().get_index(sender)
#                     index.remove_object(instance, using=using)
#                 except NotHandled:
#                     # TODO: Maybe log it or let the exception bubble?
#                     pass
#
#         translation.activate(initial_language)
#
#     def handle_save(self, sender, instance, **kwargs):
#         """
#         Given an individual model instance, determine which backends the
#         update should be sent to & update the object on those backends.
#         """
#
#         initial_language = translation.get_language()[:2]
#
#         for language, __ in settings.LANGUAGES:
#
#             translation.activate(language)
#             print(translation.get_language())
#
#             using_backends = self.connection_router.for_write(instance=instance)
#
#             for using in using_backends:
#                 try:
#                     index = self.connections[using].get_unified_index().get_index(sender)
#                     index.update_object(instance, using=using)
#                 except NotHandled:
#                     # TODO: Maybe log it or let the exception bubble?
#                     pass
#
#         translation.activate(initial_language)
#
#     def setup(self):
#         # Naive (listen to all model saves).
#         setAttValSignal.connect(self.handle_save)
#         models.signals.post_delete.connect(self.handle_delete)
#         # Efficient would be going through all backends & collecting all models
#         # being used, then hooking up signals only for those.
#
#     def teardown(self):
#         # Naive (listen to all model saves).
#         setAttValSignal.disconnect(self.handle_save)
#         models.signals.post_delete.disconnect(self.handle_delete)
#         # Efficient would be going through all backends & collecting all models
#         # being used, then disconnecting signals only for those.
