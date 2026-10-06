from enum import Enum, unique


@unique
class K8sEnvironment(Enum):
    AKS = "AKS"
    DAWN = "Dawn"
    K3S = "K3s"


@unique
class PodSecurityStandard(Enum):
    RESTRICTED = {"pod-security.kubernetes.io/enforce": "restricted"}
    PRIVILEGED = {"pod-security.kubernetes.io/enforce": "privileged"}


@unique
class TlsEnvironment(Enum):
    STAGING = "staging"
    PRODUCTION = "production"
    DEVELOPMENT = "development"


tls_issuer_names = {
    TlsEnvironment.STAGING: "letsencrypt-staging",
    TlsEnvironment.PRODUCTION: "letsencrypt-prod",
    TlsEnvironment.DEVELOPMENT: "dev-issuer",
}

# Class for software versions - e.g. for helm charts and container images
# where possible, these should be set to specific versions rather than "latest" to ensure reproducibility,
# and protect against breaking changes.
# But in some cases (e.g. curl-jq) no numbered version tags are available.
@unique
class SoftwareVersion(Enum):
    # renovate: datasource=github-releases depName=cert-manager/cert-manager versioning=loose
    CERT_MANAGER = "1.19.4"
    # NOTE: renovate does not track images marked as "latest"
    CURL_JQ = "latest"
    # renovate: datasource=docker depName=haproxy
    HAPROXY = "3.4.6"
    # renovate: datasource=helm depName=harbor registryUrl=https://goharbor.io
    HARBOR = "1.17.1"
    # renovate: datasource=github-releases depName=kubernetes/ingress-nginx
    INGRESS_NGINX = "4.13.2"
    # renovate: datasource=github-releases depName=longhorn/longhorn
    LONGHORN = "1.9.0"
    # renovate: datasource=github-releases depName=netbirdio/netbird
    NETBIRD = "0.80.0"
