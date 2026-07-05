# OpenChoreo

## What it is

OpenChoreo is an open-source internal developer platform (IDP) for
Kubernetes. It was originally built by WSO2 as the foundation for their
Choreo SaaS product, then open-sourced and contributed to the CNCF, where
it is currently a Sandbox project.

Its goal is to give engineering teams a complete, ready-to-use developer
platform on top of Kubernetes, instead of every team building one from
scratch out of raw Kubernetes primitives (Deployments, Services, Ingress,
NetworkPolicies, etc.).

## What it does

OpenChoreo takes high-level developer and platform intent - things like
"deploy this component", "expose this endpoint", "connect to this other
service" - and translates that into the underlying Kubernetes resources
needed to make it happen. It also reflects the real runtime state back up,
so what a developer sees always matches what is actually running in the
cluster.

Core capabilities:

- **Development abstractions**: Projects, Components, APIs, Environments,
  Namespaces, and Dependencies as first-class concepts instead of raw
  Kubernetes YAML.
- **Built-in CI/CD**: workflow execution (Argo Workflows by default, or
  Tekton, GitHub Actions, etc.) and native GitOps support, so both platform
  and application state can be managed entirely through Git.
- **Developer portal**: a Backstage-powered UI for managing components,
  deployments, and viewing observability data.
- **CLI (`occ`)**: a command-line tool for developers and platform
  engineers to interact with the platform, supporting both live API mode
  and file-system/GitOps mode.
- **Observability**: logs (OpenSearch), metrics (Prometheus), and traces
  (OpenTelemetry), unified under a single Observer API.
- **RBAC/ABAC authorization**: a fine-grained, declarative access-control
  engine (built on Apache Casbin) that applies consistently whether access
  comes from the UI, CLI, API, or MCP servers.
- **AI-native design**: MCP servers exposed by both the control plane and
  the observability plane, so AI agents and assistants (Claude, Cursor,
  Gemini CLI, etc.) can query and operate the platform the same way a human
  would through the UI or CLI. It also ships built-in platform agents (for
  example an SRE/root-cause-analysis agent).

## Architecture

OpenChoreo separates concerns into independently deployable planes:

- **Control Plane**: the API server, controllers, and the authorization
  engine. Also hosts the developer portal, CLI, REST APIs, and MCP servers.
- **Data Plane(s)**: where application workloads actually run, with
  cell-based network isolation between teams/tenants.
- **Workflow Plane**: CI/CD execution.
- **Observability Plane**: logs, metrics, and traces.

These can all run in a single cluster with namespace isolation (common for
local development and evaluation), or be split across dedicated clusters
for production, including across regions.

## Authentication

OpenChoreo integrates with any OAuth2/OIDC-compatible identity provider.
By default it ships with WSO2 Thunder, an open-source identity server, to
make local evaluation straightforward. Authentication is consistent across
every surface - UI, CLI, API, and MCP - since they all go through the same
identity provider and the same authorization engine.

## Local evaluation

OpenChoreo provides a quick-start setup that runs a full instance locally
using Docker and a k3d (k3s-in-Docker) cluster, giving a working platform -
including identity, CI/CD, observability, and a developer portal - in
under 15 minutes without needing any cloud infrastructure.

## Installation (local quick-start)

These are the steps used to get a local OpenChoreo instance running and
reachable, along with the environment fixes required on Windows.

### Requirements

- Docker Desktop (or another Docker-compatible runtime), running
- At least 4 GB RAM and 2 CPUs allocated to Docker (8 GB RAM / 4 CPUs if
  installing with the BuildPlane)
- Python 3.12 with a virtual environment, if connecting to it from a
  Python client

### 1. Run the quick-start container

```powershell
docker run --rm -it --name openchoreo-quick-start `
  --pull always `
  -v /var/run/docker.sock:/var/run/docker.sock `
  --network=host `
  ghcr.io/openchoreo/quick-start:v1.1.1
```

This installer container:

- Creates a k3d (k3s-in-Docker) cluster
- Installs the OpenChoreo control plane, data plane, and dependencies via
  Helm charts
- Deploys a sample web application
- Sets up the identity provider (WSO2 Thunder) and Backstage-based
  developer portal

The installation is idempotent and can be re-run safely if interrupted.

Once complete, `docker ps` should show four containers:

- `k3d-openchoreo-quick-start-server-0` (the k3s node)
- `k3d-openchoreo-quick-start-serverlb` (the k3d proxy/load balancer,
  publishes ports to the host - including `8080`)
- `k3d-openchoreo-quick-start-tools`
- `openchoreo-quick-start` (the installer container itself)

### 2. Fix local DNS resolution (Windows)

OpenChoreo's quick-start setup relies on several `*.localhost` subdomains
that Windows does not resolve by default. These need to be added manually.

Open PowerShell as Administrator:

```powershell
notepad C:\Windows\System32\drivers\etc\hosts
```

Add:

```
127.0.0.1   openchoreo.localhost
127.0.0.1   api.openchoreo.localhost
127.0.0.1   thunder.openchoreo.localhost
```

Save, then flush the DNS cache:

```powershell
ipconfig /flushdns
```

Verify resolution:

```powershell
ping api.openchoreo.localhost
```

### 3. Verify the services are reachable

Check the gateway responds (a `401` here is expected and correct - it
confirms the gateway is up and enforcing authentication):

```powershell
curl.exe -i http://api.openchoreo.localhost:8080/mcp
```

Expected response:

```
HTTP/1.1 401 Unauthorized
www-authenticate: Bearer resource_metadata="http://api.openchoreo.localhost:8080/.well-known/oauth-protected-resource"
{"error":"MISSING_TOKEN","message":"missing or invalid authentication token"}
```

### 4. Access the developer portal

The Backstage-based developer portal is available at:

```
http://openchoreo.localhost:8080/
```

Default local credentials:

```
Username: admin@openchoreo.dev
Password: Admin@123
```
