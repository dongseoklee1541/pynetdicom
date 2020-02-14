from pynetdicom import AE
from pynetdicom.sop_class import VerificationSOPClass

ae = AE()

ae.add_supported_context(VerificationSOPClass)

ae.start_server(('', 11112), block=True)