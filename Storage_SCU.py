from pydicom import dcmread

from pynetdicom import AE
from pynetdicom.sop_class import CTImageStorage

# Initialise the Application Entity
ae = AE()

# Add a requested presentation context
ae.add_requested_context(CTImageStorage)

# Read in our DICOM CT dataset
ds = dcmread('path/to/dataset')

# Associate with peer AE at IP 127.0.0.1 and port 11112
assoc = ae.associate('127.0.0.1', 11112)

if assoc.is_established:
    # Use the C-STORE service to send the dataset
    status = assoc.send_c_store(ds)

    # Check the status of the storage request
    if status:
        # If the storage request succeeded this will be 0x0000
        print('C-STORE request status: 0x{0:04x}'.format(status.Status))
    else:
        print('Connection timed out, was aborted or received invalid response')

    # Release the association
    assoc.release()
else:
    print('Association rejected, aborted or never connected')
