"""
The DICOM Relevant Patient Information Query Service provides a mechanism
 for an SCU to access relevant patient information managed by an SCP.
 This is accomplished through the DIMSE C-FIND service.
"""

from pydicom.dataset import Dataset

from pynetdicom import AE
from pynetdicom.sop_class import GeneralRelevantPatientInformationQuery

# Initialise the Application Entity
ae = AE()

# Add a requested presentation context
ae.add_requested_context(GeneralRelevantPatientInformationQuery)

# Create our Identifier (query) dataset
ds = Dataset()
ds.PatientName = ''
ds.PatientID = '1234567'
ds.ContentTemplateSequence = [Dataset()]
# Request the General Relvant Patient Information template (TID 9007)
# See DICOM Standard, Part 16, Annex A, TID 9000-9007
ds.ContentTemplateSequence[0].MappingResource = 'DCMR'
ds.ContentTemplateSequence[0].TemplateIdentifier = '9007'

# Associate with peer AE at IP 127.0.0.1 and port 11112
assoc = ae.associate('127.0.0.1', 11112)

if assoc.is_established:
    # Use the C-FIND service to send the identifier
    responses = assoc.send_c_find(ds, GeneralRelevantPatientInformationQuery)

    for (status, identifier) in responses:
        if status:
            print('C-FIND query status: 0x{0:04x}'.format(status.Status))

            # If the status is 'Pending' then identifier is the C-FIND response
            if status.Status in (0xFF00, 0xFF01):
                print(identifier)
        else:
            print('Connection timed out, was aborted or received invalid response')

    # Release the association
    assoc.release()
else:
    print('Association rejected, aborted or never connected')