from pydicom.dataset import Dataset

from pynetdicom import(
    AE, evt, build_role,
    PYNETDICOM_IMPLEMENTATION_UID,
    PYNETDICOM_IMPLEMENTATION_VERSION
)
from pynetdicom.sop_class import (
    PatientRootQueryRetrieveInformationModelGet,
    CTImageStorage
)


# Implement the handler for evt.EVT_C_STORE
def handle_store(event):
    """Handle a C-STORE request event."""
    ds = event.dataset
    context = event.context

    # Add the DICOM File Meta Information
    meta = Dataset()
    meta.MediaStorageSOPClassUID = ds.SOPClassUID
    meta.MediaStorageSOPInstanceUID = ds.SOPInstanceUID
    meta.ImplementationClassUID = PYNETDICOM_IMPLEMENTATION_UID
    meta.ImplementationVersionName = PYNETDICOM_IMPLEMENTATION_VERSION
    meta.TransferSyntaxUID = context.transfer_syntax

    # Add the file meta to the dataset
    ds.file_meta = meta

    # Set the transfer syntax attributes of the dataset
    ds.is_little_endian = context.transfer_syntax.is_little_endian
    ds.is_implicit_VR = context.transfer_syntax.is_implicit_VR

    # Save the dataset using the SOP Instance UID as the filename
    # write_like_original : if True(default) preserves information from Dataset
    # and may result in a non-conformant file.
    ds.save_as(ds.SOPInstanceUID, write_like_original=False)

    # Return a 'Success' status
    return 0x0000


handlers = [(evt.EVT_C_STORE, handle_store)]

# Initialise the Application Entity
ae = AE()

# Add the requested presentation contexts (QR SCU)
ae.add_requested_context(PatientRootQueryRetrieveInformationModelGet)
# Add the requested presentation contexts (Storage SCP)
ae.add_requested_context(CTImageStorage)

# Create an SCP/SCU Role Selection Negotiation item for CT Image Storage
role = build_role(CTImageStorage, scp_role=True)

# Create our Identifier (query) dataset
# We need to supply a Unique Key Attribute for each level above the
# Query/Retrieve level
ds = Dataset()
ds.QueryRetrieveLevel = 'SERIES'
# Unique key for PATIENT level
ds.PatientID = '1234567'
ds.StudyInstanceUID = '1.2.3'
# Unique key for SERIES level
ds.SeriesInstanceUID = '1.2.3.4'

# Associate with peer AE at IP 127.0.0.1 and port 11112
assoc = ae.associate('127.0.0.1', 11112, ext_neg=[role], evt_handlers=handlers)

if assoc.is_established:
    # Use the C-GET service to send the identifier
    responses = assoc.send_c_get(ds, PatientRootQueryRetrieveInformationModelGet)

    for (status, identifier) in responses:
        if status:
            print('C-GET query status: 0x{0:04x}'.format(status.Status))

            # If the status is 'Pending' then 'identifier' is the C-GET response
            if status.Status in (0xFF00, 0xFF01):
                print(identifier)
        else:
            print('Connection timed out, was aborted or received invalid response')

    # Release the association
    assoc.release()
else:
    print('Association rejected, aborted or never connected')
