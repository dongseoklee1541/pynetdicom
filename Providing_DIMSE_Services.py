from pynetdicom import AE, evt
from pynetdicom.sop_class import VerificationSOPClass

ae = AE()
ae.add_supported_context(VerificationSOPClass)


def handle_store(event):
    """Handle evt.EVT_C_STORE"""
    # This is just a toy implementation that doesn't store anything and
    # always returns a Success response

    return 0x0000


handlers = [(evt.EVT_C_STORE, handle_store)]

# Listen for association requests
ae.start_server(('127.0.0.1', 11112), evt_handlers=handlers)