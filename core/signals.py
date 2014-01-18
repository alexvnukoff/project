__author__ = 'Art'
from haystack.signals import BaseSignalProcessor

#----------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------
#             Indexing signal receivers
#----------------------------------------------------------------------------------------------------------
class ItemIndexSignal(BaseSignalProcessor):
    """
    Allows for observing when saves/deletes fire & automatically updates the
    search engine appropriately.
    """
    def setup(self):
        # Naive (listen to all model saves).
        setAttValSignal.connect(self.handle_save)
        models.signals.post_delete.connect(self.handle_delete)
        # Efficient would be going through all backends & collecting all models
        # being used, then hooking up signals only for those.

    def teardown(self):
        # Naive (listen to all model saves).
        setAttValSignal.disconnect(self.handle_save)
        models.signals.post_delete.disconnect(self.handle_delete)
        # Efficient would be going through all backends & collecting all models
        # being used, then disconnecting signals only for those.
