import os
from pydicom import dcmread
from pydicom.dataset import Dataset

from pynetdicom import AE, StoragePresentationContexts, evt
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelGet


# Implement the handler for evt.EVT_C_GET
def handle_get(event):
    """Handle a C-GET request event."""
    ds = event.identifier
    if 'QueryRetrieveLevel' not in ds:
        # Failure, OxC000 : Unabled to process
        yield 0xC000, None
        return

    # Import stored SOP Instance
    instances = []
    matching = []
    fdir = '/path/to/directory'
    for fpath in os.listdir(fdir):
        instances.append(dcmread(os.path.join(fdir, fpath)))

    if ds.QueryRetrieveLevel == 'PATIENT':
        if 'PatientID' in ds:
            matching = [
                inst for inst in instances if inst.PatientID == ds.PatientID
            ]

        # Skip the other possible attributes..

    # Skip the other QR levels..

    # Yield the total number of C-STORE sub-operations required
    yield len(instances)

    # Yield the matching instances
    for instance in matching:
        # Check if C-CANCEL has been received
        if event.is_cancelled:
            yield (0xFE00, None)
            return

        # Pending
        yield (0xFF00, instance)


handlers = [(evt.EVT_C_GET, handle_get)]

# Create application entity
ae = AE()

# Add the supported presentation contexts (Storage SCU)
ae.supported_contexts = StoragePresentationContexts

# Accept the association requestor's proposed SCP role in the
# SCP/SCU Role Selection Negotiation items
for cx in ae.supported_contexts:
    cx.scp_role = True
    cx.scu_role = False

# Add a supported presentation context (QR Get SCP)
ae.add_supported_context(PatientRootQueryRetrieveInformationModelGet)

# Start listening for incoming association requests
ae.start_server(('', 11112), evt_handlers=handlers)

