from pydicom.dataset import Dataset

from pynetdicom import AE, evt, StoragePresentationContexts
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelMove


def handle_store(event):
    """Handle a C-STORE service request"""
    # Ignore the request and return Success
    return 0x0000


handlers = [(evt.EVT_C_STORE, handle_store)]

# Initialise the Application Entity
ae = AE()

# Add a requested presentation context
ae.supported_contexts(PatientRootQueryRetrieveInformationModelMove)

# Add the Storage SCP's supported presentation contexts
ae.supported_contexts = StoragePresentationContexts

# Start our Storage SCP in non-blocking mode, listening on port 11120
ae.ae_title = b'OUR_STORE_SCP'
scp = ae.start_server(('', 11112), block=False, evt_handlers=handlers)

# Create out identifier (query) dataset
ds = Dataset()
ds.QueryRetrieveLevel = 'SERIES'
# Unique key for PATIENT level
ds.PatientID = '1234567'
# Unique key for STUDY level
ds.StudyInstanceUID = '1.2.3'
# Unique key for SERIES level
ds.SeriesInstanceUID = '1.2.3.4'

# Associate with peer AE at IP 127.0.0.1 and port 11112
assoc = ae.associate('127.0.0.1', 11112)

if assoc.is_established:
    # Use the C-MOVE service to send the identifier
    responses = assoc.send_c_move(ds, b'OUR_STORE_SCP', PatientRootQueryRetrieveInformationModelMove)

    for (status, identifier) in responses:
        if status:
            print('C-MOVE query status: 0x{0:04x}'.format(status.Status))

            # If the status is 'Pending' then 'identifier' is the C-MOVE response
            if status.Status in (0xFF00, 0xFF01):
                print(identifier)
        else:
            print('Connection timed out, was aborted or received invalid response')

    # Release the association
    assoc.release()
else:
    print('Association rejected, aborted or never connected')

# Stop our Storage SCP
scp.shutdown()
