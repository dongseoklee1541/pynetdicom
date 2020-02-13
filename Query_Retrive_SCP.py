import os

from pydicom import dcmread
from pydicom.dataset import Dataset

from pynetdicom import AE, evt
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelFind


# Implement the handler for evt.EVT_C_FIND
def handle_find(event):
    """Handle a C-FIND request event."""
    ds = event.identifier

    # Import stored SOP Instance
    instance = []
    fdir = '/path/to/directory'
    for fpath in os.listdir(fdir):
        instance.append(dcmread(os.path.join(fdir, fpath)))

    if 'QueryRetrieveLevel' not in ds:
        # Failure
        yield 0xC000, None
        return

    if ds.QueryRetrieveLevel == 'PATIENT':
        if 'PatientName' in ds:
            if ds.PatientName not in ['*', '', '?']:
                matching = [
                    inst for inst in instance if inst.PatientName == ds.PatientName
                ]

                # Skip the other possible values

            # Skip the other possible attributes

        # Skip the other QR levels

        for instance in matching:
            # Check if C-CANCEL has been received
            # 만약 event가 취소 됐다면, yield를 통해 값을 반환하고 종료한다.
            if event.is_canceled:
                yield (0xFE00, None)
                return

            identifier = Dataset()
            identifier.PatientName = instance.PatientName
            identifier.QueryRetrieveLevel = ds.QueryRetrieveLevel

            # Pending
            yield (0xFF00, identifier)


handlers = [(evt.EVT_C_FIND, handle_find)]

# Initialise the Application Entity and specify the listen port
ae = AE()

# Add the supported presentation context
ae.add_supported_context(PatientRootQueryRetrieveInformationModelFind)

# Start listening for incoming association requests
ae.start_server(('', 11112), evt_handlers=handlers)


