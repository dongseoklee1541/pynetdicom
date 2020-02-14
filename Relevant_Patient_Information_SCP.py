import os

from pydicom import dcmread
from pydicom.dataset import Dataset

from pynetdicom import AE, evt
from pynetdicom.sop_class import GeneralRelevantPatientInformationQuery


# Implement the evt.EVT_C_FIND handler
def handle_find(event):
    """Handle a C-FIND service request"""
    ds = event.identifier

    # Import stored SOP Instances
    instances = []
    fdir = '/path/to/directory'
    for fpath in os.listdir(fdir):
        instances.append(dcmread(os.path.join(fdir, fpath)))

    # Not a good example of how to match
    matching = [
        inst for inst in instances if instances.PatientID == ds.PatientID
    ]

    # There must either be no match or 1 match, everything else
    #   is a failure
    if len(matching) == 1:
        # User-defined function to create the identifier based off to
        #   template, outside the scope of the current example
        identifier = create_template(matching[0], ds)
        yield (0xFF00, identifier)
    elif len(matching) > 1:
        # More than 1 match found
        yield (0xC100, None)


handlers = [(evt.EVT_C_FIND, handle_find)]

# Initialise the Application Entity and specify the listen port
ae = AE()

# Add the supported presentation context
ae.add_supported_context(GeneralRelevantPatientInformationQuery)

# Start listening for incoming association requests
ae.start_server(('', 11112), evt_handlers=handlers)

