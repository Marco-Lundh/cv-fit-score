import ssl

import truststore

# Use the operating system's trust store so corporate proxies or
# antivirus TLS inspection (common on Windows) are trusted without
# disabling certificate verification.
SSL_CONTEXT = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
