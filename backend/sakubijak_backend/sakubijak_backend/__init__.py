from pyramid.config import Configurator
from pyramid.authorization import ACLAuthorizationPolicy

# Impor JWTAuthenticationPolicy yang baru dibuat
from .security import JWTAuthenticationPolicy 

from pyramid.security import (
    Allow,
    Authenticated,
    ALL_PERMISSIONS
)

class RootACLFactory:
    __acl__ = [
        (Allow, Authenticated, 'view_self'),
        (Allow, Authenticated, 'edit_self'), # Izinkan semua pengguna terautentikasi untuk permission 'view_self'
    ]

    def __init__(self, request):
        pass


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    with Configurator(settings=settings) as config:
        config.include('pyramid_jinja2')
        config.add_jinja2_renderer('.jinja2')

        config.include('.models') 
        config.include('.routes') 

        # 1. Ambil secret key dan algoritma dari settings
        jwt_secret = settings.get('jwt.secret_key')
        jwt_algorithm = settings.get('jwt.algorithm', 'HS256') # Default ke HS256 jika tidak ada

        if not jwt_secret:
            raise ValueError("JWT Secret Key tidak diatur dalam konfigurasi.")

        # 2. Buat instance dari JWTAuthenticationPolicy
        authn_policy = JWTAuthenticationPolicy(secret_key=jwt_secret, algorithm=jwt_algorithm)
        
        # 3. Atur authentication policy
        config.set_authentication_policy(authn_policy)

        # 4. Atur authorization policy
        authz_policy = ACLAuthorizationPolicy()
        config.set_authorization_policy(authz_policy)
        config.set_root_factory(RootACLFactory)

        # Konfigurasi CORS
        config.include('.cors_tween')

        config.scan() 
        
    return config.make_wsgi_app()