import datetime
import json
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
import jwt


class AuthHandler:
    security = HTTPBearer()
    pwd_context = CryptContext(
        schemes=["sha256_crypt"], deprecated="auto")
    secret = "FARMSTACKsecretString"
    algorithm_hs256 = "HS256"

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def encode_token(self, user_id, username):
        payload = {
            "exp": datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(minutes=30),
            "iat": datetime.datetime.now(datetime.timezone.utc),
            "sub": json.dumps({"user_id": user_id, "username": username}),
        }
        return jwt.encode(payload, self.secret, self.algorithm_hs256)

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=[
                                 self.algorithm_hs256])
            return payload["sub"]
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401, detail=f"Signature has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return self.decode_token(auth.credentials)
