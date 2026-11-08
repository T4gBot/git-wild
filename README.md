# git-wild

Nature Exploration by Radio and Data Streams Unlimited (NERDS uc)

*Dropping out of TU Wien to track wildlife in real time.*

---

## Overview

`git-wild` is the central web application and deployment setup for the **NERDS uc Wild Cam Observation Logger**.

The application allows operators to select a live stream, log animal sightings (species, time, and stream ID), and view the full activity log on screen. The app is packaged in a Docker container and deployed across three Ubuntu worker nodes managed via Proxmox, fronted by a Traefik load balancer.

---

## Tech Stack

* **App:** Python / HTML / CSS / JS
* **Runtime:** Docker & Docker Compose
* **Infrastructure:** Proxmox VE (Ubuntu Server VMs)
* **Load Balancer:** Traefik

---

## Features

* **Observation Logging:** Simple input widgets to submit animal sightings per stream.
* **Live Log Output:** Prints all logged observations directly to the screen.
* **Dockerized Setup:** Single-command deployment using Docker Compose across worker nodes.

---

## Setup & Deployment

### Quickstart with Docker Compose

To build and launch the application:

```bash
# Clone the repository
git clone https://github.com/your-username/git-wild.git
cd git-wild

# Start the application
docker compose up -d --build

```

Access the app at `http://localhost:8080` (or your worker VM IP).

To bring the stack down:

```bash
docker compose down

```

---

## Architecture

```text
               [ Client Traffic ]
                       │
                       ▼
            ┌────────────────────┐
            │   Traefik VM       │  (Load Balancer)
            └──────────┬─────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
  ┌───────────┐  ┌───────────┐  ┌───────────┐
  │ Worker 01 │  │ Worker 02 │  │ Worker 03 │  (Ubuntu VMs on Proxmox)
  │ [Docker]  │  │ [Docker]  │  │ [Docker]  │
  └───────────┘  └───────────┘  └───────────┘

```

Traffic routes through the Traefik VM, distributing incoming requests across the three worker VMs running the `git-wild` Docker container.

---

## License

MIT License

