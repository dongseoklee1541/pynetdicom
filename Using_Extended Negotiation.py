from pynetdicom import(
AE, StoragePresentationContexts, QueryRetrievePresentationContexts, build_role
)
from pynetdicom.pdu_primitives import UserIdentityNegotiation

ae = AE()
# Contexts proposed as a QR SCU
ae.requested_contexts = QueryRetrievePresentationContexts
# Contexts supported as a Storage SCP - requires Role Selection
ae.requested_contexts = StoragePresentationContexts

# Add role selection items for the storage contexts we will be supporting
# as an SCP
negotiation_items = []
for context in StoragePresentationContexts:
    role = build_role(context.abstract_syntax, scp_role=True)
    negotiation_items.append(role)

# Add user identity negotiation request
user_identity = UserIdentityNegotiation()
user_identity.user_identity_type = 2
user_identity.primary_field = b'username'
user_identity.secondary_field = b'password'
negotiation_items.append(user_identity)

# Associate with the peer at IP address 127.0.0.1 and port 11112
assoc = ae.associate('127.0.0.1',11112, ext_neg=negotiation_items)

if assoc.is_established:
    assoc.release()