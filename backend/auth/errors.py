from fastapi import HTTPException, status

NoRealmProvidedException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="PVE Authentication Realm Not Provided"
)

CredentialsException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)