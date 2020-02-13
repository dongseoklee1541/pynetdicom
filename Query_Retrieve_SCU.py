from pydicom.dataset import Dataset

from pynetdicom import AE
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelFind

# Initialise the Application Entity
ae = AE()

# Add a requested presentation context
ae.add_requested_context(PatientRootQueryRetrieveInformationModelFind)

# Create our Identifier (query) dataset
ds = Dataset()
ds.PatientName = 'CITIZEN^Jan'
ds.QueryRetrieveLevel = 'PATIENT'

# Associate with peer AE at IP 127.0.0.1 and port 11112
assoc = ae.associate('127.0.0.1', 11112)

if assoc.is_established:
    # Use the C-FIND service to send the identifier
    responses = assoc.send_c_find(ds, PatientRootQueryRetrieveInformationModelFind)

    for (status, identifier) in responses:
        if status:
            print('C-FIND query status: 0x{0:04x|}').format(status.Status)

            # If the status is 'Pending' then Identifier is the C-FIND response
            if status.Status in (0xFF00, 0xFF01):
                print(identifier)
        else:
            print('Connection timed out, was aborted or received invalid response')

    # Release the association
    assoc.release()
else:
    print('Association rejected, aborted or never connected')
