from pynetdicom import AE, evt
from pynetdicom.sop_class import DisplaySystemSOPClass


# Implement a handler evt.EVT_N_GET
def handle_get(event):
    """Handle an N-GET request event."""
    attr = event.request.AttributeIdentifierList
    # User defined function to generate the required attribute list dataset
    # implementation is outside the scope of the current example
    # We pretend it returns a pydicom Dataset
    dataset = create_attribute_list(attr)

    # If Display System Management returns an attribute list then the
    # SOP Class UID and SOP Instance UID must always be as given below
    assert dataset.SOPClassUID == '1.2.840.10008.5.1.1.40'
    assert dataset.SOPInstanceUID == '1.2.840.10008.5.1.1.40.1'

    # Return status, dataset
    return 0x0000, dataset


handlers = [(evt.EVT_N_GET, handle_get)]

# Initialise the Application Entity and specify the listen port
ae = AE()

# Add the supported presentation context
ae.add_supported_context(DisplaySystemSOPClass)

# Start listening for incoming association requests
ae.start_server(('', 11112), evt_handlers=handlers)
